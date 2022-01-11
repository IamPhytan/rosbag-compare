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
        self.topics = {}

    def extract_data(self):
        """Extract all the topics cointaned in the rosbags at the path {self.folder}"""
        paths = list(self.folder.glob("*.bag"))

        if len(paths) == 0:
            # Empty list of paths
            raise RuntimeWarning(f"Specified folder {self.folder} contains no bagfiles")

        if self.topics:
            # Topics have already been extracted
            warnings.warn(
                "Topics are already exported, yet the topics dict will be recreated.",
                RuntimeWarning,
            )

        # Create a dictionary with the list of topics for each bag file
        # {file1: ["/topic1", ...], ...}
        topics = {}
        with tqdm(total=len(paths)) as pbar:
            for bagfile in paths:
                pbar.set_description(bagfile.stem)
                topics[bagfile.stem] = self.get_topics(bagfile)
                pbar.update(1)

        # Make a set with all the topics and get the missing topics
        # for each file
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
        """Get a list of the topics in a rosbag file

        Args:
            filename (Union[Path, str]): path of the rosbag file

        Returns:
            [type]: list of the topics contained in the rosbag file
        """
        with Reader(filename) as bag:
            return list(bag.topics.keys())

    def to_json(self, p: Union[Path, str] = None):
        """Export topics dictionary to a json file

        Args:
            p (Union[Path, str], optional): path of the json file.
            If None, the topics will be saved in topics_<foldername>.json.
        """
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
