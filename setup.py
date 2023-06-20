import setuptools
from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="social-blade-scraper",
    version="0.0.1",
    description="Social blade scraper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/tejmagar/social-blade-scraper",
    install_requires=[
        "beautifulsoup4",
        "requests",
        "fake-useragent"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(
        where='src',
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
