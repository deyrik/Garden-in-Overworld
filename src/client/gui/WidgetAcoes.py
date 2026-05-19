from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSpinBox, QFrame, QWidget)
from PyQt6.QtCore import pyqtSignal
from . import estilos

ACOES_MAPA = ["PREPARAR", "PLANTAR", "COLHER"]

CULTURAS_INFO = {
    3:  ("🌾", "Trigo"),
    4:  ("🌿", "Arroz"),
    6:  ("🎋", "Cana"),
    10: ("🌽", "Milho"),
    11: ("🥔", "Batata"),
    12: ("🍅", "Tomate"),
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
    sinal_preparar      = pyqtSignal(int, int)      # x, y
    sinal_pegar_semente = pyqtSignal(int, int)      # cultura, quantidade
    sinal_plantar       = pyqtSignal(int, int, int) # semente, x, y
    sinal_colher        = pyqtSignal(int, int)      # x, y

    def __init__(self, parent=None):
        super().__init__("AÇÃO", parent)
        self._acao_selecionada = None
        self._botoes_acao = {}
        self._semente_na_mao = None
        self._culturas_disponiveis = [3, 4, 6]
        self._widgets_semente = {}  # cultura -> (row_widget, spinbox)
        self._montar_layout()

    def _montar_layout(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        # Botões de ação que exigem clique no mapa
        rotulos = {
            "PREPARAR": "🪵 Preparar solo",
            "PLANTAR":  "🌿 Plantar",
            "COLHER":   "✂️ Colher",
        }
        for acao in ACOES_MAPA:
            btn = QPushButton(rotulos[acao])
            btn.clicked.connect(lambda _, a=acao: self._selecionar_acao(a))
            self._botoes_acao[acao] = btn
            layout.addWidget(btn)

        # Na mão
        self._label_na_mao = QLabel("Na mão: —")
        self._label_na_mao.setStyleSheet(
            f"color: {estilos.AMBAR}; font-size: 11px;"
        )
        layout.addWidget(self._label_na_mao)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {estilos.BORDA};")
        layout.addWidget(sep)

        # Seção de sementes
        lbl_sec = QLabel("SEMENTES")
        lbl_sec.setStyleSheet(
            f"color: {estilos.DESTAQUE}; font-size: 10px; letter-spacing: 1px;"
        )
        layout.addWidget(lbl_sec)

        self._container_sementes = QVBoxLayout()
        self._container_sementes.setSpacing(3)
        layout.addLayout(self._container_sementes)

        self._reconstruir_sementes()
        layout.addStretch()

    def _reconstruir_sementes(self):
        # Limpar widgets antigos
        for cultura, (widget, _) in self._widgets_semente.items():
            widget.deleteLater()
        self._widgets_semente.clear()

        for cultura in self._culturas_disponiveis:
            if cultura not in CULTURAS_INFO:
                continue
            emoji, nome = CULTURAS_INFO[cultura]

            row = QWidget()
            row.setStyleSheet("background: transparent;")
            hl = QHBoxLayout(row)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(4)

            lbl = QLabel(f"{emoji} {nome}")
            lbl.setStyleSheet("font-size: 11px; border: none; background: transparent;")

            spin = QSpinBox()
            spin.setRange(1, 10)
            spin.setValue(1)
            spin.setFixedWidth(44)
            spin.setStyleSheet(
                f"background: {estilos.PAINEL}; color: {estilos.TEXTO};"
                f"border: 1px solid {estilos.BORDA}; border-radius: 3px; font-size: 11px;"
            )

            btn = QPushButton("Pegar")
            btn.setFixedWidth(46)
            btn.setStyleSheet("font-size: 10px; padding: 2px 4px;")
            btn.clicked.connect(lambda _, c=cultura, s=spin: self.sinal_pegar_semente.emit(c, s.value()))

            hl.addWidget(lbl, stretch=1)
            hl.addWidget(spin)
            hl.addWidget(btn)

            self._container_sementes.addWidget(row)
            self._widgets_semente[cultura] = (row, spin)

    def _selecionar_acao(self, acao):
        self._acao_selecionada = None if self._acao_selecionada == acao else acao
        self._atualizar_visuais()

    def _atualizar_visuais(self):
        for acao, btn in self._botoes_acao.items():
            btn.setStyleSheet(ESTILO_SELECIONADO if acao == self._acao_selecionada else "")

    def executar_para_celula(self, x, y, valor_tile):
        if self._acao_selecionada == "PREPARAR":
            self.sinal_preparar.emit(x, y)
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
            emoji, nome = CULTURAS_INFO.get(cultura, ("?", str(cultura)))
            self._label_na_mao.setText(f"Na mão: {emoji} {nome} ×1")

    def atualizar_culturas_disponiveis(self, culturas: list):
        self._culturas_disponiveis = culturas
        self._reconstruir_sementes()
