#!/usr/bin/env python
# Authors:
# Tomer Filiba
# Stephen Larroque
# Rotorgit
# Angus Gratton
#
# Licensed under the Public Domain or MIT License at your convenience.

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

import os, sys

try:
    # Test if Cython is installed
    if '--nocython' in sys.argv:
        # Skip if user does not want to use Cython
        sys.argv.remove('--nocython')
        raise(ImportError('Skip Cython'))
    # If Cython is installed, transpile the optimized Cython module to C and compile as a .pyd to be distributed
    from Cython.Build import cythonize
    print("Cython is installed, building creedsolo module")
    extensions = cythonize([ Extension('creedsolo', ['creedsolo.pyx']) ], force=True)
except ImportError:
    # Else Cython is not installed (or user explicitly wanted to skip)
    if '--native-compile' in sys.argv:
        # Compile pyd from pre-transpiled creedsolo.c
        print("Cython is not installed, but the creedsolo module will be built from the pre-transpiled creedsolo.c file using the locally installed C compiler")
        sys.argv.remove('--native-compile')
        extensions = [ Extension('creedsolo', ['creedsolo.c']) ]
    else:
        # Else run in pure python mode (no compilation)
        print("Cython is not installed or is explicitly skipped using --nocython, no creedsolo module will be built")
        extensions = None

setup(name = "reedsolo",
    version = "1.5.4",
    description = "Pure-Python Reed Solomon encoder/decoder",
    author = "Tomer Filiba",
    author_email = "tomerfiliba@gmail.com",
    maintainer = "Stephen Karl Larroque",
    maintainer_email = "lrq3000@gmail.com",
    license = "Public Domain",
    url = "https://github.com/tomerfiliba/reedsolomon",
    py_modules = ["reedsolo"],
    platforms = ["any"],
    long_description = open("README.rst", "r").read(),
    long_description_content_type = 'text/x-rst',
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Cython",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Recovery Tools",
    ],
    ext_modules = extensions,
)

