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
        dados = {"comando": "COLHER", "cultura": cultura, "x": x, "y": y}
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
                    "mensagem": dados.get("mensagem")
                }

            elif comando_servidor == "CHAT":
                return {
                    "tipo": "CHAT",
                    "autor": dados.get("autor"),
                    "mensagem": dados.get("mensagem")
                }

            else:
                print(f"[!] Aviso: Comando do servidor não reconhecido: {dados}")
                return {"tipo": "IGNORAR"}
                
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON.")
            return {"tipo": "IGNORAR"}