"""Rosbag comparator - Compare topics between ROS1 rosbags"""

import json
import warnings
from pathlib import Path
from typing import Union

from rosbags.rosbag1 import Reader
from tqdm import tqdm


class RosbagComparator:
    def __init__(self, path: Union[Path, str]) -> None:
        self._folder = Path(path)
        self.paths = list(self.folder.glob("*.bag"))
        self.topics = {}

    def extract_data(self):
        """Extract the list of topics from the rosbags"""
        if len(self.paths) == 0:
            # Empty list of paths
            raise RuntimeWarning(f"Specified folder {self.folder} contains no bagfiles")

        if self.topics:
            # Topics have already been extracted
            warnings.warn(
                "Topics are already exported, yet the topics dict will be recreated.",
                RuntimeWarning,
            )

        topics = {}
        with tqdm(total=len(self.paths)) as pbar:
            for bagfile in self.paths:
                pbar.set_description(bagfile.stem)
                topics[bagfile.stem] = self.get_topics(bagfile)
                pbar.update(1)

        common_set = set().union(*topics.values())
        differences = {stem: common_set - set(top) for stem, top in topics.items()}
        differences = {s: list(d) for s, d in differences.items()}

        self.topics = {
            "topics": topics,
            "difference": differences,
            "common": list(common_set),
        }

    @property
    def folder(self):
        """The folder property."""
        return self._folder

    @folder.setter
    def folder(self, value: Union[Path, str]):
        """Setter for `folder`"""
        if Path(value).is_dir():
            self._folder = value
        else:
            raise ValueError(f"{value} is not a valid directory")

    @staticmethod
    def get_topics(filename: Union[Path, str]):
        """Get topics from a filename"""
        with Reader(filename) as bag:
            return list(bag.topics.keys())

    def to_json(self, p: Union[Path, str] = None):
        if not self.topics:
            warnings.warn(
                "Topics are not extracted."
                "Use extract_data() before using to_json() instead",
                RuntimeWarning,
            )
            self.extract_data()

        p = f"topics_{self.folder.name}.json" if p is None else p
        with open(p, "w") as f:
            json.dump(self.topics, f)


if __name__ == "__main__":
    data_path = Path("data")
    rosbag_comp = RosbagComparator(data_path)
    rosbag_comp.extract_data()
    rosbag_comp.to_json()
