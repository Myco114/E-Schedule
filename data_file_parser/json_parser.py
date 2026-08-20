import json
import pathlib
from copy import deepcopy
from model.model import EventSpec, Event, Timetable, Schedule, ScheduleSelector, ScheduleRotator
from data_file_parser.base_parser import BaseParser
from PyQt6.QtCore import QTime, QDate
from collections import ChainMap

class ScheduleDataParser:
    def __init__(self, data: dict, original_data: dict):
        self.data = data
        self.original_data = original_data
        self._parsed_event_spec: dict[str: EventSpec] = {}
        self._parsed_timetable: dict[str: Timetable] = {}
        self._parsed_schedule: dict[str: Schedule] = {}
        self._parsed_schedule_selector: ScheduleSelector = None

    def parse(self) -> dict:
        for event_spec_key in self.original_data['event spec']:
            self._parse_event_spec(event_spec_key)
        for timetable_key in self.original_data['timetable']:
            self._parse_timetable(timetable_key)
        for schedule_key in self.original_data['schedule']:
            self._parse_schedule(schedule_key)
        self._parse_schedule_selector()
        # 同步至data
        to_list = lambda _dict: list(_dict.values())
        self.data['event spec'] = to_list(self._parsed_event_spec)
        self.data['timetable'] = to_list(self._parsed_timetable)
        self.data['schedule'] = to_list(self._parsed_schedule)
        self.data['schedule selector'] = self._parsed_schedule_selector

    def _parse_schedule_selector(self) -> ScheduleSelector:
        '''
        用于解析课表选择器
        '''
        data = self.original_data['schedule selector']
        rule_data = data['rule']
        rule = {}
        for day in rule_data:
            match rule_data[day]:
                case str() as schedule_key:
                    _rule = self._parse_schedule(schedule_key)
                case int() as other_day:
                    _rule = rule[other_day]
                case dict() as circular_rule:
                    schedule_list = [self._parse_schedule(schedule_key) for schedule_key in circular_rule['schedule_list']]
                    lastest_date = QDate(*circular_rule['lastest_date'])
                    _rule = ScheduleRotator(schedule_list, lastest_date, cur=circular_rule['lastest_index'])
            rule[int(day)] = _rule
        self._parsed_schedule_selector = ScheduleSelector(rule)
        return self._parsed_schedule_selector

    def _parse_schedule(self, schedule_key: str) -> Schedule:
        '''
        用于解析单个课表
        '''
        if schedule_key in self._parsed_schedule:
            schedule = self._parsed_schedule[schedule_key]
        else:
            schedule_data = self.original_data['schedule'][schedule_key]
            if 'extend' in schedule_data:
                template_data = self.original_data['schedule template'][schedule_data['extend']]
                event_spec_list_data = self._parse_extended_event_spec_list(
                    schedule_data['event_spec_list'], template_data['event_spec_list']
                )
                schedule_data = ChainMap({'event_spec_list': event_spec_list_data}, schedule_data, template_data)
            event_spec_list_data = schedule_data['event_spec_list']
            timetable = self._parse_timetable(schedule_data['timetable'])
            event_list = [Event.from_event_spec(self._parse_event_spec(event_spec_data), start, end) \
                          for event_spec_data, (start, end) in zip(event_spec_list_data, timetable)]
            schedule = Schedule(name=schedule_data['name'], event_list=event_list)
            self._parsed_schedule[schedule_key] = schedule
        return schedule

    def _parse_extended_event_spec_list(self, event_spec_list_data: list[str], template_event_spec_list_data: list[str|int]) -> list[Event]:
        '''
        用于解析课表事件列表的继承
        '''
        merged_event_spec_list_data = []
        for _ in template_event_spec_list_data:
            match _:
                case str() as key:
                    merged_event_spec_list_data.append(key)
                case int() as index:
                    merged_event_spec_list_data.append(event_spec_list_data[index])
        return merged_event_spec_list_data

    def _parse_timetable(self, timetable_key: str) -> Timetable:
        '''
        用于解析单个时间表 timetable
        '''
        if timetable_key in self._parsed_timetable:
            timetable = self._parsed_timetable[timetable_key]
        else:
            timetable_data: dict = self.original_data['timetable'][timetable_key]
            match timetable_type := timetable_data.get('type', 'default'):
                case 'default':
                    table = timetable_data['table']
                case 'linear':
                    table = [ [timetable_data['table'][i], timetable_data['table'][i+1]] \
                            for i in range(len(timetable_data['table']) - 1) ]
                case _:
                    raise ValueError(f'无效的时间表类型: {timetable_type}')
            QTime_table = [[QTime(*start), QTime(*end)] for start, end in table]
            timetable = Timetable(name=timetable_data['name'], table=QTime_table)
            self._parsed_timetable[timetable_key] = timetable
        return timetable

    def _parse_event_spec(self, event_spec_key: str) -> EventSpec:
        '''
        用于解析单个基事件 event_spec
        '''
        if event_spec_key in self._parsed_event_spec:
            # 若已被解析 则直接查表
            event_spec = self._parsed_event_spec[event_spec_key]
        else:
            DEFAULT_DATA = {
                'name': None,
                'shorthand': None,
                'tag': deepcopy([]),
                'spacing': 0
            }
            event_spec_data = self.original_data['event spec'][event_spec_key]
            if 'extend' in event_spec_data:
                # 若存在继承字段 则先获取被继承的基事件 然后用 EventSpec.from_template() 创建
                template_key = event_spec_data['extend']
                template_event_spec = self._parse_event_spec(template_key)
                event_spec = EventSpec.from_template(event_spec_data, template_event_spec)
            else:
                event_spec = EventSpec.from_dict(ChainMap(event_spec_data, DEFAULT_DATA))
            self._parsed_event_spec[event_spec_key] = event_spec
        return event_spec

class JsonFileParser(BaseParser):
    DEFAULT_DATA = {
        'Schedule Data': {
            'event spec': [],
            'schedule': [],
            'selector': ...
        }
    }

    def __init__(self, data: dict, path: str|pathlib.Path):
        super().__init__(data=data)
        self.path = pathlib.Path(path)
        if not self.path.exists():
            self._init_file()
        # original_data = deepcopy(self.DEFAULT_DATA)

    def parse(self) -> dict:
        self.load()
        self.parse_schedule_data()

    def _init_file(self):
        pass

    def load(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            self.oringinal_data = json.load(f)
        return self.oringinal_data

    def parse_schedule_data(self):
        self.schedule_data_parser = ScheduleDataParser(self.data, self.oringinal_data['Schedule Data'])
        self.schedule_data_parser.parse()

    def on_data_modified(self, path: list[str], new_data):
        pass

if __name__ == '__main__':
    print('hello vscode')
    jfp = JsonFileParser({}, 'data/data.json')
    jfp.parse()
    print(jfp.data)
    # jfp.schedule_data_parser._parse_schedule('A')
    # print(jfp.schedule_data_parser._parsed_schedule)