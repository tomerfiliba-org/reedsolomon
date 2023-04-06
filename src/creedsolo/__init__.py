# To maintain API retrocompatibility, since the module was previously packaged in a single-module layout, we now need to import * https://setuptools.pypa.io/en/latest/userguide/package_discovery.html
from .creedsolo import *  # when not compiled, it will raise an ImportError, which is exactly what we want, no problem
