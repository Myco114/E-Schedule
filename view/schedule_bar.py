from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QWidget
from model.model import Schedule, Event
from view.widget import EventBar

class ScheduleBar(QMainWindow):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self.init_ui()

    def init_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.setStyleSheet(self.data['qss'])

        self.event_bar = EventBar(self.data['event bar'])

    def set_displayed_schedule(self, schedule: Schedule):
        self.event_bar.set_schedule(schedule=schedule)

if __name__ == '__main__':
    from data_file_parser.main_parser import MainParser
    from PyQt6.QtWidgets import QApplication
    main_parser = MainParser()
    app = QApplication([])
    schedule_bar = ScheduleBar(main_parser.data['schedule bar'])
    schedule_bar.show()
    app.exec()
