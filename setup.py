from pathlib import Path

from setuptools import setup

PROJDIR = Path(__file__).resolve().parent
README = (PROJDIR / "README.md").read_text()

setup(
    name="rosbag-compare",
    version="0.1.1",
    description="Compare topics between rosbags",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/IamPhytan/rosbag-compare",
    author="damienlarocque",
    author_email="phicoltan@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["rosbag_compare"],
    install_requires=["rosbags", "tqdm", "matplotlib"],
    entry_points={
        "console_scripts": [
            "rosbag-compare=rosbag_compare.__main__:main",
        ]
    },
    include_package_data=True,
)
