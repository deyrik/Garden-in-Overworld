import TCPClienteClass as tcpC
import MapaClass as map
import time



if __name__ == "__main__":

    #COMEÇA CONECTANDO CLIENTE AO SERVER
    cliente = tcpC.TCPCliente("localhost", 12345)
    cliente.conecta_servidor()
    resposta = cliente.recebe_mensagem() # recebe a mensagem de BEM_VINDO do servidor
    print(resposta)
    
    
    #MONTA O MAPA DO JOGO COM O JSON RECEBIDO DO SERVIDOR
    cliente.solicita_matriz()
    matriz_json = cliente.receber_matriz()
    
    mapa_jogo = map.Mapa()
    mapa_jogo.linha = len(matriz_json)     # garantindo que o mapa do cliente vai ser do mesm tamango do server
    mapa_jogo.coluna = len(matriz_json[0])
    mapa_jogo.matriz = matriz_json
    mapa_jogo.exibe_colorido()


    while True:
        cliente.solicita_nickname("Homelender")
        resposta = cliente.recebe_mensagem()
        time.sleep(2)  

        cliente.solicita_plantar(3, 3, 3)  # Exemplo: planta trigo na posição (3, 3)
        resposta = cliente.recebe_mensagem()
        time.sleep(2)

        cliente.solicita_colher(3, 3, 3)  # Exemplo: colhe o que estiver na posição (3, 3)  
        resposta = cliente.recebe_mensagem()
        time.sleep(2)
    
    #cliente.fecha_conexao()