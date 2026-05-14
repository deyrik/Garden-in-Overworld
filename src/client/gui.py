import json
import os
import sys
from dataclasses import dataclass

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Permite executar via `python3 src/client/gui.py`
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from client.ClassFazendeiro import ClienteFazenda
from client.ClassTCPCliente import TCPCliente


@dataclass(frozen=True)
class ConnectionConfig:
    host: str = "localhost"
    port: int = 12345


class NetworkWorker(QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal(str)
    system_message = pyqtSignal(str, str)  # status, mensagem
    full_map = pyqtSignal(list)  # matriz
    cell_update = pyqtSignal(int, int, int)  # x, y, valor

    def __init__(self, config: ConnectionConfig):
        super().__init__()
        self._config = config
        self._tcp = TCPCliente(config.host, config.port)
        self._fazendeiro = ClienteFazenda(self._tcp)
        self._running = True

    def stop(self):
        self._running = False
        try:
            self._tcp.fecha_conexao()
        except Exception:
            pass

    def connect_and_loop(self):
        self._tcp.conecta_servidor()
        # boas vindas
        boas_vindas = self._tcp.recebe_mensagem()
        if not boas_vindas:
            self.disconnected.emit("Falha ao conectar/receber boas-vindas.")
            return

        self.connected.emit()
        # pede mapa inicial
        self._fazendeiro.solicita_matriz()

        while self._running:
            evento = self._fazendeiro.escutar_servidor()
            if evento.get("tipo") == "DESCONECTADO":
                self.disconnected.emit("Conexão encerrada.")
                return

            if evento.get("tipo") == "MAPA_COMPLETO":
                matriz = evento.get("matriz") or []
                self.full_map.emit(matriz)
                continue

            if evento.get("tipo") == "CELULA":
                try:
                    x = int(evento.get("x"))
                    y = int(evento.get("y"))
                    valor = int(evento.get("valor"))
                except Exception:
                    continue
                self.cell_update.emit(x, y, valor)
                continue

            if evento.get("tipo") == "RESPOSTA_SISTEMA":
                status = str(evento.get("status") or "")
                msg = str(evento.get("mensagem") or "")
                self.system_message.emit(status, msg)
                if msg.lower().startswith("desconectando"):
                    self.disconnected.emit(msg)
                    return

    # Commands (called from UI thread via QueuedConnection-safe direct calls)
    def cmd_nickname(self, nome: str):
        self._fazendeiro.solicita_nickname(nome)

    def cmd_plantar(self, semente: int, x: int, y: int):
        dados = {"comando": "PLANTAR", "semente": int(semente), "x": int(x), "y": int(y)}
        self._tcp.manda_mensagem(json.dumps(dados))

    def cmd_colher(self, cultura: int, x: int, y: int):
        dados = {"comando": "COLHER", "cultura": int(cultura), "x": int(x), "y": int(y)}
        self._tcp.manda_mensagem(json.dumps(dados))

    def cmd_refresh_map(self):
        self._fazendeiro.solicita_matriz()

    def cmd_sair(self):
        self._fazendeiro.solicita_sair()


class MainWindow(QMainWindow):
    def __init__(self, config: ConnectionConfig):
        super().__init__()
        self.setWindowTitle("Garden-in-Overworld - Cliente (PyQt6)")

        self._matriz = []

        # UI
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        self.status_label = QLabel("Status: desconectado")
        layout.addWidget(self.status_label)

        self.table = QTableWidget(0, 0)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        layout.addWidget(self.table, 1)

        controls_row = QHBoxLayout()
        layout.addLayout(controls_row)

        # Nickname
        nick_box = QGroupBox("Nickname")
        nick_layout = QHBoxLayout(nick_box)
        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("Seu nome…")
        self.nick_btn = QPushButton("Enviar")
        self.nick_btn.clicked.connect(self._on_send_nick)
        nick_layout.addWidget(self.nick_input)
        nick_layout.addWidget(self.nick_btn)
        controls_row.addWidget(nick_box, 2)

        # Ações
        action_box = QGroupBox("Ações")
        action_layout = QGridLayout(action_box)
        self.x_spin = QSpinBox()
        self.y_spin = QSpinBox()
        self.item_spin = QSpinBox()
        self.item_spin.setRange(0, 7)
        action_layout.addWidget(QLabel("X"), 0, 0)
        action_layout.addWidget(self.x_spin, 0, 1)
        action_layout.addWidget(QLabel("Y"), 0, 2)
        action_layout.addWidget(self.y_spin, 0, 3)
        action_layout.addWidget(QLabel("Item"), 1, 0)
        action_layout.addWidget(self.item_spin, 1, 1)

        self.plantar_btn = QPushButton("Plantar")
        self.plantar_btn.clicked.connect(self._on_plantar)
        self.colher_btn = QPushButton("Colher")
        self.colher_btn.clicked.connect(self._on_colher)
        self.refresh_btn = QPushButton("Atualizar mapa")
        self.refresh_btn.clicked.connect(self._on_refresh)
        self.sair_btn = QPushButton("Sair")
        self.sair_btn.clicked.connect(self._on_sair)

        action_layout.addWidget(self.plantar_btn, 2, 0, 1, 2)
        action_layout.addWidget(self.colher_btn, 2, 2, 1, 2)
        action_layout.addWidget(self.refresh_btn, 3, 0, 1, 2)
        action_layout.addWidget(self.sair_btn, 3, 2, 1, 2)

        controls_row.addWidget(action_box, 3)

        # Network thread
        self._worker_thread = QThread(self)
        self._worker = NetworkWorker(config)
        self._worker.moveToThread(self._worker_thread)

        self._worker_thread.started.connect(self._worker.connect_and_loop)
        self._worker.connected.connect(self._on_connected)
        self._worker.disconnected.connect(self._on_disconnected)
        self._worker.system_message.connect(self._on_system_message)
        self._worker.full_map.connect(self._on_full_map)
        self._worker.cell_update.connect(self._on_cell_update)

        self._worker_thread.start()

    def closeEvent(self, event):
        try:
            self._worker.stop()
            self._worker_thread.quit()
            self._worker_thread.wait(1500)
        finally:
            super().closeEvent(event)

    def _set_grid_size(self, rows: int, cols: int):
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        for r in range(rows):
            self.table.setRowHeight(r, 18)
        for c in range(cols):
            self.table.setColumnWidth(c, 18)
        self.x_spin.setRange(0, max(0, rows - 1))
        self.y_spin.setRange(0, max(0, cols - 1))

    def _color_for_value(self, val: int) -> QColor:
        # Mantém semântica aproximada do modo ANSI
        return {
            0: QColor("#2e7d32"),  # terra
            1: QColor("#1565c0"),  # agua
            2: QColor("#f9a825"),  # areia
            3: QColor("#8d6e63"),  # trigo
            4: QColor("#26c6da"),  # arroz
            6: QColor("#9ccc65"),  # cana terra
            7: QColor("#9ccc65"),  # cana areia
        }.get(val, QColor("#212121"))

    def _set_cell(self, x: int, y: int, val: int):
        if x < 0 or y < 0:
            return
        if x >= self.table.rowCount() or y >= self.table.columnCount():
            return
        item = self.table.item(x, y)
        if item is None:
            item = QTableWidgetItem("")
            self.table.setItem(x, y, item)
        item.setBackground(QBrush(self._color_for_value(val)))
        item.setToolTip(f"({x},{y}) = {val}")

    # Network signal handlers
    def _on_connected(self):
        self.status_label.setText("Status: conectado")

    def _on_disconnected(self, reason: str):
        self.status_label.setText(f"Status: desconectado ({reason})")
        QMessageBox.information(self, "Conexão encerrada", reason)

    def _on_system_message(self, status: str, msg: str):
        self.status_label.setText(f"Status: {status} - {msg}")

    def _on_full_map(self, matriz: list):
        self._matriz = matriz or []
        if not self._matriz:
            return
        rows = len(self._matriz)
        cols = len(self._matriz[0]) if rows else 0
        self._set_grid_size(rows, cols)
        for x in range(rows):
            for y in range(cols):
                try:
                    val = int(self._matriz[x][y])
                except Exception:
                    val = 0
                self._set_cell(x, y, val)

    def _on_cell_update(self, x: int, y: int, val: int):
        self._set_cell(x, y, val)

    # UI actions
    def _on_send_nick(self):
        nome = self.nick_input.text().strip()
        if not nome:
            QMessageBox.warning(self, "Nickname", "Informe um nickname.")
            return
        self._worker.cmd_nickname(nome)

    def _on_plantar(self):
        x = self.x_spin.value()
        y = self.y_spin.value()
        semente = self.item_spin.value()
        self._worker.cmd_plantar(semente, x, y)

    def _on_colher(self):
        x = self.x_spin.value()
        y = self.y_spin.value()
        cultura = self.item_spin.value()
        self._worker.cmd_colher(cultura, x, y)

    def _on_refresh(self):
        self._worker.cmd_refresh_map()

    def _on_sair(self):
        self._worker.cmd_sair()


def main():
    app = QApplication(sys.argv)
    win = MainWindow(ConnectionConfig())
    win.resize(900, 650)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

