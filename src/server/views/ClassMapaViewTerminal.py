class MapaView:
    """Responsável por pre-renderizar o mapa no terminal (Visão)."""
    
    @staticmethod
    def exibir_matriz(matriz):
        """Exibe a matriz do mapa em formato de números."""
        for linha in matriz:
            for val in linha:
                print(val, end=' ')
            print()

    @staticmethod
    def exibir_colorido(matriz):
        """Exibe a matriz do mapa com cores no terminal usando códigos ANSI."""
        CORES = {
            0: '\033[42m',      # Terra: Verde Escuro
            1: '\033[44m',      # Água: Azul
            2: '\033[43m',      # Areia: Amarelo
            3: '\033[48;5;94m', # Trigo: Marrom Claro
            4: '\033[46m',      # Arroz: Ciano
            6: '\033[48;5;154m',# Cana na Terra: Verde Claro
            7: '\033[48;5;154m' # Cana na Areia: Verde Claro
        }
        RESET = '\033[0m'
        
        print("\n=== Mapa Gerado ===")
        for linha in matriz:
            linha_visual = ""
            for val in linha:
                cor = CORES.get(val, '\033[40m') # Preto como fallback para erros
                linha_visual += f"{cor}   {RESET}"
            print(linha_visual)
        print("===================\n")