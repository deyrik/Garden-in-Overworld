import ClassFazendeiro as Fazendeiro
import ClassTCPCliente as TCPc
import ClassMapa as Mapa
import ClassOuvinte as Ouvinte # Importa o seu novo arquivo
import threading
import time
import random

if __name__ == "__main__":
    print("--- INICIANDO CLIENTE ---")
    
    #Configuração inicial 
    cliente = TCPc.TCPCliente("localhost", 12345)
    cliente.conecta_servidor()
    fazendeiro = Fazendeiro.ClienteFazenda(cliente)
    mapa_jogo = Mapa.Mapa()

    evento_mapa_ficar_pronto = threading.Event()

    # Instancia a SUA classe de Thread e dá o play!
    thread_escuta = Ouvinte.OuvinteThread(fazendeiro, mapa_jogo, evento_mapa_ficar_pronto)
    thread_escuta.start()
    
    print("--- ENTRANDO NO MUNDO ---")
    fazendeiro.solicita_nickname("BlackNoar")
    fazendeiro.solicita_matriz() 
    
    print("[Sistema] Aguardando o mapa do servidor...")
    mapa_recebido = evento_mapa_ficar_pronto.wait(timeout=10) 

    if mapa_recebido:
        print("[Sistema] Mapa pronto para exibição!")
        mapa_jogo.exibe_colorido()
    else:
        print("[Erro] O mapa demorou demais para chegar.")


    while True:
        time.sleep(2)
        #pega x e y aleatórios para plantar dentro dos limites do mapa
        print("Digite a corenada x")
        x = int(input())
        print("Digite a corenada y")
        y = int(input())
        fazendeiro.solicita_plantar(5, x, y)



