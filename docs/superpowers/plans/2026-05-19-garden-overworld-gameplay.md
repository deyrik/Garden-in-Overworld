# Garden in Overworld — Plano de Implementação de Jogabilidade

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar loop de jogo colaborativo com temporadas, crescimento em tempo real, estoque compartilhado de sementes e interface visual renovada.

**Architecture:** O servidor ganha duas novas classes (`ClassEstoque`, `ClassTemporada`) e recebe um callback de broadcast injetado após criação. O cliente ganha novos sinais Qt e dois novos widgets (`WidgetHUD`, `WidgetEstoque`). O mapa é redesenhado com `QLabel` coloridos de 32px.

**Tech Stack:** Python 3, sockets TCP, threading, PyQt6.

---

## Mapeamento de Arquivos

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `src/server/ClassMapa.py` | Modificar | Novos estados de tile (solo preparado, culturas prontas), método `preparar()`, `maturar()` |
| `src/server/ClassEstoque.py` | Criar | Estoque global de sementes thread-safe |
| `src/server/ClassTemporada.py` | Criar | Temporada: demanda, progresso, timer, vitória/derrota |
| `src/server/ClassUser.py` | Modificar | Campo `semente_na_mao` em `User` |
| `src/server/ClassControlador.py` | Modificar | Novos comandos, timers de crescimento, wiring de temporada |
| `src/server/mainServer.py` | Modificar | Instanciar e conectar novas classes |
| `src/client/ClassFazendeiro.py` | Modificar | Novos métodos de envio + handlers de novos comandos do servidor |
| `src/client/ClassOuvinte.py` | Modificar | Novos sinais Qt para eventos de jogo |
| `src/client/gui/estilos.py` | Modificar | Paleta de cores dos tiles |
| `src/client/gui/WidgetMapa.py` | Modificar | Redesign: QLabel 32px coloridos, cursor dos jogadores |
| `src/client/gui/WidgetHUD.py` | Criar | Barra de topo: timer + barras de progresso por cultura |
| `src/client/gui/WidgetAcoes.py` | Modificar | 4 ações (Preparar, Pegar Semente, Plantar, Colher) + "Na Mão" |
| `src/client/gui/WidgetEstoque.py` | Criar | Painel de estoque global sincronizado |
| `src/client/gui/JanelaPrincipal.py` | Modificar | Integrar WidgetHUD no topo, WidgetEstoque na esquerda, conectar novos sinais |

---

## Tarefa 1: ClassMapa — novos estados e métodos

**Arquivos:**
- Modificar: `src/server/ClassMapa.py`

Adicionar estados 8 (solo preparado terra), 9 (solo preparado areia), e estados "pronta" (trigo=13, arroz=14, cana terra=15, cana areia=16, milho=17, batata=18, tomate=19). Adicionar `preparar()` e `maturar()`.

- [ ] **Passo 1: Adicionar constantes e atualizar o comentário de cabeçalho**

Em `src/server/ClassMapa.py`, substituir o bloco de comentários no topo:

```python
# 0- terra
# 1- agua
# 2- areia
# 8- solo preparado (terra)
# 9- solo preparado (areia)
# --- Crescendo ---
# 3- trigo         (terra preparada)
# 4- arroz         (agua)
# 6- cana na terra (terra preparada)
# 7- cana na areia (areia preparada)
# 10- milho        (terra preparada)
# 11- batata       (qualquer solo preparado)
# 12- tomate       (terra preparada + agua no raio 2)
# --- Prontas para colher ---
# 13- trigo pronto
# 14- arroz pronto
# 15- cana pronta (terra)
# 16- cana pronta (areia)
# 17- milho pronto
# 18- batata pronta
# 19- tomate pronto

TEMPO_CRESCIMENTO = {3: 20, 4: 35, 6: 20, 7: 20, 10: 40, 11: 25, 12: 50}

MAPA_CRESCENDO_PARA_PRONTA = {3: 13, 4: 14, 6: 15, 7: 16, 10: 17, 11: 18, 12: 19}

MAPA_PRONTA_PARA_BASE = {13: 0, 14: 1, 15: 0, 16: 2, 17: 0, 18: 0, 19: 0}

CULTURAS_PRONTAS = {13, 14, 15, 16, 17, 18, 19}

CULTURAS_CRESCENDO = {3, 4, 6, 7, 10, 11, 12}
```

- [ ] **Passo 2: Adicionar método `preparar()`**

Logo após `__init__`, adicionar:

```python
def preparar(self, x, y):
    """Prepara o solo na posição (x, y). Terra vira 8, areia vira 9."""
    if not self.valida_posicao(x, y):
        return False
    if self.matriz[x][y] == 0:
        self.matriz[x][y] = 8
        return True
    if self.matriz[x][y] == 2:
        self.matriz[x][y] = 9
        return True
    return False
```

- [ ] **Passo 3: Atualizar `verifica_compatibilidade()` para novos terrenos e culturas**

Substituir o método inteiro:

```python
def verifica_compatibilidade(self, x, y, acao: int):
    tile = self.matriz[x][y]
    if acao == 3:   # trigo: terra preparada
        return tile == 8
    elif acao == 4:  # arroz: agua
        return tile == 1
    elif acao == 5:  # cana: terra ou areia preparada (legado, usa 6/7 internamente)
        return tile in (8, 9)
    elif acao == 10: # milho: terra preparada
        return tile == 8
    elif acao == 11: # batata: qualquer solo preparado
        return tile in (8, 9)
    elif acao == 12: # tomate: terra preparada
        return tile == 8
    return False
```

- [ ] **Passo 4: Atualizar `plantar()` para novos tiles de origem**

Substituir o método `plantar()`:

```python
def plantar(self, x, y, cultura: int):
    """Planta a cultura na posição, assumindo que a compatibilidade já foi validada."""
    if not self.valida_posicao(x, y):
        return False
    if not self.verifica_compatibilidade(x, y, cultura):
        return False
    if not self.verifica_fertilidade(x, y, cultura):
        return False
    tile = self.matriz[x][y]
    if cultura == 5:  # cana: escolhe variante por terreno
        self.matriz[x][y] = 6 if tile == 8 else 7
    else:
        self.matriz[x][y] = cultura
    return True
```

- [ ] **Passo 5: Adicionar `maturar()` — chamado pelo timer quando a planta fica pronta**

```python
def maturar(self, x, y):
    """Transiciona a célula de 'crescendo' para 'pronta'. Retorna True se bem-sucedido."""
    cultura = self.matriz[x][y]
    if cultura not in MAPA_CRESCENDO_PARA_PRONTA:
        return False
    self.matriz[x][y] = MAPA_CRESCENDO_PARA_PRONTA[cultura]
    return True
```

- [ ] **Passo 6: Atualizar `colher()` para aceitar estados "pronta"**

Substituir o método `colher()`:

```python
def colher(self, x, y):
    """Colhe a cultura pronta em (x, y). Retorna (True, cultura_base) ou (False, None)."""
    if not self.valida_posicao(x, y):
        return False, None
    tile = self.matriz[x][y]
    if tile not in MAPA_PRONTA_PARA_BASE:
        return False, None
    self.matriz[x][y] = MAPA_PRONTA_PARA_BASE[tile]
    return True, tile
```

- [ ] **Passo 7: Atualizar `exibe_colorido()` para incluir novos estados**

Adicionar os novos valores ao dict `CORES`:

