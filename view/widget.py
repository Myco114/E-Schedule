from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy, QSpacerItem
from PyQt6.QtCore import pyqtSignal, QTime, QTimer
from model.model import Schedule, Event

class EventBar(QWidget):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self._event_2_label: dict[Event: QLabel] = {}
        self._layout = QHBoxLayout(self)
        self._layout.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def set_schedule(self, schedule: Schedule):
        # 设定所展示的课表
        self.schedule = schedule
        self._event_2_label.clear()
        self.init_ui()

    def display_schedule(self):
        # 显示课表
        schedule_name = self.schedule.name
        name_label = QLabel(schedule_name)
        name_label.setObjectName('EventBar_name')
        self._layout.addWidget(name_label)
        self._layout.addSpacing(self.data['name spacing'])
        self._event_2_label['name'] = name_label
        for event in self.schedule:
            if self._is_visible(event):
                label = QLabel(event.shorthand)
                label.setObjectName('EventBar_event')
                label.setProperty('state', 'to_do')
                self._layout.addWidget(label)
                self._event_2_label[event] = label
            if event.spacing:
                self._layout.addSpacing(event.spacing)
        # 若最后一个为spacing 则删除掉
        count = self._layout.count()
        lastest_item = self._layout.itemAt(count-1)
        if isinstance(lastest_item, QSpacerItem):
            self._layout.removeItem(lastest_item)

    def _is_visible(self, event: Event) -> bool:
        visible = False
        for tag in event.tag:
            if tag in self.data['visible tag']:
                visible = True
                break
        return visible

class Clock(QLabel):
    def __init__(self, data: dict):
        super().__init__(QTime(11, 45, 14).toString(data['format']))
        self.data = data
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)

    def _update_time(self):
        text = QTime.currentTime().toString(self.data['format'])
        self.setText(text)