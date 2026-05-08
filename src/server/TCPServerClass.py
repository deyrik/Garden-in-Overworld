import socket
import threading

# !!!! Na função ConeccoesCliente, quando o cliente digitar um comando ira desligar a conexão
# ainda é string mas quando a matriz for implementada irá ser algum comando 


class TCPServer:
    def __init__(self, host='localhost', port=12345):
        """Cria uma instancia de Servidor TCP."""
        self.endereco = host
        self.porta = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #criando um socket TCP
        self.server_socket.bind((self.endereco, self.porta))                   #bind (igual Q da morgana) - vinculando o socket recem criado a um IP e porta
        self.server_socket.listen(5)                                           # define ate 5 conexoes pendentes
        print(f"Servidor iniciado em {self.endereco}:{self.porta}")

    def ConeccoesCliente(self, client_socket):
        print("Cliente conectado")
        try:
            while True:
                data = client_socket.recv(1024)    #recv = receber dados do cliente, 1024 é o tamanho do buffer (açao bloqueante)
                if not data:
                    break
                
                mensagem = data.decode().strip()  #decodificando os dados recebidos do cliente e removendo espaços em branco
                print(f"Recebido: {mensagem}")
                
                # Exemplo de saída por comando, 
                # mas sera um inteiro quando 
                # a matriz for implementada
                if mensagem.upper() == "QUIT":
                    break
                    
                client_socket.sendall(data)       # send_all = retorna qualquer dado recebido para o cliente (eco) 
       
       # consegue sair do loop quando o cliente se desconecta 
       # ou quando o cliente envia uma mensagem vazia (data vazia)
        except (ConnectionResetError, BrokenPipeError):
            print("Conexão perdida com o cliente.")
        except Exception as e:
            print(f"Erro inesperado: {e}")
        finally:
            print("Fechando conexão...")
            client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexão de {addr}")
            client_thread = threading.Thread(target=self.ConeccoesCliente, args=(client_socket,))
            client_thread.start()


#TESTE:
if __name__ == "__main__":
    server = TCPServer()
    server.start()
