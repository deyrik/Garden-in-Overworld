import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import QApplication, QDialog
from ClassTCPCliente import TCPCliente
from ClassFazendeiro import ClienteFazenda
from ClassMapa import Mapa
from ClassOuvinte import OuvinteThread
from gui.JanelaPrincipal import JanelaPrincipal
from gui.DialogConexao import DialogConexao
from gui import estilos


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(estilos.STYLESHEET)

    dialog = DialogConexao()
    if dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    nick, host, porta = dialog.resultado()

    cliente = TCPCliente(host, porta)
    cliente.conecta_servidor()

    fazendeiro = ClienteFazenda(cliente)
    mapa_jogo = Mapa()

    ouvinte = OuvinteThread(fazendeiro, mapa_jogo)

    janela = JanelaPrincipal(fazendeiro, ouvinte, nick)
    janela.show()

    fazendeiro.solicita_nickname(nick)
    ouvinte.start()
    fazendeiro.solicita_matriz()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
