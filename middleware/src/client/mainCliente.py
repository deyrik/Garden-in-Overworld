import sys
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from models import ClassFazendeiro as Fazendeiro
from views import ClassGUI as gui
from controllers import ClassControladorCliente as CtrlCliente

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    login_screen = gui.LoginDialog()
    if login_screen.exec() != QDialog.DialogCode.Accepted:
        sys.exit()    
    nickname_escolhido = login_screen.get_nickname()

    # Cria a janela e tenta conectar via RMI
    window = gui.GameWindow()
    fazendeiro = Fazendeiro.ClienteFazenda()
    
    if not fazendeiro.servidor:
        QMessageBox.critical(None, "Erro Crítico", "Não foi possível encontrar a Fazenda no Name Server. O servidor está ligado?")
        sys.exit()

    # Tenta entrar no jogo
    resposta_login = fazendeiro.solicita_nickname(nickname_escolhido)
    if resposta_login and resposta_login.get("status") == "ERRO":
        QMessageBox.critical(None, "Acesso Negado", resposta_login.get("mensagem", "Erro desconhecido"))
        sys.exit()

    window.log_message("Sistema", resposta_login.get("mensagem", "Conectado!"))

    # Liga os motores do controlador (cliques e o timer de atualização)
    controlador = CtrlCliente.ControladorCliente(window, fazendeiro)
    controlador.iniciar_conexoes()

    app.aboutToQuit.connect(fazendeiro.solicita_sair)## Avisa ao RMI para liberar o slot instantes antes do programa fechar
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()