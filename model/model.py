from dataclasses import dataclass, field
from typing import ClassVar
from PyQt6.QtCore import QTime, QDate
from collections import ChainMap

@dataclass
class EventSpec:
    name: str|None
    shorthand: str|None
    tag: list
    spacing: int

    @classmethod
    def from_dict(cls, data: dict):
        # 由字典创建
        return cls(
            name=data['name'],
            shorthand=data['shorthand'],
            tag=data['tag'],
            spacing=data['spacing']
        )

    @classmethod
    def from_template(cls, data, template_event_spec: 'EventSpec') -> 'EventSpec':
        # 由另一个基事件作为模板创建
        data = ChainMap(data, template_event_spec.__dict__)
        return cls.from_dict(data)

@dataclass
class Event(EventSpec):
    _id_count: ClassVar = 0
    id: int
    start_time: QTime
    end_time: QTime

    @classmethod
    def from_event_spec(cls, event_spec: EventSpec, start_time: QTime, end_time: QTime) -> 'Event':
        # 由基事件构造自身
        return cls(
            id=cls._id(),
            start_time=start_time,
            end_time=end_time,
            **event_spec.__dict__
        )

    @classmethod
    def _id(cls):
        cls._id_count += 1
        return cls._id_count

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return ((isinstance(other, Event) and self.id == other.id) or (self.id == other))

@dataclass
class Timetable:
    name: str
    table: list[list[QTime]]

    def __iter__(self):
        return iter(self.table)

@dataclass
class Schedule:
    name: str
    event_list: list[Event]

    def __iter__(self):
        return iter(self.event_list)

    def __len__(self):
        return len(self.event_list)

    def __getitem__(self, key):
        return self.event_list[key]

class CircularQueue:
    def __init__(self, items, cur: int = 0):
        self.items = list(items)
        self.cur = cur

    def update_cur(self) -> int:
        self.cur = (self.cur + 1) % len(self.items)
        return self.cur

    def get(self):
        item = self.items[self.cur]
        self.update_cur()
        return item

    def peek(self):
        return self.items[self.cur]

    def add(self, item, index: int = -1):
        self.items.insert(item, index)

class ScheduleRotator(CircularQueue):
    def __init__(self, schedule_list: list[Schedule], lastest_date: QDate, cur = 0):
        super().__init__(schedule_list, cur)
        self.lastest_date = lastest_date

    def update_cur(self):
        if self.lastest_date.daysTo(QDate().currentDate()) > 0:
            return super().update_cur()
        else:
            return self.cur

class ScheduleSelector:
    def __init__(self, rule: dict[int: Schedule|CircularQueue]):
        self.rule = rule

    def select(self, date: QDate = QDate.currentDate()) -> Schedule:
        day = date.dayOfWeek()
        match self.rule[day]:
            case Schedule() as schedule:
                selected_schedule = schedule
            case CircularQueue() as circular_queue:
                selected_schedule = circular_queue.get()
        return selected_schedule

if __name__ == '__main__':
    ...