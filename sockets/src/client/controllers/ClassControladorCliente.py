# Arquivo: controllers/ClassControladorCliente.py

from PyQt6.QtWidgets import QMessageBox

class ControladorCliente:
    """Orquestra a comunicação entre a Interface Gráfica (View) e a Rede (Model)."""
    
    def __init__(self, janela, fazendeiro):
        self.janela = janela
        self.fazendeiro = fazendeiro

    def iniciar_conexoes(self, thread_escuta):
        """Liga os botões da tela e os sinais da rede ao Controlador."""
        
        # 1. Quando clicar no mapa (View), avisa o Controlador
        self.janela.matrix.cellClicked.connect(self.lidar_com_clique)
        
        # 2. Quando a rede receber algo (Model), avisa o Controlador
        thread_escuta.sinal_evento.connect(self.processar_evento_rede)

    def lidar_com_clique(self, x, y):
        """Traduz o clique da tela em comandos de rede."""
        modo = self.janela.current_mode()
        
        if modo == "PLANTAR":
            semente_escolhida = self.janela.current_seed()
            self.fazendeiro.solicita_plantar(semente_escolhida, x, y)
        else:
            cultura_alvo = self.janela.matrix.cells[x][y].valor_atual
            self.fazendeiro.solicita_colher(cultura_alvo, x, y)

    def processar_evento_rede(self, evento: dict):
        """Traduz os eventos da rede em atualizações na tela (View)."""
        tipo = evento.get("tipo")
        
        if tipo == "IGNORAR":
            return

        elif tipo == "MAPA_COMPLETO":
            matriz = evento.get("matriz")
            for r in range(len(matriz)):
                for c in range(len(matriz[0])):
                    self.janela.matrix.cells[r][c].atualizar_visual(matriz[r][c])
            self.janela.log_message("Sistema", "Mapa sincronizado com sucesso!")

        elif tipo == "CELULA":
            x, y, valor = evento["x"], evento["y"], evento["valor"]
            self.janela.matrix.cells[x][y].atualizar_visual(valor)
            self.janela.server_message(f"Célula ({x}, {y}) alterada.")

        elif tipo == "RESPOSTA_SISTEMA":
            msg = evento.get("mensagem")
            status = evento.get("status")
            
            if status == "ERRO":
                if msg == "Servidor cheio":
                    QMessageBox.critical(
                        self.janela, 
                        "Acesso Negado", 
                        "A fazenda já atingiu o limite máximo de agricultores (4/4).\n\nTente conectar novamente mais tarde!"
                    )
                    self.janela.close() 
                else:
                    self.janela.log_message("Sistema", f"❌ {msg}")
            else:
                self.janela.server_message(f"✅ {msg}")

        elif tipo == "NOVO_JOGADOR":
            nome = evento.get("nome")
            self.janela.log_message("Sistema", f"🌟 O fazendeiro [{nome}] entrou no jogo!")

        elif tipo == "JOGADOR_SAIU":
            nome = evento.get("nome")
            self.janela.log_message("Sistema", f"👋 O fazendeiro [{nome}] foi embora.")                

        elif tipo == "DESCONECTADO":
            self.janela.log_message("Sistema", "Conexão perdida com o servidor.")