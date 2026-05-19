import sys
import os

# Garante que o diretório pai (src/client) esteja no path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt
from ClassTCPCliente import TCPCliente
from ClassFazendeiro import ClienteFazenda
from ClassMapa import Mapa
from ClassOuvinte import OuvinteThread
from gui.JanelaPrincipal import JanelaPrincipal
from gui import estilos

class DialogNickname(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garden in Overworld")
        self.setFixedSize(300, 150)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🌱 Seu nickname de fazendeiro:"))
        self._entrada = QLineEdit()
        self._entrada.setPlaceholderText("Ex: Homelander")
        self._entrada.returnPressed.connect(self.accept)
        layout.addWidget(self._entrada)
        btn = QPushButton("Entrar no mundo")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def nickname(self):
        return self._entrada.text().strip() or "Fazendeiro"

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(estilos.STYLESHEET)

    dialog = DialogNickname()
    if dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    nick = dialog.nickname()

    cliente = TCPCliente("localhost", 12345)
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
