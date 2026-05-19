from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel)
from PyQt6.QtCore import Qt
from .WidgetMapa import WidgetMapa
from .WidgetAcoes import WidgetAcoes
from .WidgetEstoque import WidgetEstoque
from .WidgetHUD import WidgetHUD
from .WidgetLog import WidgetLog
from .WidgetChat import WidgetChat
from . import estilos

class JanelaPrincipal(QMainWindow):
    def __init__(self, fazendeiro, ouvinte, nick, parent=None):
        super().__init__(parent)
        self._fazendeiro = fazendeiro
        self._nick = nick

        self.setWindowTitle("🌱 Garden in Overworld")
        self.setMinimumSize(960, 660)

        self._widget_hud     = WidgetHUD()
        self._widget_mapa    = WidgetMapa()
        self._widget_acoes   = WidgetAcoes()
        self._widget_estoque = WidgetEstoque()
        self._widget_log     = WidgetLog()
        self._widget_chat    = WidgetChat()

        self._label_jogadores = QLabel()
        self._label_jogadores.setStyleSheet(f"color: {estilos.DESTAQUE}; font-size: 11px;")
        self._label_jogadores.setWordWrap(True)
        self._jogadores = {}  # slot -> nick

        self._montar_layout()
        self._conectar_sinais(ouvinte)

        self.statusBar().showMessage(f"Conectado como: {nick}")
        self.statusBar().setStyleSheet(f"color: {estilos.DESTAQUE};")

    def _montar_layout(self):
        central = QWidget()
        self.setCentralWidget(central)
        raiz = QVBoxLayout(central)
        raiz.setSpacing(0)
        raiz.setContentsMargins(0, 0, 0, 0)

        raiz.addWidget(self._widget_hud)

        corpo = QHBoxLayout()
        corpo.setSpacing(8)
        corpo.setContentsMargins(6, 6, 6, 6)

        # Coluna esquerda: estoque + ações + jogadores
        col_esq = QVBoxLayout()
        col_esq.setSpacing(6)
        col_esq.addWidget(self._widget_estoque, stretch=1)
        col_esq.addWidget(self._widget_acoes, stretch=2)
        col_esq.addWidget(self._label_jogadores)
        corpo.addLayout(col_esq, stretch=1)

        # Centro: mapa
        corpo.addWidget(self._widget_mapa, stretch=3)

        # Coluna direita: log + chat
        col_dir = QVBoxLayout()
        col_dir.addWidget(self._widget_log, stretch=2)
        col_dir.addWidget(self._widget_chat, stretch=1)
        corpo.addLayout(col_dir, stretch=1)

        raiz.addLayout(corpo, stretch=1)

    def _conectar_sinais(self, ouvinte):
        # Mapa
        ouvinte.sinal_mapa_completo.connect(self._widget_mapa.atualizar_mapa_completo)
        ouvinte.sinal_celula_atualizada.connect(self._widget_mapa.atualizar_celula)

        # Respostas do servidor
        ouvinte.sinal_resposta_sistema.connect(
            lambda status, mensagem, cultura: self._widget_log.registrar_resposta(status, mensagem)
        )
        ouvinte.sinal_resposta_sistema.connect(
            lambda status, mensagem, cultura: self._on_resposta(status, mensagem, cultura)
        )

        # Chat
        ouvinte.sinal_chat_recebido.connect(self._widget_chat.adicionar_mensagem)

        # Desconexão
        ouvinte.sinal_desconectado.connect(self._on_desconectado)

        # Eventos de temporada
        ouvinte.sinal_inicio_temporada.connect(self._on_inicio_temporada)
        ouvinte.sinal_tick_timer.connect(self._widget_hud.atualizar_timer)
        ouvinte.sinal_estoque_atualizado.connect(self._widget_estoque.atualizar)
        ouvinte.sinal_progresso_atualizado.connect(self._widget_hud.atualizar_progresso)
        ouvinte.sinal_cultura_pronta.connect(self._on_cultura_pronta)
        ouvinte.sinal_posicao_jogador.connect(self._on_posicao_jogador)
        ouvinte.sinal_vitoria.connect(self._on_vitoria)
        ouvinte.sinal_derrota.connect(self._on_derrota)
        ouvinte.sinal_aviso_gelo.connect(self._on_aviso_gelo)

        # Mapa → Ações
        self._widget_mapa.sinal_celula_clicada.connect(self._on_celula_clicada)

        # Ações → Rede
        self._widget_acoes.sinal_preparar.connect(self._fazendeiro.solicita_preparar)
        self._widget_acoes.sinal_pegar_semente.connect(self._fazendeiro.solicita_pegar_semente)
        self._widget_acoes.sinal_plantar.connect(
            lambda semente, x, y: self._fazendeiro.solicita_plantar(semente, x, y)
        )
        self._widget_acoes.sinal_colher.connect(
            lambda x, y: self._fazendeiro.solicita_colher(0, x, y)
        )

        # Chat → Rede
        self._widget_chat.sinal_enviar_mensagem.connect(self._fazendeiro.solicita_chat)

    def _on_celula_clicada(self, x, y, valor):
        self._fazendeiro.solicita_cursor(x, y)
        self._widget_acoes.executar_para_celula(x, y, valor)

    def _on_resposta(self, status, mensagem, cultura):
        if status == "OK" and cultura is not None:
            self._widget_acoes.atualizar_semente_na_mao(cultura)
        elif status == "OK" and "plantada" in mensagem.lower():
            # semente foi usada
            self._widget_acoes.atualizar_semente_na_mao(None)

    def _on_inicio_temporada(self, dados: dict):
        self._widget_hud.atualizar_temporada(dados)
        culturas = [int(c) for c in dados.get("demanda", {}).keys()]
        self._widget_acoes.atualizar_culturas_disponiveis(culturas)
        nome = dados.get("nome", "")
        self._widget_log.adicionar_evento(f"🌱 Temporada {dados.get('temporada')} — {nome} iniciada!")

    def _on_cultura_pronta(self, x, y, cultura):
        self._widget_log.adicionar_evento(f"✨ Cultura pronta em ({x},{y})!")

    def _on_posicao_jogador(self, slot, nick, x, y):
        self._jogadores[slot] = nick
        self._widget_mapa.atualizar_posicao_jogador(slot, nick, x, y)
        self._atualizar_label_jogadores()

    def _atualizar_label_jogadores(self):
        cores = estilos.CORES_JOGADOR
        linhas = []
        for slot, nick in sorted(self._jogadores.items()):
            cor = cores.get(slot, "#ffffff")
            linhas.append(f"<span style='color:{cor}'>● {nick}</span>")
        self._label_jogadores.setText("<br>".join(linhas))

    def _on_vitoria(self, temporada):
        self._widget_log.adicionar_evento(f"🏆 VITÓRIA! Temporada {temporada} concluída!")
        self.statusBar().showMessage(f"🏆 Vitória na Temporada {temporada}!")

    def _on_derrota(self, temporada):
        self._widget_log.adicionar_evento(f"💀 Derrota na temporada {temporada}. Reiniciando...")
        self.statusBar().showMessage(f"💀 Derrota — tentando novamente...")

    def _on_aviso_gelo(self, x, y, segundos):
        self._widget_log.adicionar_evento(f"🧊 GELO em ({x},{y})! {segundos}s para colher!")

    def _on_desconectado(self):
        self.statusBar().showMessage("Desconectado do servidor.")
        self._widget_log.adicionar_evento("Conexão encerrada.")
