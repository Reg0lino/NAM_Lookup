from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from core.search_builder import execute_gear_search, open_in_browser
from ui.metadata_dialog import MetadataDialog


class HardwareChipsContainer(QWidget):
    """Container for primary hardware chips, dedicated metadata tools row, and candidate hints."""

    deep_search_requested = pyqtSignal()
    favorite_toggled = pyqtSignal(bool)
    notes_updated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filename = ""
        self.internal_metadata = {}
        self.user_notes = ""
        self.is_favorite = False

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(8)

        # Line 1: Primary Hardware Chips
        self.primary_widget = QWidget()
        self.primary_layout = QHBoxLayout(self.primary_widget)
        self.primary_layout.setContentsMargins(0, 0, 0, 0)
        self.primary_layout.setSpacing(8)
        self.primary_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.primary_widget)

        # Line 2: Dedicated Metadata & Capture Tools Row
        self.tools_widget = QWidget()
        self.tools_layout = QHBoxLayout(self.tools_widget)
        self.tools_layout.setContentsMargins(0, 2, 0, 0)
        self.tools_layout.setSpacing(8)
        self.tools_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.tools_widget)

        # Line 3: Candidate Terms Row
        self.candidate_widget = QWidget()
        self.candidate_layout = QHBoxLayout(self.candidate_widget)
        self.candidate_layout.setContentsMargins(0, 2, 0, 0)
        self.candidate_layout.setSpacing(6)
        self.candidate_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.candidate_widget)

    def clear_chips(self):
        """Removes all existing chip buttons across all 3 rows."""
        for layout in [self.primary_layout, self.tools_layout, self.candidate_layout]:
            while layout.count():
                item = layout.takeAt(0)
                if widget := item.widget():
                    widget.deleteLater()

    def render_chips(
        self,
        components: list,
        candidate_terms: list = None,
        tone3000_url: str = "",
        tone3000_matched: bool = False,
        internal_metadata: dict = None,
        filename: str = "",
        user_notes: str = "",
        is_favorite: bool = False,
        search_engine_provider=None,
        demo_mode_provider=None,
    ):
        """Populates dynamic chips across 3 dedicated rows."""
        self.clear_chips()
        self.filename = filename
        self.internal_metadata = internal_metadata or {}
        self.user_notes = user_notes
        self.is_favorite = is_favorite

        def get_engine() -> str:
            return search_engine_provider() if search_engine_provider else "Google"

        def get_demo_state() -> bool:
            return demo_mode_provider() if demo_mode_provider else False

        # --- LINE 1: Primary AI Extracted Hardware Chips ---
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
            btn.clicked.connect(
                lambda _, q=query: execute_gear_search(
                    q, search_engine=get_engine(), demo_mode=get_demo_state()
                )
            )
            self.primary_layout.addWidget(btn)

        # --- LINE 2: Dedicated Metadata & Capture Tools Row ---
        tools_lbl = QLabel("Capture Tools:")
        tools_lbl.setStyleSheet(
            "color: #888888; font-size: 11px; font-weight: bold;")
        self.tools_layout.addWidget(tools_lbl)

        if self.internal_metadata:
            meta_btn = QPushButton("📄 View NAM Metadata")
            meta_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E293B;
                    border: 1px solid #334155;
                    color: #38BDF8;
                    border-radius: 6px;
                    padding: 5px 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #334155; }
            """)
            meta_btn.setToolTip(
                "View internal JSON metadata embedded in this .nam file")
            meta_btn.clicked.connect(self.show_metadata_dialog)
            self.tools_layout.addWidget(meta_btn)

        if tone3000_matched and tone3000_url:
            t3k_btn = QPushButton("🌐 View on Tone3000")
            t3k_btn.setObjectName("Tone3000Button")
            t3k_btn.setToolTip("Open matched capture page on Tone3000")
            t3k_btn.clicked.connect(
                lambda _, url=tone3000_url: open_in_browser(url))
            self.tools_layout.addWidget(t3k_btn)
        else:
            deep_btn = QPushButton("🔍 Deep Tone3000 Search")
            deep_btn.setToolTip(
                "Break down search query into individual phrases and search Tone3000")
            deep_btn.clicked.connect(lambda: self.deep_search_requested.emit())
            self.tools_layout.addWidget(deep_btn)

        fav_btn = QPushButton(
            "⭐ Favorited" if self.is_favorite else "⭐ Add to Favorites")
        fav_style = """
            QPushButton {
                background-color: #78350F;
                border: 1px solid #F59E0B;
                color: #FCD34D;
                border-radius: 6px;
                padding: 5px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #92400E; }
        """ if self.is_favorite else """
            QPushButton {
                background-color: #262626;
                border: 1px solid #404040;
                color: #A3A3A3;
                border-radius: 6px;
                padding: 5px 12px;
            }
            QPushButton:hover { background-color: #333333; color: #FFFFFF; }
        """
        fav_btn.setStyleSheet(fav_style)
        fav_btn.clicked.connect(self.on_favorite_clicked)
        self.tools_layout.addWidget(fav_btn)

        # --- LINE 3: Candidate Terms Row ---
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
                    lambda _, t=term: execute_gear_search(
                        t, search_engine=get_engine(), demo_mode=get_demo_state()
                    )
                )
                self.candidate_layout.addWidget(cand_btn)

    def on_favorite_clicked(self):
        self.is_favorite = not self.is_favorite
        self.favorite_toggled.emit(self.is_favorite)

    def show_metadata_dialog(self):
        """Opens the Metadata Inspector QDialog modal."""
        if self.internal_metadata:
            dialog = MetadataDialog(
                self.filename, self.internal_metadata, user_notes=self.user_notes, parent=self
            )
            dialog.notes_saved.connect(
                lambda notes: self.notes_updated.emit(notes))
            dialog.exec()