```python
CORES = {
    0:  '\033[42m',       # Terra: verde
    1:  '\033[44m',       # Agua: azul
    2:  '\033[43m',       # Areia: amarelo
    8:  '\033[48;5;94m',  # Solo preparado terra: marrom
    9:  '\033[48;5;130m', # Solo preparado areia: marrom claro
    3:  '\033[48;5;58m',  # Trigo crescendo
    4:  '\033[46m',       # Arroz crescendo
    6:  '\033[48;5;22m',  # Cana crescendo terra
    7:  '\033[48;5;28m',  # Cana crescendo areia
    10: '\033[48;5;136m', # Milho crescendo
    11: '\033[48;5;52m',  # Batata crescendo
    12: '\033[48;5;160m', # Tomate crescendo
    13: '\033[48;5;220m', # Trigo pronto
    14: '\033[48;5;48m',  # Arroz pronto
    15: '\033[48;5;46m',  # Cana pronta terra
    16: '\033[48;5;40m',  # Cana pronta areia
    17: '\033[48;5;214m', # Milho pronto
    18: '\033[48;5;88m',  # Batata pronta
    19: '\033[48;5;196m', # Tomate pronto
}
```

- [ ] **Passo 8: Testar manualmente o módulo**

Adicionar ao bloco `if __name__ == "__main__"` no final do arquivo:

```python
if __name__ == "__main__":
    m = Mapa(5, 5)
    m.inicializa_matriz()
    # Testa preparar
    assert m.preparar(0, 0) == True,  "preparar terra deve retornar True"
    assert m.matriz[0][0] == 8,       "terra preparada deve ser 8"
    assert m.preparar(0, 0) == False, "nao pode preparar duas vezes"
    m.matriz[0][1] = 2
    assert m.preparar(0, 1) == True,  "preparar areia deve retornar True"
    assert m.matriz[0][1] == 9,       "areia preparada deve ser 9"
    # Testa plantar e maturar
    m.matriz[0][2] = 1  # agua para arroz
    assert m.plantar(0, 2, 4) == True, "plantar arroz em agua"
    assert m.matriz[0][2] == 4
    assert m.maturar(0, 2) == True
    assert m.matriz[0][2] == 14, "arroz pronto = 14"
    # Testa colher
    ok, tile = m.colher(0, 2)
    assert ok == True and tile == 14
    assert m.matriz[0][2] == 1, "apos colheita volta para agua"
    print("ClassMapa: todos os testes passaram.")
```

Executar: `python3 src/server/ClassMapa.py`
Esperado: `ClassMapa: todos os testes passaram.`

- [ ] **Passo 9: Commit**

```bash
git add src/server/ClassMapa.py
git commit -m "feat: adiciona estados de solo preparado e culturas prontas em ClassMapa"
```

---

## Tarefa 2: ClassEstoque — estoque global de sementes

**Arquivos:**
- Criar: `src/server/ClassEstoque.py`

- [ ] **Passo 1: Criar o arquivo**

```python
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
```

- [ ] **Passo 2: Testar manualmente**

Adicionar ao final do arquivo:

```python
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
```

Executar: `python3 src/server/ClassEstoque.py`
Esperado: `ClassEstoque: todos os testes passaram.`

- [ ] **Passo 3: Commit**

```bash
git add src/server/ClassEstoque.py
git commit -m "feat: cria ClassEstoque com estoque global thread-safe de sementes"
```

---

## Tarefa 3: ClassTemporada — gerenciador de temporadas

**Arquivos:**
- Criar: `src/server/ClassTemporada.py`

- [ ] **Passo 1: Criar o arquivo**

```python
import threading
import random

DURACAO_POR_TEMPORADA = {1: 180, 2: 150, 3: 120, 4: 90}

# Demanda base por temporada (multipicada pelo nº de jogadores conectados)
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
```

- [ ] **Passo 2: Testar manualmente**

Adicionar ao final:

```python
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
```

Executar: `python3 src/server/ClassTemporada.py`
Esperado: `ClassTemporada: todos os testes passaram.`

- [ ] **Passo 3: Commit**

```bash
git add src/server/ClassTemporada.py
git commit -m "feat: cria ClassTemporada com demanda, progresso e timer de temporada"
```

---

## Tarefa 4: ClassUser — campo semente_na_mao

**Arquivos:**
- Modificar: `src/server/ClassUser.py`

- [ ] **Passo 1: Adicionar `semente_na_mao` em `User.__init__`**

Substituir `User.__init__`:

```python
def __init__(self, nick):
    self.nick = nick
    self.semente_na_mao = None  # int ou None: cultura que o jogador pegou do estoque
    self.posicao = None          # (x, y) ou None: tile selecionado no mapa
```

Remover `self.inventario` e os métodos `adiciona_item`, `remove_item`, `ver_inventario` — o estoque agora é gerenciado por `ClassEstoque`.

- [ ] **Passo 2: Commit**

```bash
git add src/server/ClassUser.py
git commit -m "feat: adiciona semente_na_mao e posicao em User, remove inventario individual"
```

---

## Tarefa 5: ClassControlador — novos comandos e timers de crescimento

**Arquivos:**
- Modificar: `src/server/ClassControlador.py`

- [ ] **Passo 1: Atualizar `__init__` para receber estoque e temporada**

Substituir o método `__init__`:

```python
import json
import threading
import random
from ClassMapa import TEMPO_CRESCIMENTO, MAPA_CRESCENDO_PARA_PRONTA, CULTURAS_PRONTAS

class ControladorFazenda:
    def __init__(self, mapa_instancia, gerenciador_instancia, estoque_instancia):
        self.mapa = mapa_instancia
        self.gerenciador = gerenciador_instancia
        self.estoque = estoque_instancia
        self.temporada = None
        self._broadcast = None                  # injetado depois via registrar_broadcast()
        self._timers_crescimento = {}           # {(x, y): threading.Timer}
        self._lock_timers = threading.Lock()
```

- [ ] **Passo 2: Adicionar `registrar_broadcast()` e `iniciar_temporada()`**

