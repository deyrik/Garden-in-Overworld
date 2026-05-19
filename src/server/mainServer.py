import ClassMapa as map
import ClassUser as usManager
import ClassControlador as ctrl
import ClassServidorTCP as tcpS
import ClassAnunciadorUDP as udp

PORTA_TCP = 12345

if __name__ == "__main__":
    print("--- INICIALIZANDO MUNDO ---")
    mapa_jogo = map.Mapa()
    mapa_jogo.gerar_mapa_aleatorio()
    mapa_jogo.exibe_colorido()

    gerenciador = usManager.GerenciadorUsers()

    print("--- CONECTANDO AS CAMADAS ---")
    controlador = ctrl.ControladorFazenda(mapa_jogo, gerenciador)

    anunciador = udp.AnunciadorUDP(porta_tcp=PORTA_TCP)
    anunciador.start()

    servidor = tcpS.ServidorTCP(
        host="0.0.0.0",
        port=PORTA_TCP,
        ao_conectar=controlador.conecta_jogador,
        ao_gerar_boas_vindas=controlador.gera_boas_vindas,
        ao_receber_mensagem=controlador.processa_mensagem,
        ao_desconectar=controlador.desconecta_jogador
    )

    servidor.start()
