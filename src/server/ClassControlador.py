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

    def _coerce_int(self, value):
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

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
            jogador = self.gerenciador.slots.get(id_jogador)
            if jogador is None:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Jogador inválido"}
            else:
                jogador.nick = str(nome)
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": f"Nickname atualizado para {jogador.nick}"}

        elif comando_recebido == "PLANTAR":
            semente = self._coerce_int(dados.get("semente"))
            x = self._coerce_int(dados.get("x"))
            y = self._coerce_int(dados.get("y"))
            if semente is None or x is None or y is None:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Parâmetros inválidos"}
            elif self.mapa.plantar(x, y, semente):
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Semente plantada"}
                novo_valor = self.mapa.matriz[x][y]
                dados_broadcast = {"comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": novo_valor}
                broadcast = json.dumps(dados_broadcast) + "\n"
            else:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Nao foi possivel plantar ai"}

        elif comando_recebido == "COLHER":
            cultura = self._coerce_int(dados.get("cultura"))
            x = self._coerce_int(dados.get("x"))
            y = self._coerce_int(dados.get("y"))
            if cultura is None or x is None or y is None:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Parâmetros inválidos"}
            elif self.mapa.colher(x, y, cultura):
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Cultura colhida"}
                novo_valor = self.mapa.matriz[x][y]
                dados_broadcast = {"comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": novo_valor}
                broadcast = json.dumps(dados_broadcast) + "\n"
            else:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Nao foi possivel colher ai"}

        elif comando_recebido == "MATRIZ":
            resposta = {"comando": "ATUALIZAR_MAPA", "matriz": self.mapa.matriz}

        elif comando_recebido == "SAIR":
            # Comando especial para o servidor encerrar esta conexão
            resposta = {"comando": "SAIR", "status": "OK", "mensagem": "Desconectando..."}

        else:
            resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Comando desconhecido"}

        return json.dumps(resposta) + "\n", broadcast
