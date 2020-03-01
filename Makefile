# This Makefile runs tests and builds the package to upload to pypi
# To use this Makefile, pip install py-make
# You also need to pip install also other required modules: `pip install flake8 nose coverage twine`
# Then, cd to this folder, and type `pymake -p` to list all commands, then `pymake <command>` to run the related entry.

.PHONY:
	alltests
	all
	flake8
	test
	testsetup
	testcoverage
	distclean
	coverclean
	prebuildclean
	clean
	installdev
	install
	build
	buildupload
	pypi
	help

help:
	@pymake -p

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
     # Build the Cython extension
    python setup.py build_ext --inplace
     # Run the tests
	python -m unittest discover tests

testsetup:
	python setup.py check --metadata --restructuredtext --strict
	python setup.py make none

testcoverage:
     # Does not work yet
	@make coverclean
	nosetests reedsolo --with-coverage --cover-package=reedsolo --cover-erase --cover-min-percentage=80 -d -v

distclean:
	@+make coverclean
	@+make prebuildclean
	@+make clean
prebuildclean:
	@+python -c "import shutil; shutil.rmtree('build', True)"
	@+python -c "import shutil; shutil.rmtree('dist', True)"
	@+python -c "import shutil; shutil.rmtree('reedsolo.egg-info', True)"
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
	python setup.py develop --uninstall
	python setup.py develop

install:
	python setup.py install

build:
	@make prebuildclean
	@make testsetup
	python setup.py sdist bdist_wheel
	# python setup.py bdist_wininst

pypi:
	twine upload dist/*

buildupload:
	@make build
	@make pypi
