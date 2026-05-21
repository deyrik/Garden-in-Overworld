from models import ClassMapa as map
from models import ClassUser as usManager
from controllers import ClassControlador as ctrl
from controllers import ClassServidorTCP as tcpS
from views import ClassMapaViewTerminal as mapaV
import random


if __name__ == "__main__":
    #print("--- INICIALIZANDO MUNDO ---")
    mapa_jogo = map.Mapa()

    #aleatorizando mapa 
    num_oasis = random.randint(3, 6)
    direcao = random.choice(["horizontal", "vertical"])
    num_nascentes = random.randint(3, 6)
    prob_areia = random.uniform(0.3, 0.5)  # Probabilidade de cada célula ser areia
    num_pocas = random.randint(3, 6)
    maxtam_pocas = random.randint(2, 4)

    mapa_jogo.gerar_mapa_aleatorio(num_oasis, direcao, num_nascentes, 
                                   prob_areia, num_pocas, maxtam_pocas)
    mapaV.MapaView.exibir_colorido(mapa_jogo.matriz)

    gerenciador = usManager.GerenciadorUsers()
    
    print("--- CONECTANDO AS CAMADAS ---")
    controlador = ctrl.ControladorFazenda(mapa_jogo, gerenciador)
    
    # Cria a Rede e injeta os gatilhos(callbacks, funções de resposta) do controlador
    servidor = tcpS.ServidorTCP(
        host="localhost", 
        port=12345,
        ao_conectar=controlador.conecta_jogador,
        ao_receber_mensagem=controlador.processa_mensagem,
        ao_desconectar=controlador.desconecta_jogador
    )
    
    servidor.start()