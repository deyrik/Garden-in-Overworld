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
