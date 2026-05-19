from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal
from . import estilos

TILES_COM_PLANTA = {3, 4, 6, 7}

NOME_CULTURA = {
    3: "🌾 Plantar Trigo",
    4: "🌿 Plantar Arroz",
    5: "🎋 Plantar Cana",
}

CULTURA_COLHER = {
    3: 3,
    4: 4,
    6: 6,
    7: 7,
}

ESTILO_SELECIONADO = f"""
    QPushButton {{
        background-color: {estilos.DESTAQUE};
        color: {estilos.FUNDO};
        border: 1px solid {estilos.DESTAQUE};
        border-radius: 3px;
        padding: 4px 8px;
        font-weight: bold;
    }}
"""

class WidgetAcoes(QGroupBox):
    sinal_plantar = pyqtSignal(int, int, int)   # semente, x, y
    sinal_colher = pyqtSignal(int, int, int)    # cultura, x, y

    def __init__(self, parent=None):
        super().__init__("AÇÕES", parent)
        self._acao_selecionada = None  # None, 3, 4, 5 ou "COLHER"
        self._botoes = {}
        self._label_info = None
        self._montar_layout()

    def _montar_layout(self):
        layout = QVBoxLayout(self)
        self._label_info = QLabel("Selecione uma ação\ne clique no mapa")
        self._label_info.setWordWrap(True)
        layout.addWidget(self._label_info)

        for cultura, nome in NOME_CULTURA.items():
            btn = QPushButton(nome)
            btn.clicked.connect(lambda _, c=cultura: self._selecionar_acao(c))
            self._botoes[cultura] = btn
            layout.addWidget(btn)

        btn_colher = QPushButton("✂️ Colher")
        btn_colher.clicked.connect(lambda: self._selecionar_acao("COLHER"))
        self._botoes["COLHER"] = btn_colher
        layout.addWidget(btn_colher)
        layout.addStretch()

    def _selecionar_acao(self, acao):
        if self._acao_selecionada == acao:
            self._acao_selecionada = None
            self._label_info.setText("Selecione uma ação\ne clique no mapa")
        else:
            self._acao_selecionada = acao
            nome = NOME_CULTURA.get(acao, "✂️ Colher") if acao != "COLHER" else "✂️ Colher"
            self._label_info.setText(f"Ação: {nome}\nClique no mapa para usar")
        self._atualizar_visuais()

    def _atualizar_visuais(self):
        for chave, btn in self._botoes.items():
            if chave == self._acao_selecionada:
                btn.setStyleSheet(ESTILO_SELECIONADO)
            else:
                btn.setStyleSheet("")

    def executar_para_celula(self, x, y, valor_tile):
        if self._acao_selecionada is None:
            return
        if self._acao_selecionada == "COLHER":
            if valor_tile in TILES_COM_PLANTA:
                self.sinal_colher.emit(CULTURA_COLHER[valor_tile], x, y)
        else:
            self.sinal_plantar.emit(self._acao_selecionada, x, y)
