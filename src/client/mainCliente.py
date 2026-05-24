import sys
import socket
import json

from PyQt6.QtWidgets import QApplication, QDialog

from views.ClassGUI import GameWindow, LoginDialog
from controllers.ClassControladorCliente import ControladorCliente
from controllers.ClassOuvinte import OuvinteThread
import ClassTCPCliente as TCPc
import ClassFazendeiro as Fazendeiro

PORTA_TCP = 12345
PORTA_UDP = 37020
TIMEOUT_DESCOBERTA = 3


def descobrir_servidor():
    """Escuta broadcast UDP do servidor. Retorna (host, porta) ou None."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(TIMEOUT_DESCOBERTA)
    try:
        sock.bind(("", PORTA_UDP))
        print(f"[UDP] Procurando servidor na rede local ({TIMEOUT_DESCOBERTA}s)...")
        dados, (host, _) = sock.recvfrom(1024)
        info = json.loads(dados.decode())
        if info.get("tipo") == "GARDEN_SERVER":
            porta = info.get("porta", PORTA_TCP)
            print(f"[UDP] Servidor encontrado: {host}:{porta} — {info.get('nome', '')}")
            return host, porta
    except (socket.timeout, json.JSONDecodeError, OSError):
        pass
    finally:
        sock.close()
    return None


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Tela de login para escolher o nickname
    login_screen = LoginDialog()
    if login_screen.exec() != QDialog.DialogCode.Accepted:
        sys.exit()
    nickname_escolhido = login_screen.get_nickname()

    # Descobre o servidor (UDP) ou usa localhost como fallback
    resultado = descobrir_servidor()
    if resultado:
        host, porta = resultado
    else:
        host, porta = "localhost", PORTA_TCP
        print(f"[UDP] Nenhum servidor encontrado. Tentando {host}:{porta}...")

    # Cria a janela principal do jogo
    window = GameWindow()

    # Cria socket TCP e o fazendeiro
    cliente = TCPc.TCPCliente(host, porta)
    cliente.conecta_servidor()
    fazendeiro = Fazendeiro.ClienteFazenda(cliente)

    # Cria thread de escuta e o controlador, e liga os sinais
    controlador = ControladorCliente(window, fazendeiro)
    thread_escuta = OuvinteThread(fazendeiro)
    controlador.iniciar_conexoes(thread_escuta)

    # Mostra a janela e inicia a thread de escuta do servidor
    window.show()
    thread_escuta.start()

    # Envia comandos iniciais assim que conecta
    fazendeiro.solicita_nickname(nickname_escolhido)
    fazendeiro.solicita_matriz()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
