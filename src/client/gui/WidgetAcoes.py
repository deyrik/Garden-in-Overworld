from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import pyqtSignal
from . import estilos

ACOES = ["PREPARAR", "PEGAR", "PLANTAR", "COLHER"]

CULTURAS_DISPONIVEIS = {
    3: "🌾 Trigo",
    4: "🌿 Arroz",
    6: "🎋 Cana",
    10: "🌽 Milho",
    11: "🥔 Batata",
    12: "🍅 Tomate",
}

CULTURAS_PRONTAS = {13, 14, 15, 16, 17, 18, 19}

ESTILO_SELECIONADO = f"""
    QPushButton {{
        background-color: {estilos.DESTAQUE};
        color: {estilos.FUNDO};
        border: none;
        border-radius: 3px;
        padding: 5px;
        font-size: 11px;
        font-weight: bold;
    }}
"""

class WidgetAcoes(QGroupBox):
    sinal_preparar   = pyqtSignal(int, int)        # x, y
    sinal_pegar_semente = pyqtSignal(int)          # cultura
    sinal_plantar    = pyqtSignal(int, int, int)   # semente, x, y
    sinal_colher     = pyqtSignal(int, int)        # x, y

    def __init__(self, parent=None):
        super().__init__("AÇÃO", parent)
        self._acao_selecionada = None
        self._botoes = {}
        self._semente_na_mao = None
        self._culturas_disponiveis = list(CULTURAS_DISPONIVEIS.keys())[:3]  # Temporada 1
        self._montar_layout()

    def _montar_layout(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        for acao in ACOES:
            rotulos = {
                "PREPARAR": "🪵 Preparar solo",
                "PEGAR":    "🌱 Pegar semente",
                "PLANTAR":  "🌿 Plantar",
                "COLHER":   "✂️ Colher",
            }
            btn = QPushButton(rotulos[acao])
            btn.clicked.connect(lambda _, a=acao: self._selecionar_acao(a))
            self._botoes[acao] = btn
            layout.addWidget(btn)

        self._combo_semente = QComboBox()
        self._combo_semente.setVisible(False)
        self._combo_semente.setStyleSheet(f"background: {estilos.PAINEL}; color: {estilos.TEXTO}; border: 1px solid {estilos.BORDA};")
        layout.addWidget(self._combo_semente)

        self._label_na_mao = QLabel("Na mão: —")
        self._label_na_mao.setStyleSheet(f"color: {estilos.AMBAR}; font-size: 11px;")
        layout.addWidget(self._label_na_mao)

        layout.addStretch()
        self._atualizar_visuais()

    def _selecionar_acao(self, acao):
        if self._acao_selecionada == acao:
            self._acao_selecionada = None
        else:
            self._acao_selecionada = acao

        self._combo_semente.setVisible(self._acao_selecionada == "PEGAR")
        if self._acao_selecionada == "PEGAR":
            self._recarregar_combo()

        self._atualizar_visuais()

    def _recarregar_combo(self):
        self._combo_semente.clear()
        for c in self._culturas_disponiveis:
            self._combo_semente.addItem(CULTURAS_DISPONIVEIS[c], c)

    def _atualizar_visuais(self):
        for acao, btn in self._botoes.items():
            if acao == self._acao_selecionada:
                btn.setStyleSheet(ESTILO_SELECIONADO)
            else:
                btn.setStyleSheet("")

    def executar_para_celula(self, x, y, valor_tile):
        if self._acao_selecionada is None:
            return

        if self._acao_selecionada == "PREPARAR":
            self.sinal_preparar.emit(x, y)

        elif self._acao_selecionada == "PEGAR":
            cultura = self._combo_semente.currentData()
            if cultura is not None:
                self.sinal_pegar_semente.emit(cultura)

        elif self._acao_selecionada == "PLANTAR":
            if self._semente_na_mao is not None:
                self.sinal_plantar.emit(self._semente_na_mao, x, y)

        elif self._acao_selecionada == "COLHER":
            if valor_tile in CULTURAS_PRONTAS:
                self.sinal_colher.emit(x, y)

    def atualizar_semente_na_mao(self, cultura):
        self._semente_na_mao = cultura
        if cultura is None:
            self._label_na_mao.setText("Na mão: —")
        else:
            nome = CULTURAS_DISPONIVEIS.get(cultura, str(cultura))
            self._label_na_mao.setText(f"Na mão: {nome} ×1")

    def atualizar_culturas_disponiveis(self, culturas: list):
        self._culturas_disponiveis = culturas
        if self._acao_selecionada == "PEGAR":
            self._recarregar_combo()
