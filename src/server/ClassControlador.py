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
        return json.dumps({"status": "OK", "mensagem": f"BEM_VINDO: Jogador {id_jogador}"}) + "\n"

    def processa_mensagem(self, id_jogador, mensagem_str):
        """Recebe a string crua, executa a ação no jogo e retorna a string de resposta."""
        
        print(f"[JOGO] Comando do Jogador {id_jogador}: {mensagem_str}")
        try:
            dados = json.loads(mensagem_str)
        except json.JSONDecodeError:
            return json.dumps({"status": "ERRO", "mensagem": "JSON inválido"}) + "\n"

        comando = str(dados.get("comando", "")).strip().upper()
        resposta = {}

        if comando == "NICKNAME":
            nome = dados.get("nome", "SemNome")
            self.gerenciador.slots[id_jogador].nick = nome
            resposta = {"status": "OK", "mensagem": f"Nickname atualizado para {nome}"}

        elif comando == "PLANTAR":
            semente, x, y = dados.get("semente"), dados.get("x"), dados.get("y")
            if self.mapa.plantar(x, y, semente):
                resposta = {"status": "OK", "mensagem": "Semente plantada"}
                # Extra: Você poderia adicionar a lógica de remover a semente do inventário do User aqui!
            else:
                resposta = {"status": "ERRO", "mensagem": "Nao foi possivel plantar ai"}

        elif comando == "COLHER":
            cultura, x, y = dados.get("cultura"), dados.get("x"), dados.get("y")
            if self.mapa.colher(x, y, cultura):
                resposta = {"status": "OK", "mensagem": "Cultura colhida"}
                # Extra: Você poderia adicionar a cultura colhida ao inventário do User aqui!
            else:
                resposta = {"status": "ERRO", "mensagem": "Nao foi possivel colher ai"}

        elif comando == "MATRIZ":
            resposta = {"comando": "ATUALIZAR_MAPA", "matriz": self.mapa.matriz}

        elif comando == "SAIR":
            resposta = {"comando": "SAIR", "status": "OK", "mensagem": "Desconectando..."}

        else:
            resposta = {"status": "ERRO", "mensagem": "Comando desconhecido"}

        return json.dumps(resposta) + "\n"