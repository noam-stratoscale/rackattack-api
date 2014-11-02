all: check_convention

check_convention:
	pep8 py test* --max-line-length=109

racktest:
	UPSETO_JOIN_PYTHON_NAMESPACES=yes PYTHONPATH=$(PWD):$(PWD)/py python test/test.py
virttest:
	RACKATTACK_PROVIDER=tcp://localhost:1014@tcp://localhost:1015 $(MAKE) racktest
phystest:
	RACKATTACK_PROVIDER=tcp://rackattack-provider:1014@tcp://rackattack-provider:1015 $(MAKE) racktest
