import socket
import json
import time

class TCPCliente:
    """Instancia de cliente TCP"""
    def __init__(self, host, port):
        self.endereco = host
        self.porta = port
        self.client_socket = None

    def conecta_servidor(self):
        """Estabelece uma conexão TCP com o servidor."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)          
            self.client_socket.connect((self.endereco, self.porta))                         
            print(f"[+] Conectado no servidor {self.endereco}:{self.porta}")
        except Exception as e:                                                              
            print(f"[-] Erro ao conectar ao servidor: {e}")

    def fecha_conexao(self):
        if self.client_socket:                            
            try:                                          
                self.client_socket.close()                
                self.client_socket = None                 
                print("Conexão fechada.")
            except Exception as e:                        
                print(f"Erro ao fechar conexão: {e}")  
        else:
            print("Não estava conectado ao servidor.")

    #Tipos de mensagens ja estruradas em json para mandar (usam a func manda_mensagem)
    def manda_mensagem(self, message):
        if self.client_socket:                               
            try:
                # DICA DE OURO: Adiciona o \n no final de todas as mensagens
                # Isso garante que o servidor saiba onde o JSON termina!
                if not message.endswith('\n'):
                    message += '\n'
                                             
                self.client_socket.sendall(message.encode()) 
                print(f">>Enviado: {message.strip()}")
            except Exception as e:                           
                print(f"Erro ao enviar mensagem: {e}")
        else:
            print("Não estava conectado ao servidor.")

    def enviar_nickname(self, nome):
        dados = {"comando": "NICKNAME", "nome": nome}
        self.manda_mensagem(json.dumps(dados))

    def enviar_plantar(self, semente, x, y):
        dados = {
            "comando": "PLANTAR",
            "semente": semente,
            "x": x,
            "y": y
        }
        self.manda_mensagem(json.dumps(dados))

    def enviar_colher(self, cultura, x, y):
        dados = {
            "comando": "COLHER",
            "cultura": cultura,
            "x": x,
            "y": y
        }
        self.manda_mensagem(json.dumps(dados))

    def recebe_mensagem(self):
        if self.client_socket:                                    
            try:                                                  
                resposta = self.client_socket.recv(1024).decode() 
                if resposta:
                    print(f"<< Recebido: {resposta.strip()}")
                return resposta
            except Exception as e:                                
                print(f"Erro ao receber mensagem: {e}")
        else:
            print("Não estava conectado ao servidor.")
            return None

    def enviar_sair(self):
        dados = {"comando": "SAIR"}
        self.manda_mensagem(json.dumps(dados))

#TESTE:
if __name__ == "__main__":
    cliente = TCPCliente("localhost", 12345)
    cliente.conecta_servidor()# faz o primeiro contato pedindo pra conectar
    
    # Aguarda a mensagem de BEM_VINDO do servidor antes de interagir
    cliente.recebe_mensagem()
    
    # Define o Nickname
    cliente.enviar_nickname("Gabe")
    cliente.recebe_mensagem()
    time.sleep(1)

    print("\n--- Testando Lógica da Fazenda ---")
    
    # Tenta plantar Trigo (3) na posição 5, 5
    cliente.enviar_plantar(semente=3, x=5, y=5)
    cliente.recebe_mensagem() # Pega a resposta do servidor ("OK" ou "ERRO")
    time.sleep(1)
    
    # Tenta colher o Trigo na mesma posição
    cliente.enviar_colher(cultura=3, x=5, y=5)
    cliente.recebe_mensagem()
    time.sleep(1)

    # Tenta plantar fora do mapa para forçar o ERRO do seu servidor (ex: linha 50)
    print("\n--- Forçando um Erro ---")
    cliente.enviar_plantar(semente=5, x=50, y=50)
    cliente.recebe_mensagem()
    time.sleep(1)

    print("\n--- Desconectando ---")
    cliente.enviar_sair()
    cliente.recebe_mensagem()
    cliente.fecha_conexao()