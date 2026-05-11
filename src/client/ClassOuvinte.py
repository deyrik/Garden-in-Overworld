import threading

class OuvinteThread(threading.Thread):
    """
    Classe que funciona como uma Thread Fantasma.
    Ela vive em paralelo para escutar o servidor e atualizar a matriz local.
    """
    def __init__(self, fazendeiro, mapa_jogo, evento_mapa_pronto):
        # Inicia a Thread configurando-a como "daemon" (morre quando o jogo fecha)
        super().__init__(daemon=True) 
        
        # Guarda as ferramentas que ela vai precisar usar
        self.fazendeiro = fazendeiro
        self.mapa_jogo = mapa_jogo
        self.evento_mapa_pronto = evento_mapa_pronto
    
    #ja é padronizado usar "run" como nome do método principal da Thread, 
    # então não precisa chamar ela de outra coisa
    def run(self):
        """
        loop infinito que vai começar a rodar em segundo plano.
        """
        while True:
            evento = self.fazendeiro.escutar_servidor()

            if evento["tipo"] == "DESCONECTADO":
                print("\n[Sistema] Conexão com o servidor encerrada.")
                break 

            elif evento["tipo"] == "MAPA_COMPLETO":
                self.mapa_jogo.atualizar_matriz(evento["matriz"])
                print("\n[Sistema] Mapa global sincronizado!")
                
                # Destrava a Main Thread
                self.evento_mapa_pronto.set()

            elif evento["tipo"] == "CELULA":
                x = evento["x"]
                y = evento["y"]
                novo_valor = evento["valor"]
                
                self.mapa_jogo.matriz[x][y] = novo_valor
                print(f"\n[Broadcast] Alguém atualizou a célula ({x}, {y}) para {novo_valor}.")
                
                self.mapa_jogo.exibe_colorido()

            elif evento["tipo"] == "RESPOSTA_SISTEMA":
                if evento.get("status") == "ERRO":
                    print(f"\n[Servidor Recusou] {evento.get('mensagem')}")