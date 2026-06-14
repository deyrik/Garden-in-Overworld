# INFOS

## Clonando o repositório GIT

```bash
git clone git@github.com:deyrik/Garden-in-Overworld.git
cd Garden-in-Overworld
```

## Instalação e Gerenciamento (Local)

### Criar a pasta venv

Para isolar as bibliotecas do projeto, crie um ambiente virtual executando:

```bash
python3 -m venv .venv
```

Isso irá criar uma pasta `.venv` no diretório atual com todos os arquivos necessários para o ambiente virtual.

### Ativar o venv

Para ativar o ambiente virtual, execute:

```bash
source .venv/bin/activate
```

Após ativar, você verá `(.venv)` no início da sua linha de comando, indicando que o ambiente está ativo.

### Desativar o venv

Para sair do ambiente virtual, execute:

```bash
deactivate
```

O prefixo `(.venv)` desaparecerá, retornando o terminal ao ambiente Python padrão do seu sistema operacional.

## Configuração Automática no VSCode

Para que o VSCode ative o `.venv` automatically toda vez que você abrir o terminal:

1. Pressione `Ctrl + ,` para abrir as configurações.
2. Na barra de busca, digite: `python terminal activate`.
3. Marque a caixa de seleção: **Python › Terminal: Activate Environment**.

## Dependências Instaladas

Com o ambiente virtual ativado, instale as dependências da interface gráfica:

```bash
pip install --upgrade pip
pip install PyQt6
pip install Pyro5
```

## Execução Local (Makefile ou Manual)

**Atenção:** Recomenda-se executar o servidor antes, e só depois instanciar quantos clientes desejar.

### 1. Inicializando o Servidor

* **Com `.venv` ativado (Manual):**
    ```bash
    python src/server/mainServer.py
    ```
* **Usando Makefile (make New Server):**
    ```bash
    make NS
    ```
* **Sem `.venv` (Usando o Python global da máquina):**
    ```bash
    python3 src/server/mainServer.py
    ```

### 2. Inicializando os Clientes

É possível criar vários clientes para jogar em multiplayer. Inicie-os em terminais distintos após o servidor já estar rodando.

* **Com `.venv` ativado (Manual):**
    ```bash
    python src/client/mainCliente.py
    ```
* **Usando Makefile (make New Client):**
    ```bash
    make NC
    ```
* **Criar 5 terminais e instanciar 5 clientes simultaneamente:**
    ```bash
    make 5C
    ```
* **Sem `.venv` (Necessário ter a biblioteca PyQt6 instalada globalmente):**
    ```bash
    python3 src/client/mainCliente.py
    ```
### 3. Fazendo Todo Processo Automatico:

* **É possível instaciar um novo servidor, e 5 clientes com apenas um comando :**


    ```bash
    make all_local
    ```

## Limpeza

Para limpar o diretório e remover o pré-cache de arquivos compilados do Python (`__pycache__`), execute:

```bash
make clean 
```

---

