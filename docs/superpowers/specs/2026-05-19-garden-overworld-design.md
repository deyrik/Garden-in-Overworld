# Design: Garden in Overworld — Jogabilidade e Frontend

**Data:** 2026-05-19  
**Branch:** feature/frontend-pyqt6

---

## Visão Geral

Garden in Overworld é um jogo de farming multiplayer colaborativo sobre TCP. O objetivo desta spec é adicionar:

1. **Um loop de jogo com sentido** — temporadas com meta coletiva
2. **Mecânica de plantio em 3 passos** — preparar solo → pegar semente → plantar
3. **Crescimento em tempo real** — servidor gerencia timers e avisa clientes
4. **Progressão entre temporadas** — dificuldade crescente, novas culturas
5. **Visual renovado** — tiles 32px coloridos, HUD de temporada, posição dos jogadores

---

## Loop de Jogo

### Fluxo de uma Temporada

1. Servidor inicia temporada → broadcast `INICIO_TEMPORADA` com demanda e timer
2. Jogadores coordenam via chat quem planta o quê
3. Cada jogador executa: **preparar solo → pegar semente do estoque global → plantar**
4. Servidor inicia timer de crescimento por célula
5. Servidor faz broadcast `CULTURA_PRONTA` quando o timer de uma célula esgota
6. Jogadores colhem as culturas prontas → progresso coletivo avança
7. Se meta atingida antes do timer: vitória → próxima temporada
8. Se timer esgota: derrota → mesma temporada reinicia

### Objetivo Coletivo

Cada temporada define uma **demanda aleatória** por cultura (ex: "8 trigos, 4 arrozes, 6 canas"). A demanda é proporcional ao número de jogadores conectados e ao índice da temporada.

---

## Mecânica de Plantio em 3 Passos

### Passo 1 — Preparar Solo

- Ação: jogador seleciona "Preparar Solo" e clica em um tile
- Válido em: terra (0), areia (2) — água não precisa de preparação
- Comando: `{"comando": "PREPARAR", "x": N, "y": N}`
- Resultado: tile muda para `solo_preparado_terra` (8) ou `solo_preparado_areia` (9)
- Broadcast: `ATUALIZAR_CELULA` para todos os clientes

### Passo 2 — Pegar Semente do Estoque

- Ação: jogador seleciona "Pegar Semente", escolhe a cultura e confirma
- Comando: `{"comando": "PEGAR_SEMENTE", "cultura": "trigo"}`
- Servidor verifica estoque global → decrementa → responde OK ou ERRO
- Cliente armazena localmente "na mão": qual semente e quantidade (sempre 1)
- Broadcast: `ATUALIZAR_ESTOQUE` com novo total para todos

### Passo 3 — Plantar

- Ação: jogador (com semente na mão) clica em tile compatível e preparado
- Compatibilidade:
  - Trigo (3): só em `solo_preparado_terra` (8)
  - Arroz (4): só em água (1) — não precisa de preparação
  - Cana (5): `solo_preparado_terra` (8) ou `solo_preparado_areia` (9)
  - Milho (10): só em `solo_preparado_terra` (8)
  - Batata (11): qualquer solo preparado (8 ou 9)
  - Tomate (12): `solo_preparado_terra` (8) com água no raio de 2 blocos
- Comando: `{"comando": "PLANTAR", "semente": N, "x": N, "y": N}`
- Servidor valida compatibilidade, aplica, inicia timer de crescimento
- Broadcast: `ATUALIZAR_CELULA` + `INICIO_CRESCIMENTO` com tempo restante

### Colheita

- Ação: jogador seleciona "Colher" e clica em tile com cultura pronta
- Servidor valida estado (`PRONTA`), remove planta, incrementa progresso coletivo
- Se dois jogadores tentam colher a mesma célula simultaneamente, o primeiro vence (race condition natural do servidor single-threaded por ação)
- Broadcast: `ATUALIZAR_CELULA` + `ATUALIZAR_PROGRESSO`
- Colheita repõe sementes no estoque global (mesma quantidade colhida)

---

## Estoque Global de Sementes

- Gerenciado exclusivamente no servidor (`ClassControlador`)
- Inicializado no início de cada temporada com valores proporcionais à demanda
- Valores iniciais (Temporada 1): Trigo 30, Arroz 20, Cana 30
- Broadcast `ATUALIZAR_ESTOQUE` enviado a todos após cada `PEGAR_SEMENTE` ou colheita
- Aviso automático quando qualquer semente cai abaixo de 5: `ALERTA_ESTOQUE`

---

## Crescimento em Tempo Real

O servidor mantém um dicionário `{(x,y): timer_thread}` por partida. Ao plantar:

1. Servidor inicia uma thread/timer com o tempo da cultura
2. Quando o timer esgota, servidor muda estado da célula para `PRONTA` e faz broadcast `CULTURA_PRONTA` com coordenadas
3. Clientes atualizam o tile visualmente (borda verde brilhante)

### Tempos de Crescimento

| Cultura | Tempo | Terreno       |
|---------|-------|---------------|
| Cana    | 15s   | terra/areia   |
| Trigo   | 20s   | terra         |
| Batata  | 25s   | qualquer      |
| Arroz   | 35s   | água          |
| Milho   | 40s   | terra         |
| Tomate  | 50s   | terra + água  |

---

## Progressão de Temporadas

