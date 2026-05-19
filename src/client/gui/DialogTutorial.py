from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QWidget)
from PyQt6.QtCore import Qt
from . import estilos

TUTORIAL_T1 = """
<h2 style="color:#00ff88; margin:0 0 6px 0">🌱 Garden in Overworld</h2>
<p style="color:#aaa; margin:0 0 12px 0">Jogo colaborativo: todos plantam e colhem juntos para bater a meta antes do timer acabar.</p>

<p style="color:#ffb347; font-weight:bold; margin:0 0 4px 0">▶ Como jogar (4 passos)</p>
<table style="color:#ccc; width:100%; border-spacing:0 3px;">
  <tr><td style="color:#00ff88; width:22px">1.</td><td><b>Preparar solo</b> — clique em terra 🟫 ou areia 🟨</td></tr>
  <tr><td style="color:#00ff88">2.</td><td><b>Pegar semente</b> — escolha quantidade no painel e clique Pegar</td></tr>
  <tr><td style="color:#00ff88">3.</td><td><b>Plantar</b> — clique no tile preparado 🪵</td></tr>
  <tr><td style="color:#00ff88">4.</td><td><b>Colher</b> — tile pisca dourado quando pronto ✨</td></tr>
</table>

<p style="color:#ffb347; font-weight:bold; margin:12px 0 4px 0">🌱 Onde plantar cada semente</p>
<table style="color:#ccc; width:100%; border-spacing:0 2px;">
  <tr style="color:#888; font-size:11px"><td><b>Semente</b></td><td><b>Precisa de</b></td><td><b>Cresce em</b></td></tr>
  <tr><td>🌾 Trigo</td><td>Terra preparada 🪵</td><td>20s</td></tr>
  <tr><td>🌿 Arroz</td><td>Água 🟦 (sem preparar)</td><td>35s</td></tr>
  <tr><td>🎋 Cana</td><td>Terra <i>ou</i> areia preparada 🪵</td><td>20s</td></tr>
</table>

<p style="color:#888; font-size:11px; margin:12px 0 0 0">⏱ Timer vermelho = menos de 30s &nbsp;|&nbsp; 💬 Use o chat para combinar quem planta o quê</p>
"""

NOVIDADES_POR_TEMPORADA = {
    2: """
<h2 style="color:#ffb347; margin:0 0 6px 0">☀️ Verão — Novidade</h2>
<table style="color:#ccc; width:100%; border-spacing:0 2px;">
  <tr style="color:#888; font-size:11px"><td><b>Semente</b></td><td><b>Precisa de</b></td><td><b>Cresce em</b></td></tr>
  <tr><td>🌽 Milho</td><td>Terra preparada 🪵</td><td>40s</td></tr>
</table>
<p style="color:#aaa; margin:8px 0 0 0; font-size:12px">Timer mais curto (2:30). Estoque reduzido — não desperdicem sementes.</p>
""",
    3: """
<h2 style="color:#ff8c00; margin:0 0 6px 0">🍂 Outono — Novidade</h2>
<table style="color:#ccc; width:100%; border-spacing:0 2px;">
  <tr style="color:#888; font-size:11px"><td><b>Semente</b></td><td><b>Precisa de</b></td><td><b>Cresce em</b></td></tr>
  <tr><td>🥔 Batata</td><td>Qualquer solo preparado 🪵</td><td>25s</td></tr>
</table>
<p style="color:#ff6b6b; margin:8px 0 0 0; font-size:12px">⚠️ Sementes escassas: só voltam ao estoque após colheita. Não fiquem com sementes paradas na mão!</p>
""",
    4: """
<h2 style="color:#6b9fff; margin:0 0 6px 0">❄️ Inverno — Novidade</h2>
<table style="color:#ccc; width:100%; border-spacing:0 2px;">
  <tr style="color:#888; font-size:11px"><td><b>Semente</b></td><td><b>Precisa de</b></td><td><b>Cresce em</b></td></tr>
  <tr><td>🍅 Tomate</td><td>Terra preparada 🪵</td><td>50s</td></tr>
</table>
<p style="color:#ff4444; margin:8px 0 0 0; font-size:12px">🧊 Evento de gelo: a cada 30s uma planta pode ser destruída. Aviso aparece na tela — colham em até 10s!</p>
""",
}


class DialogTutorial(QDialog):
    def __init__(self, numero_temporada: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📖 Tutorial")
        self.setModal(True)
        self.setFixedSize(480, 420)
        self.setStyleSheet(
            f"background-color: {estilos.FUNDO}; color: {estilos.TEXTO};"
            f"font-family: 'Courier New', monospace;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel(f"  📖  Temporada {numero_temporada} — Regras")
        header.setFixedHeight(34)
        header.setStyleSheet(
            f"background-color: #0d1117; color: {estilos.DESTAQUE};"
            f"font-weight: bold; font-size: 13px; padding-left: 12px;"
            f"border-bottom: 1px solid {estilos.DESTAQUE};"
        )
        layout.addWidget(header)

        conteudo = QLabel()
        conteudo.setWordWrap(True)
        conteudo.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        conteudo.setContentsMargins(18, 14, 18, 14)
        conteudo.setStyleSheet(
            f"background: {estilos.FUNDO}; color: {estilos.TEXTO}; font-size: 12px;"
        )
        conteudo.setText(
            TUTORIAL_T1 if numero_temporada == 1
            else NOVIDADES_POR_TEMPORADA.get(min(numero_temporada, 4), "")
        )
        layout.addWidget(conteudo, stretch=1)

        rodape = QWidget()
        rodape.setFixedHeight(44)
        rodape.setStyleSheet(f"background: #0d1117; border-top: 1px solid {estilos.BORDA};")
        rl = QHBoxLayout(rodape)
        rl.setContentsMargins(12, 6, 12, 6)
        rl.addStretch()
        btn = QPushButton("▶  Jogar!")
        btn.setFixedHeight(28)
        btn.setStyleSheet(
            f"background-color: {estilos.DESTAQUE}; color: {estilos.FUNDO};"
            f"font-weight: bold; font-size: 13px; border: none; border-radius: 4px; padding: 0 20px;"
        )
        btn.clicked.connect(self.accept)
        rl.addWidget(btn)
        layout.addWidget(rodape)
