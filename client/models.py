import json
from dataclasses import dataclass, asdict
from typing import List, Tuple

from client.requests import get_file, put_file


class DirectoryManager:
    Type = 'directory'

    def add(self, name, token):
        if not (name, token) in self.list:
            self.list.append((name, token))

    def remove(self, remove_token):
        remove_name = None
        for name, token in self.list:
            if remove_token == token:
                remove_name = name
        self.list.remove((remove_name, remove_token))

    def put(self):
        data = json.dumps(dict(list=self.list, type=self.Type))
        put_file(self.token, data)

    def fetch(self):
        self.data = json.loads(get_file(self.token))

    def __init__(self, token, data=None):
        if not data:
            self.fetch()
        else:
            self.data = json.loads(data)
        if self.data['type'] != self.Type:
            raise TypeError
        self.list = self.data['list']
        self.token = token
        if not data:
            self.fetch()


@dataclass
class File:
    data: str
    type: str = 'file'

    @staticmethod
    def from_data(data):
        json_data = json.loads(data)
        return File(**json_data)

    def to_data(self):
        return json.dumps(asdict(self))


@dataclass
class Directory:
    list: List[Tuple[str, str]]
    type: str = 'directory'

    @staticmethod
    def from_data(data):
        json_data = json.loads(data)
        if json_data != 'directory':
            raise TypeError
        return File(**json_data)

    def to_data(self):
        return json.dumps(asdict(self))
