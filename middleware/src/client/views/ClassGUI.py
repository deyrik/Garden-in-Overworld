
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QPushButton, QTextEdit,
    QLabel, QFrame, QSizePolicy, QButtonGroup, QDialog, 
    QLineEdit,QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPalette
import random


# ── Paleta de cores ────────────────────────────────────────────────────────────
BG_DARK      = "#1a1a2e"
BG_PANEL     = "#16213e"
CELL_CLICKED = "#bed721"
ACCENT       = "#ffffff"
BTN_A_ON     = "#3fa541"
BTN_B_ON     = "#ff0026"
BTN_OFF      = "#2a2a4a"
TEXT_MAIN    = "#eaeaea"
TEXT_DIM     = "#7a7a9a"
BORDER       = "#2a2a4a"


# ── Célula clicável da matriz ──────────────────────────────────────────────────
class MatrixCell(QPushButton):
    """Botão que representa uma célula (x, y) da matriz."""

    coordClicked = pyqtSignal(int, int)   

    # O mesmo dicionário de cores que você usava no terminal, mas em Hexadecimal!
    DICIONARIO_CORES = {
        0: "#056C00", # Terra: Forest Green
        1: "#003972", # Água: Dodger Blue
        2: "#DAA520", # Areia: Goldenrod
        3: "#544C21", # Trigo: Gold
        4: "#00CED1", # Arroz: Dark Turquoise
        6: "#32CD32", # Cana na Terra: Lime Green
        #7: "#F5F5DC", # Cana na Areia: Beige
        7: "#05FF05" # Cana na Terra: Lime Green
    }

    def __init__(self, x: int, y: int, parent=None):
        super().__init__(parent)
        self.x = x
        self.y = y
        self.valor_atual = 0 # Guarda o que tem plantado aqui (começa com 0 - Terra)

        self.setFixedSize(QSize(30, 30))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"({x}, {y})")
        
        self.atualizar_visual(self.valor_atual) # Pinta com a cor inicial
        self.clicked.connect(self._on_click)

    def atualizar_visual(self, valor_terreno: int):
        """Pinta o botão com a cor do terreno/plantação atual."""
        self.valor_atual = valor_terreno
        # Se vier um número estranho, pinta de preto
        cor_fundo = self.DICIONARIO_CORES.get(valor_terreno, "#000000") 
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {cor_fundo};
                border: 1px solid {BORDER};
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 2px solid #FFFFFF; 
            }}
        """)

    def _on_click(self):
        # Emite o sinal dizendo quem foi clicado, a Main Window decide o que fazer
        self.coordClicked.emit(self.x, self.y)

# ── Widget da Matriz ───────────────────────────────────────────────────────────
class MatrixWidget(QWidget):
    """Grade NxN de células clicáveis."""

    cellClicked = pyqtSignal(int, int)

    def __init__(self, rows: int = 20, cols: int = 20, parent=None):
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        self.cells: list[list[MatrixCell]] = []

        self.setStyleSheet(f"background-color: {BG_PANEL};")
        layout = QGridLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(8, 8, 8, 8)

        for row in range(rows):
            row_cells = []
            for col in range(cols):
                # CORREÇÃO: x=row (linha), y=col (coluna)
                cell = MatrixCell(row, col)          
                cell.coordClicked.connect(self._on_cell_clicked)
                layout.addWidget(cell, row, col)
                row_cells.append(cell)
            self.cells.append(row_cells)

    def _on_cell_clicked(self, x: int, y: int):
        self.cellClicked.emit(x, y)

    def reset_all(self):
        for row in self.cells:
            for cell in row:
                cell.reset()


# ── Botões de modo exclusivo ───────────────────────────────────────────────────
class ModeButton(QPushButton):
    """Botão de modo com visual on/off."""

    def __init__(self, label: str, color_on: str, parent=None):
        super().__init__(label, parent)
        self.color_on = color_on
        self.setCheckable(True)
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggled.connect(self._refresh)
        self._refresh(False)

    def _refresh(self, checked: bool):
        bg    = self.color_on if checked else BTN_OFF
        border= self.color_on if checked else "#444466"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {TEXT_MAIN};
                border: 2px solid {border};
                border-radius: 6px;
                padding: 6px 18px;
            }}
            QPushButton:hover {{
                background-color: {self.color_on};
                border-color: {self.color_on};
            }}
        """)


