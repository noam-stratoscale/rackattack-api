all: check_convention

check_convention:
	pep8 rackattack --max-line-length=109
