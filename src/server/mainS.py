import TCPServerClass as tcpS
import MapaClass as map
import UserClass as uc
import socket
import random
import threading
import time


# aloca o mapa
mapa = map.Mapa()
mapa.gerar_mapa_aleatorio()
mapa.exibe_colorido()

# aloca o gerenciador de jogadores
gerenciador = uc.GerenciadorUsers()
gerenciador.exibir_jogadores_conectados()


# iniciar o servidor TCP
servidor = tcpS.TCPServerClass("localhost", 12345, mapa, gerenciador)
servidor.mapa.exibe_colorido()  # Exibe o mapa do servidor para conferência
servidor.start()

