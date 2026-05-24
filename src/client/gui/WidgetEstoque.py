from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel
from . import estilos

EMOJIS_CULTURA = {3: "🌾", 4: "🌿", 6: "🎋", 10: "🌽", 11: "🥔", 12: "🍅"}
NOMES_CULTURA  = {3: "Trigo", 4: "Arroz", 6: "Cana", 10: "Milho", 11: "Batata", 12: "Tomate"}

LIMIAR_BAIXO = 5

class WidgetEstoque(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("ESTOQUE GLOBAL", parent)
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(4)
        self._linhas = {}  # cultura -> QLabel de quantidade

    def atualizar(self, estoque: dict):
        # Adiciona linhas novas e atualiza existentes
        for cultura_str, quantidade in estoque.items():
            cultura = int(cultura_str)
            if cultura not in self._linhas:
                self._criar_linha(cultura)
            self._atualizar_linha(cultura, quantidade)

        # Remove culturas que sumiram do estoque
        for cultura in list(self._linhas.keys()):
            if str(cultura) not in estoque and cultura not in estoque:
                self._remover_linha(cultura)

    def _criar_linha(self, cultura):
        emoji = EMOJIS_CULTURA.get(cultura, "?")
        nome  = NOMES_CULTURA.get(cultura, str(cultura))
        row = QHBoxLayout()
        lbl_nome = QLabel(f"{emoji} {nome}")
        lbl_nome.setStyleSheet("font-size: 11px; border: none; background: transparent;")
        lbl_qtd = QLabel("—")
        lbl_qtd.setStyleSheet(f"color: {estilos.AMBAR}; font-size: 11px; border: none; background: transparent;")
        row.addWidget(lbl_nome)
        row.addStretch()
        row.addWidget(lbl_qtd)
        self._layout.addLayout(row)
        self._linhas[cultura] = lbl_qtd

    def _atualizar_linha(self, cultura, quantidade):
        lbl = self._linhas[cultura]
        lbl.setText(str(quantidade))
        if quantidade <= LIMIAR_BAIXO:
            lbl.setStyleSheet("color: #ff4444; font-weight: bold; font-size: 11px; border: none; background: transparent;")
        else:
            lbl.setStyleSheet(f"color: {estilos.AMBAR}; font-size: 11px; border: none; background: transparent;")

    def _remover_linha(self, cultura):
        self._linhas.pop(cultura, None)
