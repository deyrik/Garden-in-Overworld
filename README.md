# Garden in Overworld — Sistemas Distribuídos

Repositório organizado com as duas implementações do trabalho prático da disciplina de Sistemas Distribuídos, além da documentação e especificações.

## Estrutura do Repositório

```text
.
├── sockets/                   # Implementação usando Sockets TCP (branch feature/front-end)
├── middleware/                # Implementação usando Middleware Pyro5 (branch feature/middleware)
└── DOCS/
    ├── Especificacao/         # Enunciados e especificações do trabalho (Partes 1 a 4)
    └── Artefatos/
        ├── sockets/           # Relatórios e diagramas da versão com Sockets
        └── middleware/        # Relatórios e diagramas da versão com Middleware
```

## Como Executar

Cada implementação possui seu próprio ambiente virtual (`.venv`), `makefile` e `README.md` com instruções detalhadas.

### Versão com Sockets (`sockets/`)

Consulte [sockets/README.md](sockets/README.md) para detalhes completos.

```bash
cd sockets
make NS   # Inicia o servidor
make NC   # Inicia um cliente (em outro terminal)
```

### Versão com Middleware Pyro5 (`middleware/`)

Consulte [middleware/README.md](middleware/README.md) para detalhes completos.

```bash
cd middleware
make NS   # Inicia o Name Server Pyro5 e o servidor do jogo
make NC   # Inicia um cliente (em outro terminal)
```
