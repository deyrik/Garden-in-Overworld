from models import ClassMapa as map
from models import ClassUser as usManager
from controllers import ClassControlador as ctrl
#from controllers import ClassServidorTCP as tcpS
from views import ClassMapaViewTerminal as mapaV
import random
import Pyro5.api

if __name__ == "__main__":

    #contruindo mapa aleatorio 
    mapa_jogo = map.Mapa()
    num_oasis = random.randint(3, 6)
    direcao = random.choice(["horizontal", "vertical"])
    num_nascentes = random.randint(3, 6)
    prob_areia = random.uniform(0.3, 0.5)  #Probabilidade de cada célula perto do rio ser areia
    num_pocas = random.randint(3, 6)
    maxtam_pocas = random.randint(2, 4)

    mapa_jogo.gerar_mapa_aleatorio(num_oasis, direcao, num_nascentes, 
                                   prob_areia, num_pocas, maxtam_pocas)
    mapaV.MapaView.exibir_colorido(mapa_jogo.matriz)

    gerenciador = usManager.GerenciadorUsers()
    controlador = ctrl.ControladorFazenda(mapa_jogo, gerenciador)
    
    print("--- CONECTANDO AS CAMADAS ---")
    
    daemon = Pyro5.api.Daemon()#Cria o Daemon, e quem atende as chamadas de rede no Pyro5
    ns = Pyro5.api.locate_ns()#Busca o Name Server, que é o serviço de diretório do Pyro5
    uri = daemon.register(controlador)#Registra o nosso controlador no Daemon (ganha um endereço de memória/URI)
    ns.register("fazenda.servidor", uri) #Anota esse endereço físico na Lista Telefônica com um nome lógico e fácil

    
    print("Servidor RMI online e registrado como 'fazenda.servidor'")
    print("Aguardando os métodos serem invocados pelos clientes...")
    
 
    daemon.requestLoop()#loop infinito escutando as chamadas