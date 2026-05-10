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

    def exibe_matriz(self):
        """Exibe a matriz do mapa, mostrando o estado atual de cada posição."""
        for i in range(self.linha):
            for j in range(self.coluna):
                print(self.matriz[i][j], end=' ')
            print()

    def exibe_colorido(self):
        # Códigos ANSI expandidos para as plantações
        CORES = {
            0: '\033[42m',     # Terra: Verde Escuro
            1: '\033[44m',     # Água: Azul
            2: '\033[43m',     # Areia: Amarelo
            3: '\033[43;1m',   # Trigo: Amarelo Claro
            4: '\033[46m',     # Arroz: Ciano (Água com planta)
            6: '\033[42;1m',   # Cana na Terra: Verde Claro
            7: '\033[47m'      # Cana na Areia: Branco/Cinza Claro
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

    def processar_pacote_matriz(self, pacote_json):
        """
        Recebe um dicionário JSON contendo uma parte da matriz e a anexa ao buffer.
        Retorna a matriz completa quando todas as partes chegam, ou None caso contrário.
        """
        parte_atual = pacote_json.get("parte_atual")
        total_partes = pacote_json.get("total_partes")
        matriz_parcial = pacote_json.get("matriz_parcial")

        # Se for o pacote número 1, garantimos que o buffer está limpo
        if parte_atual == 1:
            self.matriz_temporaria = []
            self.partes_recebidas = 0

        # O método .extend() pega as linhas fatiadas e adiciona no final da nossa lista principal
        self.matriz_temporaria.extend(matriz_parcial)
        self.partes_recebidas += 1

        # Verifica se já montamos o quebra-cabeça inteiro
        if self.partes_recebidas == total_partes:
            print(f"Matriz montada com sucesso! Tamanho: {len(self.matriz_temporaria)} linhas.")
            
            # Salva a matriz pronta em uma variável final
            matriz_pronta = self.matriz_temporaria
            
            # Limpa o buffer para a próxima vez que o servidor enviar uma atualização
            self.matriz_temporaria = []
            self.partes_recebidas = 0
            
            return matriz_pronta
        
        # Se ainda faltam partes (ex: recebeu a 1 de 4), retorna None e espera a próxima
        return None
    