# ── Janela Principal ───────────────────────────────────────────────────────────
class GameWindow(QMainWindow):

    ROWS = 20
    COLS = 20

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Client")
        self.setMinimumSize(900, 680)
        self._build_ui()
        self._connect_signals()
        self.log_message("Sistema", "Interface iniciada. Aguardando conexão com o servidor...")

    # ── construção da UI ───────────────────────────────────────────────────────
    def _build_ui(self):
        # Fundo geral
        self.setStyleSheet(f"background-color: {BG_DARK}; color: {TEXT_MAIN};")

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # ── coluna esquerda: matriz ────────────────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(8)

        title_matrix = QLabel("CAMPO DE BATALHA")
        title_matrix.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_matrix.setStyleSheet(f"color: {ACCENT}; letter-spacing: 2px;")
        title_matrix.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left.addWidget(title_matrix)

        self.matrix = MatrixWidget(self.ROWS, self.COLS)
        matrix_frame = QFrame()
        matrix_frame.setStyleSheet(
            f"border: 2px solid {BORDER}; border-radius: 8px; background: {BG_PANEL};"
        )
        matrix_frame.setLayout(QVBoxLayout())
        matrix_frame.layout().setContentsMargins(0, 0, 0, 0)
        matrix_frame.layout().addWidget(self.matrix)
        left.addWidget(matrix_frame)

        # coordenada da última célula clicada
        self.coord_label = QLabel("Clique em uma célula")
        self.coord_label.setFont(QFont("Courier New", 10))
        self.coord_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.coord_label.setStyleSheet(
            f"color: {TEXT_DIM}; background: {BG_PANEL}; "
            f"border: 1px solid {BORDER}; border-radius: 4px; padding: 4px;"
        )
        left.addWidget(self.coord_label)

        root.addLayout(left, stretch=3)

        # ── coluna direita: controles + log ────────────────────────────────────
        right = QVBoxLayout()
        right.setSpacing(10)

        # -- Botões de modo (exclusivos) ----------------------------------------
        mode_title = QLabel("MODO DE AÇÃO")
        mode_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        mode_title.setStyleSheet(f"color: {TEXT_DIM}; letter-spacing: 1px;")
        right.addWidget(mode_title)

        self.btn_a = ModeButton("𖧧   PLANTAR", BTN_A_ON)
        self.btn_b = ModeButton("𑁍ܓ COLHER", BTN_B_ON)
       
        self.btn_a.setChecked(True)   # padrão inicial

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.addWidget(self.btn_a)
        btn_row.addWidget(self.btn_b)
        right.addLayout(btn_row)

        # separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {BORDER};")
        right.addWidget(sep)

        # -- Botões de Seleção de Semente ---------------------------------------
        seed_title = QLabel("TIPO DE SEMENTE")
        seed_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        seed_title.setStyleSheet(f"color: {TEXT_DIM}; letter-spacing: 1px;")
        right.addWidget(seed_title)

        # Usamos a sua própria classe ModeButton, passando as cores certas!
        self.btn_trigo = ModeButton("🌾 TRIGO", "#DAA520")
        self.btn_arroz = ModeButton("🍚 ARROZ", "#00CED1")
        self.btn_cana = ModeButton("🎋 CANA", "#32CD32")

        # O QButtonGroup gerencia a exclusividade automaticamente!
        self.seed_group = QButtonGroup(self)
        
        # Adicionamos o botão e o ID (que é o próprio número da semente no servidor!)
        self.seed_group.addButton(self.btn_trigo, 3) 
        self.seed_group.addButton(self.btn_arroz, 4)
        self.seed_group.addButton(self.btn_cana, 5)

        self.btn_trigo.setChecked(True) # O Trigo já começa selecionado

        seed_row = QHBoxLayout()
        seed_row.setSpacing(4)
        seed_row.addWidget(self.btn_trigo)
        seed_row.addWidget(self.btn_arroz)
        seed_row.addWidget(self.btn_cana)
        right.addLayout(seed_row)

        # Novo separador
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {BORDER};")
        right.addWidget(sep2)

        # -- Log de mensagens do servidor ---------------------------------------
        log_title = QLabel("MENSAGENS DO SERVIDOR")
        log_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        log_title.setStyleSheet(f"color: {TEXT_DIM}; letter-spacing: 1px;")
        right.addWidget(log_title)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFont(QFont("Courier New", 9))
        self.log_box.setStyleSheet(f"""
            QTextEdit {{
                background-color: {BG_PANEL};
                color: {TEXT_MAIN};
                border: 2px solid {BORDER};
                border-radius: 6px;
                padding: 6px;
            }}
            QScrollBar:vertical {{
                background: {BG_DARK};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 4px;
            }}
        """)
        right.addWidget(self.log_box, stretch=1)

        # -- botão limpar log ---------------------------------------------------
        self.btn_clear = QPushButton("Limpar log")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.setStyleSheet(f"""
            QPushButton {{
                background: {BTN_OFF};
                color: {TEXT_DIM};
                border: 1px solid {BORDER};
                border-radius: 5px;
                padding: 5px;
                font-size: 9pt;
            }}
            QPushButton:hover {{ color: {TEXT_MAIN}; border-color: #666688; }}
        """)
        right.addWidget(self.btn_clear)

        # -- botão reset da grade ----------------------------------------------
        self.btn_reset = QPushButton("Resetar matriz")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setStyleSheet(f"""
            QPushButton {{
                background: {BTN_OFF};
                color: {TEXT_DIM};
                border: 1px solid {BORDER};
                border-radius: 5px;
                padding: 5px;
                font-size: 9pt;
            }}
            QPushButton:hover {{ color: {TEXT_MAIN}; border-color: #666688; }}
        """)
        right.addWidget(self.btn_reset)

        root.addLayout(right, stretch=1)

    # ── conexão de sinais ──────────────────────────────────────────────────────
    def _connect_signals(self):
        # célula clicada → atualiza label + loga
        self.matrix.cellClicked.connect(self._on_cell_clicked)

        # botões exclusivos: quando A liga, desliga B e vice-versa
        self.btn_a.toggled.connect(self._sync_mode_buttons)
        self.btn_b.toggled.connect(self._sync_mode_buttons_b)

        # utilitários
        self.btn_clear.clicked.connect(self.log_box.clear)
        self.btn_reset.clicked.connect(self._reset_matrix)

    # ── handlers ──────────────────────────────────────────────────────────────
    def _on_cell_clicked(self, x: int, y: int):
        mode = "PLANTAR" if self.btn_a.isChecked() else "COLHER"
        self.coord_label.setText(f"Selecionado: ({x}, {y})  │  Modo: {mode}")
        self.log_message("Jogador", f"Célula ({x}, {y}) → [{mode}]")

    def _sync_mode_buttons(self, checked: bool):
        """Garante exclusividade: btn_a ligado → btn_b desligado."""
        if checked:
            self.btn_b.blockSignals(True)
            self.btn_b.setChecked(False)
            self.btn_b._refresh(False)
            self.btn_b.blockSignals(False)
        else:
            # impede que ambos fiquem desligados
            if not self.btn_b.isChecked():
                self.btn_b.blockSignals(True)
                self.btn_b.setChecked(True)
                self.btn_b._refresh(True)
                self.btn_b.blockSignals(False)

    def _sync_mode_buttons_b(self, checked: bool):
        """Garante exclusividade: btn_b ligado → btn_a desligado."""
        if checked:
            self.btn_a.blockSignals(True)
            self.btn_a.setChecked(False)
            self.btn_a._refresh(False)
            self.btn_a.blockSignals(False)
        else:
            if not self.btn_a.isChecked():
                self.btn_a.blockSignals(True)
                self.btn_a.setChecked(True)
                self.btn_a._refresh(True)
                self.btn_a.blockSignals(False)

    def _reset_matrix(self):
        self.matrix.reset_all()
        self.coord_label.setText("Clique em uma célula")
        self.log_message("Sistema", "Matriz resetada.")

    # ── API pública para integração com servidor ───────────────────────────────
    def log_message(self, origin: str, text: str):
        """
        Adiciona uma mensagem formatada ao log.
        Chame este método a partir do seu cliente de rede para exibir
        mensagens recebidas do servidor.
        """
        color = ACCENT if origin == "Sistema" else ("#4fc3f7" if origin == "Servidor" else TEXT_MAIN)
        self.log_box.append(
            f'<span style="color:{TEXT_DIM};">[{origin}]</span> '
            f'<span style="color:{color};">{text}</span>'
        )

    def server_message(self, text: str):
        """Atalho: mensagem vinda do servidor."""
        self.log_message("Servidor", text)

    def current_mode(self) -> str:
        """Retorna 'PLANTAR' ou 'COLHER' — útil para enviar ao servidor."""
        return "PLANTAR" if self.btn_a.isChecked() else "COLHER"

    def processar_mensagem_servidor(self, evento: dict):
        """Recebe o dicionário da Thread de Rede e atualiza a interface."""
        tipo = evento.get("tipo")
        
        if tipo == "IGNORAR":
            return # Não faz nada, apenas volta a ouvir

        elif tipo == "MAPA_COMPLETO":
            matriz = evento.get("matriz")
            for r in range(len(matriz)):
                for c in range(len(matriz[0])):
                    # Atualiza a cor de cada célula usando o seu método!
                    self.matrix.cells[r][c].atualizar_visual(matriz[r][c])
            self.log_message("Sistema", "Mapa sincronizado com sucesso!")

        elif tipo == "CELULA":
            x, y, valor = evento["x"], evento["y"], evento["valor"]
            # CORREÇÃO: Como invertemos ali em cima, agora a lista acessa [x][y] corretamente!
            self.matrix.cells[x][y].atualizar_visual(valor)
            self.server_message(f"Célula ({x}, {y}) alterada.")

        elif tipo == "RESPOSTA_SISTEMA":
            msg = evento.get("mensagem")
            status = evento.get("status")
            
            if status == "ERRO":
                if msg == "Servidor cheio":
                    QMessageBox.critical(
                        self, 
                        "Acesso Negado", 
                        "A fazenda já atingiu o limite máximo de agricultores (4/4).\n\nTente conectar novamente mais tarde!"
                    )
                    self.close() # Fecha a janela do jogo e encerra o programa
                else:
                    self.log_message("Sistema", f"❌ {msg}")
            else:
                self.server_message(f"✅ {msg}")

        elif tipo == "NOVO_JOGADOR":
            nome = evento.get("nome")
            self.log_message("Sistema", f"🌟 O fazendeiro [{nome}] entrou no jogo!")

        elif tipo == "JOGADOR_SAIU":
            nome = evento.get("nome")
            self.log_message("Sistema", f"👋 O fazendeiro [{nome}] foi embora.")                



        elif tipo == "DESCONECTADO":
            self.log_message("Sistema", "Conexão perdida com o servidor.")

    def current_seed(self) -> int:
        """Retorna o ID da semente selecionada (3, 4 ou 5)."""
        return self.seed_group.checkedId()


