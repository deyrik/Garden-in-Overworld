import Pyro5.api


# No retorno das funçoes nao preciso preocupar mais em coverter para json para facilitar do outro lado,
# com o Pyro5 ele vai fazer isso da maneira dele, entao posso so retornar um dicionario mesmo.

@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single") # Garante que todos os jogadores usem a mesma instância da fazenda
class ControladorFazenda:
    def __init__(self, mapa_instancia, gerenciador_instancia):
        self.mapa = mapa_instancia
        self.gerenciador = gerenciador_instancia

    def conectar(self, nome):
        """O cliente RMI chama esse método direto para entrar no jogo."""
        id_jogador = self.gerenciador.adiciona_na_vaga()
        if id_jogador is not None:
            self.gerenciador.slots[id_jogador].nick = nome
            return {"status": "OK", "id": id_jogador, "mensagem": f"BEM_VINDO: {nome}"}
        return {"status": "ERRO", "mensagem": "A fazenda já atingiu o limite máximo de agricultores (4/4)"}

    def desconectar(self, id_jogador):
        self.gerenciador.remove_da_vaga(id_jogador)
        return {"status": "OK"}

    def plantar(self, id_jogador, x, y, semente):
        """O cliente chama passando direto os inteiros x, y e semente"""
        resultado = self.mapa.plantar(x, y, semente)
        return resultado 

    def colher(self, id_jogador, x, y, cultura):
        resultado = self.mapa.colher(x, y, cultura)
        return resultado

    def pegar_matriz(self):
        """Método simples para o cliente estado atual do mapa."""
        return self.mapa.matriz