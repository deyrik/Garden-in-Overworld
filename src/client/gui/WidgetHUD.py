from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from . import estilos

NOMES_CULTURA = {3: "Trigo", 4: "Arroz", 6: "Cana", 10: "Milho", 11: "Batata", 12: "Tomate"}
EMOJIS_CULTURA = {3: "🌾", 4: "🌿", 6: "🎋", 10: "🌽", 11: "🥔", 12: "🍅"}

class WidgetHUD(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setStyleSheet(f"background-color: #0d1117; border-bottom: 1px solid {estilos.DESTAQUE};")
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(12, 4, 12, 4)
        self._layout.setSpacing(16)

        self._label_temporada = QLabel("🌱 —")
        self._label_temporada.setStyleSheet(f"color: {estilos.DESTAQUE}; font-weight: bold; font-size: 13px; border: none; background: transparent;")
        self._layout.addWidget(self._label_temporada)

        self._barras = {}  # cultura -> (label, QProgressBar)
        self._container_barras = QWidget()
        self._container_barras.setStyleSheet("background: transparent; border: none;")
        self._layout_barras = QHBoxLayout(self._container_barras)
        self._layout_barras.setContentsMargins(0, 0, 0, 0)
        self._layout_barras.setSpacing(8)
        self._layout.addWidget(self._container_barras, stretch=1)

        self._label_timer = QLabel("--:--")
        self._label_timer.setStyleSheet(f"color: {estilos.AMBAR}; font-weight: bold; font-size: 16px; border: none; background: transparent;")
        self._label_timer.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._layout.addWidget(self._label_timer)

    def atualizar_temporada(self, dados: dict):
        nome = dados.get("nome", "")
        numero = dados.get("temporada", 1)
        self._label_temporada.setText(f"🌱 {nome} — T{numero}")

        demanda = dados.get("demanda", {})
        # Limpar barras antigas
        for i in reversed(range(self._layout_barras.count())):
            w = self._layout_barras.itemAt(i).widget()
            if w:
                w.deleteLater()
        self._barras.clear()

        for cultura_str, meta in demanda.items():
            cultura = int(cultura_str)
            emoji = EMOJIS_CULTURA.get(cultura, "?")
            lbl = QLabel(f"{emoji} 0/{meta}")
            lbl.setStyleSheet("color: #ccc; font-size: 11px; border: none; background: transparent;")
            barra = QProgressBar()
            barra.setRange(0, meta)
            barra.setValue(0)
            barra.setFixedWidth(60)
            barra.setFixedHeight(8)
            barra.setTextVisible(False)
            barra.setStyleSheet(
                "QProgressBar { background: #333; border-radius: 3px; border: none; }"
                f"QProgressBar::chunk {{ background: {estilos.DESTAQUE}; border-radius: 3px; }}"
            )
            self._layout_barras.addWidget(lbl)
            self._layout_barras.addWidget(barra)
            self._barras[cultura] = (lbl, barra, meta)

    def atualizar_progresso(self, progresso: dict, demanda: dict):
        for cultura_str, atual in progresso.items():
            cultura = int(cultura_str)
            if cultura not in self._barras:
                continue
            lbl, barra, meta = self._barras[cultura]
            emoji = EMOJIS_CULTURA.get(cultura, "?")
            lbl.setText(f"{emoji} {atual}/{meta}")
            barra.setValue(min(atual, meta))

    def atualizar_timer(self, segundos: int):
        minutos = segundos // 60
        segs = segundos % 60
        texto = f"⏱ {minutos}:{segs:02d}"
        if segundos < 30:
            cor = "#ff4444"
        else:
            cor = estilos.AMBAR
        self._label_timer.setText(texto)
        self._label_timer.setStyleSheet(f"color: {cor}; font-weight: bold; font-size: 16px; border: none; background: transparent;")
