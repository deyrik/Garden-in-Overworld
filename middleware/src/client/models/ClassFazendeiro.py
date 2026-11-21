import Pyro5.api

class ClienteFazenda:
    """Responsável por se comunicar com o Servidor via Middleware RMI (Pyro5)."""
    def __init__(self):
        self.servidor = None
        self.id_jogador = None
        self.conectar_rmi()

    def conectar_rmi(self):
        """Busca o Name Server e conecta ao objeto remoto da fazenda."""
        try:
            print("[+] Procurando o Name Server na rede...")
            ns = Pyro5.api.locate_ns()
            uri = ns.lookup("fazenda.servidor")
            print(f"[+] Fazenda encontrada na URI: {uri}")
            
            # Cria o "proxy", que age como se fosse a classe local
            self.servidor = Pyro5.api.Proxy(uri)
        except Exception as e:
            print(f"[-] Erro fatal: Não foi possível conectar ao Middleware: {e}")
            self.servidor = None

    def solicita_nickname(self, nome):
        """Conecta o jogador e pega o ID da vaga."""
        if not self.servidor: return None
        
        try:
            resposta = self.servidor.conectar(nome)
            if resposta.get("status") == "OK":
                self.id_jogador = resposta.get("id")
            return resposta
        except Exception as e:
            print(f"Erro no RMI: {e}")
            return {"status": "ERRO", "mensagem": "Conexão perdida com o Servidor"}

    def solicita_plantar(self, semente, x, y):
        if not self.servidor or self.id_jogador is None: return None
        try:
            return self.servidor.plantar(self.id_jogador, x, y, semente)
        except Exception as e:
             return {"status": "ERRO", "mensagem": "Falha de comunicação RMI"}

    def solicita_colher(self, cultura, x, y):
        if not self.servidor or self.id_jogador is None: return None
        try:
             return self.servidor.colher(self.id_jogador, x, y, cultura)
        except Exception as e:
             return {"status": "ERRO", "mensagem": "Falha de comunicação RMI"}

    def solicita_matriz(self):
        """Puxa a matriz inteira de uma vez e a retorna."""
        if not self.servidor: return []
        try:
             return self.servidor.pegar_matriz()
        except Exception as e:
             print("Erro ao atualizar matriz.")
             return []
             
    def solicita_sair(self):
        if self.servidor and self.id_jogador is not None:
            try:
                self.servidor.desconectar(self.id_jogador)
            except Exception:
                pass # Se deu erro ao sair, já caiu mesmo