import socket
import TCPClienteClass as tcpC

if __name__ == "__main__":
    cliente = tcpC.TCPCliente("localhost", 12345)
    cliente.conecta_servidor()
    cliente.manda_mensagem("Hello, Server!")
    response = cliente.recebe_mensagem()
    print(f"Resposta do servidor: {response}")
    cliente.fecha_conexao()