# ── Tela Inicial de Login ──────────────────────────────────────────────────────
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Entrar na Fazenda")
        self.setFixedSize(320, 180) # Uma janelinha pequena e centralizada
        self.setStyleSheet(f"background-color: {BG_DARK}; color: {TEXT_MAIN};")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Título
        title = QLabel("BEM-VINDO À FAZENDA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ACCENT}; letter-spacing: 2px;")
        layout.addWidget(title)

        # Caixa de texto para o Nickname
        self.input_nick = QLineEdit()
        self.input_nick.setPlaceholderText("Digite seu Nickname...")
        self.input_nick.setFont(QFont("Segoe UI", 10))
        self.input_nick.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_PANEL};
                border: 2px solid {BORDER};
                border-radius: 5px;
                padding: 8px;
                color: {TEXT_MAIN};
            }}
            QLineEdit:focus {{
                border: 2px solid {ACCENT};
            }}
        """)
        layout.addWidget(self.input_nick)

        # Botão de Conectar
        self.btn_connect = QPushButton("ENTRAR NO JOGO")
        self.btn_connect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_connect.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_connect.setStyleSheet(f"""
            QPushButton {{
                background-color: {BTN_A_ON};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: #bed721;
            }}
        """)
        # Quando clicar, ele "Aceita" o diálogo e fecha a janelinha
        self.btn_connect.clicked.connect(self.accept) 
        layout.addWidget(self.btn_connect)

    def get_nickname(self):
        """Pega o texto digitado. Se estiver vazio, dá um nome padrão."""
        numero = random.randint(1,99)
        nome = self.input_nick.text().strip()
        return nome if nome else f"Fazendeiro_Misterioso_{numero}"


















