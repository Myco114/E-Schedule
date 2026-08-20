'''解析器父类'''

class BaseParser:
    def __init__(self, data: dict):
        self.data = data

    def parse(self):
        ...