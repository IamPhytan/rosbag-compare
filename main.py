"""Rosbag comparator - Compare topics between ROS1 rosbags"""

import json
import warnings
from itertools import chain
from pathlib import Path
from typing import Union

import matplotlib as mtp
import matplotlib.pyplot as plt
from rosbags.rosbag1 import Reader
from tqdm import tqdm


class RosbagComparator:
    """Rosbag Comparator : Compare the topics of a list of rosbags.
    Determine which topics are missing for each rosbag, by comparing with others"""

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
        print(f"Extracting topics from {len(paths)} rosbags in {self.folder.name}")
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

    def verify_data_extraction(self):
        """Assert that extract_data() was called.
        Else, this will call extract_data()"""
        if not self.topics:
            warnings.warn(
                "Topics are not extracted."
                "Use extract_data() before using to_json() instead",
                RuntimeWarning,
            )
            self.extract_data()

    def to_json(self, path: Union[Path, str] = None):
        """Export topics dictionary to a json file

        Args:
            p (Union[Path, str], optional): path of the json file.
            If None, the topics will be saved in topics_<foldername>.json.
        """
        self.verify_data_extraction()

        path = f"topics_{self.folder.name}.json" if path is None else path
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.topics, file)

    def plot(self, img_path: Union[Path, str] = None):
        """Show the missing topics between the rosbags in each bag using a scatterplot with matplotlib

        Args:
            img_path (Union[Path, str], optional): Figure export path. Defaults to None. If None, figure will be saved in `missing_topics.png`
        """
        self.verify_data_extraction()

        # Get the difference dictionary
        diff = self.topics["difference"]
        # Create a set of all topics inside difference values
        diff_set = set(chain.from_iterable(diff.values()))

        # Names and topics list, sorted topics list
        names_list = list(diff.keys())
        tops_list = list(diff_set)
        tops_sort = sorted(tops_list)

        # Instantiate figure
        fig, ax = plt.subplots(figsize=(10, 5))

        # Function to create sorted axes labels
        def axsetter(xunits, yunits, ax=None, sort=True, reversed_y=True):
            ax = ax or plt.gca()
            if sort:
                xunits = sorted(xunits)
                yunits = sorted(yunits, reverse=reversed_y)
            us = plt.plot(
                xunits, [yunits[0]] * len(xunits), [xunits[0]] * len(yunits), yunits
            )
            for u in us:
                u.remove()

        # Sort axes labels
        axsetter(names_list, tops_list, ax=ax)

        # Sorted diff dict
        diff_sort = {k: sorted(v) for k, v in sorted(diff.items())}

        # Colors normalisation
        norm = mtp.colors.Normalize(vmin=0, vmax=len(tops_sort) - 1)
        colors = {k: norm(i) for i, k in enumerate(tops_sort)}

        for run, tops in diff_sort.items():
            cols = [plt.cm.turbo(colors[top]) for top in tops]
            ax.scatter([run] * len(tops), tops, c=cols, cmap="turbo")

        # plt.draw()
        # ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

        fig.suptitle(f"Missing topics in the rosbags of '{self.folder.name}'")
        plt.tight_layout()
        plt.show()

        path = img_path or "missing_topics.png"
        fig.savefig(path)


if __name__ == "__main__":
    data_path = Path("data")
    rosbag_comp = RosbagComparator(data_path)
    rosbag_comp.extract_data()
    rosbag_comp.to_json()
    rosbag_comp.plot()