```python
    def registrar_broadcast(self, fn_broadcast):
        """Injeta a função de broadcast do servidor TCP."""
        self._broadcast = fn_broadcast

    def iniciar_temporada(self, numero: int):
        """Para a temporada atual (se houver) e inicia uma nova."""
        from ClassTemporada import Temporada
        num_jogadores = sum(1 for v in self.gerenciador.slots.values() if v is not None)
        if self.temporada:
            self.temporada.parar()
        self.estoque.inicializar(numero)
        self.temporada = Temporada(
            numero=numero,
            num_jogadores=num_jogadores,
            ao_tick=self._ao_tick_temporada,
            ao_vitoria=self._ao_vitoria,
            ao_derrota=self._ao_derrota,
            ao_gelo=self._ao_gelo if numero >= 4 else None,
        )
        self.temporada.iniciar()
        estado = self.temporada.get_estado()
        msg = json.dumps({
            "comando": "INICIO_TEMPORADA",
            "numero": estado["numero"],
            "demanda": estado["demanda"],
            "restante": estado["restante"],
            "estoque": self.estoque.snapshot(),
        }) + "\n"
        if self._broadcast:
            self._broadcast(msg)
        print(f"[JOGO] Temporada {numero} iniciada.")

    def _ao_tick_temporada(self, restante: int):
        if self._broadcast:
            self._broadcast(json.dumps({"comando": "TICK_TIMER", "restante": restante}) + "\n")

    def _ao_vitoria(self):
        numero_atual = self.temporada.numero if self.temporada else 1
        print(f"[JOGO] Vitoria na temporada {numero_atual}!")
        if self._broadcast:
            self._broadcast(json.dumps({"comando": "VITORIA", "temporada": numero_atual}) + "\n")
        t = threading.Timer(5.0, lambda: self.iniciar_temporada(numero_atual + 1))
        t.daemon = True
        t.start()

    def _ao_derrota(self):
        numero_atual = self.temporada.numero if self.temporada else 1
        print(f"[JOGO] Derrota na temporada {numero_atual}.")
        if self._broadcast:
            self._broadcast(json.dumps({"comando": "DERROTA", "temporada": numero_atual}) + "\n")
        t = threading.Timer(5.0, lambda: self.iniciar_temporada(numero_atual))
        t.daemon = True
        t.start()

    def _ao_gelo(self):
        """Escolhe uma célula plantada aleatória e avisa que vai gelar."""
        celulas = [
            (x, y)
            for x in range(self.mapa.linha)
            for y in range(self.mapa.coluna)
            if self.mapa.matriz[x][y] in CULTURAS_PRONTAS or
               self.mapa.matriz[x][y] in MAPA_CRESCENDO_PARA_PRONTA
        ]
        if not celulas:
            return
        x, y = random.choice(celulas)
        if self._broadcast:
            self._broadcast(json.dumps({"comando": "AVISO_GELO", "x": x, "y": y, "segundos": 10}) + "\n")
        t = threading.Timer(10.0, lambda: self._aplicar_gelo(x, y))
        t.daemon = True
        t.start()

    def _aplicar_gelo(self, x, y):
        from ClassMapa import MAPA_PRONTA_PARA_BASE, CULTURAS_PRONTAS, CULTURAS_CRESCENDO
        tile = self.mapa.matriz[x][y]
        if tile not in CULTURAS_PRONTAS and tile not in CULTURAS_CRESCENDO:
            return
        valor_anterior = tile
        # Cancela timer de crescimento se existir
        with self._lock_timers:
            timer = self._timers_crescimento.pop((x, y), None)
        if timer:
            timer.cancel()
        from ClassMapa import MAPA_PRONTA_PARA_BASE
        if tile in MAPA_PRONTA_PARA_BASE:
            self.mapa.matriz[x][y] = MAPA_PRONTA_PARA_BASE[tile]
        else:
            # Crescendo: volta para o estado base da cultura
            from ClassMapa import MAPA_CRESCENDO_PARA_PRONTA
            pronta = MAPA_CRESCENDO_PARA_PRONTA.get(tile)
            if pronta:
                from ClassMapa import MAPA_PRONTA_PARA_BASE
                self.mapa.matriz[x][y] = MAPA_PRONTA_PARA_BASE.get(pronta, 0)
        if self._broadcast:
            self._broadcast(json.dumps({
                "comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": self.mapa.matriz[x][y]
            }) + "\n")
```

- [ ] **Passo 3: Adicionar método `_iniciar_timer_crescimento()`**

```python
    def _iniciar_timer_crescimento(self, x, y, cultura):
        tempo = TEMPO_CRESCIMENTO.get(cultura, 30)
        with self._lock_timers:
            timer_antigo = self._timers_crescimento.pop((x, y), None)
        if timer_antigo:
            timer_antigo.cancel()
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
        if self._broadcast:
            self._broadcast(json.dumps({
                "comando": "CULTURA_PRONTA", "x": x, "y": y, "valor": tile_pronto
            }) + "\n")
```

- [ ] **Passo 4: Substituir `processa_mensagem()` completo**

```python
    def processa_mensagem(self, id_jogador, mensagem_str):
        print(f"[JOGO] Comando do Jogador {id_jogador}: {mensagem_str}")
        try:
            dados = json.loads(mensagem_str)
        except json.JSONDecodeError:
            return json.dumps({"comando": "RESPOSTA", "status": "ERRO", "mensagem": "JSON invalido"}) + "\n", None

        comando = str(dados.get("comando", "")).strip().upper()
        resposta = {}
        broadcast = None

        if comando == "NICKNAME":
            nome = dados.get("nome", "SemNome")
            self.gerenciador.slots[id_jogador].nick = nome
            resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": f"Nickname: {nome}"}

        elif comando == "PREPARAR":
            x, y = dados.get("x"), dados.get("y")
            if self.mapa.preparar(x, y):
                novo_valor = self.mapa.matriz[x][y]
                broadcast = json.dumps({"comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": novo_valor}) + "\n"
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Solo preparado"}
            else:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Nao foi possivel preparar"}

        elif comando == "PEGAR_SEMENTE":
            cultura = dados.get("cultura")
            jogador = self.gerenciador.slots.get(id_jogador)
            if jogador is None:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Jogador nao encontrado"}
            elif self.estoque.pegar(cultura):
                jogador.semente_na_mao = cultura
                snap = self.estoque.snapshot()
                broadcast = json.dumps({"comando": "ATUALIZAR_ESTOQUE", "estoque": snap}) + "\n"
                resposta = {"comando": "RESPOSTA", "status": "OK",
                            "mensagem": f"Semente {cultura} na mao", "cultura": cultura}
            else:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Sem sementes desse tipo"}

        elif comando == "PLANTAR":
            semente = dados.get("semente")
            x, y = dados.get("x"), dados.get("y")
            jogador = self.gerenciador.slots.get(id_jogador)
            if jogador is None or jogador.semente_na_mao != semente:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Sem semente na mao"}
            elif self.mapa.plantar(x, y, semente):
                jogador.semente_na_mao = None
                cultura_plantada = self.mapa.matriz[x][y]
                self._iniciar_timer_crescimento(x, y, cultura_plantada)
                broadcast = json.dumps({"comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": cultura_plantada}) + "\n"
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Plantado"}
            else:
                # Devolve a semente ao estoque se o plantio falhar
                self.estoque.repor(semente)
                jogador.semente_na_mao = None
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Nao foi possivel plantar ai"}

        elif comando == "COLHER":
            x, y = dados.get("x"), dados.get("y")
            ok, tile_pronto = self.mapa.colher(x, y)
            if ok:
                novo_valor = self.mapa.matriz[x][y]
                # Repõe 1 semente no estoque
                from ClassTemporada import PRONTA_PARA_DEMANDA
                cultura_demanda = PRONTA_PARA_DEMANDA.get(tile_pronto)
                if cultura_demanda:
                    self.estoque.repor(cultura_demanda)
                snap = self.estoque.snapshot()
                broadcast_celula = json.dumps({"comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": novo_valor}) + "\n"
                broadcast_estoque = json.dumps({"comando": "ATUALIZAR_ESTOQUE", "estoque": snap}) + "\n"
                # Registra colheita na temporada
                progresso_msgs = ""
                if self.temporada:
                    vitoria = self.temporada.registrar_colheita(tile_pronto)
                    estado = self.temporada.get_estado()
                    progresso_msgs = json.dumps({"comando": "ATUALIZAR_PROGRESSO",
                                                 "progresso": estado["progresso"],
                                                 "demanda": estado["demanda"]}) + "\n"
                    if vitoria:
                        self.temporada.parar()
                        self._ao_vitoria()
                broadcast = broadcast_celula + broadcast_estoque + progresso_msgs
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Colhido"}
            else:
                resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Nao ha cultura pronta ai"}

        elif comando == "CURSOR":
            x, y = dados.get("x"), dados.get("y")
            jogador = self.gerenciador.slots.get(id_jogador)
            if jogador:
                jogador.posicao = (x, y)
            nick = jogador.nick if jogador else "?"
            broadcast = json.dumps({
                "comando": "POSICAO_JOGADOR", "id": id_jogador, "nick": nick, "x": x, "y": y
            }) + "\n"
            resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Cursor atualizado"}

        elif comando == "MATRIZ":
            resposta = {"comando": "ATUALIZAR_MAPA", "matriz": self.mapa.matriz}

        elif comando == "CHAT":
            mensagem = dados.get("mensagem", "")
            nick = self.gerenciador.slots[id_jogador].nick
            broadcast = json.dumps({"comando": "CHAT", "autor": nick, "mensagem": mensagem}) + "\n"
            resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Chat enviado"}

        elif comando == "SAIR":
            resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Desconectando..."}

        else:
            resposta = {"comando": "RESPOSTA", "status": "ERRO", "mensagem": "Comando desconhecido"}

        return json.dumps(resposta) + "\n", broadcast
```

