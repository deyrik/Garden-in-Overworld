import socket
import threading

class ServidorTCP:
    """Lida estritamente com Sockets e Threads. Totalmente agnóstico ao jogo."""
    def __init__(self, host="localhost", port=12345, 
                 ao_conectar=None,  
                 ao_receber_mensagem=None, 
                 ao_desconectar=None):
        
        
        self.host = host
        self.port = port
        # Callbacks (Gatilhos/Funcoes) passados pelo Controlador
        self.ao_conectar = ao_conectar 
        self.ao_receber_mensagem = ao_receber_mensagem
        self.ao_desconectar = ao_desconectar

        self.conexoes_ativas = {}

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))

    def start(self):
        self.server_socket.listen(4)
        print(f"[REDE] Servidor escutando em {self.host}:{self.port}...")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"[REDE] Conexão de {addr}")
            
            id_jogador = self.ao_conectar()

            if id_jogador is not None:
                client_thread = threading.Thread(target=self.trata_cliente, args=(client_socket, id_jogador))
                client_thread.start()
            else:
                client_socket.sendall(b'{"status": "ERRO", "mensagem": "Servidor cheio"}\n')
                client_socket.close()

    def enviar_broadcast(self, mensagem_str):
        """Pega a mensagem e atira para TODOS os sockets ativos no momento."""
        
        #list() para evitar erros caso alguém desconecte bem na hora do loop
        for socket_cliente in list(self.conexoes_ativas.values()):
            try:
                socket_cliente.sendall(mensagem_str.encode())
            except Exception as e:
                print(f"[REDE] Erro ao enviar broadcast: {e}")

    def trata_cliente(self, client_socket, id_jogador):
        buffer_sobras = ""
        
        #Registra o socket desse jogador no dicionário de conexões ativas
        self.conexoes_ativas[id_jogador] = client_socket 
        
        try:

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
                        #o Controlador devolve DUAS variáveis!
                        resposta_str, broadcast_str = self.ao_receber_mensagem(id_jogador, mensagem_completa)
                        
                        #Manda o "OK" ou "ERRO" só pro cara que pediu
                        if resposta_str:
                            client_socket.sendall(resposta_str.encode())
                            
                        #Se o controlador mandou uma "fofoca", espalha pra todo mundo! (broadcast)
                        if broadcast_str:
                            self.enviar_broadcast(broadcast_str)
                            
                        if '"comando": "SAIR"' in resposta_str:
                            return

        except Exception as e:
            print(f"[REDE] Erro: {e}")
        finally:
            #Tira o socket da lista de ativos antes de fechar
            if id_jogador in self.conexoes_ativas:
                del self.conexoes_ativas[id_jogador]
                
            client_socket.close()
            self.ao_desconectar(id_jogador)