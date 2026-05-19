import json

class ClienteFazenda:
    """Responsável por estruturar os comandos do jogo e enviá-los via TCP."""
    def __init__(self, cliente_tcp):
        # Recebe a classe de rede pronta (Injeção de Dependência!)
        self.rede = cliente_tcp

    def solicita_nickname(self, nome):
        dados = {"comando": "NICKNAME", "nome": nome}
        self.rede.manda_mensagem(json.dumps(dados))

    def solicita_plantar(self, semente, x, y):
        dados = {"comando": "PLANTAR", "semente": semente, "x": x, "y": y}
        self.rede.manda_mensagem(json.dumps(dados))

    def solicita_colher(self, cultura, x, y):
        dados = {"comando": "COLHER", "x": x, "y": y}
        self.rede.manda_mensagem(json.dumps(dados))

    def solicita_matriz(self):
        dados = {"comando": "MATRIZ"}
        self.rede.manda_mensagem(json.dumps(dados))

    def solicita_sair(self):
        dados = {"comando": "SAIR"}
        self.rede.manda_mensagem(json.dumps(dados))

    def solicita_chat(self, mensagem):
        dados = {"comando": "CHAT", "mensagem": mensagem}
        self.rede.manda_mensagem(json.dumps(dados))

    def solicita_preparar(self, x, y):
        dados = {"comando": "PREPARAR", "x": x, "y": y}
        self.rede.manda_mensagem(json.dumps(dados))

    def solicita_pegar_semente(self, cultura: int):
        dados = {"comando": "PEGAR_SEMENTE", "cultura": cultura}
        self.rede.manda_mensagem(json.dumps(dados))

    def solicita_cursor(self, x, y):
        dados = {"comando": "CURSOR", "x": x, "y": y}
        self.rede.manda_mensagem(json.dumps(dados))

    def escutar_servidor(self):
        mensagem = self.rede.recebe_mensagem()
        
        if not mensagem:
            return {"tipo": "DESCONECTADO"}
            
        try:
            dados = json.loads(mensagem)
            
            #ler a chave mestre "comando" enviada pelo servidor no json
            comando_servidor = dados.get("comando")

            if comando_servidor == "ATUALIZAR_MAPA":
                return {"tipo": "MAPA_COMPLETO", "matriz": dados.get("matriz")}
            
            elif comando_servidor == "ATUALIZAR_CELULA":
                return {
                    "tipo": "CELULA", 
                    "x": dados.get("x"), 
                    "y": dados.get("y"), 
                    "valor": dados.get("valor")
                }
            
            elif comando_servidor == "RESPOSTA":
                # Respostas de sistema (BEM_VINDO, OK (de plantio), ERRO, SAIR)
                return {
                    "tipo": "RESPOSTA_SISTEMA",
                    "status": dados.get("status"),
                    "mensagem": dados.get("mensagem"),
                    "cultura": dados.get("cultura")
                }

            elif comando_servidor == "CHAT":
                return {
                    "tipo": "CHAT",
                    "autor": dados.get("autor"),
                    "mensagem": dados.get("mensagem")
                }

            elif comando_servidor == "INICIO_TEMPORADA":
                return {
                    "tipo": "INICIO_TEMPORADA",
                    "numero": dados.get("numero"),
                    "demanda": dados.get("demanda"),
                    "restante": dados.get("restante"),
                    "estoque": dados.get("estoque"),
                }

            elif comando_servidor == "TICK_TIMER":
                return {"tipo": "TICK_TIMER", "restante": dados.get("restante")}

            elif comando_servidor == "ATUALIZAR_ESTOQUE":
                return {"tipo": "ATUALIZAR_ESTOQUE", "estoque": dados.get("estoque")}

            elif comando_servidor == "ATUALIZAR_PROGRESSO":
                return {
                    "tipo": "ATUALIZAR_PROGRESSO",
                    "progresso": dados.get("progresso"),
                    "demanda": dados.get("demanda"),
                }

            elif comando_servidor == "CULTURA_PRONTA":
                return {
                    "tipo": "CULTURA_PRONTA",
                    "x": dados.get("x"),
                    "y": dados.get("y"),
                    "valor": dados.get("valor"),
                }

            elif comando_servidor == "POSICAO_JOGADOR":
                return {
                    "tipo": "POSICAO_JOGADOR",
                    "id": dados.get("id"),
                    "nick": dados.get("nick"),
                    "x": dados.get("x"),
                    "y": dados.get("y"),
                }

            elif comando_servidor == "VITORIA":
                return {"tipo": "VITORIA", "temporada": dados.get("temporada")}

            elif comando_servidor == "DERROTA":
                return {"tipo": "DERROTA", "temporada": dados.get("temporada")}

            elif comando_servidor == "AVISO_GELO":
                return {
                    "tipo": "AVISO_GELO",
                    "x": dados.get("x"),
                    "y": dados.get("y"),
                    "segundos": dados.get("segundos"),
                }

            else:
                print(f"[!] Aviso: Comando do servidor não reconhecido: {dados}")
                return {"tipo": "IGNORAR"}
                
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON.")
            return {"tipo": "IGNORAR"}