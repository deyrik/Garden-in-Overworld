# Garden-in-Overworld (TP – Sistemas Distribuídos – Parte 3)

Implementação cliente/servidor usando **Sockets TCP** e troca de mensagens **JSON delimitadas por `\\n`**.

## Requisitos (alvo do TP)

- Ubuntu 22.04
- Python **3.10+**
- (Obrigatório no TP) **PyQt6** para interface gráfica
- (Obrigatório no TP) **SQLite** com arquivo `.db` já populado
- (Obrigatório no TP) **Makefile** ou **Docker** para execução fácil

## Rodando (estado atual do repositório)

Este repositório contém a versão terminal (ANSI) do mapa e comunicação por TCP.

### 1) Servidor

```bash
cd src/server
python3 mainServer.py
```

Servidor sobe em `localhost:12345`.

### 2) Cliente (exemplo)

Em outro terminal:

```bash
cd src
python3 client/mainCliente.py
```

### 3) Cliente com interface (PyQt6)

Instale o PyQt6 (Ubuntu 22.04):

```bash
python3 -m pip install PyQt6
```

Execute:

```bash
make run-gui
```

## Protocolo de mensagens (resumo)

Todas as mensagens são JSON e **terminam com `\\n`**.

### Cliente → Servidor

- `{"comando":"NICKNAME","nome":"..."}`
- `{"comando":"MATRIZ"}`
- `{"comando":"PLANTAR","semente":3,"x":1,"y":2}`
- `{"comando":"COLHER","cultura":3,"x":1,"y":2}`
- `{"comando":"SAIR"}`

### Servidor → Cliente

- `{"comando":"RESPOSTA","status":"OK|ERRO","mensagem":"..."}`
- `{"comando":"ATUALIZAR_MAPA","matriz":[...]}`
- `{"comando":"ATUALIZAR_CELULA","x":1,"y":2,"valor":3}` (broadcast)
- `{"comando":"SAIR","status":"OK","mensagem":"Desconectando..."}` (encerra a conexão)

## Checklist / Tarefas restantes (Parte 3)

Para atender integralmente ao enunciado da **Parte 3**, ainda falta:

1. Implementar GUI obrigatória em **PyQt6**
   - (Feito - MVP) `src/client/gui.py` com grid + ações básicas + thread de rede
   - (Falta) refinar UX: seleção por clique, legenda de cores, validações melhores

2. Adicionar **SQLite (arquivo)** já populado
   - Definir o que persistir (ex.: usuários, inventário, histórico de ações, mapa inicial)
   - Criar `*.db` versionado no repositório (ou gerado automaticamente no `make init`)
   - Garantir que o SD “funcione de primeira” sem configuração manual

3. Orquestração com **Makefile** e/ou **Docker**
   - `make run-server`, `make run-client`
   - (Opcional recomendado) `docker compose up` com servidor e múltiplos clientes

4. Documentação do TP (PDF)
   - Componentes (cliente/servidor), responsabilidades e permissões
   - Mensagens: campos, exemplos e fluxos
   - Uso de threads e (se necessário) sincronização
   - Conclusão: dificuldades com sockets e como contornar

5. Robustez e qualidade
   - Validar parâmetros (`x,y,semente,cultura`) e erros de parsing
   - Tratar desconexões/queda de rede
   - (Se múltiplos clientes) proteger acesso concorrente ao estado do jogo (lock) ou documentar limitações
