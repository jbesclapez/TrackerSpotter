"""
TrackerSpotter - Local BitTorrent Tracker Monitor
Setup configuration for package distribution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="trackerspotter",
    version="1.0.0",
    author="TrackerSpotter Contributors",
    author_email="",
    description="Local BitTorrent tracker monitor for validating client behavior",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jbesclapez/TrackerSpotter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "trackerspotter": [
            "static/**/*",
            "templates/**/*",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Networking :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.9",
    install_requires=[
        "Flask>=3.0.0",
        "Flask-SocketIO>=5.3.6",
        "python-socketio>=5.11.0",
        "bencodepy>=0.9.5",
    ],
    entry_points={
        "console_scripts": [
            "trackerspotter=trackerspotter.main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/jbesclapez/TrackerSpotter/issues",
        "Source": "https://github.com/jbesclapez/TrackerSpotter",
    },
)

