import socket
import json
import threading
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QListWidget,
                              QListWidgetItem, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from . import estilos

PORTA_UDP = 37020
TEMPO_BUSCA_MS = 3000  # ms para escutar broadcasts


class DialogConexao(QDialog):
    """Tela inicial: busca servidores na LAN e escolhe nickname."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garden in Overworld — Conectar")
        self.setFixedSize(420, 380)

        self._servidores = {}  # addr -> {"nome": ..., "porta": ...}
        self._buscando = False

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("🌱 Seu nickname de fazendeiro:"))
        self._entrada_nick = QLineEdit()
        self._entrada_nick.setPlaceholderText("Ex: Homelander")
        self._entrada_nick.returnPressed.connect(self._tentar_conectar)
        layout.addWidget(self._entrada_nick)

        grp = QGroupBox("Servidores encontrados na rede local")
        grp_layout = QVBoxLayout(grp)

        self._lista = QListWidget()
        self._lista.setStyleSheet(f"background-color: {estilos.PAINEL};")
        grp_layout.addWidget(self._lista)

        linha = QHBoxLayout()
        self._btn_buscar = QPushButton("🔍 Buscar novamente")
        self._btn_buscar.clicked.connect(self._iniciar_busca)
        linha.addWidget(self._btn_buscar)
        grp_layout.addLayout(linha)

        layout.addWidget(grp)

        layout.addWidget(QLabel("— ou conecte manualmente —"))
        linha_manual = QHBoxLayout()
        self._entrada_ip = QLineEdit()
        self._entrada_ip.setPlaceholderText("IP (ex: 192.168.1.10)")
        self._entrada_porta = QLineEdit("12345")
        self._entrada_porta.setFixedWidth(70)
        linha_manual.addWidget(self._entrada_ip)
        linha_manual.addWidget(QLabel(":"))
        linha_manual.addWidget(self._entrada_porta)
        layout.addLayout(linha_manual)

        btn_conectar = QPushButton("Entrar no mundo")
        btn_conectar.clicked.connect(self._tentar_conectar)
        layout.addWidget(btn_conectar)

        self._host_escolhido = None
        self._porta_escolhida = None

        QTimer.singleShot(100, self._iniciar_busca)

    def _iniciar_busca(self):
        if self._buscando:
            return
        self._buscando = True
        self._lista.clear()
        self._servidores.clear()
        self._btn_buscar.setText("⏳ Buscando...")
        self._btn_buscar.setEnabled(False)

        t = threading.Thread(target=self._escutar_udp, daemon=True)
        t.start()

        QTimer.singleShot(TEMPO_BUSCA_MS, self._finalizar_busca)

    def _escutar_udp(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(TEMPO_BUSCA_MS / 1000 + 0.5)
        try:
            sock.bind(("", PORTA_UDP))
            deadline = __import__("time").time() + TEMPO_BUSCA_MS / 1000
            while __import__("time").time() < deadline:
                try:
                    dados, addr = sock.recvfrom(512)
                    info = json.loads(dados.decode())
                    if info.get("tipo") == "GARDEN_SERVER":
                        ip = addr[0]
                        self._servidores[ip] = {
                            "nome": info.get("nome", "Fazenda"),
                            "porta": info.get("porta", 12345)
                        }
                except socket.timeout:
                    break
                except Exception:
                    pass
        except Exception as e:
            print(f"[UDP] Erro ao escutar: {e}")
        finally:
            sock.close()

    def _finalizar_busca(self):
        self._buscando = False
        self._btn_buscar.setText("🔍 Buscar novamente")
        self._btn_buscar.setEnabled(True)
        self._lista.clear()
        if not self._servidores:
            self._lista.addItem("Nenhum servidor encontrado")
            return
        for ip, info in self._servidores.items():
            item = QListWidgetItem(f"🌾 {info['nome']}  —  {ip}:{info['porta']}")
            item.setData(Qt.ItemDataRole.UserRole, (ip, info["porta"]))
            self._lista.addItem(item)
        self._lista.setCurrentRow(0)

    def _tentar_conectar(self):
        nick = self._entrada_nick.text().strip() or "Fazendeiro"

        item = self._lista.currentItem()
        if item and item.data(Qt.ItemDataRole.UserRole):
            host, porta = item.data(Qt.ItemDataRole.UserRole)
        else:
            host = self._entrada_ip.text().strip()
            porta_str = self._entrada_porta.text().strip()
            if not host:
                self._entrada_ip.setFocus()
                return
            try:
                porta = int(porta_str)
            except ValueError:
                porta = 12345

        self._host_escolhido = host
        self._porta_escolhida = porta
        self._nick_escolhido = nick
        self.accept()

    def resultado(self):
        """Retorna (nick, host, porta) após accept()."""
        return self._nick_escolhido, self._host_escolhido, self._porta_escolhida
