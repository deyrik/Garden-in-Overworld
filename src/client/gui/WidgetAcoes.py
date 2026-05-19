from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

# Quais culturas podem ser plantadas em cada tipo de terreno
ACOES_POR_TILE = {
    0: [3, 5],    # terra: trigo (3), cana (5)
    1: [4],       # agua: arroz (4)
    2: [5],       # areia: cana (5)
    3: [],        # trigo plantado: só colher
    4: [],        # arroz plantado: só colher
    6: [],        # cana na terra: só colher
    7: [],        # cana na areia: só colher
}

TILES_COM_PLANTA = {3, 4, 6, 7}

NOME_CULTURA = {
    3: "🌾 Plantar Trigo",
    4: "🌿 Plantar Arroz",
    5: "🎋 Plantar Cana",
}

CULTURA_COLHER = {
    3: 3,   # trigo
    4: 4,   # arroz
    6: 6,   # cana na terra
    7: 7,   # cana na areia
}

class WidgetAcoes(QGroupBox):
    sinal_plantar = pyqtSignal(int, int, int)   # semente, x, y
    sinal_colher = pyqtSignal(int, int, int)    # cultura, x, y

    def __init__(self, parent=None):
        super().__init__("AÇÕES", parent)
        self._x = None
        self._y = None
        self._valor_tile = None
        self._botoes_plantar = {}
        self._btn_colher = None
        self._label_info = None
        self._montar_layout()

    def _montar_layout(self):
        layout = QVBoxLayout(self)
        self._label_info = QLabel("Selecione uma célula\nno mapa")
        self._label_info.setWordWrap(True)
        layout.addWidget(self._label_info)

        for cultura, nome in NOME_CULTURA.items():
            btn = QPushButton(nome)
            btn.setEnabled(False)
            btn.clicked.connect(lambda _, c=cultura: self._on_plantar(c))
            self._botoes_plantar[cultura] = btn
            layout.addWidget(btn)

        self._btn_colher = QPushButton("✂️ Colher")
        self._btn_colher.setEnabled(False)
        self._btn_colher.clicked.connect(self._on_colher)
        layout.addWidget(self._btn_colher)
        layout.addStretch()

    def atualizar_para_celula(self, x, y, valor):
        self._x, self._y, self._valor_tile = x, y, valor
        self._label_info.setText(f"Célula ({x}, {y})")

        culturas_possiveis = ACOES_POR_TILE.get(valor, [])
        for cultura, btn in self._botoes_plantar.items():
            # cana (5) aparece como botão único mas representa culturas 6 e 7
            btn.setEnabled(cultura in culturas_possiveis)

        pode_colher = valor in TILES_COM_PLANTA
        self._btn_colher.setEnabled(pode_colher)

    def _on_plantar(self, cultura):
        if self._x is not None:
            self.sinal_plantar.emit(cultura, self._x, self._y)

    def _on_colher(self):
        if self._x is not None and self._valor_tile in TILES_COM_PLANTA:
            cultura_real = CULTURA_COLHER[self._valor_tile]
            self.sinal_colher.emit(cultura_real, self._x, self._y)
