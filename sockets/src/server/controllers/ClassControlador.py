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
        broadcast = json.dumps({"comando": "NOVO_JOGADOR", "nome": nome}) + "\n"
        return resposta, broadcast

#-------------------------------------------------------------------------------------------------
    def resposta_plantar(self, id_jogador, dados):

        #vou usar pra fazer o broadcast, pra mostrar quem fez a ação, talves mais um campo, mas ai teria que tratar no cliente. 
        #nick_jogador = self.gerenciador.slots[id_jogador].nick

        broadcast = None

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

        broadcast = None 

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
    def resposta_sair(self, id_jogador):
        nome = self.gerenciador.slots[id_jogador].nick
        resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Desconectando..."}
        broadcast = json.dumps({"comando": "JOGADOR_SAIU", "nome": nome}) + "\n"
        return resposta, broadcast

#-------------------------------------------------------------------------------------------------
    def resposta_erro(self):
        resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Comando desconhecido"}
        return resposta, None
#-------------------------------------------------------------------------------------------------

    def processa_mensagem(self, id_jogador, mensagem_str):
        try:
            # print(f"[JOGO] Comando do Jogador {id_jogador}: {mensagem_str}") #comentado para não floodar o terminal
            try:
                dados = json.loads(mensagem_str)
            except json.JSONDecodeError:
                return json.dumps({"comando": "RESPOSTA", "status": "ERRO", "mensagem": "JSON inválido"}) + "\n", None

            comando_recebido = str(dados.get("comando", "")).strip().upper()


            if comando_recebido == "NICKNAME":
                resposta, broadcast = self.resposta_nickname(id_jogador, dados)

            elif comando_recebido == "PLANTAR":
                resposta, broadcast = self.resposta_plantar(id_jogador, dados)

            elif comando_recebido == "COLHER":
                resposta, broadcast = self.resposta_colher(id_jogador, dados)

            elif comando_recebido == "MATRIZ":
                resposta, broadcast = self.resposta_matriz()

            elif comando_recebido == "SAIR":
                resposta, broadcast = self.resposta_sair(id_jogador)

            else:
                resposta, broadcast = self.resposta_erro()

            # Converte a resposta pra String e repassa o broadcast intacto
            return json.dumps(resposta) + "\n", broadcast
            
        except Exception as e:
            import traceback
            print("\n" + "="*50)
            print("ESCUDO ANTI-CRASH ATIVADO NO SERVIDOR")
            print(f"O jogador {id_jogador} clicou rápido demais e gerou um erro interno!")
            print(f"JSON que causou a falha: {mensagem_str}")
            print("--- Detalhes do Erro ---")
            traceback.print_exc() # Isso vai imprimir a exata linha de código que quebrou!
            print("="*50 + "\n")
            
            # Devolvemos um erro seguro para o Cliente, para a interface dele não desconectar
            resposta_segura = {
                "comando": "RESPOSTA", 
                "status": "ERRO", 
                "mensagem": "Nao espame clickes, jogue na calma !!!."
            }
            return json.dumps(resposta_segura) + "\n", None
