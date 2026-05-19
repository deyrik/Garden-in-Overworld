FUNDO = "#1a1a2e"
PAINEL = "#16213e"
TEXTO = "#e0e0e0"
DESTAQUE = "#00ff88"
AMBAR = "#ffb347"
BORDA = "#333333"
HOVER = "#2a2a4e"

STYLESHEET = f"""
    QWidget {{
        background-color: {FUNDO};
        color: {TEXTO};
        font-family: 'Courier New', monospace;
        font-size: 13px;
    }}
    QGroupBox {{
        border: 1px solid {DESTAQUE};
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
        font-weight: bold;
        color: {DESTAQUE};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 8px;
    }}
    QPushButton {{
        background-color: {PAINEL};
        color: {TEXTO};
        border: 1px solid {DESTAQUE};
        border-radius: 3px;
        padding: 4px 8px;
    }}
    QPushButton:hover {{
        background-color: {HOVER};
        border-color: {AMBAR};
    }}
    QPushButton:pressed {{
        background-color: {DESTAQUE};
        color: {FUNDO};
    }}
    QPushButton:disabled {{
        color: #555555;
        border-color: #333333;
    }}
    QTextEdit, QLineEdit {{
        background-color: {PAINEL};
        color: {TEXTO};
        border: 1px solid {BORDA};
        border-radius: 3px;
    }}
    QScrollBar:vertical {{
        background: {FUNDO};
        width: 8px;
    }}
    QScrollBar::handle:vertical {{
        background: {DESTAQUE};
        border-radius: 4px;
    }}
"""

CORES_TILE = {
    0:  "#2d5a27",  # terra
    1:  "#1a3a6e",  # água
    2:  "#8b7355",  # areia
    8:  "#4a3000",  # solo preparado (terra)
    9:  "#6b5a2d",  # solo preparado (areia)
    3:  "#3a6e30",  # trigo crescendo
    4:  "#1a5080",  # arroz crescendo
    6:  "#2d7a30",  # cana crescendo (terra)
    7:  "#5a7a30",  # cana crescendo (areia)
    10: "#6e5a1a",  # milho crescendo
    11: "#5a3a1a",  # batata crescendo
    12: "#7a2a2a",  # tomate crescendo
    13: "#5a9a30",  # trigo pronto
    14: "#1a7aaa",  # arroz pronto
    15: "#30aa35",  # cana pronta (terra)
    16: "#7aaa30",  # cana pronta (areia)
    17: "#aaaa1a",  # milho pronto
    18: "#aa5a1a",  # batata pronta
    19: "#cc3030",  # tomate pronto
}

EMOJIS_TILE = {
    0:  "",
    1:  "",
    2:  "",
    8:  "🪵",
    9:  "🪵",
    3:  "🌾",
    4:  "🌿",
    6:  "🎋",
    7:  "🎋",
    10: "🌽",
    11: "🥔",
    12: "🍅",
    13: "🌾",
    14: "🌿",
    15: "🎋",
    16: "🎋",
    17: "🌽",
    18: "🥔",
    19: "🍅",
}

CORES_JOGADOR = {
    1: "#ff6b6b",
    2: "#6b9fff",
    3: "#ffd93d",
    4: "#a29bfe",
}
