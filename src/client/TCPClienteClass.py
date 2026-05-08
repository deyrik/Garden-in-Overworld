import socket 

class TCPCliente:
    """Instancia de cliente TCP"""
    def __init__(self, host, port):
        self.endereco = host
        self.porta = port
        self.client_socket = None
        #chama a função conecta_servidor assim que instancia classe TCPCliente, 
        #abistraindo a necessidade de chamar a função de conexao.
        self.conecta_servidor() 

    #Essa função sera usada no core apenas para tentar restabelecer a conexao 
    # caso haja uma falha, ou seja, caso o cliente perca a conexao com o 
    # servidor, ele pode tentar se reconectar usando essa função.
    def conecta_servidor(self):
        """Estabelece uma conexão TCP com o servidor usando o 
        endereço e porta fornecidos."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)          #Cria um socket TCP/IP
            self.client_socket.connect((self.endereco, self.porta))                         #Conecta ao servidor usando o endereço e porta fornecidos e função connect() do socket
            print(f"Conectado no servidor de endereco: {self.endereco} porta:{self.porta}")
        except Exception as e:                                                              #Tratamento de exceção para erros de conexão, como falha ao conectar ou endereço inválido
            print(f"Error ao conectar ao servidor: {e}")

    def manda_mensagem(self, message):
        if self.client_socket:                               #Verifica se client_socket é verdadeiro ( != de nulo (None))
            try:                                             #tenta:
                self.client_socket.sendall(message.encode()) #Usando send_all {envia qualquer mensagem} para o servidor, codificando a mensagem em bytes usando encode() antes de enviar
                print(f"Mensagem enviada: {message}")
            except Exception as e:                           #tratamento de execeção
                print(f"Erro ao enviar mensagem: {e}")
        else:
            print("Nao estava conectado ao servidor.")

    def recebe_mensagem(self):
        if self.client_socket:                                    #verifica se client_socket é verdadeiro ( != de nulo (None))
            try:                                                  #tenta:
                resposta = self.client_socket.recv(1024).decode() #Usando recv() para receber a resposta do servidor, especificando um buffer de 1024 bytes. A resposta é decodificada de bytes para string usando decode()
                print(f"Mensagem recebida: {resposta}")
                return resposta
            except Exception as e:                                #tratamento de execeção
                print(f"Erro ao receber mensagem: {e}")
        else:
            print("Nao estava conectado ao servidor.")
            return None

    def fecha_conexao(self):
        if self.client_socket:                            # Verifica se client_socket é verdadeiro ( != de nulo (None))
            try:                                          #tenta
                self.client_socket.close()                #fecha a conexao
                self.client_socket = None                 #Garante client_socket como None para indicar que a conexão foi fechada
                print("Conexão fechada.")
            except Exception as e:                        #tratamento de execeções 
                print(f"Erro ao fechar conexão: {e}")  
        else:
            print("Nao estava conectado ao servidor.")

#teste
if __name__ == "__main__":
    cliente = TCPCliente("localhost", 12345)
    cliente.conecta_servidor()
    cliente.manda_mensagem("Hello, Server!")
    response = cliente.recebe_mensagem()
    print(f"Resposta do servidor: {response}")
    cliente.fecha_conexao()