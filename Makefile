# This Makefile runs tests and builds the package to upload to pypi
# To use this Makefile, pip install py-make
# then do: pymake <command>
# or: python.exe -m pymake <command>
# You also need to pip install also other required modules: `pip install flake8 coverage twine pytest pytest-cov validate-pyproject[all] pytest-xdist`
# Up to Python 3.9 included, nosetests was used, but from 3.10 onward, support for it was dropped since it is not maintained anymore, so that pytest and pytest-cov are used instead.
# Then, cd to this folder, and type `pymake -p` to list all commands, then `pymake <command>` to run the related entry.
# To test on multiple Python versions, install them, install also the C++ redistributables for each (so that Cython works), and then type `pymake testtox`.
# To pymake buildupload (deploy on pypi), you need to `pip install cython` and install a C++ compiler, on Windows and with Python 3.7 you need Microsoft Visual C++ 14.0. Get it with "Microsoft Visual C++ Build Tools": https://visualstudio.microsoft.com/fr/visual-cpp-build-tools/
# for Python 3.10, read the updated instructions at: https://wiki.python.org/moin/WindowsCompilers
# CRITICAL NOTE: if you get a "FileNotFoundError" exception when trying to call @+python or @+make, then it is because you used spaces instead of a hard TAB character to indent! TODO: bugfix this. It happens only for @+ commands and for those after the first command (if the @+ command with spaces as indentation is the first and only statement in a command, it works!)

.PHONY:
	alltests
	all
	flake8
	test
	testsetup
    testpyproject
    testsetuppost
	testcoverage
    testtox
	distclean
	coverclean
	prebuildclean
	clean
    toxclean
	installdev
	install
	build
	buildupload
	pypi
	help

help:
	@+make -p

alltests:
	@+make test
	@+make flake8
	@+make testsetup

all:
	@+make alltests
	@+make build

flake8:
	@+flake8 -j 8 --count --statistics --exit-zero .

test:
    # Only for Py2
     # Build the Cython extension
	python setup.py build_ext --inplace
     # Run the tests
	@+python -m unittest discover tests

testnobinary:
    # Only for Py2
     # Run the tests
	@+python -m unittest discover tests
     #pytest --cov-branch

testnose:
    # Only for Py2
	@+python -m nose -vv --with-coverage

testtox:
    # Test for multiple Python versions
	tox --skip-missing-interpreters -p all

testsetup:
	python setup.py check --metadata --restructuredtext --strict

testpyproject:
    # Only for Py2
	validate-pyproject pyproject.toml -v

testsetuppost:
	twine check "dist/*"

testcoverage:
     # This is the preferred way to run the tests since Python 3.10
	@+make coverclean
     # Build the Cython extension and install module in editable mode
	#python setup.py build_ext --inplace --cythonize  # unnecessary to call build_ext --inplace now
     #python -m pip install -e . --config-setting="--build-option=--cythonize"
	python setup.py develop --cythonize  # unfortunately much faster than current pep517 options which do not allow to only build the extension
     # Run the tests
	# nosetests reedsolo --with-coverage --cover-package=reedsolo --cover-erase --cover-min-percentage=80 -d -v
     # With PyTest, it is now necessary to first install the python module so that it is found (--cov=<module>)
     #python setup.py develop
     #pytest --cov-report term-missing --cov-config=.coveragerc --cov=. tests/ --cov-branch
     #python setup.py develop --uninstall
	coverage run --branch -m pytest -v
	coverage report -m

testcoveragexdist:
     # This parallelizes tests to make them run faster, thanks to pytest-xdist
	@+make coverclean
     # Build the Cython extension and install module in editable mode
	#python setup.py build_ext --inplace --cythonize  # unnecessary to call build_ext --inplace now
     #python setup.py develop --cythonize  # unfortunately much faster than current pep517 options which do not allow to only build the extension
	@+make installdevpep517
     # Run the tests
	# nosetests reedsolo --with-coverage --cover-package=reedsolo --cover-erase --cover-min-percentage=80 -d -v
     # With PyTest, it is now necessary to first install the python module so that it is found (--cov=<module>)
     #python setup.py develop
     #pytest --cov-report term-missing --cov-config=.coveragerc --cov=. tests/ --cov-branch
     #python setup.py develop --uninstall
	coverage run --branch -m pytest -n auto -v
     #coverage report -m  # cannot send a report from parallelized xdist

testcoveragenocython:
     # This is the preferred way to run the tests since Python 3.10
	@+make coverclean
     # Run the tests
	# nosetests reedsolo --with-coverage --cover-package=reedsolo --cover-erase --cover-min-percentage=80 -d -v
     # With PyTest, it is now necessary to first install the python module so that it is found (--cov=<module>)
     #python setup.py develop
     #pytest --cov-report term-missing --cov-config=.coveragerc --cov=. tests/ --cov-branch
     #python setup.py develop --uninstall
	coverage run --branch -m pytest -v
	coverage report -m

distclean:
	@+make coverclean
	@+make prebuildclean
	@+make clean
	@+make toxclean
prebuildclean:
	@+python -c "import shutil; shutil.rmtree('build', True)"
	@+python -c "import shutil; shutil.rmtree('dist', True)"
	@+python -c "import shutil; shutil.rmtree('reedsolo.egg-info', True)"
    # IMPORTANT: systematically delete `src/<project.name>.egg-info` folder before rebuilding, otherwise the list of included files will not get updated (it's in `SOURCES.txt` file in this folder)
	@+python -c "import shutil; shutil.rmtree('src/reedsolo.egg-info', True)"
coverclean:
	@+python -c "import os; os.remove('.coverage') if os.path.exists('.coverage') else None"
	@+python -c "import shutil; shutil.rmtree('__pycache__', True)"
	@+python -c "import shutil; shutil.rmtree('tests/__pycache__', True)"
clean:
	@+python -c "import os, glob; [os.remove(i) for i in glob.glob('*.py[co]')]"
	@+python -c "import os, glob; [os.remove(i) for i in glob.glob('tests/*.py[co]')]"
toxclean:
	@+python -c "import shutil; shutil.rmtree('.tox', True)"

installdev:
	@+python setup.py develop --uninstall
	@+python setup.py develop

installdevpep517:
	@+python -m pip install --upgrade --editable . --config-setting="--build-option=--cythonize" --verbose --use-pep517

install:
	@+python setup.py install

installpep517:
	@+python -m pip install --upgrade . --config-setting="--build-option=--cythonize" --verbose --use-pep517

buildpep517:
    # requires `pip install build`
	@+python -sBm build --config-setting="--build-option=--cythonize"  # do NOT use the -w flag, otherwise only the wheel will be built, but we need sdist for source distros such as Debian and Gentoo!

bandit:
    bandit reedsolo.py

build:
	@+make prebuildclean
	#@+make testsetup
	@+make testpyproject
	@+python -sBm build --config-setting="--build-option=--cythonize"
	#@+python setup.py sdist bdist_wheel  # deprecated with pep517
	#@+python setup.py bdist_wininst
    @+make testsetuppost

buildwheelhouse:
	cibuildwheel --platform auto

pypi:
	twine upload dist/*

buildupload:
	@+make build
	@+make pypi
