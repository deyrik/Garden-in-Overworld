# src/client/ClassPonteSinais.py
from PyQt6.QtCore import QObject, pyqtSignal


class PonteSinais(QObject):
    """Carrega os mesmos sinais que a antiga OuvinteThread expunha.
    A JanelaPrincipal conecta-se a estes sinais sem qualquer alteração.
    Emitidos a partir da thread-daemon do Pyro; o Qt entrega na thread da GUI
    via conexão enfileirada automática (objeto vive na thread principal)."""

    sinal_mapa_completo        = pyqtSignal(list)
    sinal_celula_atualizada    = pyqtSignal(int, int, int)
    sinal_resposta_sistema     = pyqtSignal(str, str, object)
    sinal_chat_recebido        = pyqtSignal(str, str)
    sinal_desconectado         = pyqtSignal()
    sinal_inicio_temporada     = pyqtSignal(dict)
    sinal_tick_timer           = pyqtSignal(int)
    sinal_estoque_atualizado   = pyqtSignal(dict)
    sinal_progresso_atualizado = pyqtSignal(dict, dict)
    sinal_cultura_pronta       = pyqtSignal(int, int, int)
    sinal_posicao_jogador      = pyqtSignal(int, str, int, int)
    sinal_vitoria              = pyqtSignal(int)
    sinal_derrota              = pyqtSignal(int)
    sinal_aviso_gelo           = pyqtSignal(int, int, int)
