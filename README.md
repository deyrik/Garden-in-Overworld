# 🌱 Garden in Overworld

Jogo de fazenda multiplayer em tempo real, desenvolvido em Python com interface gráfica PyQt6. Jogadores se conectam a um servidor compartilhado e cooperam para cumprir as metas de colheita de cada temporada antes que o tempo acabe.

---

## O Jogo

O mapa é uma grade 20×20 gerada proceduralmente com três tipos de terreno — **terra**, **água** e **areia** — cada um determinando quais culturas podem ser plantadas ali. Todos os jogadores veem e agem sobre o mesmo mapa em tempo real.

### Culturas disponíveis

| Cultura  | Terreno necessário           | Tempo de crescimento |
|----------|------------------------------|----------------------|
| 🌾 Trigo  | Terra preparada + água próxima | 20 s               |
| 🌿 Arroz  | Água                         | 35 s                |
| 🎋 Cana   | Terra ou areia preparada     | 20 s                |
| 🌽 Milho  | Terra preparada              | 40 s                |
| 🥔 Batata | Qualquer solo preparado      | 25 s                |
| 🍅 Tomate | Terra preparada + água próxima | 50 s               |

### Temporadas

O jogo é dividido em 4 temporadas, cada uma com uma demanda de colheita e um timer regressivo. Se a meta não for atingida no tempo, a temporada recomeça.

| # | Nome       | Duração | Novidades                        |
|---|------------|---------|----------------------------------|
| 1 | Primavera  | 180 s   | Trigo, Arroz, Cana               |
| 2 | Verão      | 150 s   | + Milho                          |
| 3 | Outono     | 120 s   | + Batata                         |
| 4 | Inverno    | 90 s    | + Tomate + eventos de gelo 🧊    |

> No Inverno, células plantadas podem ser destruídas por geadas — fique de olho nos avisos e colha a tempo!

A demanda de cada temporada é **multiplicada pelo número de jogadores conectados**, então o desafio cresce conforme mais pessoas entram.

---

## Interface

```
┌──────────────────────────────────────────────────────────┐
│  🌱 Primavera — T1        META: ▓▓░░ ▓░░░   02:45       │  ← HUD
├──────────────┬─────────────────────────┬─────────────────┤
│ ESTOQUE      │                         │ LOG              │
│ 🌾 Trigo: 6  │   MAPA 20×20 clicável   │ ✅ Plantado      │
│ 🌿 Arroz: 3  │   (terra/água/areia)    │ ✨ Cultura pronta│
│ 🎋 Cana: 5  │                         │                  │
│              │                         ├─────────────────┤
│ AÇÃO         │                         │ CHAT             │
│ 🪵 Preparar  │                         │ Jogador1: oi!    │
│ 🌿 Plantar   │                         │ > [mensagem...] │
│ ✂️ Colher    │                         │                  │
│              │                         │                  │
│ Na mão: —    │                         │                  │
│ SEMENTES     │                         │                  │
│ 🌾 [1] Pegar │                         │ ● Jogador1       │
│ 🌿 [1] Pegar │                         │ ● Jogador2       │
└──────────────┴─────────────────────────┴─────────────────┘
```

### Funcionalidades da UI

- **Descoberta automática de servidor** — ao abrir o cliente, ele escaneia a rede local via UDP e lista os servidores disponíveis. É possível também conectar manualmente por IP
- **HUD** — exibe nome e número da temporada, timer regressivo e barras de progresso por cultura
- **Mapa interativo** — clique em uma célula para executar a ação selecionada (preparar, plantar ou colher)
- **Painel de ações** — selecione a ação e a semente antes de clicar no mapa; mostra a semente e quantidade atual na mão
- **Estoque** — quantidade de sementes disponíveis no servidor em tempo real
- **Chat** — comunicação entre jogadores em tempo real
- **Log de eventos** — registra todas as respostas do servidor e eventos do jogo
- **Cursores dos jogadores** — cada jogador aparece destacado no mapa com uma cor única
- **Toasts** — notificações temporárias para ações, erros e culturas prontas
- **Tutorial** — diálogo explicativo aparece automaticamente no início de cada temporada nova

---

## Requisitos

- Python 3.10 ou superior
- `make` (padrão em Linux/macOS)
- `gnome-terminal` ou `xterm` (para abrir múltiplos clientes de uma vez)

---

