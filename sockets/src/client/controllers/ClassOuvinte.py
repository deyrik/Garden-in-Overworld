from PyQt6.QtCore import QThread, pyqtSignal

class OuvinteThread(QThread):
    """Thread Fantasma que escuta o servidor e avisa a interface."""
    sinal_evento = pyqtSignal(dict)
    
    def __init__(self, fazendeiro):
        super().__init__() 
        self.fazendeiro = fazendeiro
        self.running = True
    
    def run(self):
        while self.running:
            evento = self.fazendeiro.escutar_servidor()
            self.sinal_evento.emit(evento)
            
            if evento["tipo"] == "DESCONECTADO":
                self.running = False
                break