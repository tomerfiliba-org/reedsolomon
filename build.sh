#!/bin/sh
rm -rf build/ dist/ *.egg-info/
python setup.py register sdist --formats=gztar,zip bdist_wininst --plat-name=win32 upload