- [ ] **Passo 5: Commit**

```bash
git add src/server/ClassControlador.py
git commit -m "feat: adiciona comandos PREPARAR/PEGAR_SEMENTE/COLHER, timers de crescimento e logica de temporada"
```

---

## Tarefa 6: mainServer.py — conectar as novas classes

**Arquivos:**
- Modificar: `src/server/mainServer.py`

- [ ] **Passo 1: Atualizar mainServer.py**

```python
import ClassMapa as mapa_mod
import ClassUser as usManager
import ClassControlador as ctrl
import ClassServidorTCP as tcpS
import ClassEstoque as est

PORTA_TCP = 12345

if __name__ == "__main__":
    print("--- INICIALIZANDO MUNDO ---")
    mapa_jogo = mapa_mod.Mapa()
    mapa_jogo.gerar_mapa_aleatorio()
    mapa_jogo.exibe_colorido()

    gerenciador = usManager.GerenciadorUsers()
    estoque = est.Estoque()

    print("--- CONECTANDO AS CAMADAS ---")
    controlador = ctrl.ControladorFazenda(mapa_jogo, gerenciador, estoque)

    servidor = tcpS.ServidorTCP(
        host="0.0.0.0",
        port=PORTA_TCP,
        ao_conectar=controlador.conecta_jogador,
        ao_gerar_boas_vindas=controlador.gera_boas_vindas,
        ao_receber_mensagem=controlador.processa_mensagem,
        ao_desconectar=controlador.desconecta_jogador
    )

    # Injeta broadcast no controlador APÓS criar o servidor
    controlador.registrar_broadcast(servidor.enviar_broadcast)

    # Inicia a primeira temporada
    controlador.iniciar_temporada(1)

    servidor.start()
```

- [ ] **Passo 2: Testar integração básica do servidor**

Executar: `python3 src/server/mainServer.py`
Esperado: servidor inicia, exibe o mapa colorido, imprime `[JOGO] Temporada 1 iniciada.` e fica escutando na porta 12345.

- [ ] **Passo 3: Commit**

```bash
git add src/server/mainServer.py
git commit -m "feat: conecta ClassEstoque e ClassTemporada no servidor principal"
```

---

## Tarefa 7: ClassFazendeiro — novos métodos e handlers

**Arquivos:**
- Modificar: `src/client/ClassFazendeiro.py`

- [ ] **Passo 1: Adicionar `solicita_preparar()`, `solicita_pegar_semente()` e `solicita_cursor()`**

Após `solicita_chat()`, adicionar:

```python
    def solicita_preparar(self, x, y):
        dados = {"comando": "PREPARAR", "x": x, "y": y}
        self.rede.manda_mensagem(json.dumps(dados))

    def solicita_pegar_semente(self, cultura: int):
        dados = {"comando": "PEGAR_SEMENTE", "cultura": cultura}
        self.rede.manda_mensagem(json.dumps(dados))

    def solicita_cursor(self, x, y):
        dados = {"comando": "CURSOR", "x": x, "y": y}
        self.rede.manda_mensagem(json.dumps(dados))
```

- [ ] **Passo 2: Atualizar `escutar_servidor()` com os novos tipos de mensagem**

No bloco `elif/else` de `escutar_servidor()`, adicionar antes do `else`:

```python
            elif comando_servidor == "INICIO_TEMPORADA":
                return {
                    "tipo": "INICIO_TEMPORADA",
                    "numero": dados.get("numero"),
                    "demanda": dados.get("demanda"),
                    "restante": dados.get("restante"),
                    "estoque": dados.get("estoque"),
                }

            elif comando_servidor == "TICK_TIMER":
                return {"tipo": "TICK_TIMER", "restante": dados.get("restante")}

            elif comando_servidor == "ATUALIZAR_ESTOQUE":
                return {"tipo": "ATUALIZAR_ESTOQUE", "estoque": dados.get("estoque")}

            elif comando_servidor == "ATUALIZAR_PROGRESSO":
                return {
                    "tipo": "ATUALIZAR_PROGRESSO",
                    "progresso": dados.get("progresso"),
                    "demanda": dados.get("demanda"),
                }

            elif comando_servidor == "CULTURA_PRONTA":
                return {"tipo": "CULTURA_PRONTA", "x": dados.get("x"), "y": dados.get("y"), "valor": dados.get("valor")}

            elif comando_servidor == "POSICAO_JOGADOR":
                return {
                    "tipo": "POSICAO_JOGADOR",
                    "id": dados.get("id"),
                    "nick": dados.get("nick"),
                    "x": dados.get("x"),
                    "y": dados.get("y"),
                }

            elif comando_servidor == "VITORIA":
                return {"tipo": "VITORIA", "temporada": dados.get("temporada")}

            elif comando_servidor == "DERROTA":
                return {"tipo": "DERROTA", "temporada": dados.get("temporada")}

            elif comando_servidor == "AVISO_GELO":
                return {"tipo": "AVISO_GELO", "x": dados.get("x"), "y": dados.get("y"), "segundos": dados.get("segundos")}

            elif comando_servidor == "RESPOSTA":
                return {
                    "tipo": "RESPOSTA_SISTEMA",
                    "status": dados.get("status"),
                    "mensagem": dados.get("mensagem"),
                    "cultura": dados.get("cultura"),  # presente em PEGAR_SEMENTE OK
                }
```

- [ ] **Passo 3: Commit**

```bash
git add src/client/ClassFazendeiro.py
git commit -m "feat: adiciona solicita_preparar, solicita_pegar_semente e handlers de novos comandos"
```

---

## Tarefa 8: ClassOuvinte — novos sinais Qt

**Arquivos:**
- Modificar: `src/client/ClassOuvinte.py`

- [ ] **Passo 1: Substituir o arquivo completo**

