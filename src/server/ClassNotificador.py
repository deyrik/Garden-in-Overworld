# src/server/ClassNotificador.py
import threading
import queue


class Notificador:
    """Empurra eventos de jogo para os callbacks dos clientes.

    Todo uso de proxies Pyro é isolado numa única thread trabalhadora
    (proxies Pyro não são thread-safe entre threads). Quem produz evento
    apenas enfileira; o worker drena a fila e invoca o método tipado em
    cada callback registrado, descartando os que caíram.
    """

    def __init__(self):
        self._callbacks = {}            # id_jogador -> callback (proxy ou objeto)
        self._lock = threading.Lock()
        self._fila = queue.Queue()
        self._worker = threading.Thread(target=self._processar, daemon=True)
        self._worker.start()

    def registrar(self, id_jogador, callback):
        with self._lock:
            self._callbacks[id_jogador] = callback

    def remover(self, id_jogador):
        with self._lock:
            self._callbacks.pop(id_jogador, None)

    def aguardar_processamento(self):
        """Bloqueia até a fila esvaziar (usado em testes)."""
        self._fila.join()

    def _enfileirar(self, metodo, *args):
        self._fila.put((metodo, args))

    # --- API tipada (1:1 com os métodos de ClienteCallback) ---
    def atualizar_mapa(self, matriz):            self._enfileirar("atualizar_mapa", matriz)
    def atualizar_celula(self, x, y, valor):     self._enfileirar("atualizar_celula", x, y, valor)
    def inicio_temporada(self, estado):          self._enfileirar("inicio_temporada", estado)
    def tick_timer(self, restante):              self._enfileirar("tick_timer", restante)
    def atualizar_estoque(self, estoque):        self._enfileirar("atualizar_estoque", estoque)
    def atualizar_progresso(self, prog, dem):    self._enfileirar("atualizar_progresso", prog, dem)
    def cultura_pronta(self, x, y, valor):       self._enfileirar("cultura_pronta", x, y, valor)
    def posicao_jogador(self, idj, nick, x, y):  self._enfileirar("posicao_jogador", idj, nick, x, y)
    def chat(self, autor, msg):                  self._enfileirar("chat", autor, msg)
    def aviso_gelo(self, x, y, seg):             self._enfileirar("aviso_gelo", x, y, seg)
    def vitoria(self, num):                      self._enfileirar("vitoria", num)
    def derrota(self, num):                      self._enfileirar("derrota", num)

    def _processar(self):
        while True:
            metodo, args = self._fila.get()
            try:
                with self._lock:
                    alvos = list(self._callbacks.items())
                mortos = []
                for idj, callback in alvos:
                    try:
                        if hasattr(callback, "_pyroClaimOwnership"):
                            callback._pyroClaimOwnership()
                        getattr(callback, metodo)(*args)
                    except Exception:
                        # Cliente caiu (CommunicationError) ou callback falhou: descarta.
                        mortos.append(idj)
                for idj in mortos:
                    self.remover(idj)
            finally:
                self._fila.task_done()
