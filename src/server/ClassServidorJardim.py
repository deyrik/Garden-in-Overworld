# src/server/ClassServidorJardim.py
import threading
import random

from models.ClassMapa import (TEMPO_CRESCIMENTO, MAPA_CRESCENDO_PARA_PRONTA,
                               MAPA_PRONTA_PARA_BASE, CULTURAS_PRONTAS,
                               CULTURAS_CRESCENDO)
from ClassTemporada import Temporada, PRONTA_PARA_DEMANDA

try:
    import Pyro5.api
    expose = Pyro5.api.expose
except ImportError:  # permite testar a lógica sem Pyro instalado
    def expose(classe):
        return classe

NOMES_TEMPORADA = {1: "Primavera", 2: "Verão", 3: "Outono", 4: "Inverno"}


def _ok(mensagem, **extra):
    return {"status": "OK", "mensagem": mensagem, **extra}


def _erro(mensagem, **extra):
    return {"status": "ERRO", "mensagem": mensagem, **extra}


@expose
class ServidorJardim:
    """Objeto remoto fachada. Cada método substitui um ramo do antigo
    processa_mensagem; retorna a resposta ao chamador e empurra eventos
    de jogo via Notificador."""

    def __init__(self, mapa, gerenciador, estoque, notificador, banco):
        self.mapa = mapa
        self.gerenciador = gerenciador
        self.estoque = estoque
        self.notificador = notificador
        self.banco = banco
        self.temporada = None
        self._timers_crescimento = {}
        self._lock_timers = threading.Lock()
        # Garante que a temporada seja encerrada (vitória OU derrota) uma só vez,
        # mesmo com colheitas concorrentes ou colheitas após a meta atingida.
        self._lock_temporada = threading.Lock()
        self._temporada_resolvida = False

    def _resolver_temporada(self):
        """Retorna True apenas para o primeiro chamador que encerra a temporada atual."""
        with self._lock_temporada:
            if self._temporada_resolvida:
                return False
            self._temporada_resolvida = True
            return True

    # -------------------------------------------------------------------------
    # Conexão
    # -------------------------------------------------------------------------

    def entrar(self, nick, callback):
        """Aloca um slot, registra o callback e devolve (id, estado_inicial)."""
        idj = self.gerenciador.adiciona_na_vaga()
        if idj is None:
            return None, _erro("Servidor cheio")
        self.gerenciador.slots[idj].nick = nick
        self.notificador.registrar(idj, callback)
        estado = {
            "id": idj,
            "mensagem": f"BEM_VINDO: {nick} (Jogador {idj})",
            "matriz": self.mapa.matriz,
            "estoque": self.estoque.snapshot(),
            "temporada": self._payload_inicio_temporada() if self.temporada else None,
            "chat": self.banco.ultimas_mensagens(50),
        }
        return idj, estado

    def sair(self, idj):
        self.notificador.remover(idj)
        self.gerenciador.remove_da_vaga(idj)
        return _ok("Desconectando...")

    def obter_matriz(self):
        return self.mapa.matriz

    # -------------------------------------------------------------------------
    # Ações do jogador
    # -------------------------------------------------------------------------

    def preparar(self, idj, x, y):
        if self.mapa.preparar(x, y):
            valor = self.mapa.matriz[x][y]
            self.notificador.atualizar_celula(x, y, valor)
            return _ok("Solo preparado")
        return _erro("Nao foi possivel preparar")

    def pegar_semente(self, idj, cultura):
        jogador = self.gerenciador.slots.get(idj)
        if jogador is None:
            return _erro("Jogador nao encontrado")
        if not self.estoque.pegar(cultura):
            return _erro("Sem sementes desse tipo")
        if jogador.semente_na_mao == cultura:
            jogador.quantidade_na_mao += 1
        else:
            if jogador.semente_na_mao is not None:
                self.estoque.repor(jogador.semente_na_mao, jogador.quantidade_na_mao)
            jogador.semente_na_mao = cultura
            jogador.quantidade_na_mao = 1
        self.notificador.atualizar_estoque(self.estoque.snapshot())
        return _ok(f"Semente {cultura} na mao",
                   cultura=cultura, quantidade=jogador.quantidade_na_mao)

    def plantar(self, idj, semente, x, y):
        jogador = self.gerenciador.slots.get(idj)
        if jogador is None or jogador.semente_na_mao != semente:
            return _erro("Sem semente na mao")
        if not self.mapa.plantar(x, y, semente):
            return _erro("Nao foi possivel plantar ai",
                         cultura=jogador.semente_na_mao,
                         quantidade=jogador.quantidade_na_mao)
        jogador.quantidade_na_mao -= 1
        restante = jogador.quantidade_na_mao
        if restante <= 0:
            jogador.semente_na_mao = None
            jogador.quantidade_na_mao = 0
        cultura_plantada = self.mapa.matriz[x][y]
        self._iniciar_timer_crescimento(x, y, cultura_plantada)
        self.notificador.atualizar_celula(x, y, cultura_plantada)
        return _ok("Plantado",
                   cultura=semente if restante > 0 else None,
                   quantidade=restante)

    def colher(self, idj, x, y):
        ok, tile_pronto = self.mapa.colher(x, y)
        if not ok:
            return _erro("Nao ha cultura pronta ai")
        valor = self.mapa.matriz[x][y]
        cultura_demanda = PRONTA_PARA_DEMANDA.get(tile_pronto)
        if cultura_demanda:
            self.estoque.repor(cultura_demanda)
        self.notificador.atualizar_celula(x, y, valor)
        self.notificador.atualizar_estoque(self.estoque.snapshot())
        if self.temporada:
            vitoria = self.temporada.registrar_colheita(tile_pronto)
            estado = self.temporada.get_estado()
            self.notificador.atualizar_progresso(estado["progresso"], estado["demanda"])
            if vitoria and self._resolver_temporada():
                numero = self.temporada.numero
                self.temporada.parar()
                self._ao_vitoria(numero)
        return _ok("Colhido")

    def mover_cursor(self, idj, x, y):
        if x is None or y is None:
            return _erro("Coordenadas invalidas")
        jogador = self.gerenciador.slots.get(idj)
        if jogador:
            jogador.posicao = (x, y)
        nick = jogador.nick if jogador else "?"
        self.notificador.posicao_jogador(idj, nick, x, y)
        return _ok("Cursor atualizado")

    def enviar_chat(self, idj, mensagem):
        jogador = self.gerenciador.slots.get(idj)
        nick = jogador.nick if jogador else "?"
        self.banco.inserir_chat(nick, mensagem)
        self.notificador.chat(nick, mensagem)
        return _ok("Chat enviado")

    # -------------------------------------------------------------------------
    # Temporada
    # -------------------------------------------------------------------------

    def iniciar_temporada(self, numero):
        num_jogadores = sum(1 for v in self.gerenciador.slots.values() if v is not None)
        if self.temporada:
            self.temporada.parar()
        with self._lock_temporada:
            self._temporada_resolvida = False
        self.estoque.inicializar(numero)
        self.temporada = Temporada(
            numero=numero,
            num_jogadores=num_jogadores,
            ao_tick=self._ao_tick_temporada,
            ao_derrota=lambda n=numero: self._ao_derrota(n),
            ao_gelo=self._ao_gelo if numero >= 4 else None,
        )
        self.temporada.iniciar()
        self.notificador.inicio_temporada(self._payload_inicio_temporada())
        print(f"[JOGO] Temporada {numero} iniciada.")

    def _payload_inicio_temporada(self):
        estado = self.temporada.get_estado()
        numero = estado["numero"]
        return {
            "temporada": numero,
            "nome": NOMES_TEMPORADA.get(min(numero, 4), f"Temporada {numero}"),
            "demanda": {str(k): v for k, v in estado["demanda"].items()},
            "restante": estado["restante"],
            "estoque": self.estoque.snapshot(),
        }

    def _ao_tick_temporada(self, restante):
        self.notificador.tick_timer(restante)

    def _ao_vitoria(self, numero_temporada):
        print(f"[JOGO] Vitória na temporada {numero_temporada}!")
        self.notificador.vitoria(numero_temporada)
        t = threading.Timer(5.0, lambda: self.iniciar_temporada(numero_temporada + 1))
        t.daemon = True
        t.start()

    def _ao_derrota(self, numero):
        if not self._resolver_temporada():
            return
        print(f"[JOGO] Derrota na temporada {numero}.")
        self.notificador.derrota(numero)
        t = threading.Timer(5.0, lambda: self.iniciar_temporada(numero))
        t.daemon = True
        t.start()

    def _ao_gelo(self):
        celulas = [
            (x, y)
            for x in range(self.mapa.linha)
            for y in range(self.mapa.coluna)
            if (self.mapa.matriz[x][y] in CULTURAS_PRONTAS or
                self.mapa.matriz[x][y] in CULTURAS_CRESCENDO)
        ]
        if not celulas:
            return
        x, y = random.choice(celulas)
        self.notificador.aviso_gelo(x, y, 10)
        t = threading.Timer(10.0, lambda: self._aplicar_gelo(x, y))
        t.daemon = True
        t.start()

    def _aplicar_gelo(self, x, y):
        with self._lock_timers:
            timer = self._timers_crescimento.pop((x, y), None)
        if timer:
            timer.cancel()
        tile = self.mapa.matriz[x][y]
        if tile not in CULTURAS_PRONTAS and tile not in CULTURAS_CRESCENDO:
            return
        if tile in MAPA_PRONTA_PARA_BASE:
            self.mapa.matriz[x][y] = MAPA_PRONTA_PARA_BASE[tile]
        elif tile in MAPA_CRESCENDO_PARA_PRONTA:
            pronta = MAPA_CRESCENDO_PARA_PRONTA[tile]
            self.mapa.matriz[x][y] = MAPA_PRONTA_PARA_BASE.get(pronta, 0)
        self.notificador.atualizar_celula(x, y, self.mapa.matriz[x][y])

    # -------------------------------------------------------------------------
    # Timers de crescimento
    # -------------------------------------------------------------------------

    def _iniciar_timer_crescimento(self, x, y, cultura):
        tempo = TEMPO_CRESCIMENTO.get(cultura, 30)
        with self._lock_timers:
            antigo = self._timers_crescimento.pop((x, y), None)
        if antigo:
            antigo.cancel()
        timer = threading.Timer(tempo, lambda: self._planta_maturou(x, y))
        timer.daemon = True
        with self._lock_timers:
            self._timers_crescimento[(x, y)] = timer
        timer.start()

    def _planta_maturou(self, x, y):
        with self._lock_timers:
            self._timers_crescimento.pop((x, y), None)
        if not self.mapa.maturar(x, y):
            return
        tile_pronto = self.mapa.matriz[x][y]
        self.notificador.atualizar_celula(x, y, tile_pronto)
        self.notificador.cultura_pronta(x, y, tile_pronto)
