# src/client/gui/main.py
import sys
import os
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import Pyro5.api
import Pyro5.errors
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

from ClassPonteSinais import PonteSinais
from ClassClienteCallback import ClienteCallback
from ClassFazendeiro import ClienteFazenda
from gui.JanelaPrincipal import JanelaPrincipal
from gui.DialogConexao import DialogConexao
from gui import estilos

NOME_SERVICO = "garden.servidor"


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(estilos.STYLESHEET)

    dialog = DialogConexao()
    if dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)
    nick, ns_host = dialog.resultado()

    # Localiza o Name Server e o proxy do servidor
    try:
        ns = Pyro5.api.locate_ns(host=ns_host or None)
        uri = ns.lookup(NOME_SERVICO)
        servidor = Pyro5.api.Proxy(uri)
    except Pyro5.errors.PyroError as e:
        QMessageBox.critical(None, "Erro de conexão",
                             f"Não foi possível localizar o servidor:\n{e}")
        sys.exit(1)

    # Sobe o daemon do cliente (thread dedicada) para receber callbacks
    ponte = PonteSinais()
    daemon = Pyro5.api.Daemon()
    callback = ClienteCallback(ponte)
    uri_callback = daemon.register(callback)
    threading.Thread(target=daemon.requestLoop, daemon=True).start()

    # Entra no jogo
    try:
        id_jogador, estado = servidor.entrar(nick, Pyro5.api.Proxy(uri_callback))
    except Pyro5.errors.PyroError as e:
        QMessageBox.critical(None, "Erro de conexão", f"Falha ao entrar:\n{e}")
        sys.exit(1)

    if id_jogador is None:
        QMessageBox.critical(None, "Acesso negado",
                             estado.get("mensagem", "Servidor cheio (4/4)."))
        sys.exit(1)

    fazendeiro = ClienteFazenda(servidor, ponte, id_jogador)
    janela = JanelaPrincipal(fazendeiro, ponte, nick)
    janela.show()

    # Aplica o estado inicial recebido no entrar()
    ponte.sinal_mapa_completo.emit(estado["matriz"])
    ponte.sinal_estoque_atualizado.emit(estado.get("estoque", {}))
    if estado.get("temporada"):
        ponte.sinal_inicio_temporada.emit(estado["temporada"])
    for autor, msg in estado.get("chat", []):
        ponte.sinal_chat_recebido.emit(autor, msg)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
