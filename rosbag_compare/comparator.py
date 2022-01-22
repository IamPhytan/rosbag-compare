"""Comparator class for comparing topics between ROS1 rosbags"""

from __future__ import annotations

import json
import warnings
from itertools import chain
from pathlib import Path
from typing import List, Union

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

    @classmethod
    def from_dict(cls, topics: dict) -> RosbagComparator:
        """Instantiate RosbagComparator with a topics dictionary

        Args:
            topics (dict): Topics dictionary

        Returns:
            RosbagComparator: Instance of RosbagComparator
        """
        folder_name = Path.cwd()
        rbag_comp = cls(folder_name)
        rbag_comp.topics = topics
        return rbag_comp

    @classmethod
    def from_json(cls, json_path: Union[Path, str]) -> RosbagComparator:
        """Instantiate RosbagComparator from a JSON file path

        Args:
            json_path (Union[Path, str]): Path to a JSON file

        Returns:
            RosbagComparator: Instance of RosbagComparator
        """
        with open(json_path, "r", encoding="utf-8") as file:
            return cls.from_dict(json.load(file))

    def extract_data(self) -> None:
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

    @staticmethod
    def get_topics(filename: Union[Path, str]) -> List:
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

    def to_json(self, path: Union[Path, str] = None) -> None:
        """Export topics dictionary to a json file

        Args:
            p (Union[Path, str], optional): path of the json file.
            If None, the topics will be saved in topics_<foldername>.json.
        """
        self.verify_data_extraction()

        path = f"topics_{self.folder.name}.json" if path is None else path
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.topics, file)

    def plot(self, save_fig: bool = False, img_path: Union[Path, str] = None) -> None:
        """Show the missing topics between the rosbags in each bag
         using a scatterplot with matplotlib

        Args:
            save_fig (bool, optional): Indicate whether or not the generated figure will be saved. Defaults to False
            img_path (Union[Path, str], optional): Figure export path.
            Defaults to None. If None, figure will be saved in `missing_topics.png`
        """
        self.verify_data_extraction()

        # Get the difference dictionary
        diff = self.topics["difference"]
        # Create a set of all topics inside difference values
        diff_set = set(chain.from_iterable(diff.values()))

        # Topics list and sorted topics list
        tops_list = list(diff_set)
        tops_sort = sorted(tops_list)

        # Instantiate figure
        fig, ax = plt.subplots(figsize=(10, 7.5), num="Missing topics comparison")

        # Function to create sorted axes labels
        def axsetter(xunits, yunits, ax=None, sort=True, reversed_y=True):
            ax = ax or plt.gca()
            if sort:
                xunits = sorted(xunits)
                yunits = sorted(yunits, reverse=reversed_y)
            units = plt.plot(
                xunits, [yunits[0]] * len(xunits), [xunits[0]] * len(yunits), yunits
            )
            for unit in units:
                unit.remove()

        # Sort axes labels
        axsetter(list(diff.keys()), tops_list, ax=ax)

        # Sorted diff dict
        diff_sort = {k: sorted(v) for k, v in sorted(diff.items())}

        # Colors normalisation
        norm = mtp.colors.Normalize(vmin=0, vmax=len(tops_sort) - 1)
        colors = {k: norm(i) for i, k in enumerate(tops_sort)}

        for name, tops in diff_sort.items():
            cols = [plt.cm.turbo(colors[top]) for top in tops]
            ax.scatter([name] * len(tops), tops, c=cols, cmap="turbo")

        # Rotate x axis labels by 45 degrees
        ax.set_xticklabels(sorted(list(diff.keys())), rotation=45, ha="right")

        # Figure parameters
        fig.suptitle(f"Missing topics in the rosbags of '{self.folder.name}'")
        plt.tight_layout()

        if save_fig:
            # Save figure to file
            fig.savefig(img_path or "missing_topics.png")

        # Show figure
        plt.show()
