# -*- coding: utf-8 -*-
#!python
#cython: language_level=3

# To maintain API retrocompatibility, since the module was previously packaged in a single-module layout, we now need to import * https://setuptools.pypa.io/en/latest/userguide/package_discovery.html
try:
    from .creedsolo import *
except ImportError:
    # Standard CPython import failed, probably the creedsolo cython extension was not compiled, just pass
    pass
