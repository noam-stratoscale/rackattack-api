all: check_convention

check_convention:
	pep8 py --max-line-length=109
