from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout)
from PyQt6.QtCore import Qt
from .WidgetMapa import WidgetMapa
from .WidgetAcoes import WidgetAcoes
from .WidgetPlacar import WidgetPlacar
from .WidgetLog import WidgetLog
from .WidgetChat import WidgetChat
from . import estilos

class JanelaPrincipal(QMainWindow):
    def __init__(self, fazendeiro, ouvinte, nick, parent=None):
        super().__init__(parent)
        self._fazendeiro = fazendeiro
        self._nick = nick

        self.setWindowTitle("🌱 Garden in Overworld")
        self.setMinimumSize(900, 620)

        # Widgets
        self._widget_mapa = WidgetMapa()
        self._widget_acoes = WidgetAcoes()
        self._widget_placar = WidgetPlacar(nick)
        self._widget_log = WidgetLog()
        self._widget_chat = WidgetChat()

        self._montar_layout()
        self._conectar_sinais(ouvinte)

        self.statusBar().showMessage(f"Conectado como: {nick}")
        self.statusBar().setStyleSheet(f"color: {estilos.DESTAQUE};")

    def _montar_layout(self):
        central = QWidget()
        self.setCentralWidget(central)
        raiz = QHBoxLayout(central)
        raiz.setSpacing(8)

        # Coluna esquerda: placar + acoes
        col_esq = QVBoxLayout()
        col_esq.addWidget(self._widget_placar, stretch=1)
        col_esq.addWidget(self._widget_acoes, stretch=2)
        raiz.addLayout(col_esq, stretch=1)

        # Centro: mapa
        raiz.addWidget(self._widget_mapa, stretch=3)

        # Coluna direita: log + chat
        col_dir = QVBoxLayout()
        col_dir.addWidget(self._widget_log, stretch=2)
        col_dir.addWidget(self._widget_chat, stretch=1)
        raiz.addLayout(col_dir, stretch=1)

    def _conectar_sinais(self, ouvinte):
        # Rede → UI
        ouvinte.sinal_mapa_completo.connect(self._widget_mapa.atualizar_mapa_completo)
        ouvinte.sinal_celula_atualizada.connect(self._widget_mapa.atualizar_celula)
        ouvinte.sinal_celula_atualizada.connect(self._widget_log.registrar_celula)
        ouvinte.sinal_resposta_sistema.connect(self._widget_log.registrar_resposta)
        ouvinte.sinal_resposta_sistema.connect(self._widget_placar.registrar_acao)
        ouvinte.sinal_chat_recebido.connect(self._widget_chat.adicionar_mensagem)
        ouvinte.sinal_desconectado.connect(self._on_desconectado)

        # Mapa → Acoes
        self._widget_mapa.sinal_celula_clicada.connect(self._widget_acoes.atualizar_para_celula)

        # Acoes → Rede
        self._widget_acoes.sinal_plantar.connect(
            lambda semente, x, y: self._fazendeiro.solicita_plantar(semente, x, y)
        )
        self._widget_acoes.sinal_colher.connect(
            lambda cultura, x, y: self._fazendeiro.solicita_colher(cultura, x, y)
        )

        # Chat → Rede
        self._widget_chat.sinal_enviar_mensagem.connect(self._fazendeiro.solicita_chat)

    def _on_desconectado(self):
        self.statusBar().showMessage("Desconectado do servidor.")
        self._widget_log.adicionar_evento("Conexão encerrada.")
