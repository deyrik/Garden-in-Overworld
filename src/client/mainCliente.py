import os
import sys
import time

# Permite executar tanto via `cd src && python3 client/mainCliente.py`
# quanto via `python3 src/client/mainCliente.py`
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import client.ClassFazendeiro as Fazendeiro
import client.ClassTCPCliente as TCPc
import client.ClassMapa as Mapa


def main():
    cliente = TCPc.TCPCliente("localhost", 12345)
    cliente.conecta_servidor()

    resposta = cliente.recebe_mensagem()  # BEM_VINDO
    print(resposta)

    fazendeiro = Fazendeiro.ClienteFazenda(cliente)

    fazendeiro.solicita_matriz()
    matriz_json = fazendeiro.receber_matriz()
    if not matriz_json:
        return

    mapa_jogo = Mapa.Mapa()
    mapa_jogo.linha = len(matriz_json)
    mapa_jogo.coluna = len(matriz_json[0])
    mapa_jogo.matriz = matriz_json
    mapa_jogo.exibe_colorido()

    while True:
        fazendeiro.solicita_nickname("Homelender")
        fazendeiro.ler_resposta()
        time.sleep(2)

        fazendeiro.solicita_plantar(3, 3, 3)
        fazendeiro.ler_resposta()
        time.sleep(2)

        fazendeiro.solicita_colher(3, 3, 3)
        fazendeiro.ler_resposta()
        time.sleep(2)

        fazendeiro.solicita_sair()
        while True:
            evento = fazendeiro.ler_resposta()
            if evento.get("tipo") == "DESCONECTADO":
                break
            if (evento.get("mensagem") or "").lower().startswith("desconectando"):
                break

        cliente.fecha_conexao()
        break


if __name__ == "__main__":
    main()
    
