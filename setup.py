#!/usr/bin/env python
# Authors:
# Tomer Filiba
# Stephen Larroque
# Rotorgit
# Angus Gratton
#
# Licensed under the Unlicense or MIT-0 License at your convenience (essentially equivalent to Public Domain).

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

if '--cythonize' in sys.argv or os.getenv('REEDSOLO_CYTHONIZE'):
    # Remove the special argument, otherwise setuptools will raise an exception
    if '--cythonize' in sys.argv:
        sys.argv.remove('--cythonize')
    try:
        # If Cython is installed, transpile the optimized Cython module to C and compile as a .pyd to be distributed
        from Cython.Build import cythonize, build_ext  # this acts as a check whether Cython is installed, otherwise this will fail
        print("Cython is installed, building creedsolo module")
        extensions = cythonize([ Extension('creedsolo', ['creedsolo.pyx']) ], annotate=True, force=True,  # this may fail hard if Cython is installed but there is no C compiler for current Python version, and we have no way to know. Alternatively, we could supply exclude_failures=True , but then for those who really want the cythonized compiled extension, it would be much harder to debug
                        compiler_directives={'embedsignature': True, 'binding': False, 'initializedcheck': True})
        cmdclass = {'build_ext': build_ext}  # avoids the need to call python setup.py build_ext --inplace # TODO: this is likely unnecessary with modern python packaging since using python setup.py as a clip was deprecated
    except ImportError:
        # Else Cython is not installed (or user explicitly wanted to skip)
        # Else run in pure python mode (no compilation)
        print("WARNING: Cython is not installed despite specifying --cythonize, creedsolo module will NOT be built.")
        extensions = None
        cmdclass = {}
elif '--native-compile' in sys.argv:
    sys.argv.remove('--native-compile')
    # Compile pyd from pre-transpiled creedsolo.c
    # Here we use an explicit flag to compile, whereas implicit fallback is recommended by Cython, but in practice it's too difficult to maintain, because some people on Windows have Cython installed but no C compiler https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
    print("Notice: Compiling the creedsolo module from the pre-transpiled creedsolo.c file using the locally installed C compiler...")
    extensions = [ Extension('creedsolo', ['creedsolo.c']) ]
    cmdclass = {}
else:
    extensions = None
    cmdclass = {}
    
with open("README.rst", encoding="utf-8") as f:
    long_description = f.read()    

setup(name = "reedsolo",
    version = "2.0.16b1",
    description = "Pythonic universal errors-and-erasures Reed-Solomon codec to protect your data from errors and bitrot, with a future-proof zero-dependencies pure-python implementation and an optional speed-optimized Cython/C extension.",
    author = "Tomer Filiba",
    author_email = "tomerfiliba@gmail.com",
    maintainer = "Stephen Karl Larroque",
    maintainer_email = "lrq3000@gmail.com",
    license = "Public Domain",  # the license field can only store one license, use classifiers below to declare multiple licenses https://github.com/pypi/warehouse/issues/8960
    project_urls = {
        "Homepage": "https://github.com/tomerfiliba/reedsolomon",
        "Documentation": "https://github.com/tomerfiliba/reedsolomon/blob/master/README.rst",
        "Source": "https://github.com/tomerfiliba/reedsolomon",
        "Tracker": "https://github.com/tomerfiliba/reedsolomon/issues",
        "Download": "https://github.com/tomerfiliba/reedsolomon/releases",
        "Conda-Forge": "https://anaconda.org/conda-forge/reedsolo",
        "Gentoo": "https://packages.gentoo.org/packages/dev-python/reedsolomon",
        },  # see: https://stackoverflow.com/questions/61156290/how-to-set-project-links-in-pypi and https://github.com/pypi/warehouse/blob/main/warehouse/templates/packaging/detail.html
    py_modules = ["reedsolo"],
    platforms = ["any"],
    long_description = long_description,
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
    keywords = ["data", "protection", "correction", "recovery", "restore", "save", "data-recovery", "reed-solomon", "error-correction-code", "qr", "qr-codes", "barcodes"],
    ext_modules = extensions,
    cmdclass = cmdclass,
)

