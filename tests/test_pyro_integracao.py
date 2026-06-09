# tests/test_pyro_integracao.py
import threading
import time

import Pyro5.api
import pytest

from models.ClassMapa import Mapa
from models.ClassUser import GerenciadorUsers
from ClassEstoque import Estoque
from ClassNotificador import Notificador
from ClassServidorJardim import ServidorJardim
from ClassClienteCallback import ClienteCallback


class SinalFake:
    """Imita um pyqtSignal: registra emissões e sinaliza um Event."""
    def __init__(self, evento):
        self.emitidos = []
        self._evento = evento

    def emit(self, *args):
        self.emitidos.append(args)
        self._evento.set()


class PonteFake:
    def __init__(self):
        self.evento_celula = threading.Event()
        self.sinal_mapa_completo = SinalFake(threading.Event())
        self.sinal_celula_atualizada = SinalFake(self.evento_celula)
        self.sinal_inicio_temporada = SinalFake(threading.Event())
        self.sinal_tick_timer = SinalFake(threading.Event())
        self.sinal_estoque_atualizado = SinalFake(threading.Event())
        self.sinal_progresso_atualizado = SinalFake(threading.Event())
        self.sinal_cultura_pronta = SinalFake(threading.Event())
        self.sinal_posicao_jogador = SinalFake(threading.Event())
        self.sinal_chat_recebido = SinalFake(threading.Event())
        self.sinal_aviso_gelo = SinalFake(threading.Event())
        self.sinal_vitoria = SinalFake(threading.Event())
        self.sinal_derrota = SinalFake(threading.Event())


class FakeBanco:
    def inserir_chat(self, autor, mensagem):
        pass

    def ultimas_mensagens(self, limite=50):
        return []


def _estoque():
    e = Estoque()
    e.inicializar(1)
    return e


@pytest.fixture
def ambiente():
    mapa = Mapa(5, 5)
    servidor_obj = ServidorJardim(mapa, GerenciadorUsers(), _estoque(),
                                  Notificador(), FakeBanco())
    daemon_srv = Pyro5.api.Daemon()
    uri_srv = daemon_srv.register(servidor_obj)
    t_srv = threading.Thread(target=daemon_srv.requestLoop, daemon=True)
    t_srv.start()

    ponte = PonteFake()
    daemon_cli = Pyro5.api.Daemon()
    uri_cli = daemon_cli.register(ClienteCallback(ponte))
    t_cli = threading.Thread(target=daemon_cli.requestLoop, daemon=True)
    t_cli.start()

    yield uri_srv, uri_cli, ponte

    daemon_srv.shutdown()
    daemon_cli.shutdown()


def test_entrar_e_receber_callback_de_preparar(ambiente):
    uri_srv, uri_cli, ponte = ambiente
    servidor = Pyro5.api.Proxy(uri_srv)

    idj, estado = servidor.entrar("Bob", Pyro5.api.Proxy(uri_cli))
    assert idj == 1
    assert estado["matriz"] == [[0] * 5 for _ in range(5)]

    resp = servidor.preparar(idj, 1, 1)
    assert resp["status"] == "OK"

    # O callback atualizar_celula deve chegar de forma assíncrona.
    assert ponte.evento_celula.wait(timeout=5.0), "callback não chegou a tempo"
    assert (1, 1, 8) in ponte.sinal_celula_atualizada.emitidos
