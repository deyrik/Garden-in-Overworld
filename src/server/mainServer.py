import ClassMapa as mapa_mod
import ClassUser as usManager
import ClassControlador as ctrl
import ClassServidorTCP as tcpS
import ClassEstoque as est

PORTA_TCP = 12345

if __name__ == "__main__":
    print("--- INICIALIZANDO MUNDO ---")
    mapa_jogo = mapa_mod.Mapa()
    mapa_jogo.gerar_mapa_aleatorio()
    mapa_jogo.exibe_colorido()

    gerenciador = usManager.GerenciadorUsers()
    estoque = est.Estoque()

    print("--- CONECTANDO AS CAMADAS ---")
    controlador = ctrl.ControladorFazenda(mapa_jogo, gerenciador, estoque)

    servidor = tcpS.ServidorTCP(
        host="0.0.0.0",
        port=PORTA_TCP,
        ao_conectar=controlador.conecta_jogador,
        ao_gerar_boas_vindas=controlador.gera_boas_vindas,
        ao_receber_mensagem=controlador.processa_mensagem,
        ao_desconectar=controlador.desconecta_jogador
    )

    # Injeta broadcast no controlador APÓS criar o servidor
    controlador.registrar_broadcast(servidor.enviar_broadcast)

    # Inicia a primeira temporada
    controlador.iniciar_temporada(1)

    servidor.start()
