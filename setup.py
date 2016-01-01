#!/usr/bin/env python

# See:
# https://docs.python.org/2/distutils/setupscript.html
# http://docs.cython.org/src/reference/compilation.html
# https://docs.python.org/2/extending/building.html
# http://docs.cython.org/src/userguide/source_files_and_compilation.html

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

import os

try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

ext = '.pyx' if USE_CYTHON else '.c'

extensions = [
                        Extension('creedsolo', [os.path.join('creedsolo'+ext)]),
                    ]

if USE_CYTHON: extensions = cythonize(extensions)

setup(name = "reedsolo",
    version = "1.2.0",
    description = "Pure-Python Reed Solomon encoder/decoder",
    author = "Tomer Filiba",
    author_email = "tomerfiliba@gmail.com",
    license = "Public Domain",
    url = "https://github.com/tomerfiliba/reedsolomon",
    py_modules = ["reedsolo"],
    platforms = ["any"],
    long_description = open("README.rst", "r").read(),
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Cython",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Recovery Tools",
    ],
    ext_modules = extensions,
)