| Temporada | Nome      | Timer | Culturas disponíveis          | Sementes | Evento especial                       |
|-----------|-----------|-------|-------------------------------|----------|---------------------------------------|
| 1         | Primavera | 3:00  | Trigo, Arroz, Cana            | Abundantes | —                                   |
| 2         | Verão     | 2:30  | + Milho                       | Moderadas  | —                                   |
| 3         | Outono    | 2:00  | + Batata                      | Escassas   | Reposição só via colheita            |
| 4+        | Inverno   | 1:30  | + Tomate                      | Mínimas    | Evento de gelo avisado com 10s       |

### Evento de Gelo (Temporada 4+)

- A cada 30s o servidor sorteia uma célula plantada
- Broadcast `AVISO_GELO` com coordenadas e contagem regressiva de 10s
- Se não colhida em 10s: `CULTURA_DESTRUIDA` — tile volta ao estado anterior ao plantio
- Jogadores têm tempo de reação; não é punitivo, é tenso

### Vitória e Derrota

- **Vitória:** meta atingida antes do timer → broadcast `VITORIA` → nova temporada após 5s
- **Derrota:** timer esgota → broadcast `DERROTA` → mesma temporada reinicia após 5s com estoque reposto

---

## Novos Estados de Tile

| Valor | Significado                  |
|-------|------------------------------|
| 0     | terra                        |
| 1     | água                         |
| 2     | areia                        |
| 8     | solo preparado (terra)       |
| 9     | solo preparado (areia)       |
| 3     | trigo crescendo              |
| 4     | arroz crescendo              |
| 6     | cana crescendo (terra)       |
| 7     | cana crescendo (areia)       |
| 10    | milho crescendo              |
| 11    | batata crescendo             |
| 12    | tomate crescendo             |
| 13    | trigo pronto                 |
| 14    | arroz pronto                 |
| 15    | cana pronta                  |
| 16    | milho pronto                 |
| 17    | batata pronta                |
| 18    | tomate pronto                |

---

## Novos Comandos do Protocolo (JSON + `\n`)

### Cliente → Servidor

```json
{"comando": "PREPARAR", "x": 3, "y": 7}
{"comando": "PEGAR_SEMENTE", "cultura": 3}
{"comando": "PLANTAR", "semente": 3, "x": 3, "y": 7}
{"comando": "COLHER", "x": 3, "y": 7}
```

### Servidor → Clientes (broadcasts)

```json
{"comando": "INICIO_TEMPORADA", "temporada": 1, "nome": "Primavera", "timer": 180, "demanda": {"3": 8, "4": 4, "6": 6}}
{"comando": "ATUALIZAR_ESTOQUE", "estoque": {"3": 18, "4": 3, "6": 22}}
{"comando": "CULTURA_PRONTA", "x": 3, "y": 7, "cultura": 13}
{"comando": "ATUALIZAR_PROGRESSO", "progresso": {"3": 4, "4": 2, "6": 4}, "demanda": {"3": 8, "4": 4, "6": 6}}
{"comando": "TICK_TIMER", "restante": 107}
{"comando": "AVISO_GELO", "x": 5, "y": 9, "segundos": 10}
{"comando": "CULTURA_DESTRUIDA", "x": 5, "y": 9, "valor_anterior": 2}
{"comando": "VITORIA", "temporada": 1}
{"comando": "DERROTA", "temporada": 1}
{"comando": "ALERTA_ESTOQUE", "cultura": 4, "restante": 3}
```

---

## Frontend — Mudanças na Interface

### WidgetMapa

- Tiles: `QLabel` com fundo colorido 32×32px (substituir `QPushButton`)
- Paleta de cores por terreno: verde escuro (terra), azul (água), bege/dourado (areia), marrom escuro (preparado)
- Emoji centralizado no label, font-size 18px
- Tiles com cultura pronta: borda verde brilhante (`border: 2px solid #00ff88`)
- Posição do jogador: letra inicial colorida sobreposta ao tile (QLabel sobre QLabel)

### HUD de Temporada (novo widget: `WidgetHUD`)

- Faixa no topo da janela
- Exibe: nome da temporada, timer regressivo (vermelho quando < 30s), barras de progresso por cultura

### WidgetPainel Esquerdo

- **Estoque Global:** contadores por cultura, aviso vermelho quando baixo
- **Na Mão:** mostra semente atual do jogador
- **Ações:** 4 botões (Preparar Solo, Pegar Semente, Plantar, Colher) — só um ativo por vez
- **Jogadores:** lista com ponto colorido por jogador

### WidgetLog → WidgetEventos

- Renomear para deixar claro que mostra eventos do jogo, não só respostas
- Colorir por tipo: verde para culturas prontas, vermelho para alertas, cor do jogador para ações

### WidgetChat

- Sem mudanças funcionais

---

## Conceitos de SD Demonstrados

| Conceito                        | Onde aparece                                              |
|---------------------------------|-----------------------------------------------------------|
| Estado compartilhado            | Estoque de sementes, progresso coletivo                   |
| Concorrência controlada         | Dois jogadores tentam colher o mesmo tile                 |
| Máquina de estados distribuída  | Servidor é fonte da verdade para estado de cada célula    |
| Broadcasts temporizados         | `CULTURA_PRONTA`, `TICK_TIMER`, `AVISO_GELO`              |
| Sincronização de evento global  | `INICIO_TEMPORADA`, `VITORIA`, `DERROTA`                  |

---

## Fora de Escopo

- Autenticação de jogadores
- Persistência entre sessões
- Mapa maior que 20×20
- Sons ou animações CSS
