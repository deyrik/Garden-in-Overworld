import socket
import threading
import json
import time

PORTA_UDP = 37020
INTERVALO_ANUNCIO = 2  # segundos

class AnunciadorUDP(threading.Thread):
    """Transmite a presença do servidor via broadcast UDP na rede local."""

    def __init__(self, porta_tcp=12345, nome_mundo="Mundo da Fazenda"):
        super().__init__(daemon=True)
        self.porta_tcp = porta_tcp
        self.nome_mundo = nome_mundo
        self._rodando = True

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mensagem = json.dumps({
            "tipo": "GARDEN_SERVER",
            "nome": self.nome_mundo,
            "porta": self.porta_tcp
        }).encode()
        print(f"[UDP] Anunciando servidor na porta broadcast {PORTA_UDP}...")
        while self._rodando:
            try:
                sock.sendto(mensagem, ("<broadcast>", PORTA_UDP))
            except Exception as e:
                print(f"[UDP] Erro ao anunciar: {e}")
            time.sleep(INTERVALO_ANUNCIO)
        sock.close()

    def parar(self):
        self._rodando = False
