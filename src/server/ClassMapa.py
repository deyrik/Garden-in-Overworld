import random

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

class Mapa:
    def __init__(self, linha=20, coluna=20):
        self.linha = linha
        self.coluna = coluna
        # Cria a matriz preenchida com 0 usando List Comprehension , 0 é terra
        self.matriz = [[0 for i in range(self.coluna)] for j in range(self.linha)]

    # RF01 ----------------------------------------------------------------------------------------

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

    #é bom fazer na ordem oasis -> rios -> poças
    #Para evitar que os elementros se sobreponham,
    def inicializa_matriz(self):
        """constroi a matriz do mapa, onde cada posição é inicializada com o valor 0 (terra)."""
        for i in range(self.linha):
            for j in range(self.coluna):
                self.matriz[i][j] = 0 #inicializa a matriz com o valor 0, terra

    def gerar_oasis(self, num_oasis=6):
        """
        Gera oásis aleatórios. Um oásis é um tile de água (1) cercado por areia (2).
        """
        for _ in range(num_oasis):
            # Sorteia o centro do oásis.
            # Limitamos de 1 até tamanho-2 para não tentar colocar areia fora da matriz
            r = random.randint(1, self.linha - 2)
            c = random.randint(1, self.coluna - 2)

            # Centro vira água
            self.matriz[r][c] = 1

            # Percorre os vizinhos (cima, baixo, lados e diagonais)
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    # Ignora o centro (pois já é água)
                    if dr == 0 and dc == 0:
                        continue

                    # Só coloca areia se a posição já não for água (para não apagar rios ou outros oásis)
                    if self.matriz[r + dr][c + dc] != 1:
                        self.matriz[r + dr][c + dc] = 2

    def gerar_rio(self, direcao='vertical', num_nascentes=3, prob_areia=0.4):
        """
        Gera rios com possibilidade de ter areia nas margens.
        prob_areia: float de 0.0 a 1.0 indicando a chance de gerar areia ao lado do rio.
        """
        for _ in range(num_nascentes):
            if direcao == 'vertical':
                linha_atual = 0
                coluna_atual = random.randint(0, self.coluna - 1)

                while linha_atual < self.linha:
                    self.matriz[linha_atual][coluna_atual] = 1

                    # --- Lógica de gerar areia nas margens ---
                    # Verificamos os lados (esquerda e direita)
                    for dc in [-1, 1]:
                        vizinho_c = coluna_atual + dc
                        # Verifica se o vizinho não saiu do mapa
                        if 0 <= vizinho_c < self.coluna:
                            # Sorteia a chance E garante que não vai sobrescrever outra água
                            if self.matriz[linha_atual][vizinho_c] != 1 and random.random() <= prob_areia:
                                self.matriz[linha_atual][vizinho_c] = 2
                    # -----------------------------------------

                    movimento = random.choices([-1, 0, 1], weights=[1, 3, 1])[0]
                    coluna_atual += movimento
                    coluna_atual = max(0, min(self.coluna - 1, coluna_atual))
                    linha_atual += 1

            elif direcao == 'horizontal':
                linha_atual = random.randint(0, self.linha - 1)
                coluna_atual = 0

                while coluna_atual < self.coluna:
                    self.matriz[linha_atual][coluna_atual] = 1

                    # --- Lógica de gerar areia nas margens ---
                    # Verificamos em cima e embaixo
                    for dr in [-1, 1]:
                        vizinho_r = linha_atual + dr
                        if 0 <= vizinho_r < self.linha:
                            if self.matriz[vizinho_r][coluna_atual] != 1 and random.random() <= prob_areia:
                                self.matriz[vizinho_r][coluna_atual] = 2
                    # -----------------------------------------

                    movimento = random.choices([-1, 0, 1], weights=[1, 3, 1])[0]
                    linha_atual += movimento
                    linha_atual = max(0, min(self.linha - 1, linha_atual))
                    coluna_atual += 1

    def gerar_pocas(self, num_pocas=10, tamanho_maximo=4):
        """
        Gera pequenas poças de água orgânicas pelo mapa.
        num_pocas: quantidade de poças para tentar gerar.
        tamanho_maximo: número máximo de tiles que uma poça pode ocupar.
        """
        for _ in range(num_pocas):
            # Escolhe um ponto de origem aleatório para a poça
            linha = random.randint(0, self.linha - 1)
            coluna = random.randint(0, self.coluna - 1)

            # Sorteia qual será o tamanho desta poça específica
            tamanho_poca = random.randint(1, tamanho_maximo)

            for _ in range(tamanho_poca):
                # Só cria a poça se o local for grama (0).
                # Isso evita que a poça apague a areia de um rio ou de um oásis.
                if self.matriz[linha][coluna] == 0:
                    self.matriz[linha][coluna] = 1

                # A água se espalha para um dos lados ortogonais (Cima, Baixo, Esquerda, Direita)
                dr, dc = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                linha += dr
                coluna += dc

                # Garante que a poça não tente se espalhar para fora do mapa
                linha = max(0, min(self.linha - 1, linha))
                coluna = max(0, min(self.coluna - 1, coluna))

    def gerar_mapa_aleatorio(self, num_oasis=6,
                             direcao='vertical', num_nascentes=3, prob_areia=0.4,
                             num_pocas=10,tamanho_maximo_pocas=4):
        """Gera um mapa completo com oásis, rios e poças."""
        #self.inicializa_matriz()
        self.gerar_oasis(num_oasis)
        self.gerar_rio(direcao, num_nascentes, prob_areia)
        self.gerar_pocas(num_pocas, tamanho_maximo_pocas)

    def exibe_matriz(self):
        """Exibe a matriz do mapa, mostrando o estado atual de cada posição."""
        for i in range(self.linha):
            for j in range(self.coluna):
                print(self.matriz[i][j], end=' ')
            print()

    def exibe_colorido(self):
        # Códigos ANSI expandidos para as plantações
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
        RESET = '\033[0m'

        print("\n=== Mapa Gerado ===")
        for linha in self.matriz:
            linha_visual = ""
            for val in linha:
                cor = CORES.get(val, '\033[40m') # Preto como fallback para erros
                linha_visual += f"{cor}   {RESET}"
            print(linha_visual)
        print("===================\n")

    # RF05 ----------------------------------------------------------------------------------------
    def valida_posicao(self, x, y):
        """Verifica se as coordenadas (x, y) estão dentro dos limites da matriz."""
        return (0 <= x < self.linha and 0 <= y < self.coluna) # se estiverem retorna true

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

    def verifica_fertilidade(self, x, y, acao: int):
        """
        Verifica se a posição (x, y) está a um raio de até 2 blocos da água.
        O uso de max() e min() garante que a busca não ultrapasse os limites da matriz.
        """
        # Se for arroz, a própria posição já é água (passa direto na compatibilidade)
        if self.matriz[x][y] == 1:
            return True

        # Define a janela de busca (um quadrado de 5x5 ao redor do ponto)
        # movimento do cavalo em xadrez, 1 bloco pra um lado e 2 blocos pra outro lado
        linha_inicio = max(0, x - 2)
        linha_fim = min(self.linha - 1, x + 2)
        coluna_inicio = max(0, y - 2)
        coluna_fim = min(self.coluna - 1, y + 2)

        for i in range(linha_inicio, linha_fim + 1):
            for j in range(coluna_inicio, coluna_fim + 1):
                if self.matriz[i][j] == 1:
                    return True # Encontrou água no raio de 2 blocos

        return False

    def valida_acao(self, x, y, acao: int):
        if not self.valida_posicao(x, y):
            print("Ação inválida: Posição fora do mapa.")
            return False

        if not self.verifica_compatibilidade(x, y, acao):
            print("Ação inválida: Solo incompatível.")
            return False

        if not self.verifica_fertilidade(x, y, acao):
            print("Ação inválida: Longe da água.")
            return False

        print("Ação válida: Pode plantar nessa posição.")
        return True

    # RF04 ----------------------------------------------------------------------------------------
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

    def maturar(self, x, y):
        """Transiciona a célula de 'crescendo' para 'pronta'. Retorna True se bem-sucedido."""
        cultura = self.matriz[x][y]
        if cultura not in MAPA_CRESCENDO_PARA_PRONTA:
            return False
        self.matriz[x][y] = MAPA_CRESCENDO_PARA_PRONTA[cultura]
        return True

    # RF06 ----------------------------------------------------------------------------------------
    def colher(self, x, y):
        """Colhe a cultura pronta em (x, y). Retorna (True, tile_pronto) ou (False, None)."""
        if not self.valida_posicao(x, y):
            return False, None
        tile = self.matriz[x][y]
        if tile not in MAPA_PRONTA_PARA_BASE:
            return False, None
        self.matriz[x][y] = MAPA_PRONTA_PARA_BASE[tile]
        return True, tile
    #----------------------------------------------------------------------------------------------

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
