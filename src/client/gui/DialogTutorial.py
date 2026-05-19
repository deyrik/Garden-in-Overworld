from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QWidget)
from PyQt6.QtCore import Qt
from . import estilos

# Conteúdo completo da Temporada 1
TUTORIAL_COMPLETO = """
<h2 style="color:#00ff88">🌱 Bem-vindo a Garden in Overworld!</h2>
<p style="color:#ccc">Este é um jogo de fazenda <b>colaborativo</b>. Todos os jogadores trabalham juntos para cumprir a <b>meta de colheita</b> antes do timer acabar.</p>

<h3 style="color:#ffb347">🎯 Objetivo</h3>
<p style="color:#ccc">Colha a quantidade de cada cultura indicada na barra do topo antes que o tempo esgote. Trabalhem em equipe e usem o chat para se coordenar!</p>

<h3 style="color:#ffb347">🔄 Fluxo de jogo</h3>
<ol style="color:#ccc">
  <li><b style="color:#e0e0e0">Preparar solo</b> — Selecione "🪵 Preparar solo" e clique em um tile de <b>terra</b> ou <b>areia</b> no mapa.</li>
  <li><b style="color:#e0e0e0">Pegar semente</b> — No painel esquerdo, escolha a cultura e a quantidade desejada e clique em <b>Pegar</b>. As sementes são compartilhadas entre todos!</li>
  <li><b style="color:#e0e0e0">Plantar</b> — Selecione "🌿 Plantar" e clique no tile preparado. Cada cultura tem um terreno compatível.</li>
  <li><b style="color:#e0e0e0">Aguardar crescimento</b> — A planta cresce automaticamente. Quando estiver pronta, o tile <b>piscará</b> em dourado.</li>
  <li><b style="color:#e0e0e0">Colher</b> — Selecione "✂️ Colher" e clique no tile dourado para colher e avançar o progresso coletivo.</li>
</ol>

<h3 style="color:#ffb347">🌱 Culturas desta temporada</h3>
<table style="color:#ccc; width:100%; border-collapse:collapse;">
  <tr style="color:#888"><td><b>Cultura</b></td><td><b>Terreno</b></td><td><b>Tempo</b></td></tr>
  <tr><td>🌾 Trigo</td><td>Terra preparada</td><td>20s</td></tr>
  <tr><td>🌿 Arroz</td><td>Água (sem preparar)</td><td>35s</td></tr>
  <tr><td>🎋 Cana</td><td>Terra ou areia preparada</td><td>20s</td></tr>
</table>

<h3 style="color:#ffb347">💡 Dicas</h3>
<ul style="color:#ccc">
  <li>Coordenem via chat quem planta o quê</li>
  <li>O estoque de sementes é limitado — não desperdicem</li>
  <li>Tiles piscando em dourado = prontos para colher</li>
  <li>Timer vermelho = menos de 30 segundos restantes!</li>
</ul>
"""

# Conteúdo por temporada — só o que é novo
NOVIDADES_POR_TEMPORADA = {
    2: """
<h2 style="color:#ffb347">☀️ Temporada 2 — Verão</h2>
<p style="color:#ccc">Bem-vindos ao Verão! O timer ficou <b>mais curto</b> e uma nova cultura está disponível.</p>
<h3 style="color:#00ff88">🌽 Novidade: Milho</h3>
<table style="color:#ccc; width:100%; border-collapse:collapse;">
  <tr><td>🌽 Milho</td><td>Terra preparada</td><td>40s</td></tr>
</table>
<p style="color:#888; font-size:11px">O estoque de sementes foi reduzido. Planejem com cuidado!</p>
""",
    3: """
<h2 style="color:#ff8c00">🍂 Temporada 3 — Outono</h2>
<p style="color:#ccc">O Outono chegou. Sementes estão <b>escassas</b> — só reaparecem quando vocês colhem!</p>
<h3 style="color:#00ff88">🥔 Novidade: Batata</h3>
<table style="color:#ccc; width:100%; border-collapse:collapse;">
  <tr><td>🥔 Batata</td><td>Qualquer solo preparado</td><td>25s</td></tr>
</table>
<p style="color:#ff6b6b"><b>⚠️ Atenção:</b> Nesta temporada, o estoque não é reposto automaticamente — cada semente volta ao estoque apenas quando a colheita é feita. Não guardem sementes na mão sem plantar!</p>
""",
    4: """
<h2 style="color:#6b9fff">❄️ Temporada 4+ — Inverno</h2>
<p style="color:#ccc">O Inverno chegou com sementes mínimas e um novo perigo: <b>eventos de gelo</b>!</p>
<h3 style="color:#00ff88">🍅 Novidade: Tomate</h3>
<table style="color:#ccc; width:100%; border-collapse:collapse;">
  <tr><td>🍅 Tomate</td><td>Terra preparada</td><td>50s</td></tr>
</table>
<h3 style="color:#ff4444">🧊 Evento de Gelo</h3>
<p style="color:#ccc">A cada 30 segundos, uma planta aleatória pode ser <b>destruída pelo gelo</b>. Quando o aviso aparecer, corram colher a planta indicada em até 10 segundos!</p>
""",
}


class DialogTutorial(QDialog):
    def __init__(self, numero_temporada: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📖 Tutorial")
        self.setModal(True)
        self.setMinimumSize(520, 480)
        self.setStyleSheet(
            f"background-color: {estilos.FUNDO}; color: {estilos.TEXTO};"
            f"font-family: 'Courier New', monospace;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Cabeçalho
        header = QLabel(f"  📖  Tutorial — Temporada {numero_temporada}")
        header.setFixedHeight(36)
        header.setStyleSheet(
            f"background-color: #0d1117; color: {estilos.DESTAQUE};"
            f"font-weight: bold; font-size: 13px; padding-left: 12px;"
            f"border-bottom: 1px solid {estilos.DESTAQUE};"
        )
        layout.addWidget(header)

        # Conteúdo rolável
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background: {estilos.FUNDO};")

        conteudo = QLabel()
        conteudo.setWordWrap(True)
        conteudo.setOpenExternalLinks(False)
        conteudo.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        conteudo.setContentsMargins(20, 16, 20, 16)
        conteudo.setStyleSheet(f"background: {estilos.FUNDO}; color: {estilos.TEXTO}; font-size: 13px;")

        if numero_temporada == 1:
            html = TUTORIAL_COMPLETO
        else:
            html = NOVIDADES_POR_TEMPORADA.get(min(numero_temporada, 4), "")

        conteudo.setText(html)
        scroll.setWidget(conteudo)
        layout.addWidget(scroll, stretch=1)

        # Botão
        rodape = QWidget()
        rodape.setStyleSheet(f"background: #0d1117; border-top: 1px solid {estilos.BORDA};")
        rl = QHBoxLayout(rodape)
        rl.setContentsMargins(12, 8, 12, 8)
        rl.addStretch()
        btn = QPushButton("▶  Começar a jogar!")
        btn.setFixedHeight(32)
        btn.setStyleSheet(
            f"background-color: {estilos.DESTAQUE}; color: {estilos.FUNDO};"
            f"font-weight: bold; font-size: 13px; border: none; border-radius: 4px; padding: 0 20px;"
        )
        btn.clicked.connect(self.accept)
        rl.addWidget(btn)
        layout.addWidget(rodape)
