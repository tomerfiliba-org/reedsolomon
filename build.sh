#!/bin/sh
rm -rf build/ dist/ *.egg-info/
python setup.py register sdist --formats=gztar,zip upload