```python
from PyQt6.QtCore import QThread, pyqtSignal

class OuvinteThread(QThread):
    """Thread de escuta do servidor. Emite sinais Qt para atualizar a UI."""
    sinal_mapa_completo        = pyqtSignal(list)
    sinal_celula_atualizada    = pyqtSignal(int, int, int)       # x, y, valor
    sinal_resposta_sistema     = pyqtSignal(str, str, object)    # status, mensagem, cultura (ou None)
    sinal_chat_recebido        = pyqtSignal(str, str)            # autor, mensagem
    sinal_desconectado         = pyqtSignal()
    sinal_inicio_temporada     = pyqtSignal(dict)                # {numero, demanda, restante, estoque}
    sinal_tick_timer           = pyqtSignal(int)                 # segundos restantes
    sinal_estoque_atualizado   = pyqtSignal(dict)                # {cultura_int: quantidade}
    sinal_progresso_atualizado = pyqtSignal(dict, dict)          # progresso, demanda
    sinal_cultura_pronta       = pyqtSignal(int, int, int)       # x, y, valor
    sinal_posicao_jogador      = pyqtSignal(int, str, int, int)  # id, nick, x, y
    sinal_vitoria              = pyqtSignal(int)                 # numero da temporada
    sinal_derrota              = pyqtSignal(int)
    sinal_aviso_gelo           = pyqtSignal(int, int, int)       # x, y, segundos

    def __init__(self, fazendeiro, mapa_jogo):
        super().__init__()
        self.fazendeiro = fazendeiro
        self.mapa_jogo = mapa_jogo

    def run(self):
        while True:
            evento = self.fazendeiro.escutar_servidor()
            tipo = evento["tipo"]

            if tipo == "DESCONECTADO":
                self.sinal_desconectado.emit()
                break

            elif tipo == "MAPA_COMPLETO":
                self.mapa_jogo.atualizar_matriz(evento["matriz"])
                self.sinal_mapa_completo.emit(evento["matriz"])

            elif tipo == "CELULA":
                x, y, valor = evento["x"], evento["y"], evento["valor"]
                self.mapa_jogo.matriz[x][y] = valor
                self.sinal_celula_atualizada.emit(x, y, valor)

            elif tipo == "RESPOSTA_SISTEMA":
                self.sinal_resposta_sistema.emit(
                    evento.get("status", ""),
                    evento.get("mensagem", ""),
                    evento.get("cultura"),
                )

            elif tipo == "CHAT":
                self.sinal_chat_recebido.emit(evento.get("autor", "?"), evento.get("mensagem", ""))

            elif tipo == "INICIO_TEMPORADA":
                self.sinal_inicio_temporada.emit({
                    "numero": evento["numero"],
                    "demanda": evento["demanda"],
                    "restante": evento["restante"],
                    "estoque": evento["estoque"],
                })

            elif tipo == "TICK_TIMER":
                self.sinal_tick_timer.emit(evento["restante"])

            elif tipo == "ATUALIZAR_ESTOQUE":
                self.sinal_estoque_atualizado.emit(evento["estoque"])

            elif tipo == "ATUALIZAR_PROGRESSO":
                self.sinal_progresso_atualizado.emit(evento["progresso"], evento["demanda"])

            elif tipo == "CULTURA_PRONTA":
                self.sinal_cultura_pronta.emit(evento["x"], evento["y"], evento["valor"])
                self.sinal_celula_atualizada.emit(evento["x"], evento["y"], evento["valor"])

            elif tipo == "POSICAO_JOGADOR":
                self.sinal_posicao_jogador.emit(
                    evento["id"], evento["nick"], evento["x"], evento["y"]
                )

            elif tipo == "VITORIA":
                self.sinal_vitoria.emit(evento["temporada"])

            elif tipo == "DERROTA":
                self.sinal_derrota.emit(evento["temporada"])

            elif tipo == "AVISO_GELO":
                self.sinal_aviso_gelo.emit(evento["x"], evento["y"], evento["segundos"])
```

- [ ] **Passo 2: Commit**

```bash
git add src/client/ClassOuvinte.py
git commit -m "feat: adiciona novos sinais Qt em OuvinteThread para eventos de jogo"
```

---

## Tarefa 9: estilos.py — paleta de cores dos tiles

**Arquivos:**
- Modificar: `src/client/gui/estilos.py`

- [ ] **Passo 1: Adicionar dicionário `CORES_TILE` e cores de jogadores**

Ao final do arquivo, adicionar:

```python
# Cores de fundo dos tiles do mapa (QSS background-color)
CORES_TILE = {
    0:  "#3a7d44",  # terra
    1:  "#1a6b8a",  # agua
    2:  "#c8a84b",  # areia
    8:  "#5a3e1b",  # solo preparado (terra)
    9:  "#7a5a2b",  # solo preparado (areia)
    3:  "#4a6e35",  # trigo crescendo
    4:  "#1a5a78",  # arroz crescendo
    6:  "#2d5e28",  # cana crescendo terra
    7:  "#3d6e38",  # cana crescendo areia
    10: "#8a6a1a",  # milho crescendo
    11: "#5a3a2a",  # batata crescendo
    12: "#8a3a2a",  # tomate crescendo
    13: "#d4a800",  # trigo pronto
    14: "#00b4d8",  # arroz pronto
    15: "#00c853",  # cana pronta terra
    16: "#00e676",  # cana pronta areia
    17: "#ffab00",  # milho pronto
    18: "#6d4c41",  # batata pronta
    19: "#e53935",  # tomate pronto
}

# Emojis por estado de tile
EMOJIS_TILE = {
    0: "",   1: "",   2: "",
    8: "🪵", 9: "🪵",
    3: "🌱", 4: "🌱", 6: "🌱", 7: "🌱", 10: "🌱", 11: "🌱", 12: "🌱",
    13: "🌾", 14: "🌿", 15: "🎋", 16: "🎋", 17: "🌽", 18: "🥔", 19: "🍅",
}

# Cores dos cursores dos jogadores (por id 1-4)
CORES_JOGADOR = {1: "#ff6b6b", 2: "#6b9fff", 3: "#ffd93d", 4: "#a29bfe"}
```

- [ ] **Passo 2: Commit**

```bash
git add src/client/gui/estilos.py
git commit -m "feat: adiciona paleta de cores de tiles e emojis em estilos.py"
```

---

## Tarefa 10: WidgetMapa — redesign visual com QLabel coloridos

**Arquivos:**
- Modificar: `src/client/gui/WidgetMapa.py`

- [ ] **Passo 1: Substituir o arquivo completo**

```python
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from . import estilos

TAMANHO_TILE = 32

class WidgetMapa(QWidget):
    sinal_celula_clicada = pyqtSignal(int, int, int)  # x, y, valor_atual

    def __init__(self, parent=None):
        super().__init__(parent)
        self._matriz = [[0] * 20 for _ in range(20)]
        self._tiles = {}          # (x, y) -> QLabel principal
        self._cursores = {}       # id_jogador -> (x, y) anterior
        self._labels_cursor = {}  # (x, y) -> QLabel de cursor sobreposto
        self._celula_selecionada = None
        self._montar_grid()

    def _montar_grid(self):
        layout = QGridLayout(self)
        layout.setSpacing(1)
        layout.setContentsMargins(4, 4, 4, 4)
        font = QFont()
        font.setPointSize(14)
        for x in range(20):
            for y in range(20):
                label = QLabel()
                label.setFixedSize(TAMANHO_TILE, TAMANHO_TILE)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setFont(font)
                label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                label.mousePressEvent = lambda e, cx=x, cy=y: self._on_clique(cx, cy)
                self._tiles[(x, y)] = label
                layout.addWidget(label, x, y)
        self._atualizar_todos()

    def _on_clique(self, x, y):
        if self._celula_selecionada and self._celula_selecionada != (x, y):
            px, py = self._celula_selecionada
            self._aplicar_estilo(px, py, self._matriz[px][py])
        self._celula_selecionada = (x, y)
        self._aplicar_estilo_selecionado(x, y)
        self.sinal_celula_clicada.emit(x, y, self._matriz[x][y])

    def _aplicar_estilo(self, x, y, valor):
        cor = estilos.CORES_TILE.get(valor, "#1a1a2e")
        emoji = estilos.EMOJIS_TILE.get(valor, "")
        label = self._tiles[(x, y)]
        label.setStyleSheet(
            f"background-color: {cor}; border-radius: 3px; border: 1px solid #111;"
        )
        label.setText(emoji)

    def _aplicar_estilo_selecionado(self, x, y):
        valor = self._matriz[x][y]
        cor = estilos.CORES_TILE.get(valor, "#1a1a2e")
        emoji = estilos.EMOJIS_TILE.get(valor, "")
        label = self._tiles[(x, y)]
        label.setStyleSheet(
            f"background-color: {cor}; border-radius: 3px;"
            f"border: 2px solid {estilos.AMBAR};"
        )
        label.setText(emoji)

    def _aplicar_estilo_pronta(self, x, y):
        valor = self._matriz[x][y]
        cor = estilos.CORES_TILE.get(valor, "#1a1a2e")
        emoji = estilos.EMOJIS_TILE.get(valor, "")
        label = self._tiles[(x, y)]
        label.setStyleSheet(
            f"background-color: {cor}; border-radius: 3px;"
            f"border: 2px solid {estilos.DESTAQUE};"
        )
        label.setText(emoji)

    def _atualizar_todos(self):
        for x in range(20):
            for y in range(20):
                self._aplicar_estilo(x, y, self._matriz[x][y])

    def atualizar_mapa_completo(self, matriz):
        self._matriz = matriz
        self._atualizar_todos()

    def atualizar_celula(self, x, y, valor):
        from ClassMapa import CULTURAS_PRONTAS
        self._matriz[x][y] = valor
        if valor in CULTURAS_PRONTAS:
            self._aplicar_estilo_pronta(x, y)
        elif self._celula_selecionada == (x, y):
            self._aplicar_estilo_selecionado(x, y)
        else:
            self._aplicar_estilo(x, y, valor)

    def atualizar_cursor_jogador(self, id_jogador: int, nick: str, x: int, y: int):
        """Mostra a inicial colorida do jogador no tile onde ele está."""
        cor = estilos.CORES_JOGADOR.get(id_jogador, "#ffffff")
        # Apaga cursor anterior desse jogador
        pos_anterior = self._cursores.get(id_jogador)
        if pos_anterior and pos_anterior != (x, y):
            px, py = pos_anterior
            self._tiles[(px, py)].setText(estilos.EMOJIS_TILE.get(self._matriz[px][py], ""))
        self._cursores[id_jogador] = (x, y)
        inicial = nick[0].upper() if nick else "?"
        label = self._tiles[(x, y)]
        label.setText(f'<span style="color:{cor};font-weight:bold">{inicial}</span>')
```

