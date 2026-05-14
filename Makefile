.PHONY: run-server run-client lint

PY ?= python3

run-server:
	cd src/server && $(PY) mainServer.py

run-client:
	cd src && $(PY) client/mainCliente.py

run-gui:
	$(PY) src/client/gui.py

lint:
	$(PY) -m py_compile $$(find src -type f -name "*.py")
