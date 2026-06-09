# src/client/gui/DialogConexao.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton)
from . import estilos


class DialogConexao(QDialog):
    """Tela inicial: nickname e (opcional) host do Name Server do Pyro.
    Em branco, o cliente localiza o Name Server por broadcast na LAN."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garden in Overworld — Conectar")
        self.setFixedSize(420, 240)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("🌱 Seu nickname de fazendeiro:"))
        self._entrada_nick = QLineEdit()
        self._entrada_nick.setPlaceholderText("Ex: Homelander")
        self._entrada_nick.returnPressed.connect(self._confirmar)
        layout.addWidget(self._entrada_nick)

        layout.addWidget(QLabel("🖧 Host do Name Server (deixe vazio para busca automática):"))
        self._entrada_ns = QLineEdit()
        self._entrada_ns.setPlaceholderText("Ex: 192.168.1.10  (vazio = LAN)")
        layout.addWidget(self._entrada_ns)

        btn = QPushButton("Entrar no mundo")
        btn.clicked.connect(self._confirmar)
        layout.addWidget(btn)

        self._nick_escolhido = None
        self._ns_host = ""

    def _confirmar(self):
        self._nick_escolhido = self._entrada_nick.text().strip() or "Fazendeiro"
        self._ns_host = self._entrada_ns.text().strip()
        self.accept()

    def resultado(self):
        """Retorna (nick, ns_host). ns_host == '' significa busca automática."""
        return self._nick_escolhido, self._ns_host
