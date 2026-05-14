import os
import sys

# Permite executar tanto via `cd src && python3 client/mainCliente.py`
# quanto via `python3 src/client/mainCliente.py`
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import client.ClassFazendeiro as Fazendeiro
import client.ClassTCPCliente as TCPc
import client.ClassMapa as Mapa
import time

if __name__ == "__main__":


    #COMEÇA CONECTANDO CLIENTE AO SERVER
    cliente = TCPc.TCPCliente("localhost", 12345)
    cliente.conecta_servidor()
    resposta = cliente.recebe_mensagem() # recebe a mensagem de BEM_VINDO do servidor
    print(resposta)
    
    #INSTANCIA O FAZENDEIRO QUE VAI JOGAR
    fazendeiro = Fazendeiro.ClienteFazenda(cliente)

    
    #MONTA O MAPA DO JOGO COM O JSON RECEBIDO DO SERVIDOR
    fazendeiro.solicita_matriz()
    matriz_json = fazendeiro.receber_matriz()
    
    mapa_jogo = Mapa.Mapa()
    mapa_jogo.linha = len(matriz_json)     # garantindo que o mapa do cliente vai ser do mesm tamango do server
    mapa_jogo.coluna = len(matriz_json[0])
    mapa_jogo.matriz = matriz_json
    mapa_jogo.exibe_colorido()


    while True:

        fazendeiro.solicita_nickname("Homelender")
        fazendeiro.ler_resposta() # lê a resposta do servidor, mas não faz nada com ela
        time.sleep(2)

        fazendeiro.solicita_plantar(3, 3, 3)  # Exemplo: planta trigo na posição (3, 3)
        fazendeiro.ler_resposta()
        time.sleep(2)

        fazendeiro.solicita_colher(3, 3, 3)  # Exemplo: colhe o que estiver na posição (3, 3)  
        fazendeiro.ler_resposta()
        time.sleep(2)

        #AQUI VAI FICAR DANDO ERRO, MAS JA É ESPERADO ISSO MSM
        fazendeiro.solicita_sair() # Envia o comando de sair para o servidor
        fazendeiro.ler_resposta() # Lê a resposta do servidor, mas não faz nada com ela
        time.sleep(2)
    
