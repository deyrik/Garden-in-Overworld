# TIPOS DE TERRENO:
# 0- terra  
# 1- agua      
# 2- areia

# TIPOS DE SEMENTE:
# 3- trigo ------------------(planta em terra)
# 4- arroz ------------------(planta so em agua)            
# 5- cana de acucar ---------(planta em terra ou areia)
#   - 6- cana de acucar plantada na terra
#   - 7- cana de acucar plantada na areia


class Mapa:
    def __init__(self, linha=20, coluna=20):
        self.linha = linha
        self.coluna = coluna
        self.matriz = [[0 for _ in range(self.coluna)] 
                           for _ in range(self.linha)]
 
    def atualizar_matriz(self, nova_matriz):
        """Atualiza o mapa com a matriz inteira recebida do servidor."""
        if not nova_matriz:
            return
            
        self.matriz = nova_matriz
        # Atualiza o tamanho caso o servidor mande um mapa maior/menor
        self.linha = len(nova_matriz)
        self.coluna = len(nova_matriz[0])

    def exibe_matriz(self):
        """Exibe estado atual da matriz do mapa por numeros"""
        for i in range(self.linha):
            for j in range(self.coluna):
                print(self.matriz[i][j], end=' ')
            print()

    def exibe_colorido(self):
        """Exibe a matriz colorida no terminal usando ANSI."""
        CORES = {
            0: '\033[42m',     # Terra: Verde Escuro
            1: '\033[44m',     # Água: Azul
            2: '\033[43m',     # Areia: Amarelo
            3: '\033[43;1m',   # Trigo: Amarelo Claro
            4: '\033[46m',     # Arroz: Ciano
            6: '\033[42;1m',   # Cana na Terra: Verde Claro
            7: '\033[47m'      # Cana na Areia: Branco
        }
        RESET = '\033[0m'
        
        for linha in self.matriz:
            linha_visual = ""
            for val in linha:
                cor = CORES.get(val, '\033[40m') 
                linha_visual += f"{cor}   {RESET}"
            print(linha_visual)
        print("\n")