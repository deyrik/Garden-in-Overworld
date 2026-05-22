#limpa todos arquivos __pycache__ 
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

#new server:
NS:
	sudo docker rm -f farm_server || true
	python src/server/mainServer.py

#new client:
NC:
	python src/client/mainCliente.py


#cria 4 terminais fisicamente separados e 4 clientes:
4C:
	bash -c "source .venv/bin/activate && python src/client/mainCliente.py > /dev/null 2>&1 &"
	bash -c "source .venv/bin/activate && python src/client/mainCliente.py > /dev/null 2>&1 &"
	bash -c "source .venv/bin/activate && python src/client/mainCliente.py > /dev/null 2>&1 &"
	bash -c "source .venv/bin/activate && python src/client/mainCliente.py > /dev/null 2>&1 &"

#---------------------------------DOCKER--------------------------------------------------------------
#docker new server:
docker_NS:
	sudo docker rm -f farm_server || true
	sudo docker run -d --name farm_server --net host garden-in-overworld_server:latest 

#docker close server:
docker_CS:
	sudo docker rm -f farm_server || true

#docker new client:
docker_NC:
	sudo docker run -it --net=host -e DISPLAY=$$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:ro garden-in-overworld_client1:latest

docker_all:
	sudo docker rm -f farm_server || true
	sudo docker run -d --name farm_server --net host garden-in-overworld_server:latest 
	sudo docker run -it --net=host -e DISPLAY=$$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:ro garden-in-overworld_client1:latest