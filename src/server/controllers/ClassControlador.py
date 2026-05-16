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


#-------------------------------------------------------------------------------------------------
    def gera_boas_vindas(self, id_jogador):
        # Retorna apenas o dicionário Python!
        return {
            "comando": "RESPOSTA", 
            "status": "OK", 
            "mensagem": f"BEM_VINDO: {self.gerenciador.slots[id_jogador].nick}"
        }
    
    def resposta_nickname(self, id_jogador, dados):
        nome = dados.get("nome", "SemNome") #var nome vai receber  o q ta no campo "nome" ou vai receber a string "SemNome" se o campo n existir
        self.gerenciador.slots[id_jogador].nick = nome
        resposta = self.gera_boas_vindas(id_jogador)
        return resposta, None 

#-------------------------------------------------------------------------------------------------
    def resposta_plantar(self, id_jogador, dados):

        #vou usar pra fazer o broadcast, pra mostrar quem fez a ação, talves mais um campo, mas ai teria que tratar no cliente. 
        #nick_jogador = self.gerenciador.slots[id_jogador].nick

        semente, x, y = dados.get("semente"), dados.get("x"), dados.get("y")
        resultado = self.mapa.plantar(x, y, semente)
        
        if resultado["validar"] == True:
            resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": resultado["motivo"]}
            novo_valor = self.mapa.matriz[x][y]
            dados_broadcast = {"comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": novo_valor}
            broadcast = json.dumps(dados_broadcast) + "\n"
        else:
            resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": resultado["motivo"]}
            
        return resposta, broadcast

#-------------------------------------------------------------------------------------------------
    def resposta_colher(self, id_jogador, dados):

        #vou usar pra fazer o broadcast, pra mostrar quem fez a ação, talves mais um campo, mas ai teria que tratar no cliente. 
        #nick_jogador = self.gerenciador.slots[id_jogador].nick

        cultura, x, y = dados.get("cultura"), dados.get("x"), dados.get("y")
        resultado = self.mapa.colher(x, y, cultura)
        
        if resultado["validar"] == True:
            resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": resultado["motivo"]}   
            novo_valor = self.mapa.matriz[x][y]
            dados_broadcast = {"comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": novo_valor}
            broadcast = json.dumps(dados_broadcast) + "\n"
        else:
            resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": resultado["motivo"]}

        return resposta, broadcast

#-------------------------------------------------------------------------------------------------
    def resposta_matriz(self):
        resposta = {"comando": "ATUALIZAR_MAPA", "matriz": self.mapa.matriz}
        return resposta, None

#-------------------------------------------------------------------------------------------------
    def resposta_sair(self):
        resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Desconectando..."}
        return resposta, None

#-------------------------------------------------------------------------------------------------
    def resposta_erro(self):
        resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Comando desconhecido"}
        return resposta, None
#-------------------------------------------------------------------------------------------------

    def processa_mensagem(self, id_jogador, mensagem_str):
        print(f"[JOGO] Comando do Jogador {id_jogador}: {mensagem_str}")
        try:
            dados = json.loads(mensagem_str)
        except json.JSONDecodeError:
            return json.dumps({"comando": "RESPOSTA", "status": "ERRO", "mensagem": "JSON inválido"}) + "\n", None

        comando_recebido = str(dados.get("comando", "")).strip().upper()

        # O Roteador (Dispatcher): Chama a função certa baseada no comando!
        if comando_recebido == "NICKNAME":
            resposta, broadcast = self.resposta_nickname(id_jogador, dados)

        elif comando_recebido == "PLANTAR":
            resposta, broadcast = self.resposta_plantar(id_jogador, dados)

        elif comando_recebido == "COLHER":
            resposta, broadcast = self.resposta_colher(id_jogador, dados)

        elif comando_recebido == "MATRIZ":
            resposta, broadcast = self.resposta_matriz()

        elif comando_recebido == "SAIR":
            resposta, broadcast = self.resposta_sair()

        else:
            resposta, broadcast = self.resposta_erro()

        # Converte a resposta pra String e repassa o broadcast intacto
        return json.dumps(resposta) + "\n", broadcast




