from dataclasses import dataclass, asdict
from encodings.base64_codec import base64_encode, base64_decode
from typing import List, Tuple


@dataclass
class File:
    data: str
    type: str = 'file'

    @staticmethod
    def from_data(data):
        json_data = base64_decode(data)
        return File(**json_data)

    def to_data(self):
        return base64_encode(asdict(self))


@dataclass
class Directory:
    list: List[Tuple[str, str]]
    type: str = 'directory'

    @staticmethod
    def from_data(data):
        json_data = base64_decode(data)
        return File(**json_data)

    def to_data(self):
        return base64_encode(asdict(self))
