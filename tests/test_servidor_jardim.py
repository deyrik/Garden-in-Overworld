# tests/test_servidor_jardim.py
import pytest

from models.ClassMapa import Mapa
from models.ClassUser import GerenciadorUsers
from ClassEstoque import Estoque
from ClassTemporada import Temporada
from ClassServidorJardim import ServidorJardim


class FakeNotificador:
    def __init__(self):
        self.chamadas = []

    def __getattr__(self, nome):
        def registrar(*args):
            self.chamadas.append((nome,) + args)
        return registrar


class FakeBanco:
    def __init__(self):
        self.mensagens = []

    def inserir_chat(self, autor, mensagem):
        self.mensagens.append((autor, mensagem))

    def ultimas_mensagens(self, limite=50):
        return list(self.mensagens[-limite:])


def montar_servidor():
    mapa = Mapa(5, 5)            # matriz toda terra (0)
    gerenciador = GerenciadorUsers()
    estoque = Estoque()
    estoque.inicializar(1)
    notificador = FakeNotificador()
    banco = FakeBanco()
    return ServidorJardim(mapa, gerenciador, estoque, notificador, banco)


def test_entrar_aloca_slot_e_devolve_estado_inicial():
    s = montar_servidor()
    idj, estado = s.entrar("Alice", callback=object())
    assert idj == 1
    assert s.gerenciador.slots[1].nick == "Alice"
    assert estado["matriz"] == s.mapa.matriz
    assert estado["estoque"][3] == 30          # trigo inicial da temporada 1
    assert any(c[0] == "registrar" and c[1] == 1 for c in s.notificador.chamadas)


def test_entrar_servidor_cheio_retorna_none():
    s = montar_servidor()
    for nome in ["a", "b", "c", "d"]:
        s.entrar(nome, callback=object())
    idj, estado = s.entrar("excedente", callback=object())
    assert idj is None
    assert estado["status"] == "ERRO"


def test_preparar_terra_atualiza_celula_e_faz_broadcast():
    s = montar_servidor()
    idj, _ = s.entrar("Alice", callback=object())
    resp = s.preparar(idj, 0, 0)
    assert resp["status"] == "OK"
    assert s.mapa.matriz[0][0] == 8
    assert ("atualizar_celula", 0, 0, 8) in s.notificador.chamadas


def test_pegar_semente_e_plantar_consome_da_mao():
    s = montar_servidor()
    idj, _ = s.entrar("Alice", callback=object())
    s.preparar(idj, 0, 0)                       # terra -> 8
    resp_pegar = s.pegar_semente(idj, 3)        # trigo
    assert resp_pegar["status"] == "OK"
    assert resp_pegar["quantidade"] == 1
    s.mapa.matriz[0][1] = 1                      # água adjacente p/ fertilidade do trigo
    resp_plantar = s.plantar(idj, 3, 0, 0)
    assert resp_plantar["status"] == "OK"
    assert s.mapa.matriz[0][0] == 3             # trigo crescendo
    assert s.gerenciador.slots[idj].quantidade_na_mao == 0


def test_colher_repoe_estoque_e_registra_progresso():
    s = montar_servidor()
    idj, _ = s.entrar("Alice", callback=object())
    # Temporada sem timers (não chamamos iniciar()).
    s.temporada = Temporada(numero=1, num_jogadores=1,
                            ao_tick=lambda r: None, ao_derrota=lambda: None)
    s.mapa.matriz[0][0] = 13                     # trigo pronto
    resp = s.colher(idj, 0, 0)
    assert resp["status"] == "OK"
    assert s.mapa.matriz[0][0] == 0             # volta para terra
    assert s.temporada.progresso[3] == 1
    assert any(c[0] == "atualizar_progresso" for c in s.notificador.chamadas)


def test_enviar_chat_persiste_e_faz_broadcast():
    s = montar_servidor()
    idj, _ = s.entrar("Alice", callback=object())
    s.enviar_chat(idj, "ola mundo")
    assert ("Alice", "ola mundo") in s.banco.mensagens
    assert ("chat", "Alice", "ola mundo") in s.notificador.chamadas
