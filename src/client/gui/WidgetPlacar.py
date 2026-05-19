from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QLabel
from . import estilos

class WidgetPlacar(QGroupBox):
    def __init__(self, meu_nick, parent=None):
        super().__init__("PLACAR", parent)
        self._pontuacoes = {meu_nick: 0}
        self._layout = QVBoxLayout(self)
        self._labels = {}
        self._atualizar_display()

    def _atualizar_display(self):
        for label in self._labels.values():
            self._layout.removeWidget(label)
            label.deleteLater()
        self._labels.clear()

        for nick, pts in sorted(self._pontuacoes.items(), key=lambda x: -x[1]):
            texto = f"👤 {nick}  {pts}"
            label = QLabel(texto)
            self._layout.addWidget(label)
            self._labels[nick] = label

        self._layout.addStretch()

    def registrar_acao(self, status, mensagem):
        """Atualiza pontuação com base na resposta do servidor."""
        if status != "OK":
            return
        if "plantada" in mensagem.lower():
            self._incrementar_meu_ponto(1)
        elif "colhida" in mensagem.lower():
            self._incrementar_meu_ponto(2)

    def _incrementar_meu_ponto(self, valor):
        meu_nick = list(self._pontuacoes.keys())[0]
        self._pontuacoes[meu_nick] = self._pontuacoes.get(meu_nick, 0) + valor
        self._atualizar_display()
