import json

class ControladorFazenda:
    """Responsável por traduzir JSONs e aplicar as regras de negócio do jogo."""
    def __init__(self, mapa_instancia, gerenciador_instancia):
        self.mapa = mapa_instancia
        self.gerenciador = gerenciador_instancia

    def conecta_jogador(self):
        """Tenta achar um slot livre e retorna o ID (ou None se cheio)."""
        return self.gerenciador.adiciona_na_vaga()

    def desconecta_jogador(self, id_jogador):
        self.gerenciador.remove_da_vaga(id_jogador)

    def gera_boas_vindas(self, id_jogador):
        return json.dumps({"comando": "RESPOSTA", "status": "OK", "mensagem": f"BEM_VINDO: Jogador {id_jogador}"}) + "\n"

    def processa_mensagem(self, id_jogador, mensagem_str):
        print(f"[JOGO] Comando do Jogador {id_jogador}: {mensagem_str}")
        try:
            dados = json.loads(mensagem_str)
        except json.JSONDecodeError:
            return json.dumps({"comando": "RESPOSTA", "status": "ERRO", "mensagem": "JSON inválido"}) + "\n", None

        comando_recebido = str(dados.get("comando", "")).strip().upper()
        resposta = {}
        broadcast = None

        if comando_recebido == "NICKNAME":
            nome = dados.get("nome", "SemNome")
            self.gerenciador.slots[id_jogador].nick = nome
            resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": f"Nickname atualizado para {nome}"}

        elif comando_recebido == "PLANTAR":
            semente, x, y = dados.get("semente"), dados.get("x"), dados.get("y")
            if self.mapa.plantar(x, y, semente):
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Semente plantada"}
                novo_valor = self.mapa.matriz[x][y]
                dados_broadcast = {"comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": novo_valor}
                broadcast = json.dumps(dados_broadcast) + "\n"
            else:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Nao foi possivel plantar ai"}

        elif comando_recebido == "COLHER":
            cultura, x, y = dados.get("cultura"), dados.get("x"), dados.get("y")
            if self.mapa.colher(x, y, cultura):
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Cultura colhida"}
                novo_valor = self.mapa.matriz[x][y]
                dados_broadcast = {"comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": novo_valor}
                broadcast = json.dumps(dados_broadcast) + "\n"
            else:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Nao foi possivel colher ai"}

        elif comando_recebido == "MATRIZ":
            resposta = {"comando": "ATUALIZAR_MAPA", "matriz": self.mapa.matriz}

        elif comando_recebido == "SAIR":
            resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Desconectando..."}

        else:
            resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Comando desconhecido"}

        return json.dumps(resposta) + "\n", broadcast