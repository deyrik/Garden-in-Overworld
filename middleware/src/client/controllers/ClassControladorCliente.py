from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer

class ControladorCliente:
    """Orquestra a comunicação entre a Interface Gráfica e o Proxy RMI."""
    
    def __init__(self, janela, fazendeiro):
        self.janela = janela
        self.fazendeiro = fazendeiro
        
        # Cria um timer para atualizar o mapa periodicamente (Polling)
        self.timer_atualizacao = QTimer()
        self.timer_atualizacao.timeout.connect(self.atualizar_mapa_periodicamente)

    def iniciar_conexoes(self):
        """Liga os cliques da tela às funções do RMI."""
        self.janela.matrix.cellClicked.connect(self.lidar_com_clique)
        
        # Puxa o mapa pela primeira vez e liga o timer (1 segundo = 1000ms)
        self.atualizar_mapa_periodicamente()
        self.timer_atualizacao.start(1000) 

    def lidar_com_clique(self, x, y):
        """Traduz o clique direto numa chamada de método RMI."""
        modo = self.janela.current_mode()
        
        if modo == "PLANTAR":
            semente = self.janela.current_seed()
            resposta = self.fazendeiro.solicita_plantar(semente, x, y)
        else:
            cultura = self.janela.matrix.cells[x][y].valor_atual
            resposta = self.fazendeiro.solicita_colher(cultura, x, y)
            
        self.processar_resposta_acao(resposta, x, y)

    def processar_resposta_acao(self, resposta, x, y):
        """Processa a resposta imediata da ação de plantar/colher."""
        if not resposta: return
        
        # A API do Mapa RMI retorna a chave "validar" (Booleano) e "motivo" (String)
        if resposta.get("validar") == True:
            self.janela.server_message(f"✅ Célula ({x}, {y}): " + resposta.get("motivo", "Sucesso!"))
            
            # Força uma atualização imediata do mapa para refletir o clique na hora!
            self.atualizar_mapa_periodicamente()
        else:
            self.janela.log_message("Sistema", f"❌ " + resposta.get("motivo", "Ação inválida."))

    def atualizar_mapa_periodicamente(self):
        """Método chamado pelo QTimer para puxar a foto da matriz do servidor."""
        matriz = self.fazendeiro.solicita_matriz()
        if matriz:
            for r in range(len(matriz)):
                for c in range(len(matriz[0])):
                    # Só atualiza a cor se mudou, pra não dar flicking (piscar) na tela
                    celula = self.janela.matrix.cells[r][c]
                    if celula.valor_atual != matriz[r][c]:
                        celula.atualizar_visual(matriz[r][c])