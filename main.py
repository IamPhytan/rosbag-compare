import json
from pathlib import Path
from typing import Union
from rosbags.rosbag1 import Reader


class RosbagComparator:
    def __init__(self, path: Union[Path, str]) -> None:
        self._folder = Path(path)
        self.paths = self._folder.glob("*.bag")
        self.topics_dict = {}

    @property
    def folder(self):
        """The folder property."""
        return self._folder

    @folder.setter
    def folder(self, value: Union[Path, str]):
        if Path(value).is_dir():
            self._folder = value
        else:
            raise ValueError(f"{value} is not a valid directory")

    @staticmethod
    def get_topics(filename: Union[Path, str]):
        with Reader(filename) as bag:
            return list(bag.topics.keys())

    def get_bagfilepaths(self):
        return self.paths

    def to_json(self, p: Union[Path, str] = None):
        p = f"topics_{self.folder.name}.json" if p is None else p
        with open(p, "w") as f:
            json.dump(self.topics_dict, f)


if __name__ == "__main__":
    data_path = Path("data")
    rosbag_comp = RosbagComparator(data_path)
    rosbag_comp.to_json()
