from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import pyqtSignal
from . import estilos

EMOJIS = {
    0: "🟫",
    1: "🟦",
    2: "🟨",
    3: "🌾",
    4: "🌿",
    6: "🎋",
    7: "🎍",
}

ESTILO_NORMAL = f"""
    QPushButton {{
        background-color: {estilos.PAINEL};
        border: 1px solid {estilos.BORDA};
        font-size: 16px;
        padding: 0px;
    }}
    QPushButton:hover {{
        background-color: {estilos.HOVER};
    }}
"""
ESTILO_SELECIONADO = f"""
    QPushButton {{
        background-color: {estilos.HOVER};
        border: 2px solid {estilos.DESTAQUE};
        font-size: 16px;
        padding: 0px;
    }}
"""

class WidgetMapa(QWidget):
    sinal_celula_clicada = pyqtSignal(int, int, int)  # x, y, valor_atual

    def __init__(self, parent=None):
        super().__init__(parent)
        self._celula_selecionada = None
        self._botoes = {}
        self._matriz = [[0] * 20 for _ in range(20)]
        self._montar_grid()

    def _montar_grid(self):
        layout = QGridLayout(self)
        layout.setSpacing(1)
        layout.setContentsMargins(0, 0, 0, 0)
        for x in range(20):
            for y in range(20):
                btn = QPushButton(EMOJIS[0])
                btn.setFixedSize(30, 30)
                btn.setStyleSheet(ESTILO_NORMAL)
                btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                btn.clicked.connect(lambda _, cx=x, cy=y: self._on_clique(cx, cy))
                self._botoes[(x, y)] = btn
                layout.addWidget(btn, x, y)

    def _on_clique(self, x, y):
        if self._celula_selecionada and self._celula_selecionada != (x, y):
            px, py = self._celula_selecionada
            self._botoes[(px, py)].setStyleSheet(ESTILO_NORMAL)
        self._celula_selecionada = (x, y)
        self._botoes[(x, y)].setStyleSheet(ESTILO_SELECIONADO)
        self.sinal_celula_clicada.emit(x, y, self._matriz[x][y])

    def atualizar_mapa_completo(self, matriz):
        self._matriz = matriz
        for x in range(len(matriz)):
            for y in range(len(matriz[x])):
                self._atualizar_celula(x, y, matriz[x][y])

    def atualizar_celula(self, x, y, valor):
        self._matriz[x][y] = valor
        self._atualizar_celula(x, y, valor)

    def _atualizar_celula(self, x, y, valor):
        emoji = EMOJIS.get(valor, "❓")
        self._botoes[(x, y)].setText(emoji)
