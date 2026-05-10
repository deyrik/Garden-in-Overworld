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

    #Tipos de mensagens ja estruradas em json para mandar (usam a func manda_mensagem ())
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

    def solicita_nickname(self, nome):
        dados = {"comando": "NICKNAME", "nome": nome}
        self.manda_mensagem(json.dumps(dados) + "\n")

    def solicita_plantar(self, semente, x, y):
        dados = {
            "comando": "PLANTAR",
            "semente": semente,
            "x": x,
            "y": y
        }
        self.manda_mensagem(json.dumps(dados) + "\n")

    def solicita_colher(self, cultura, x, y):
        dados = {
            "comando": "COLHER",
            "cultura": cultura,
            "x": x,
            "y": y
        }
        self.manda_mensagem(json.dumps(dados) + "\n")

    def solicita_matriz(self):
        dados = {"comando": "MATRIZ"}
        self.manda_mensagem(json.dumps(dados) + "\n")
    
    def solicita_sair(self):
        dados = {"comando": "SAIR"}
        self.manda_mensagem(json.dumps(dados) + "\n")



    def recebe_mensagem(self):
        if self.client_socket:                                    
            buffer_completo = ""
            
            try:
                while True:
                    pedaco = self.client_socket.recv(1024).decode()
                    if not pedaco:
                        print("Conexão com o servidor foi perdida.")
                        return None
                        
                    buffer_completo += pedaco
                    
                    # Se o servidor mandou o \n, significa que o JSON terminou!
                    if '\n' in buffer_completo:
                        break 
                
                # Limpa os espaços em branco e o \n do final
                mensagem_final = buffer_completo.strip()
                print(f"<< Recebido: {mensagem_final}")
                return mensagem_final
             
            except Exception as e:                                
                print(f"Erro ao receber mensagem: {e}")
                return None
        else:
            print("Não estava conectado ao servidor.")
            return None
        
    def montar_pacotes(self, numero_pacotes):
        """
        Bloqueia a execução e espera os N pacotes da matriz chegarem.
        Junta todas as partes e retorna a matriz completa (2D).
        """
        matriz_completa = []

        print(f"[Sistema] Recebendo mapa em {numero_pacotes} pacotes...")

        for i in range(numero_pacotes):
            # Lê 1 pacote completo do socket
            mensagem = self.recebe_mensagem()
            
            if not mensagem:
                print("Erro: Conexão caiu antes de receber toda a matriz.")
                return None
                
            try:
                dados_json = json.loads(mensagem)
                
                if dados_json.get("comando") == "ATUALIZAR_MAPA":
                    matriz_parcial = dados_json.get("matriz_parcial", [])
                    # O extend gruda as linhas recebidas no fundo da matriz completa
                    matriz_completa.extend(matriz_parcial)
                    print(f"Pacote {i+1}/{numero_pacotes} recebido com sucesso.")
                else:
                    print(f"Aviso: Recebeu um comando inesperado durante a montagem: {dados_json}")
                    
            except json.JSONDecodeError:
                print(f"Erro ao decodificar JSON do pacote {i+1}.")
                return None

        print(f"Matriz montada com sucesso! Tamanho total: {len(matriz_completa)} linhas.")
        return matriz_completa

    def receber_matriz(self):
        """
        Função específica para quando o jogo inicia.
        Pede a matriz e espera o pacote gigante do servidor chegar.
        """

        # 2. Fica esperando a resposta gigante (o recebe_mensagem lida com o tamanho)
        mensagem = self.recebe_mensagem()
        
        if not mensagem:
            print("Erro: Não recebeu resposta do servidor.")
            return None
            
        try:
            dados_json = json.loads(mensagem)
            
            if dados_json.get("comando") == "ATUALIZAR_MAPA":
                # Como o servidor mandou tudo de uma vez, é só extrair!
                matriz_completa = dados_json.get("matriz", [])
                print(f"[Sistema] Matriz recebida com sucesso! Tamanho: {len(matriz_completa)} linhas.")
                return matriz_completa
            else:
                print(f"Aviso: Esperava a matriz, mas recebeu: {dados_json}")
                return None
                
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da matriz.")
            return None


































#TESTE:
if __name__ == "__main__":
    cliente = TCPCliente("localhost", 12345)
    cliente.conecta_servidor()# faz o primeiro contato pedindo pra conectar
    
    #pede o mapa do jogo
    cliente.solicita_matriz()




    # Aguarda a mensagem de BEM_VINDO do servidor antes de interagir
    cliente.recebe_mensagem()
    
    # Define o Nickname
    cliente.solicita_nickname("Gabe")
    cliente.recebe_mensagem()
    time.sleep(1)

    print("\n--- Testando Lógica da Fazenda ---")
    
    # Tenta plantar Trigo (3) na posição 5, 5
    cliente.solicita_plantar(semente=3, x=5, y=5)
    cliente.recebe_mensagem() # Pega a resposta do servidor ("OK" ou "ERRO")
    time.sleep(1)
    
    # Tenta colher o Trigo na mesma posição
    cliente.solicita_colher(cultura=3, x=5, y=5)
    cliente.recebe_mensagem()
    time.sleep(1)

    # Tenta plantar fora do mapa para forçar o ERRO do seu servidor (ex: linha 50)
    print("\n--- Forçando um Erro ---")
    cliente.solicita_plantar(semente=5, x=50, y=50)
    cliente.recebe_mensagem()
    time.sleep(1)

    print("\n--- matriz ---")
    cliente.solicita_matriz()
    cliente.recebe_mensagem()
    time.sleep(1)

    print("\n--- Desconectando ---")
    cliente.solicita_sair()
    cliente.recebe_mensagem()
    cliente.fecha_conexao()