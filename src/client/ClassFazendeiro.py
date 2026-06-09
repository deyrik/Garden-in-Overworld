# src/client/ClassFazendeiro.py
class ClienteFazenda:
    """Traduz as ações da GUI em chamadas de método no proxy do servidor.
    O valor de retorno (resposta) é re-emitido como sinal_resposta_sistema,
    preservando o comportamento de toasts/log da JanelaPrincipal."""

    def __init__(self, servidor, ponte, id_jogador):
        self.servidor = servidor      # Pyro5 Proxy de garden.servidor
        self.ponte = ponte            # PonteSinais
        self.id = id_jogador

    def _emitir_resposta(self, resp):
        if not resp:
            return
        self.ponte.sinal_resposta_sistema.emit(
            resp.get("status", ""),
            resp.get("mensagem", ""),
            {"cultura": resp.get("cultura"), "quantidade": resp.get("quantidade", 0)},
        )

    def solicita_preparar(self, x, y):
        self._emitir_resposta(self.servidor.preparar(self.id, x, y))

    def solicita_pegar_semente(self, cultura, quantidade=1):
        resp = None
        for _ in range(max(1, int(quantidade))):
            resp = self.servidor.pegar_semente(self.id, int(cultura))
        self._emitir_resposta(resp)

    def solicita_plantar(self, semente, x, y):
        self._emitir_resposta(self.servidor.plantar(self.id, semente, x, y))

    def solicita_colher(self, cultura, x, y):
        self._emitir_resposta(self.servidor.colher(self.id, x, y))

    def solicita_chat(self, mensagem):
        self.servidor.enviar_chat(self.id, mensagem)

    def solicita_cursor(self, x, y):
        self.servidor.mover_cursor(self.id, x, y)

    def solicita_sair(self):
        try:
            self.servidor.sair(self.id)
        except Exception:
            pass
