# tests/test_notificador.py
from ClassNotificador import Notificador


class FakeCallback:
    def __init__(self):
        self.recebidos = []

    def atualizar_celula(self, x, y, valor):
        self.recebidos.append(("atualizar_celula", x, y, valor))

    def chat(self, autor, msg):
        self.recebidos.append(("chat", autor, msg))


def test_broadcast_chega_a_todos_os_registrados():
    notificador = Notificador()
    a, b = FakeCallback(), FakeCallback()
    notificador.registrar(1, a)
    notificador.registrar(2, b)

    notificador.atualizar_celula(3, 4, 8)
    notificador.aguardar_processamento()

    assert a.recebidos == [("atualizar_celula", 3, 4, 8)]
    assert b.recebidos == [("atualizar_celula", 3, 4, 8)]


def test_removido_nao_recebe_mais():
    notificador = Notificador()
    a = FakeCallback()
    notificador.registrar(1, a)
    notificador.remover(1)

    notificador.chat("Alice", "oi")
    notificador.aguardar_processamento()

    assert a.recebidos == []


def test_callback_que_lanca_excecao_e_descartado():
    notificador = Notificador()

    class Quebrado:
        def chat(self, *a):
            raise RuntimeError("caiu")

    bom = FakeCallback()
    notificador.registrar(1, Quebrado())
    notificador.registrar(2, bom)

    notificador.chat("Alice", "oi")
    notificador.aguardar_processamento()
    notificador.chat("Bob", "ola")
    notificador.aguardar_processamento()

    # O bom recebe as duas; o quebrado foi removido após a primeira falha.
    assert bom.recebidos == [("chat", "Alice", "oi"), ("chat", "Bob", "ola")]
