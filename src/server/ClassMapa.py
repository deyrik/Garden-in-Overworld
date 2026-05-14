import random

# 0- terra      # 3- trigo ------------------(planta em terra)
# 1- agua       # 4- arroz ------------------(planta so em agua)
# 2- areia      # 5- cana de acucar ---------(planta em terra ou areia)
                    #* 6- cana de acucar plantada na terra
                    #* 7- cana de acucar plantada na areia

class Mapa:
    def __init__(self, linha=20, coluna=20):
        self.linha = linha
        self.coluna = coluna
        # Cria a matriz preenchida com 0 usando List Comprehension , 0 é terra
        self.matriz = [[0 for i in range(self.coluna)] for j in range(self.linha)]

    # RF01 ----------------------------------------------------------------------------------------
 
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
            0: '\033[42m',      # Terra: Verde Escuro
            1: '\033[44m',      # Água: Azul
            2: '\033[43m',      # Areia: Amarelo
            3: '\033[48;5;94m', # Trigo: Marrom Claro
            4: '\033[46m',      # Arroz: Ciano (Água com planta)
            6: '\033[48;5;154m',# Cana na Terra: Verde Claro
            7: '\033[48;5;154m' # Cana na Areia: Verde Claro (mesma cor para diferenciar do trigo)
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
        """Verifica se a ação é compatível com o tipo de terreno na posição (x, y)."""

        if acao == 3 and self.matriz[x][y] != 0:            #trigo pode ser plantado apenas em terra
            return False
        elif acao == 4 and self.matriz[x][y] != 1:          #arroz pode ser plantado apenas em agua
            return False
        elif acao == 5 and self.matriz[x][y] not in [0, 2]: #cana de acucar pode ser plantada em terra ou areia
            return False
        return True

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
        """Realiza a ação de plantar o item correspondente ao valor da ação na posição (x, y) da matriz."""
        if cultura not in [3, 4, 5]:
            print("Ação inválida: Cultura inválida para plantio.")
            return False

        if self.valida_acao(x, y, cultura):
            if cultura == 5 and self.matriz[x][y] == 0:       #cana de acucar plantada na terra
                self.matriz[x][y] = 6
            elif cultura == 5 and self.matriz[x][y] == 2:     #cana de acucar plantada na areia
                self.matriz[x][y] = 7
            else:   
                self.matriz[x][y] = cultura                   #planta o item na matriz
            return True
        print("Ação inválida: Não é possível plantar nessa posição.")
        return False
    
    # RF06 ----------------------------------------------------------------------------------------
    def colher (self, x, y, cultura: int):
        """Realiza a ação de colher o item correspondente ao valor da ação na posição (x, y) da matriz."""

        if not self.valida_posicao(x, y):
            print("Ação inválida: Posição fora do mapa.")
            return False

        # Para colheita, o cliente deve pedir 3 (trigo), 4 (arroz) ou 5 (cana).
        # Aceitamos 6/7 por compatibilidade (cana plantada em terra/areia).
        if cultura not in [3, 4, 5, 6, 7]:
            print("Ação inválida: O item a ser " \
            "colhido não é uma cultura válida.")
            return False

        valor_atual = self.matriz[x][y]

        # trigo
        if cultura == 3:
            if valor_atual != 3:
                print("Ação inválida: Não há trigo nessa posição.")
                return False
            self.matriz[x][y] = 0
            return True

        # arroz
        if cultura == 4:
            if valor_atual != 4:
                print("Ação inválida: Não há arroz nessa posição.")
                return False
            self.matriz[x][y] = 1
            return True

        # cana (pedido como 5, ou legado 6/7)
        if cultura in [5, 6, 7]:
            if valor_atual == 6:
                self.matriz[x][y] = 0
                return True
            if valor_atual == 7:
                self.matriz[x][y] = 2
                return True
            print("Ação inválida: Não há cana nessa posição.")
            return False

        print("Ação inválida: Não é possível colher nessa posição.")
        return False
    #----------------------------------------------------------------------------------------------

#teste
if __name__ == "__main__":
    mapa = Mapa()
    mapa.exibe_matriz()

    mapa.gerar_oasis(num_oasis=3)
    mapa.exibe_colorido()

    mapa.gerar_rio(direcao='vertical', num_nascentes=3)
    mapa.exibe_colorido()

    mapa.gerar_pocas(num_pocas=10, tamanho_maximo=4)
    mapa.exibe_colorido()

    print(mapa.matriz)
