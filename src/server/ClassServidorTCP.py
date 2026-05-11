import socket
import threading

class ServidorTCP:
    """Lida estritamente com Sockets e Threads. Totalmente agnóstico ao jogo."""
    def __init__(self, host="localhost", port=12345, 
                 ao_conectar=None,  
                 ao_gerar_boas_vindas=None,
                 ao_receber_mensagem=None, 
                 ao_desconectar=None):
        
        
        self.host = host
        self.port = port
        # Callbacks (Gatilhos/Funcoes) passados pelo Controlador
        self.ao_conectar = ao_conectar 
        self.ao_gerar_boas_vindas = ao_gerar_boas_vindas
        self.ao_receber_mensagem = ao_receber_mensagem
        self.ao_desconectar = ao_desconectar
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

    def start(self):
        self.server_socket.listen(4)
        print(f"[REDE] Servidor escutando em {self.host}:{self.port}...")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"[REDE] Conexão de {addr}")
            
            # 1. Pede permissão e pega o ID com o Controlador
            id_jogador = self.ao_conectar()

            if id_jogador is not None:
                client_thread = threading.Thread(target=self.trata_cliente, args=(client_socket, id_jogador))
                client_thread.start()
            else:
                client_socket.sendall(b'{"status": "ERRO", "mensagem": "Servidor cheio"}\n')
                client_socket.close()

    def trata_cliente(self, client_socket, id_jogador):
        buffer_sobras = ""
        try:
            # 2. Pede pro Controlador gerar a mensagem de BEM_VINDO
            boas_vindas = self.ao_gerar_boas_vindas(id_jogador)
            client_socket.sendall(boas_vindas.encode())

            while True:
                pedaco = client_socket.recv(1024).decode()
                if not pedaco:
                    break 

                buffer_sobras += pedaco
                
                while '\n' in buffer_sobras:
                    partes = buffer_sobras.split('\n', 1)
                    mensagem_completa = partes[0].strip()
                    buffer_sobras = partes[1]

                    if mensagem_completa:
                        # 3. Entrega a mensagem pro Controlador e devolve a resposta
                        resposta_str = self.ao_receber_mensagem(id_jogador, mensagem_completa)
                        
                        if resposta_str:
                            client_socket.sendall(resposta_str.encode())
                            
                        # Se o cliente mandou o comando de sair
                        if '"comando": "SAIR"' in resposta_str:
                            return # Sai do loop e vai pro finally

        except Exception as e:
            print(f"[REDE] Erro: {e}")
        finally:
            client_socket.close()
            # 4. Avisa o Controlador para limpar a vaga do jogador
            self.ao_desconectar(id_jogador)