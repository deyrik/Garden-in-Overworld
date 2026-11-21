PYRO5_IP = 127.0.0.1
PYRO5_PORTA = 9090

#limpa todos arquivos __pycache__ 
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

#new server:
NS:
# 1. Mata qualquer Name Server ou Servidor antigo sem o pkill se matar
	pkill -f "[p]yro5-ns" || true
	pkill -f "[m]ainServer.py" || true

	
# 2. Liga a (Name Server) no fundo e espera 1 segundo
	bash -c "source .venv/bin/activate && pyro5-ns -n $(PYRO5_IP) -p $(PYRO5_PORTA) &"
	sleep 1
	
# 3. Liga o Servidor do Jogo na tela atual
	bash -c "source .venv/bin/activate && python src/server/mainServer.py $(PYRO5_IP) $(PYRO5_PORTA)"


#new client:
NC:
	bash -c "source .venv/bin/activate && python src/client/mainCliente.py $(PYRO5_IP) $(PYRO5_PORTA)"


#cria 5 terminais fisicamente separados e 5 clientes:
5C:
	bash -c "source .venv/bin/activate && python src/client/mainCliente.py $(PYRO5_IP) $(PYRO5_PORTA) > /dev/null 2>&1 &"
	bash -c "source .venv/bin/activate && python src/client/mainCliente.py $(PYRO5_IP) $(PYRO5_PORTA) > /dev/null 2>&1 &"
	bash -c "source .venv/bin/activate && python src/client/mainCliente.py $(PYRO5_IP) $(PYRO5_PORTA) > /dev/null 2>&1 &"
	bash -c "source .venv/bin/activate && python src/client/mainCliente.py $(PYRO5_IP) $(PYRO5_PORTA) > /dev/null 2>&1 &"
	bash -c "source .venv/bin/activate && python src/client/mainCliente.py $(PYRO5_IP) $(PYRO5_PORTA) > /dev/null 2>&1 &"

# Automação total (Se você ainda for usar para testar os 5 clientes de uma vez):
all_local:
	pkill -f "[p]yro5-ns" || true
	pkill -f "[m]ainServer.py" || true
	
# Liga o Name Server
	bash -c "source .venv/bin/activate && pyro5-ns &"
	sleep 1
	
# Liga o Servidor do Jogo no fundo
	bash -c "source .venv/bin/activate && python src/server/mainServer.py &"
	sleep 1
	
# Chama regra 5C para criar 5 clientes
	make 5C


