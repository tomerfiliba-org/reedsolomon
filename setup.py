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

if '--cythonize' in sys.argv or os.getenv('REEDSOLO_CYTHONIZE'):  # --cythonize is usable through PEP517 by supplying --config-setting="--build-option=--cythonize" in PEP517-compliant tools (pip, build, setuptools, pytest, cibuildwheel). REEDSOLO_CYTHONIZE env variable was necessary before for cibuildwheel but not anymore, it is only kept as an alternative option, but is not used.
    # Remove the special argument, otherwise setuptools will raise an exception
    if '--cythonize' in sys.argv:
        sys.argv.remove('--cythonize')
    try:
        # If Cython is installed, transpile the optimized Cython module to C and compile as a .pyd to be distributed
        from Cython.Build import cythonize #, build_ext
        print("Cython is installed, building creedsolo module")
        extensions = cythonize([ Extension('creedsolo.creedsolo', ['src/creedsolo/creedsolo.pyx']) ], annotate=True, force=True,  # this may fail hard if Cython is installed but there is no C compiler for current Python version, and we have no way to know. Alternatively, we could supply exclude_failures=True , but then for those who really want the cythonized compiled extension, it would be much harder to debug
                        compiler_directives={'embedsignature': True, 'binding': False, 'initializedcheck': True})
        #cmdclass = {'build_ext': build_ext}  # avoids the need to call python setup.py build_ext --inplace # TODO: this is likely unnecessary with modern python packaging since using python setup.py as a clip was deprecated -- DEPRECATED with PEP517
        cmdclass = {}
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
    extensions = [ Extension('creedsolo.creedsolo', ['src/creedsolo/creedsolo.c']) ]
    cmdclass = {}
else:
    extensions = None
    cmdclass = {}

setup(
    ext_modules = extensions,  # see also for Cython optimized maths functions: https://github.com/Technologicat/setup-template-cython/blob/master/setup.py
    cmdclass = cmdclass,
)

