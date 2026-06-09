VENV    = .venv
PYTHON  = $(VENV)/bin/python3
PIP     = $(VENV)/bin/pip
SERVER  = src/server/mainServer.py
CLIENT  = src/client/gui/main.py

# Cria o venv e instala dependências
install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install PyQt6 Pyro5 pytest

# Name Server do Pyro5 (subir ANTES do servidor)
NAMESERVER: $(VENV)
	$(PYTHON) -m Pyro5.nameserver

# Novo Servidor (registra-se no Name Server)
NS: $(VENV)
	$(PYTHON) $(SERVER)

# Novo Cliente
NC: $(VENV)
	$(PYTHON) $(CLIENT)

# 5 clientes em terminais separados (requer gnome-terminal ou xterm)
5C: $(VENV)
	@for i in 1 2 3 4 5; do \
		gnome-terminal -- bash -c "$(PYTHON) $(CLIENT); exec bash" 2>/dev/null || \
		xterm -e "$(PYTHON) $(CLIENT); bash" & \
	done

# Sobe Name Server + servidor + 5 clientes na ordem correta
all_local: $(VENV)
	gnome-terminal -- bash -c "$(PYTHON) -m Pyro5.nameserver; exec bash" 2>/dev/null || \
	xterm -e "$(PYTHON) -m Pyro5.nameserver; bash" &
	sleep 2
	gnome-terminal -- bash -c "$(PYTHON) $(SERVER); exec bash" 2>/dev/null || \
	xterm -e "$(PYTHON) $(SERVER); bash" &
	sleep 1
	$(MAKE) 5C

# Garante que o venv existe antes de rodar qualquer target
$(VENV):
	@echo "Venv não encontrado. Execute 'make install' primeiro."
	@exit 1

# Roda a suíte de testes
test: $(VENV)
	$(PYTHON) -m pytest -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true

.PHONY: install NAMESERVER NS NC 5C all_local test clean
