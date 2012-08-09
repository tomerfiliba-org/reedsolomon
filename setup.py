#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name = "reedsolo",
    version = "0.3",
    description = "Pure-Python Reed Solomon encoder/decoder",
    author = "Tomer Filiba",
    author_email = "tomerfiliba@gmail.com",
    license = "Public Domain",
    url = "https://github.com/tomerfiliba/reedsolomon",
    py_modules = ["reedsolo"],
    platforms = ["POSIX", "Windows"],
    long_description = open("README.rst", "r").read(),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: Public Domain",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)

