import sys
from PyQt6.QtWidgets import QApplication, QDialog
from models import ClassTCPCliente as TCPc
from models import ClassFazendeiro as Fazendeiro
from views import ClassGUI as gui
from controllers import ClassOuvinte as Ouvinte
from controllers import ClassControladorCliente as CtrlCliente

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    #tela de login para escolher o nickname
    login_screen = gui.LoginDialog()
    if login_screen.exec() != QDialog.DialogCode.Accepted:
        sys.exit()    
    nickname_escolhido = login_screen.get_nickname()

    #cria a janela principal do jogo
    window = gui.GameWindow()

    #cria socket TCP e o fazendeiro
    cliente = TCPc.TCPCliente("localhost", 12345)
    cliente.conecta_servidor()
    fazendeiro = Fazendeiro.ClienteFazenda(cliente)
    
    #cria thread de escuta e o controlador, e liga os sinais do controlador
    controlador = CtrlCliente.ControladorCliente(window, fazendeiro)
    thread_escuta = Ouvinte.OuvinteThread(fazendeiro)
    
    #Ligar os sinais do Controller
    controlador.iniciar_conexoes(thread_escuta)

    #Mostra a janela e inicia a thread de escuta do servidor
    window.show()
    thread_escuta.start()

    #Envia os comandos iniciais assim que conecta
    fazendeiro.solicita_nickname(nickname_escolhido)
    fazendeiro.solicita_matriz()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()