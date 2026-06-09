# src/client/ClassClienteCallback.py
import Pyro5.api


@Pyro5.api.expose
class ClienteCallback:
    """Objeto Pyro registrado no daemon do cliente. O servidor invoca estes
    métodos para empurrar eventos; cada um apenas re-emite o sinal Qt."""

    def __init__(self, ponte):
        self._ponte = ponte

    @Pyro5.api.oneway
    def atualizar_mapa(self, matriz):
        self._ponte.sinal_mapa_completo.emit(matriz)

    @Pyro5.api.oneway
    def atualizar_celula(self, x, y, valor):
        self._ponte.sinal_celula_atualizada.emit(x, y, valor)

    @Pyro5.api.oneway
    def inicio_temporada(self, estado):
        self._ponte.sinal_inicio_temporada.emit(estado)

    @Pyro5.api.oneway
    def tick_timer(self, restante):
        self._ponte.sinal_tick_timer.emit(restante)

    @Pyro5.api.oneway
    def atualizar_estoque(self, estoque):
        self._ponte.sinal_estoque_atualizado.emit(estoque)

    @Pyro5.api.oneway
    def atualizar_progresso(self, progresso, demanda):
        self._ponte.sinal_progresso_atualizado.emit(progresso, demanda)

    @Pyro5.api.oneway
    def cultura_pronta(self, x, y, valor):
        self._ponte.sinal_cultura_pronta.emit(x, y, valor)

    @Pyro5.api.oneway
    def posicao_jogador(self, idj, nick, x, y):
        self._ponte.sinal_posicao_jogador.emit(idj, nick, x, y)

    @Pyro5.api.oneway
    def chat(self, autor, mensagem):
        self._ponte.sinal_chat_recebido.emit(autor, mensagem)

    @Pyro5.api.oneway
    def aviso_gelo(self, x, y, segundos):
        self._ponte.sinal_aviso_gelo.emit(x, y, segundos)

    @Pyro5.api.oneway
    def vitoria(self, temporada):
        self._ponte.sinal_vitoria.emit(temporada)

    @Pyro5.api.oneway
    def derrota(self, temporada):
        self._ponte.sinal_derrota.emit(temporada)
