from PyQt6.QtCore import QThread, pyqtSignal

class OuvinteThread(QThread):
    """Thread de escuta do servidor. Emite sinais Qt para atualizar a UI."""
    sinal_mapa_completo = pyqtSignal(list)
    sinal_celula_atualizada = pyqtSignal(int, int, int)
    sinal_resposta_sistema = pyqtSignal(str, str)
    sinal_chat_recebido = pyqtSignal(str, str)
    sinal_desconectado = pyqtSignal()

    def __init__(self, fazendeiro, mapa_jogo):
        super().__init__()
        self.fazendeiro = fazendeiro
        self.mapa_jogo = mapa_jogo

    def run(self):
        while True:
            evento = self.fazendeiro.escutar_servidor()

            if evento["tipo"] == "DESCONECTADO":
                self.sinal_desconectado.emit()
                break

            elif evento["tipo"] == "MAPA_COMPLETO":
                self.mapa_jogo.atualizar_matriz(evento["matriz"])
                self.sinal_mapa_completo.emit(evento["matriz"])

            elif evento["tipo"] == "CELULA":
                x, y, valor = evento["x"], evento["y"], evento["valor"]
                self.mapa_jogo.matriz[x][y] = valor
                self.sinal_celula_atualizada.emit(x, y, valor)

            elif evento["tipo"] == "RESPOSTA_SISTEMA":
                self.sinal_resposta_sistema.emit(
                    evento.get("status", ""),
                    evento.get("mensagem", "")
                )

            elif evento["tipo"] == "CHAT":
                self.sinal_chat_recebido.emit(
                    evento.get("autor", "?"),
                    evento.get("mensagem", "")
                )