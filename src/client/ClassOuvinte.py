from PyQt6.QtCore import QThread, pyqtSignal

class OuvinteThread(QThread):
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

    def __init__(self, fazendeiro, mapa_jogo):
        super().__init__()
        self.fazendeiro = fazendeiro
        self.mapa_jogo = mapa_jogo

    def run(self):
        while True:
            evento = self.fazendeiro.escutar_servidor()
            tipo = evento["tipo"]

            if tipo == "DESCONECTADO":
                self.sinal_desconectado.emit()
                break

            elif tipo == "MAPA_COMPLETO":
                self.mapa_jogo.atualizar_matriz(evento["matriz"])
                self.sinal_mapa_completo.emit(evento["matriz"])

            elif tipo == "CELULA":
                x, y, valor = evento["x"], evento["y"], evento["valor"]
                self.mapa_jogo.matriz[x][y] = valor
                self.sinal_celula_atualizada.emit(x, y, valor)

            elif tipo == "RESPOSTA_SISTEMA":
                self.sinal_resposta_sistema.emit(
                    evento.get("status", ""),
                    evento.get("mensagem", ""),
                    {"cultura": evento.get("cultura"), "quantidade": evento.get("quantidade", 0)}
                )

            elif tipo == "CHAT":
                self.sinal_chat_recebido.emit(
                    evento.get("autor", "?"),
                    evento.get("mensagem", "")
                )

            elif tipo == "INICIO_TEMPORADA":
                self.sinal_inicio_temporada.emit(evento)

            elif tipo == "TICK_TIMER":
                self.sinal_tick_timer.emit(evento.get("restante", 0))

            elif tipo == "ATUALIZAR_ESTOQUE":
                self.sinal_estoque_atualizado.emit(evento.get("estoque", {}))

            elif tipo == "ATUALIZAR_PROGRESSO":
                self.sinal_progresso_atualizado.emit(
                    evento.get("progresso", {}),
                    evento.get("demanda", {})
                )

            elif tipo == "CULTURA_PRONTA":
                self.sinal_cultura_pronta.emit(
                    evento.get("x", 0),
                    evento.get("y", 0),
                    evento.get("cultura", 0)
                )

            elif tipo == "POSICAO_JOGADOR":
                self.sinal_posicao_jogador.emit(
                    evento.get("slot", 0),
                    evento.get("nick", ""),
                    evento.get("x", 0),
                    evento.get("y", 0)
                )

            elif tipo == "VITORIA":
                self.sinal_vitoria.emit(evento.get("temporada", 0))

            elif tipo == "DERROTA":
                self.sinal_derrota.emit(evento.get("temporada", 0))

            elif tipo == "AVISO_GELO":
                self.sinal_aviso_gelo.emit(
                    evento.get("x", 0),
                    evento.get("y", 0),
                    evento.get("segundos", 0)
                )
