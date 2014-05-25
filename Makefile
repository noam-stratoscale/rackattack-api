all: test check_convention

clean:
	rm -fr build dist rackattack.egg-info images.fortests

TESTS=$(addprefix rackattack.tests.,$(shell find rackattack/tests/test*.py | sed 's@.*/\(.*\)\.py@\1@' | sort))
test:
	PYTHONPATH=. python -m unittest $(TESTS)

testone:
	PYTHONPATH=. python rackattack/tests/test$(NUMBER)_*.py

check_convention:
	pep8 rackattack --max-line-length=109

uninstall:
	sudo pip uninstall rackattack
	sudo rm /usr/bin/rackattack

install:
	-sudo pip uninstall rackattack
	python setup.py build
	python setup.py bdist
	sudo python setup.py install
	sudo cp rackattack.sh /usr/bin/rackattack
	sudo chmod 755 /usr/bin/rackattack
