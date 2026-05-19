from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit
from PyQt6.QtCore import QDateTime
from . import estilos

class WidgetLog(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("LOG", parent)
        layout = QVBoxLayout(self)
        self._texto = QTextEdit()
        self._texto.setReadOnly(True)
        self._texto.setStyleSheet(f"background-color: {estilos.PAINEL}; color: {estilos.TEXTO};")
        layout.addWidget(self._texto)

    def adicionar_evento(self, mensagem: str):
        hora = QDateTime.currentDateTime().toString("hh:mm:ss")
        self._texto.append(f"<span style='color:{estilos.AMBAR}'>[{hora}]</span> {mensagem}")
        self._texto.verticalScrollBar().setValue(
            self._texto.verticalScrollBar().maximum()
        )

    def registrar_resposta(self, status, mensagem):
        cor = estilos.DESTAQUE if status == "OK" else "#ff6b6b"
        hora = QDateTime.currentDateTime().toString("hh:mm:ss")
        self._texto.append(
            f"<span style='color:{estilos.AMBAR}'>[{hora}]</span> "
            f"<span style='color:{cor}'>{mensagem}</span>"
        )
        self._texto.verticalScrollBar().setValue(
            self._texto.verticalScrollBar().maximum()
        )

    def registrar_celula(self, x, y, valor):
        NOMES = {0:"terra",1:"água",2:"areia",3:"trigo",4:"arroz",6:"cana(terra)",7:"cana(areia)"}
        nome = NOMES.get(valor, str(valor))
        self.adicionar_evento(f"Célula ({x},{y}) → {nome}")
