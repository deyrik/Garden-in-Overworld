from models import ClassMapa as map
from models import ClassUser as usManager
from controllers import ClassControlador as ctrl
from views import ClassServidorTCP as tcpS
from views import ClassMapaViewTerminal as mapaV


if __name__ == "__main__":
    print("--- INICIALIZANDO MUNDO ---")
    mapa_jogo = map.Mapa()
    mapa_jogo.gerar_mapa_aleatorio(direcao="horizontal")
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