import Pyro5.api
import Pyro5.errors

from models.ClassMapa import Mapa
from models.ClassUser import GerenciadorUsers
from ClassEstoque import Estoque
from ClassNotificador import Notificador
from persistencia import BancoDados
from ClassServidorJardim import ServidorJardim

NOME_SERVICO = "garden.servidor"


def main():
    print("--- INICIALIZANDO MUNDO ---")
    mapa = Mapa()
    mapa.gerar_mapa_aleatorio()
    mapa.exibe_colorido()

    gerenciador = GerenciadorUsers()
    estoque = Estoque()
    notificador = Notificador()
    banco = BancoDados()

    servidor = ServidorJardim(mapa, gerenciador, estoque, notificador, banco)

    daemon = Pyro5.api.Daemon()
    try:
        ns = Pyro5.api.locate_ns()
    except Pyro5.errors.NamingError:
        print("[ERRO] Name Server não encontrado. Suba 'make NAMESERVER' antes.")
        return
    uri = daemon.register(servidor)
    ns.register(NOME_SERVICO, uri)
    print(f"[PYRO] Servidor registrado como '{NOME_SERVICO}' -> {uri}")

    servidor.iniciar_temporada(1)
    print("[PYRO] Aguardando jogadores (Ctrl+C para encerrar)...")
    try:
        daemon.requestLoop()
    except KeyboardInterrupt:
        print("\n[PYRO] Encerrando servidor.")
    finally:
        try:
            ns.remove(NOME_SERVICO)
        except Exception:
            pass


if __name__ == "__main__":
    main()
