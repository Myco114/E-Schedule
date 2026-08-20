import pathlib
from data_file_parser.base_parser import BaseParser

class QSSParser(BaseParser):
    def __init__(self, data: dict, path: str):
        super().__init__(data=data)
        self.path = pathlib.Path(path)
        if not self.path.is_dir():
            self._init_file()

    def _init_file(self):
        ...

    def _load(self, path: pathlib.Path):
        # 读取单个文件数据
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
        return data

    def parse(self):
        file_list = self.path.iterdir()
        for file in file_list:
            stem = file.stem
            data = self._load(file)
            self.data[stem]['qss'] = data

if __name__ == '__main__':
    qss_parser = QSSParser({'schedule bar': {}}, 'data/qss')
    qss_parser.parse()
    print(qss_parser.data)