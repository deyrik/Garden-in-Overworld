from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from . import estilos

NOMES_CULTURA = {3: "Trigo", 4: "Arroz", 6: "Cana", 10: "Milho", 11: "Batata", 12: "Tomate"}
EMOJIS_CULTURA = {3: "🌾", 4: "🌿", 6: "🎋", 10: "🌽", 11: "🥔", 12: "🍅"}

class WidgetHUD(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self.setStyleSheet(f"background-color: #0d1117; border-bottom: 2px solid {estilos.DESTAQUE};")
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(16, 6, 16, 6)
        self._layout.setSpacing(20)

        self._label_temporada = QLabel("🌱 —")
        self._label_temporada.setStyleSheet(
            f"color: {estilos.DESTAQUE}; font-weight: bold; font-size: 14px; border: none; background: transparent;"
        )
        self._layout.addWidget(self._label_temporada)

        sep = QLabel("|")
        sep.setStyleSheet("color: #444; border: none; background: transparent;")
        self._layout.addWidget(sep)

        lbl_meta = QLabel("META:")
        lbl_meta.setStyleSheet("color: #888; font-size: 11px; letter-spacing: 1px; border: none; background: transparent;")
        self._layout.addWidget(lbl_meta)

        self._barras = {}
        self._container_barras = QWidget()
        self._container_barras.setStyleSheet("background: transparent; border: none;")
        self._layout_barras = QHBoxLayout(self._container_barras)
        self._layout_barras.setContentsMargins(0, 0, 0, 0)
        self._layout_barras.setSpacing(12)
        self._layout.addWidget(self._container_barras, stretch=1)

        self._label_timer = QLabel("--:--")
        self._label_timer.setStyleSheet(
            f"color: {estilos.AMBAR}; font-weight: bold; font-size: 18px; border: none; background: transparent;"
        )
        self._label_timer.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._layout.addWidget(self._label_timer)

    def atualizar_temporada(self, dados: dict):
        nome = dados.get("nome", "")
        numero = dados.get("temporada", 1)
        self._label_temporada.setText(f"🌱 {nome} — T{numero}")

        demanda = dados.get("demanda", {})
        # Limpar barras antigas de forma síncrona
        while self._layout_barras.count():
            item = self._layout_barras.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        self._barras.clear()

        for cultura_str, meta in demanda.items():
            cultura = int(cultura_str)
            emoji = EMOJIS_CULTURA.get(cultura, "?")
            nome = NOMES_CULTURA.get(cultura, str(cultura))

            bloco = QWidget()
            bloco.setStyleSheet("background: transparent; border: none;")
            bl = QVBoxLayout(bloco)
            bl.setContentsMargins(0, 0, 0, 0)
            bl.setSpacing(2)

            lbl = QLabel(f"{emoji} {nome}  0/{meta}")
            lbl.setStyleSheet("color: #e0e0e0; font-size: 12px; font-weight: bold; border: none; background: transparent;")

            barra = QProgressBar()
            barra.setRange(0, meta)
            barra.setValue(0)
            barra.setFixedHeight(6)
            barra.setTextVisible(False)
            barra.setStyleSheet(
                "QProgressBar { background: #333; border-radius: 3px; border: none; }"
                f"QProgressBar::chunk {{ background: {estilos.DESTAQUE}; border-radius: 3px; }}"
            )

            bl.addWidget(lbl)
            bl.addWidget(barra)
            self._layout_barras.addWidget(bloco)
            self._barras[cultura] = (lbl, barra, meta)

    def atualizar_progresso(self, progresso: dict, demanda: dict):
        for cultura_str, atual in progresso.items():
            cultura = int(cultura_str)
            if cultura not in self._barras:
                continue
            lbl, barra, meta = self._barras[cultura]
            emoji = EMOJIS_CULTURA.get(cultura, "?")
            nome = NOMES_CULTURA.get(cultura, str(cultura))
            concluido = atual >= meta
            cor = estilos.DESTAQUE if concluido else "#e0e0e0"
            sufixo = " ✓" if concluido else ""
            lbl.setText(f"{emoji} {nome}  {atual}/{meta}{sufixo}")
            lbl.setStyleSheet(f"color: {cor}; font-size: 12px; font-weight: bold; border: none; background: transparent;")
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
