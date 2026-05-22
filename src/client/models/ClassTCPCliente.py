import socket

class TCPCliente:
    """Responsável estritamente pela comunicação TCP."""
    def __init__(self, host, port):
        self.endereco = host
        self.porta = port
        self.client_socket = None
        self.buffer_sobras = b""#'b' na frente para criar um buffer de BYTES puros

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
        """Lê bytes da rede e só converte para texto quando a mensagem estiver inteira."""
        if not self.client_socket:
            return None
            
        try:
            while True: 
                # Agora procuramos pela quebra de linha em formato BYTE (b'\n')
                if b'\n' in self.buffer_sobras:
                    partes = self.buffer_sobras.split(b'\n', 1)
                    
                    # Decodificamos SOMENTE a mensagem limpa! 
                    # O "errors='replace'" impede crashs se vier lixo na rede.
                    mensagem_final = partes[0].decode('utf-8', errors='replace').strip()
                    self.buffer_sobras = partes[1]
                    
                    if mensagem_final:
                        return mensagem_final
                    else:
                        continue 

                # Tirei o .decode() para só receber os bytes puros.
                pedaco = self.client_socket.recv(1024)
                
                if not pedaco:
                    print("Conexão com o servidor foi perdida.")
                    return None
                    
                self.buffer_sobras += pedaco
                
        except Exception as e:                                
            print(f"Erro ao receber mensagem TCP: {e}")
            return None