- [ ] **Passo 2: Commit**

```bash
git add src/client/gui/WidgetMapa.py
git commit -m "feat: redesign do WidgetMapa com QLabel coloridos 32px e cursores de jogadores"
```

---

## Tarefa 11: WidgetHUD — barra de status da temporada

**Arquivos:**
- Criar: `src/client/gui/WidgetHUD.py`

- [ ] **Passo 1: Criar o arquivo**

```python
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from . import estilos

NOME_TEMPORADA = {1: "🌱 Primavera", 2: "☀️ Verão", 3: "🍂 Outono", 4: "❄️ Inverno"}

EMOJI_CULTURA = {3: "🌾", 4: "🌿", 6: "🎋", 7: "🎋", 10: "🌽", 11: "🥔", 12: "🍅"}

class WidgetHUD(QWidget):
    """Barra horizontal no topo: nome da temporada, barras de progresso e timer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self._demanda = {}
        self._progresso = {}
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(12, 4, 12, 4)
        self._layout.setSpacing(16)

        self._label_temporada = QLabel("Aguardando temporada...")
        self._label_temporada.setStyleSheet(f"color: {estilos.DESTAQUE}; font-weight: bold;")
        self._layout.addWidget(self._label_temporada)

        self._barras = {}   # cultura_int -> (QLabel emoji, QProgressBar, QLabel contagem)
        self._container_barras = QHBoxLayout()
        self._container_barras.setSpacing(8)
        self._layout.addLayout(self._container_barras)

        self._layout.addStretch()

        self._label_timer = QLabel("--:--")
        self._label_timer.setStyleSheet(f"color: {estilos.AMBAR}; font-weight: bold; font-size: 18px;")
        self._layout.addWidget(self._label_timer)

    def _limpar_barras(self):
        while self._container_barras.count():
            item = self._container_barras.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._barras.clear()

    def atualizar_temporada(self, dados: dict):
        """Recebe dict {numero, demanda, restante, estoque} do sinal_inicio_temporada."""
        numero = dados.get("numero", 1)
        nome = NOME_TEMPORADA.get(numero, f"Temporada {numero}")
        self._label_temporada.setText(f"{nome} — T{numero}")
        self._demanda = {int(k): v for k, v in dados.get("demanda", {}).items()}
        self._progresso = {k: 0 for k in self._demanda}
        self._reconstruir_barras()
        self.atualizar_timer(dados.get("restante", 0))

    def _reconstruir_barras(self):
        self._limpar_barras()
        for cultura, total in self._demanda.items():
            emoji = EMOJI_CULTURA.get(cultura, "?")
            lbl_emoji = QLabel(emoji)
            barra = QProgressBar()
            barra.setMinimum(0)
            barra.setMaximum(total)
            barra.setValue(0)
            barra.setFixedWidth(70)
            barra.setFixedHeight(12)
            barra.setTextVisible(False)
            barra.setStyleSheet(
                f"QProgressBar {{background: #333; border-radius: 4px;}}"
                f"QProgressBar::chunk {{background: {estilos.DESTAQUE}; border-radius: 4px;}}"
            )
            lbl_count = QLabel(f"0/{total}")
            lbl_count.setStyleSheet(f"color: {estilos.TEXTO}; font-size: 11px;")
            self._container_barras.addWidget(lbl_emoji)
            self._container_barras.addWidget(barra)
            self._container_barras.addWidget(lbl_count)
            self._barras[cultura] = (lbl_emoji, barra, lbl_count)

    def atualizar_progresso(self, progresso: dict, demanda: dict):
        self._progresso = {int(k): v for k, v in progresso.items()}
        self._demanda = {int(k): v for k, v in demanda.items()}
        for cultura, (_, barra, lbl_count) in self._barras.items():
            atual = self._progresso.get(cultura, 0)
            total = self._demanda.get(cultura, 1)
            barra.setValue(atual)
            lbl_count.setText(f"{atual}/{total}")

    def atualizar_timer(self, segundos: int):
        minutos = segundos // 60
        segs = segundos % 60
        texto = f"{minutos:01d}:{segs:02d}"
        cor = "#ff4444" if segundos <= 30 else estilos.AMBAR
        self._label_timer.setStyleSheet(f"color: {cor}; font-weight: bold; font-size: 18px;")
        self._label_timer.setText(texto)
```

- [ ] **Passo 2: Registrar no `__init__.py` do pacote gui**

Verificar se `src/client/gui/__init__.py` existe — se existir, não precisa de alteração. Se estiver vazio ou não existir o import, está OK.

- [ ] **Passo 3: Commit**

```bash
git add src/client/gui/WidgetHUD.py
git commit -m "feat: cria WidgetHUD com timer e barras de progresso da temporada"
```

---

## Tarefa 12: WidgetAcoes — 4 ações + painel "Na Mão"

**Arquivos:**
- Modificar: `src/client/gui/WidgetAcoes.py`

- [ ] **Passo 1: Substituir o arquivo completo**

