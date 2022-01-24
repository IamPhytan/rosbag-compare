"""Rosbags topic comparator

Usage:
------

 $ rosbag-compare [OPTIONS] -b BAGFOLDER

Compare the topics in rosbags inside BAGFOLDER and summarize in a JSON file:

 $ rosbag-compare -b path/to/BAGFOLDER

Compare the topics in rosbags inside BAGFOLDER, summarize in a JSON file
    and plot missing topics in each rosbag:

 $ rosbag-compare -b path/to/BAGFOLDER -p

Available options are:

 -h, --help                                Show this help
 -b BAGFOLDER, --bagfolder BAGFOLDER       Path to folder with rosbags
 -p, --plot                                Optional. Plot missing topics

Version:
--------

- rosbag-compare v0.1.1
"""


import argparse
from pathlib import Path

from .comparator import RosbagComparator


def parse_arguments():
    """Parse bagfile name"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b",
        "--bagfolder",
        help="""Path to the folder that contains rosbags""",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--plot",
        help="Flag for plotting and showing the result",
        action="store_true",
    )
    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()
    data_path = Path(args.bagfolder)
    is_plot = args.plot
    rosbag_comp = RosbagComparator(data_path)
    rosbag_comp.extract_data()
    rosbag_comp.to_json()
    if is_plot:
        rosbag_comp.plot()


if __name__ == "__main__":
    main()
