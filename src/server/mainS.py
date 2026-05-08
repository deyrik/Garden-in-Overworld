import TCPServerClass as tcp

if __name__ == "__main__":
    
    #REGRA DE NEGOCIO da matriz 
    # Inicialiaza matrix 
    # ...
    server = tcp.TCPServer() #instancia do servidor TCP
    server.start()       #inicializa (liga) o servidor TCP
