from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from core.search_builder import execute_hardware_search, open_in_browser


class HardwareChipsContainer(QWidget):
    """Container for primary hardware chips and candidate search hints."""

    deep_search_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(8)

        # Primary Row
        self.primary_widget = QWidget()
        self.primary_layout = QHBoxLayout(self.primary_widget)
        self.primary_layout.setContentsMargins(0, 0, 0, 0)
        self.primary_layout.setSpacing(8)
        self.primary_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.primary_widget)

        # Candidate Terms Row
        self.candidate_widget = QWidget()
        self.candidate_layout = QHBoxLayout(self.candidate_widget)
        self.candidate_layout.setContentsMargins(0, 4, 0, 0)
        self.candidate_layout.setSpacing(6)
        self.candidate_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.candidate_widget)

    def clear_chips(self):
        """Removes all existing chip buttons."""
        while self.primary_layout.count():
            item = self.primary_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        while self.candidate_layout.count():
            item = self.candidate_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

    def render_chips(
        self,
        components: list,
        candidate_terms: list = None,
        tone3000_url: str = "",
        tone3000_matched: bool = False,
    ):
        """Populates dynamic chips for extracted hardware components and candidate hints."""
        self.clear_chips()

        # 1. Primary Row Rendering
        if tone3000_matched and tone3000_url:
            t3k_btn = QPushButton("🌐 View on Tone3000")
            t3k_btn.setObjectName("Tone3000Button")
            t3k_btn.setToolTip("Open matched capture page on Tone3000")
            t3k_btn.clicked.connect(
                lambda _, url=tone3000_url: open_in_browser(url))
            self.primary_layout.addWidget(t3k_btn)
        else:
            deep_btn = QPushButton("🔍 Deep Tone3000 Search")
            deep_btn.setToolTip(
                "Break down search query into individual phrases and search Tone3000")
            deep_btn.clicked.connect(lambda: self.deep_search_requested.emit())
            self.primary_layout.addWidget(deep_btn)

        type_icons = {
            "amplifier": "🔊",
            "amp": "🔊",
            "cabinet": "📢",
            "cab": "📢",
            "pedal": "🎛️",
            "overdrive": "🎛️",
            "microphone": "🎙️",
            "mic": "🎙️",
        }

        for comp in components:
            gear_type = comp.get("type", "Hardware")
            query = comp.get("query", "")

            if not query:
                continue

            icon = "🎸"
            type_lower = gear_type.lower()
            for key, emoji in type_icons.items():
                if key in type_lower:
                    icon = emoji
                    break

            btn = QPushButton(f"{icon} {query}")
            btn.setProperty("class", "HardwareChip")
            btn.setToolTip(f"Search physical {gear_type}: '{query}'")
            btn.clicked.connect(lambda _, q=query: execute_hardware_search(q))
            self.primary_layout.addWidget(btn)

        # 2. Candidate Terms Row Rendering
        if candidate_terms:
            lbl = QLabel("Candidate Terms:")
            lbl.setStyleSheet(
                "color: #888888; font-size: 11px; font-weight: bold;")
            self.candidate_layout.addWidget(lbl)

            for term in candidate_terms[:5]:
                if not term:
                    continue
                cand_btn = QPushButton(f"🔎 {term}")
                cand_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1A222D;
                        border: 1px solid #2B384A;
                        border-radius: 12px;
                        padding: 3px 10px;
                        font-size: 11px;
                        color: #90CDF4;
                    }
                    QPushButton:hover {
                        background-color: #2B384A;
                        color: #FFFFFF;
                    }
                """)
                cand_btn.setToolTip(f"Search candidate phrase: '{term}'")
                cand_btn.clicked.connect(
                    lambda _, t=term: execute_hardware_search(t))
                self.candidate_layout.addWidget(cand_btn)
