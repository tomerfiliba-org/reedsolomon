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

if '--cythonize' in sys.argv:
    # Remove the special argument, otherwise setuptools will raise an exception
    sys.argv.remove('--cythonize')
    try:
        # If Cython is installed, transpile the optimized Cython module to C and compile as a .pyd to be distributed
        from Cython.Build import cythonize, build_ext  # this acts as a check whether Cython is installed, otherwise this will fail
        print("Cython is installed, building creedsolo module")
        extensions = cythonize([ Extension('creedsolo', ['creedsolo.pyx']) ], force=True)  # this may fail hard if Cython is installed but there is no C compiler for current Python version, and we have no way to know. Alternatively, we could supply exclude_failures=True , but then for those who really want the cythonized compiled extension, it would be much harder to debug
        cmdclass = {'build_ext': build_ext}  # avoids the need to call python setup.py build_ext --inplace
    except ImportError:
        # Else Cython is not installed (or user explicitly wanted to skip)
        #if '--native-compile' in sys.argv:
            # Compile pyd from pre-transpiled creedsolo.c
            # This is recommended by Cython, but in practice it's too difficult to maintain https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
            #print("Cython is not installed, but the creedsolo module will be built from the pre-transpiled creedsolo.c file using the locally installed C compiler")
            #sys.argv.remove('--native-compile')
            #extensions = [ Extension('creedsolo', ['creedsolo.c']) ]
        #else:
        # Else run in pure python mode (no compilation)
        print("Cython is not installed or is explicitly skipped using --nocython, no creedsolo module will be built")
        extensions = None
        cmdclass = {}
else:
    extensions = None
    cmdclass = {}

setup(name = "reedsolo",
    version = "1.7.0",
    description = "Pure-Python Reed Solomon encoder/decoder",
    author = "Tomer Filiba",
    author_email = "tomerfiliba@gmail.com",
    maintainer = "Stephen Karl Larroque",
    maintainer_email = "lrq3000@gmail.com",
    license = "Public Domain",  # the license field can only store one license, use classifiers below to declare multiple licenses https://github.com/pypi/warehouse/issues/8960
    url = "https://github.com/tomerfiliba/reedsolomon",
    py_modules = ["reedsolo"],
    platforms = ["any"],
    long_description = open("README.rst", "r").read(),
    long_description_content_type = 'text/x-rst',
    license_files = ('LICENSE',),  # force include LICENSE file, requires setuptools >= 42.0.0. Note that this field only support one line text, do not input the full license content here. The full LICENSE file is currently forcefully included via MANIFEST.in, but other methods exist, see: https://stackoverflow.com/a/66443941/1121352
    classifiers = [
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: The Unlicense (Unlicense)",  # Unlicense OR MIT-0 at the user preference
        "License :: OSI Approved :: MIT No Attribution License (MIT-0)",
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Cython",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Recovery Tools",
    ],
    ext_modules = extensions,
    cmdclass = cmdclass,
)

