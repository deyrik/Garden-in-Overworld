import threading
import random

DURACAO_POR_TEMPORADA = {1: 180, 2: 150, 3: 120, 4: 90}

# Demanda base por temporada (multiplicada pelo nº de jogadores conectados)
DEMANDA_BASE = {
    1: {3: 6,  4: 3,  6: 5},
    2: {3: 7,  4: 4,  6: 5,  10: 3},
    3: {3: 8,  4: 5,  6: 6,  10: 4,  11: 4},
    4: {3: 10, 4: 6,  6: 7,  10: 5,  11: 5,  12: 3},
}

# Mapa: estado "pronto" -> chave de cultura na demanda
PRONTA_PARA_DEMANDA = {13: 3, 14: 4, 15: 6, 16: 6, 17: 10, 18: 11, 19: 12}

class Temporada:
    """
    Gerencia uma temporada: demanda, progresso, timer regressivo.
    Chama os callbacks ao_tick, ao_vitoria e ao_derrota.
    """

    def __init__(self, numero: int, num_jogadores: int,
                 ao_tick, ao_vitoria, ao_derrota, ao_gelo=None):
        self.numero = numero
        self._lock = threading.Lock()
        nivel = min(numero, 4)
        base = DEMANDA_BASE[nivel]
        fator = max(1, num_jogadores)
        self.demanda = {k: v * fator for k, v in base.items()}
        self.progresso = {k: 0 for k in self.demanda}
        self.duracao = DURACAO_POR_TEMPORADA.get(nivel, 90)
        self._restante = self.duracao
        self._ao_tick = ao_tick
        self._ao_vitoria = ao_vitoria
        self._ao_derrota = ao_derrota
        self._ao_gelo = ao_gelo
        self._timer = None
        self._rodando = False
        self._proxima_geada = 30  # Temporada 4+: geada a cada 30s

    def iniciar(self):
        self._rodando = True
        self._agendar_tick()

    def parar(self):
        self._rodando = False
        if self._timer:
            self._timer.cancel()

    def _agendar_tick(self):
        if not self._rodando:
            return
        self._timer = threading.Timer(1.0, self._tick)
        self._timer.daemon = True
        self._timer.start()

    def _tick(self):
        with self._lock:
            self._restante -= 1
            restante = self._restante

        self._ao_tick(restante)

        # Evento de geada no inverno (temporada 4+)
        if self.numero >= 4 and self._ao_gelo:
            self._proxima_geada -= 1
            if self._proxima_geada <= 0:
                self._proxima_geada = 30
                self._ao_gelo()

        if restante <= 0:
            self._rodando = False
            self._ao_derrota()
        else:
            self._agendar_tick()

    def registrar_colheita(self, tile_pronto: int) -> bool:
        """Registra colheita e retorna True se a meta foi atingida."""
        cultura = PRONTA_PARA_DEMANDA.get(tile_pronto)
        if cultura is None or cultura not in self.progresso:
            return False
        with self._lock:
            if self.progresso[cultura] < self.demanda[cultura]:
                self.progresso[cultura] += 1
            return self._meta_atingida_sem_lock()

    def _meta_atingida_sem_lock(self) -> bool:
        return all(self.progresso[k] >= self.demanda[k] for k in self.demanda)

    def get_estado(self) -> dict:
        with self._lock:
            return {
                "numero": self.numero,
                "demanda": dict(self.demanda),
                "progresso": dict(self.progresso),
                "restante": self._restante,
            }

    def get_culturas_disponiveis(self) -> list:
        return list(self.demanda.keys())


if __name__ == "__main__":
    ticks = []
    resultado = []

    t = Temporada(
        numero=1, num_jogadores=2,
        ao_tick=lambda r: ticks.append(r),
        ao_vitoria=lambda: resultado.append("vitoria"),
        ao_derrota=lambda: resultado.append("derrota"),
    )
    # Testa demanda proporcional ao nº de jogadores
    assert t.demanda[3] == 12, f"6 base * 2 jogadores = 12, got {t.demanda[3]}"
    # Testa registrar colheita
    for _ in range(12):
        t.registrar_colheita(13)  # trigo pronto = 13
    for _ in range(6):
        t.registrar_colheita(14)  # arroz pronto = 14
    for _ in range(10):
        t.registrar_colheita(15)  # cana pronta terra = 15
    assert t._meta_atingida_sem_lock() == True
    print("ClassTemporada: todos os testes passaram.")