```python
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import pyqtSignal
from . import estilos

CULTURAS_DISPONIVEIS = {3: "🌾 Trigo", 4: "🌿 Arroz", 6: "🎋 Cana",
                        10: "🌽 Milho", 11: "🥔 Batata", 12: "🍅 Tomate"}

CULTURAS_PRONTAS = {13, 14, 15, 16, 17, 18, 19}

ESTILO_ATIVO = f"""
    QPushButton {{
        background-color: {estilos.DESTAQUE};
        color: {estilos.FUNDO};
        border: 1px solid {estilos.DESTAQUE};
        border-radius: 3px;
        padding: 5px 8px;
        font-weight: bold;
        text-align: left;
    }}
"""

class WidgetAcoes(QGroupBox):
    sinal_preparar      = pyqtSignal(int, int)        # x, y
    sinal_pegar_semente = pyqtSignal(int)             # cultura
    sinal_plantar       = pyqtSignal(int, int, int)   # semente, x, y
    sinal_colher        = pyqtSignal(int, int)        # x, y

    def __init__(self, culturas_ativas=None, parent=None):
        super().__init__("AÇÕES", parent)
        self._acao_selecionada = None   # "PREPARAR", "PEGAR", "PLANTAR", "COLHER"
        self._semente_na_mao = None     # int ou None
        self._culturas_ativas = culturas_ativas or [3, 4, 6]
        self._botoes = {}
        self._montar_layout()

    def _montar_layout(self):
        layout = QVBoxLayout(self)

        # Painel "Na Mão"
        self._label_na_mao = QLabel("Na mão: —")
        self._label_na_mao.setStyleSheet(
            f"color: {estilos.AMBAR}; padding: 4px; background: {estilos.PAINEL};"
            f"border: 1px solid {estilos.BORDA}; border-radius: 3px;"
        )
        layout.addWidget(self._label_na_mao)

        # Seletor de semente para "Pegar"
        self._combo_semente = QComboBox()
        self._atualizar_combo()
        layout.addWidget(self._combo_semente)

        # Botões de ação
        acoes = [
            ("PREPARAR", "🪵 Preparar Solo"),
            ("PEGAR",    "📦 Pegar Semente"),
            ("PLANTAR",  "🌱 Plantar"),
            ("COLHER",   "✂️ Colher"),
        ]
        for chave, nome in acoes:
            btn = QPushButton(nome)
            btn.setStyleSheet("text-align: left; padding: 5px 8px;")
            btn.clicked.connect(lambda _, c=chave: self._selecionar_acao(c))
            self._botoes[chave] = btn
            layout.addWidget(btn)

        layout.addStretch()

    def _atualizar_combo(self):
        self._combo_semente.clear()
        for cultura in self._culturas_ativas:
            nome = CULTURAS_DISPONIVEIS.get(cultura, str(cultura))
            self._combo_semente.addItem(nome, cultura)

    def _selecionar_acao(self, acao):
        self._acao_selecionada = acao if self._acao_selecionada != acao else None
        self._atualizar_visuais()

    def _atualizar_visuais(self):
        for chave, btn in self._botoes.items():
            btn.setStyleSheet(ESTILO_ATIVO if chave == self._acao_selecionada
                              else "text-align: left; padding: 5px 8px;")

    def executar_para_celula(self, x, y, valor_tile):
        if self._acao_selecionada is None:
            return
        if self._acao_selecionada == "PREPARAR":
            self.sinal_preparar.emit(x, y)
        elif self._acao_selecionada == "PEGAR":
            cultura = self._combo_semente.currentData()
            if cultura is not None:
                self.sinal_pegar_semente.emit(cultura)
        elif self._acao_selecionada == "PLANTAR":
            if self._semente_na_mao is not None:
                self.sinal_plantar.emit(self._semente_na_mao, x, y)
        elif self._acao_selecionada == "COLHER":
            if valor_tile in CULTURAS_PRONTAS:
                self.sinal_colher.emit(x, y)

    def atualizar_semente_na_mao(self, cultura):
        """Chamado quando servidor confirma PEGAR_SEMENTE."""
        from . import estilos as _e
        self._semente_na_mao = cultura
        nome = CULTURAS_DISPONIVEIS.get(cultura, str(cultura)) if cultura else "—"
        self._label_na_mao.setText(f"Na mão: {nome}")

    def limpar_semente_na_mao(self):
        self._semente_na_mao = None
        self._label_na_mao.setText("Na mão: —")

    def atualizar_culturas_ativas(self, culturas: list):
        self._culturas_ativas = culturas
        self._atualizar_combo()
```

- [ ] **Passo 2: Commit**

```bash
git add src/client/gui/WidgetAcoes.py
git commit -m "feat: atualiza WidgetAcoes com 4 acoes, combo de semente e painel Na Mao"
```

---

## Tarefa 13: WidgetEstoque — painel de estoque global

**Arquivos:**
- Criar: `src/client/gui/WidgetEstoque.py`

- [ ] **Passo 1: Criar o arquivo**

```python
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel
from . import estilos

EMOJI_CULTURA = {3: "🌾", 4: "🌿", 6: "🎋", 7: "🎋", 10: "🌽", 11: "🥔", 12: "🍅"}
NOME_CULTURA  = {3: "Trigo", 4: "Arroz", 6: "Cana", 10: "Milho", 11: "Batata", 12: "Tomate"}

LIMIAR_BAIXO = 5

class WidgetEstoque(QGroupBox):
    """Exibe o estoque global de sementes sincronizado com o servidor."""

    def __init__(self, parent=None):
        super().__init__("ESTOQUE GLOBAL", parent)
        self._layout = QVBoxLayout(self)
        self._linhas = {}  # cultura_int -> QLabel

    def atualizar(self, estoque: dict):
        """Recebe dict {str_cultura: quantidade} e atualiza o display."""
        estoque_int = {int(k): v for k, v in estoque.items()}
        # Remove culturas que sumiram
        for cultura in list(self._linhas.keys()):
            if cultura not in estoque_int:
                self._linhas[cultura].deleteLater()
                del self._linhas[cultura]
        # Adiciona ou atualiza
        for cultura, qtd in sorted(estoque_int.items()):
            if cultura not in self._linhas:
                linha = self._criar_linha(cultura)
                self._layout.addWidget(linha)
            self._atualizar_linha(cultura, qtd)

    def _criar_linha(self, cultura: int) -> QLabel:
        emoji = EMOJI_CULTURA.get(cultura, "?")
        nome = NOME_CULTURA.get(cultura, str(cultura))
        label = QLabel(f"{emoji} {nome}: —")
        label.setStyleSheet(f"padding: 2px 0;")
        self._linhas[cultura] = label
        return label

    def _atualizar_linha(self, cultura: int, qtd: int):
        emoji = EMOJI_CULTURA.get(cultura, "?")
        nome = NOME_CULTURA.get(cultura, str(cultura))
        cor = "#ff6b6b" if qtd <= LIMIAR_BAIXO else estilos.TEXTO
        aviso = " ⚠" if qtd <= LIMIAR_BAIXO else ""
        self._linhas[cultura].setText(f"{emoji} {nome}: {qtd}{aviso}")
        self._linhas[cultura].setStyleSheet(f"padding: 2px 0; color: {cor};")
```

- [ ] **Passo 2: Commit**

```bash
git add src/client/gui/WidgetEstoque.py
git commit -m "feat: cria WidgetEstoque com contadores sincronizados de sementes globais"
```

---

## Tarefa 14: JanelaPrincipal — integração final

**Arquivos:**
- Modificar: `src/client/gui/JanelaPrincipal.py`

- [ ] **Passo 1: Substituir o arquivo completo**

