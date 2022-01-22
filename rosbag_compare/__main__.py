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
