import os
import sys

# Permite executar tanto via `cd src/server && python3 mainServer.py`
# quanto via `python3 src/server/mainServer.py`
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

import ClassMapa as map
import ClassUser as usManager
import ClassControlador as ctrl
import ClassServidorTCP as tcpS

if __name__ == "__main__":
    print("--- INICIALIZANDO MUNDO ---")
    mapa_jogo = map.Mapa()
    mapa_jogo.gerar_mapa_aleatorio()
    mapa_jogo.exibe_colorido()

    gerenciador = usManager.GerenciadorUsers()
    
    print("--- CONECTANDO AS CAMADAS ---")
    controlador = ctrl.ControladorFazenda(mapa_jogo, gerenciador)
    
    # Cria a Rede e injeta os gatilhos do Cérebro
    servidor = tcpS.ServidorTCP(
        host="localhost", 
        port=12345,
        ao_conectar=controlador.conecta_jogador,
        ao_gerar_boas_vindas=controlador.gera_boas_vindas,
        ao_receber_mensagem=controlador.processa_mensagem,
        ao_desconectar=controlador.desconecta_jogador
    )
    
    servidor.start()