```python
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt
from .WidgetMapa import WidgetMapa
from .WidgetAcoes import WidgetAcoes
from .WidgetEstoque import WidgetEstoque
from .WidgetHUD import WidgetHUD
from .WidgetLog import WidgetLog
from .WidgetChat import WidgetChat
from . import estilos

class JanelaPrincipal(QMainWindow):
    def __init__(self, fazendeiro, ouvinte, nick, parent=None):
        super().__init__(parent)
        self._fazendeiro = fazendeiro
        self._nick = nick

        self.setWindowTitle("🌱 Garden in Overworld")
        self.setMinimumSize(1000, 680)

        # Widgets
        self._widget_hud     = WidgetHUD()
        self._widget_mapa    = WidgetMapa()
        self._widget_acoes   = WidgetAcoes()
        self._widget_estoque = WidgetEstoque()
        self._widget_log     = WidgetLog()
        self._widget_chat    = WidgetChat()

        self._montar_layout()
        self._conectar_sinais(ouvinte)

        self.statusBar().showMessage(f"Conectado como: {nick}")
        self.statusBar().setStyleSheet(f"color: {estilos.DESTAQUE};")

    def _montar_layout(self):
        central = QWidget()
        self.setCentralWidget(central)
        raiz = QVBoxLayout(central)
        raiz.setSpacing(4)
        raiz.setContentsMargins(4, 4, 4, 4)

        # HUD no topo
        raiz.addWidget(self._widget_hud)

        # Corpo principal
        corpo = QHBoxLayout()
        corpo.setSpacing(8)

        # Coluna esquerda: estoque + acoes
        col_esq = QVBoxLayout()
        col_esq.addWidget(self._widget_estoque, stretch=1)
        col_esq.addWidget(self._widget_acoes, stretch=2)
        corpo.addLayout(col_esq, stretch=1)

        # Centro: mapa
        corpo.addWidget(self._widget_mapa, stretch=3)

        # Coluna direita: log + chat
        col_dir = QVBoxLayout()
        col_dir.addWidget(self._widget_log, stretch=2)
        col_dir.addWidget(self._widget_chat, stretch=1)
        corpo.addLayout(col_dir, stretch=1)

        raiz.addLayout(corpo)

    def _conectar_sinais(self, ouvinte):
        # Rede → Mapa
        ouvinte.sinal_mapa_completo.connect(self._widget_mapa.atualizar_mapa_completo)
        ouvinte.sinal_celula_atualizada.connect(self._widget_mapa.atualizar_celula)
        ouvinte.sinal_posicao_jogador.connect(self._widget_mapa.atualizar_cursor_jogador)

        # Rede → HUD
        ouvinte.sinal_inicio_temporada.connect(self._widget_hud.atualizar_temporada)
        ouvinte.sinal_tick_timer.connect(self._widget_hud.atualizar_timer)
        ouvinte.sinal_progresso_atualizado.connect(self._widget_hud.atualizar_progresso)

        # Rede → Estoque
        ouvinte.sinal_estoque_atualizado.connect(self._widget_estoque.atualizar)
        ouvinte.sinal_inicio_temporada.connect(
            lambda d: self._widget_estoque.atualizar(d.get("estoque", {}))
        )

        # Rede → Acoes (atualiza semente na mão e culturas disponíveis)
        ouvinte.sinal_resposta_sistema.connect(self._on_resposta_sistema)
        ouvinte.sinal_inicio_temporada.connect(
            lambda d: self._widget_acoes.atualizar_culturas_ativas(
                [int(k) for k in d.get("demanda", {}).keys()]
            )
        )

        # Rede → Log
        ouvinte.sinal_celula_atualizada.connect(self._widget_log.registrar_celula)
        ouvinte.sinal_resposta_sistema.connect(
            lambda status, msg, _: self._widget_log.registrar_resposta(status, msg)
        )
        ouvinte.sinal_cultura_pronta.connect(
            lambda x, y, v: self._widget_log.adicionar_evento(f"✨ Cultura pronta em ({x},{y})!")
        )
        ouvinte.sinal_aviso_gelo.connect(
            lambda x, y, s: self._widget_log.adicionar_evento(f"❄️ GELO em ({x},{y}) em {s}s!")
        )
        ouvinte.sinal_vitoria.connect(
            lambda t: self._widget_log.adicionar_evento(f"🏆 VITÓRIA! Temporada {t} concluída!")
        )
        ouvinte.sinal_derrota.connect(
            lambda t: self._widget_log.adicionar_evento(f"❌ Derrota na temporada {t}. Tentando novamente...")
        )

        # Rede → Chat
        ouvinte.sinal_chat_recebido.connect(self._widget_chat.adicionar_mensagem)
        ouvinte.sinal_desconectado.connect(self._on_desconectado)

        # Mapa → Acoes
        self._widget_mapa.sinal_celula_clicada.connect(self._widget_acoes.executar_para_celula)
        self._widget_mapa.sinal_celula_clicada.connect(
            lambda x, y, _: self._fazendeiro.solicita_cursor(x, y)
        )

        # Acoes → Rede
        self._widget_acoes.sinal_preparar.connect(self._fazendeiro.solicita_preparar)
        self._widget_acoes.sinal_pegar_semente.connect(self._fazendeiro.solicita_pegar_semente)
        self._widget_acoes.sinal_plantar.connect(
            lambda semente, x, y: self._fazendeiro.solicita_plantar(semente, x, y)
        )
        self._widget_acoes.sinal_colher.connect(
            lambda x, y: self._fazendeiro.solicita_colher(None, x, y)
        )

        # Chat → Rede
        self._widget_chat.sinal_enviar_mensagem.connect(self._fazendeiro.solicita_chat)

    def _on_resposta_sistema(self, status, mensagem, cultura):
        if status == "OK" and cultura is not None:
            self._widget_acoes.atualizar_semente_na_mao(cultura)
        elif "plantado" in mensagem.lower():
            self._widget_acoes.limpar_semente_na_mao()

    def _on_desconectado(self):
        self.statusBar().showMessage("Desconectado do servidor.")
        self._widget_log.adicionar_evento("Conexão encerrada.")
```

- [ ] **Passo 2: Atualizar `solicita_colher` em ClassFazendeiro para não exigir cultura**

Em `src/client/ClassFazendeiro.py`, substituir `solicita_colher`:

```python
    def solicita_colher(self, cultura, x, y):
        dados = {"comando": "COLHER", "x": x, "y": y}
        self.rede.manda_mensagem(json.dumps(dados))
```

- [ ] **Passo 3: Commit**

```bash
git add src/client/gui/JanelaPrincipal.py src/client/ClassFazendeiro.py
git commit -m "feat: integra WidgetHUD, WidgetEstoque e novos sinais em JanelaPrincipal"
```

---

## Tarefa 15: Teste de integração completo

- [ ] **Passo 1: Iniciar servidor**

```bash
cd src/server && python3 mainServer.py
```

Esperado:
```
--- INICIALIZANDO MUNDO ---
[mapa colorido no terminal]
--- CONECTANDO AS CAMADAS ---
[JOGO] Temporada 1 iniciada.
[REDE] Servidor escutando em 0.0.0.0:12345...
```

- [ ] **Passo 2: Iniciar dois clientes**

Em dois terminais separados:
```bash
python3 src/client/gui/main.py
```

Esperado em cada cliente:
- Dialog de nickname aparece
- Janela principal abre com HUD no topo mostrando timer regressivo
- Mapa colorido com tiles 32px
- Estoque global visível na coluna esquerda

- [ ] **Passo 3: Testar fluxo completo de plantio**

No Cliente 1:
1. Selecionar ação "🪵 Preparar Solo"
2. Clicar em um tile de terra — tile deve mudar para marrom escuro (🪵)
3. Selecionar "📦 Pegar Semente" + escolher Trigo no combo
4. Clicar em qualquer tile — painel "Na Mão" deve mostrar "🌾 Trigo"
5. Selecionar "🌱 Plantar"
6. Clicar no tile marrom preparado — tile deve mudar para 🌱

No Cliente 2: verificar que o tile mudou em tempo real.

Após ~20 segundos: o tile deve ganhar borda verde e mostrar 🌾 (trigo pronto).

- [ ] **Passo 4: Testar colheita e progresso**

1. Selecionar "✂️ Colher"
2. Clicar no tile com borda verde
3. Verificar: tile volta ao estado original, barra de progresso do HUD avança, estoque de trigo aumenta em 1

- [ ] **Passo 5: Testar posições dos jogadores**

Clicar em tiles diferentes em cada cliente — verificar que a inicial colorida do outro jogador aparece no mapa.

- [ ] **Passo 6: Commit final**

```bash
git add .
git commit -m "feat: implementacao completa do loop de jogo colaborativo com temporadas"
```
