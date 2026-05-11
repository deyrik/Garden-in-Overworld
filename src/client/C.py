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
    fazendeiro.solicita_nickname("Homelander")
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
        x = random.randint(0, mapa_jogo.linha - 1)
        y = random.randint(0, mapa_jogo.coluna - 1)
        fazendeiro.solicita_plantar(3, x, y)

        time.sleep(2)
        a = random.randint(0, mapa_jogo.linha - 1)
        b = random.randint(0, mapa_jogo.coluna - 1)
        fazendeiro.solicita_plantar(3, a, b)

        time.sleep(2)
        c = random.randint(0, mapa_jogo.linha - 1)
        d = random.randint(0, mapa_jogo.coluna - 1)
        fazendeiro.solicita_plantar(3, c, d)

        time.sleep(2)
        fazendeiro.solicita_colher(3, x, y)
        time.sleep(2)
        fazendeiro.solicita_colher(3, a, b)
        time.sleep(2)
        fazendeiro.solicita_colher(3, c, d)


