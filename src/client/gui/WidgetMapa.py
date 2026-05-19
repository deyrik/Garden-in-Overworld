from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from . import estilos

CULTURAS_PRONTAS = {13, 14, 15, 16, 17, 18, 19}

class WidgetMapa(QWidget):
    sinal_celula_clicada = pyqtSignal(int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._celula_selecionada = None
        self._tiles = {}
        self._pos_jogadores = {}  # slot -> (x, y)
        self._matriz = [[0] * 20 for _ in range(20)]
        self._piscar_estado = True
        self._timer_piscar = QTimer(self)
        self._timer_piscar.timeout.connect(self._alternar_piscar)
        self._timer_piscar.start(600)
        self._montar_grid()

    def _montar_grid(self):
        layout = QGridLayout(self)
        layout.setSpacing(1)
        layout.setContentsMargins(0, 0, 0, 0)
        for x in range(20):
            for y in range(20):
                tile = QLabel()
                tile.setFixedSize(32, 32)
                tile.setAlignment(Qt.AlignmentFlag.AlignCenter)
                tile.mousePressEvent = lambda _, cx=x, cy=y: self._on_clique(cx, cy)
                self._tiles[(x, y)] = tile
                layout.addWidget(tile, x, y)
                self._aplicar_estilo(x, y, 0)

    def _estilo_tile(self, valor, selecionado=False):
        cor = estilos.CORES_TILE.get(valor, "#2d5a27")
        if selecionado:
            borda = f"border: 2px solid {estilos.AMBAR};"
        elif valor in CULTURAS_PRONTAS:
            borda_cor = "#00ff88" if self._piscar_estado else "#ffff00"
            borda = f"border: 2px solid {borda_cor};"
            cor = "#1a4a1a" if self._piscar_estado else estilos.CORES_TILE.get(valor, "#2d5a27")
        else:
            borda = "border: 1px solid #1a1a1a;"
        return (
            f"background-color: {cor};"
            f"{borda}"
            f"border-radius: 2px;"
            f"font-size: 18px;"
        )

    def _alternar_piscar(self):
        self._piscar_estado = not self._piscar_estado
        for x in range(20):
            for y in range(20):
                if self._matriz[x][y] in CULTURAS_PRONTAS:
                    self._aplicar_estilo(x, y, self._matriz[x][y], self._celula_selecionada == (x, y))

    def _aplicar_estilo(self, x, y, valor, selecionado=False):
        tile = self._tiles[(x, y)]
        tile.setStyleSheet(self._estilo_tile(valor, selecionado))
        tile.setText(estilos.EMOJIS_TILE.get(valor, ""))

    def _on_clique(self, x, y):
        if self._celula_selecionada and self._celula_selecionada != (x, y):
            px, py = self._celula_selecionada
            self._aplicar_estilo(px, py, self._matriz[px][py])
        self._celula_selecionada = (x, y)
        self._aplicar_estilo(x, y, self._matriz[x][y], selecionado=True)
        self.sinal_celula_clicada.emit(x, y, self._matriz[x][y])

    def atualizar_mapa_completo(self, matriz):
        self._matriz = matriz
        for x in range(len(matriz)):
            for y in range(len(matriz[x])):
                self._atualizar_celula_interna(x, y, matriz[x][y])

    def atualizar_celula(self, x, y, valor):
        self._matriz[x][y] = valor
        self._atualizar_celula_interna(x, y, valor)

    def _atualizar_celula_interna(self, x, y, valor):
        selecionado = self._celula_selecionada == (x, y)
        self._aplicar_estilo(x, y, valor, selecionado)

    def atualizar_posicao_jogador(self, slot, nick, x, y):
        if slot in self._pos_jogadores:
            px, py = self._pos_jogadores[slot]
            tile = self._tiles.get((px, py))
            if tile:
                for child in tile.findChildren(QLabel):
                    child.deleteLater()

        if x < 0 or y < 0:
            self._pos_jogadores.pop(slot, None)
            return

        self._pos_jogadores[slot] = (x, y)
        tile = self._tiles[(x, y)]
        cor = estilos.CORES_JOGADOR.get(slot, "#ffffff")
        overlay = QLabel(nick[0].upper() if nick else "?", tile)
        overlay.setStyleSheet(
            f"color: {cor}; font-weight: bold; font-size: 11px;"
            f"background: transparent; border: none;"
        )
        overlay.setFixedSize(12, 12)
        overlay.move(1, 1)
        overlay.show()
