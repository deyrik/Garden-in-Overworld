from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout,
                              QTextEdit, QLineEdit, QPushButton)
from PyQt6.QtCore import pyqtSignal
from . import estilos

class WidgetChat(QGroupBox):
    sinal_enviar_mensagem = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__("CHAT", parent)
        layout = QVBoxLayout(self)

        self._historico = QTextEdit()
        self._historico.setReadOnly(True)
        self._historico.setStyleSheet(f"background-color: {estilos.PAINEL};")
        layout.addWidget(self._historico)

        linha = QHBoxLayout()
        self._entrada = QLineEdit()
        self._entrada.setPlaceholderText("Digite aqui...")
        self._entrada.returnPressed.connect(self._on_enviar)
        linha.addWidget(self._entrada)

        btn_enviar = QPushButton("Enviar")
        btn_enviar.clicked.connect(self._on_enviar)
        linha.addWidget(btn_enviar)

        layout.addLayout(linha)

    def _on_enviar(self):
        texto = self._entrada.text().strip()
        if texto:
            self.sinal_enviar_mensagem.emit(texto)
            self._entrada.clear()

    def adicionar_mensagem(self, autor, mensagem):
        self._historico.append(
            f"<span style='color:{estilos.DESTAQUE}'>{autor}:</span> {mensagem}"
        )
        self._historico.verticalScrollBar().setValue(
            self._historico.verticalScrollBar().maximum()
        )
