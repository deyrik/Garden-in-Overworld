# tests/test_persistencia.py
from persistencia import BancoDados


def test_insere_e_recupera_em_ordem_cronologica():
    banco = BancoDados(":memory:")
    banco.inserir_chat("Alice", "oi")
    banco.inserir_chat("Bob", "ola")
    assert banco.ultimas_mensagens() == [("Alice", "oi"), ("Bob", "ola")]


def test_limite_retorna_apenas_as_ultimas():
    banco = BancoDados(":memory:")
    for i in range(5):
        banco.inserir_chat("X", f"msg{i}")
    assert banco.ultimas_mensagens(limite=2) == [("X", "msg3"), ("X", "msg4")]


def test_banco_vazio_retorna_lista_vazia():
    banco = BancoDados(":memory:")
    assert banco.ultimas_mensagens() == []
