import threading

# Mapeamento cultura -> nome legível
NOME_CULTURA = {3: "trigo", 4: "arroz", 6: "cana", 7: "cana",
                10: "milho", 11: "batata", 12: "tomate"}

# Sementes iniciais por número de temporada
SEMENTES_POR_TEMPORADA = {
    1: {3: 30, 4: 20, 6: 30},
    2: {3: 25, 4: 15, 6: 25, 10: 20},
    3: {3: 20, 4: 10, 6: 20, 10: 15, 11: 20},
    4: {3: 15, 4: 8,  6: 15, 10: 10, 11: 15, 12: 10},
}

class Estoque:
    """Estoque global de sementes compartilhado entre todos os jogadores. Thread-safe."""

    def __init__(self):
        self._lock = threading.Lock()
        self._sementes = {}

    def inicializar(self, numero_temporada: int):
        """Repõe o estoque para os valores da temporada indicada."""
        nivel = min(numero_temporada, 4)
        with self._lock:
            self._sementes = dict(SEMENTES_POR_TEMPORADA[nivel])

    def pegar(self, cultura: int) -> bool:
        """Tenta retirar 1 semente do tipo indicado. Retorna True se bem-sucedido."""
        with self._lock:
            if self._sementes.get(cultura, 0) > 0:
                self._sementes[cultura] -= 1
                return True
            return False

    def repor(self, cultura: int, quantidade: int = 1):
        """Recoloca sementes no estoque (chamado após colheita)."""
        with self._lock:
            if cultura in self._sementes:
                self._sementes[cultura] += quantidade

    def snapshot(self) -> dict:
        """Retorna cópia do estado atual do estoque."""
        with self._lock:
            return dict(self._sementes)

    def esta_baixo(self, cultura: int, limiar: int = 5) -> bool:
        with self._lock:
            return self._sementes.get(cultura, 0) <= limiar


if __name__ == "__main__":
    e = Estoque()
    e.inicializar(1)
    snap = e.snapshot()
    assert snap[3] == 30, "trigo inicial deve ser 30"
    assert e.pegar(3) == True
    assert e.snapshot()[3] == 29
    assert e.pegar(999) == False, "cultura inexistente retorna False"
    e.repor(3, 2)
    assert e.snapshot()[3] == 31
    assert e.esta_baixo(4, limiar=21) == True
    print("ClassEstoque: todos os testes passaram.")
