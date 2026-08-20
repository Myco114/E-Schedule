from data_file_parser.json_parser import JsonFileParser
from data_file_parser.qss_parser import QSSParser
from data_file_parser.parser import Parser

class MainParser:
    PARSER_TABLE = [
        {
            'parser': JsonFileParser,
            'kwargs': {
                'path': 'data/data.json'
            }
        },
        {
            'parser': QSSParser,
            'kwargs': {
                'path': 'data/qss'
            }
        }
    ]

    def __init__(self):
        self.data = {}
        for parser_config in self.PARSER_TABLE:
            parser: Parser = parser_config['parser'](data=self.data, **parser_config['kwargs'])
            parser.parse()