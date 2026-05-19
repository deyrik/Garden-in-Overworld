import socket

class TCPCliente:
    """Responsável estritamente pela comunicação TCP."""
    def __init__(self, host, port):
        self.endereco = host
        self.porta = port
        self.client_socket = None
        self._buffer = ""

    def conecta_servidor(self):
        """Estabelece uma conexão TCP com o servidor."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)          
            self.client_socket.connect((self.endereco, self.porta))                         
            print(f"[+] Conectado no servidor {self.endereco}:{self.porta}")
        except Exception as e:                                                              
            print(f"[-] Erro ao conectar ao servidor: {e}")

    def fecha_conexao(self):
        """Fecha a conexão TCP com o servidor."""
        if self.client_socket:                            
            try:                                          
                self.client_socket.close()                
                self.client_socket = None                 
                print("Conexão fechada.")
            except Exception as e:                        
                print(f"Erro ao fechar conexão: {e}")  
        else:
            print("Não estava conectado ao servidor.")
 
    def manda_mensagem(self, message):
        """Envia uma string genérica para o servidor."""
        if self.client_socket:                               
            try:
                if not message.endswith('\n'): # se nao tem \n no final, adiciona 
                    message += '\n'
                self.client_socket.sendall(message.encode()) 
                print(f">> Enviado: {message.strip()}")
            except Exception as e:                           
                print(f"Erro ao enviar mensagem: {e}")
        else:
            print("Não estava conectado ao servidor.")

    def recebe_mensagem(self):
        """Lê uma mensagem JSON da rede (terminada por \n).
        Mantém buffer persistente para não descartar mensagens que chegam juntas no mesmo recv().
        """
        if self.client_socket:
            try:
                while '\n' not in self._buffer:
                    pedaco = self.client_socket.recv(1024).decode()
                    if not pedaco:
                        print("Conexão com o servidor foi perdida.")
                        return None
                    self._buffer += pedaco

                partes = self._buffer.split('\n', 1)
                mensagem_final = partes[0].strip()
                self._buffer = partes[1]  # preserva sobras para a próxima chamada
                print(f"<< Recebido: {mensagem_final}")
                return mensagem_final
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                return None
        return None