## Instalação e Execução

### 1. Clonar o repositório

```bash
git clone git@github.com:deyrik/Garden-in-Overworld.git
cd Garden-in-Overworld
```

### 2. Criar o ambiente virtual e instalar dependências

```bash
make install
```

Isso cria o `.venv` e instala o PyQt6 automaticamente.

### 3. Iniciar o servidor

```bash
make NS
```

### 4. Abrir um cliente (em outro terminal)

```bash
make NC
```

Uma tela de conexão será exibida. O cliente busca o servidor automaticamente na rede local. Escolha seu nickname e clique em **Entrar no mundo**.

### Atalhos do Makefile

| Comando        | O que faz                                        |
|----------------|--------------------------------------------------|
| `make install` | Cria o `.venv` e instala as dependências         |
| `make NS`      | Inicia um novo servidor                          |
| `make NC`      | Abre um novo cliente                             |
| `make 5C`      | Abre 5 clientes em terminais separados           |
| `make all_local` | Servidor + 5 clientes de uma só vez           |
| `make KS`      | Encerra o servidor (libera a porta 12345)        |
| `make clean`   | Remove os arquivos `__pycache__`                 |

> **Dica:** sempre suba o servidor antes de abrir os clientes.

---

## Como Jogar

1. **Preparar o solo** — selecione "🪵 Preparar solo" e clique em uma célula de terra ou areia
2. **Pegar sementes** — no painel de sementes, defina a quantidade e clique em "Pegar"
3. **Plantar** — selecione "🌿 Plantar" e clique na célula preparada compatível
4. **Aguardar** — a cultura cresce automaticamente; um aviso aparece quando está pronta
5. **Colher** — selecione "✂️ Colher" e clique na célula com a cultura pronta

Cumpra a demanda da temporada antes do timer chegar a zero para avançar. Coopere com outros jogadores para cobrir o mapa com eficiência!

---

## Multiplayer em rede local

O servidor anuncia sua presença via broadcast UDP. Qualquer máquina na mesma rede que abrir o cliente encontrará o servidor automaticamente na tela de conexão.

Para jogar entre máquinas diferentes:
1. Rode `make NS` na máquina que será o servidor
2. Nos outros computadores, rode `make NC` — o servidor aparecerá na lista automaticamente
3. Se não aparecer, insira o IP manualmente na tela de conexão

---

## Arquitetura

```
Garden-in-Overworld/
├── src/
│   ├── server/
│   │   ├── mainServer.py          # Ponto de entrada do servidor
│   │   ├── ClassServidorTCP.py    # Gerencia conexões TCP dos clientes
│   │   ├── ClassAnunciadorUDP.py  # Anuncia o servidor via broadcast UDP
│   │   ├── ClassControlador.py   # Lógica central do jogo
│   │   ├── ClassMapa.py           # Geração e estado do mapa
│   │   ├── ClassTemporada.py      # Timer e demanda por temporada
│   │   ├── ClassEstoque.py        # Controle de sementes disponíveis
│   │   └── ClassUser.py           # Gerenciamento de slots de jogadores
│   └── client/
│       ├── ClassTCPCliente.py     # Camada de rede TCP
│       ├── ClassFazendeiro.py     # Comandos do jogo (plantar, colher...)
│       ├── ClassMapa.py           # Estado local do mapa
│       ├── ClassOuvinte.py        # Thread de escuta do servidor
│       └── gui/
│           ├── main.py            # Ponto de entrada do cliente
│           ├── JanelaPrincipal.py # Janela principal do jogo
│           ├── DialogConexao.py   # Tela de login e descoberta de servidor
│           ├── DialogTutorial.py  # Tutorial por temporada
│           ├── WidgetMapa.py      # Grade 20×20 interativa
│           ├── WidgetHUD.py       # Timer e barras de progresso
│           ├── WidgetAcoes.py     # Seleção de ação e sementes
│           ├── WidgetEstoque.py   # Contadores de sementes
│           ├── WidgetChat.py      # Chat entre jogadores
│           ├── WidgetLog.py       # Log de eventos
│           └── estilos.py         # Paleta de cores e stylesheet global
```

O servidor utiliza threads para atender múltiplos clientes simultaneamente, com broadcast para sincronizar o estado do mapa entre todos em tempo real. A comunicação é feita via JSON sobre TCP, com delimitador `\n`.
