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

    def solicita_sair(self):
        dados = {"comando": "SAIR"}
        self.rede.manda_mensagem(json.dumps(dados))

    def solicita_matriz(self):
        dados = {"comando": "MATRIZ"}
        self.rede.manda_mensagem(json.dumps(dados))

    def receber_matriz(self):
        """Espera a matriz do servidor e converte o JSON."""
        mensagem = self.rede.recebe_mensagem()
        
        if not mensagem:
            print("Erro: Não recebeu resposta do servidor.")
            return None
            
        try:
            dados_json = json.loads(mensagem)
            if dados_json.get("comando") == "ATUALIZAR_MAPA":
                matriz_completa = dados_json.get("matriz", [])
                return matriz_completa
            else:
                print(f"Aviso: Esperava a matriz, mas recebeu: {dados_json}")
                return None
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da matriz.")
            return None
        
    def ler_resposta(self):
        """Lê a resposta do servidor e retorna o conteúdo."""
        mensagem = self.rede.recebe_mensagem()
        
        if not mensagem:
            print("Erro: Não recebeu resposta do servidor.")
            return None
            
        try:
            dados_json = json.loads(mensagem)
            return dados_json
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da resposta.")
            return None