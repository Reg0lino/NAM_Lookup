import json
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class MetadataDialog(QDialog):
    """Sleek dark-mode modal dialog displaying internal .nam JSON metadata and editable user notes."""

    notes_saved = pyqtSignal(str)

    def __init__(self, filename: str, metadata: dict, user_notes: str = "", parent=None):
        super().__init__(parent)
        self.filename = filename
        self.metadata = metadata
        self.user_notes = user_notes

        self.setWindowTitle(f"Internal Metadata: {filename}")
        self.setMinimumSize(540, 480)
        self.setStyleSheet("""
            QDialog {
                background-color: #161616;
                color: #E0E0E0;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#TitleLabel {
                font-size: 15px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QLabel#NotesHeader {
                font-size: 12px;
                font-weight: bold;
                color: #38BDF8;
                margin-top: 6px;
            }
            QTableWidget {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 6px;
                gridline-color: #2D2D2D;
                color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #262626;
                color: #007ACC;
                font-weight: bold;
                border: none;
                padding: 6px;
            }
            QPlainTextEdit#NotesInput {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 6px;
                color: #FFFFFF;
                font-size: 12px;
            }
            QPushButton {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 6px;
                padding: 6px 14px;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #383838;
            }
            QPushButton#SaveNotesBtn {
                background-color: #0284C7;
                border: none;
                font-weight: bold;
            }
            QPushButton#SaveNotesBtn:hover {
                background-color: #0369A1;
            }
        """)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel(f"📄 Embedded JSON Metadata ({self.filename})")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # Key-Value Metadata Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Attribute", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)

        key_labels = {
            "gear_make": "Gear Make",
            "gear_model": "Gear Model",
            "gear_type": "Gear Category",
            "modeled_by": "Author / Captured By",
            "name": "Model Title",
            "trainer": "Trainer Tool",
            "tone_type": "Sound Characteristics",
            "input_level_dbu": "Input Level (dBu)",
            "output_level_dbu": "Output Level (dBu)",
            "loudness": "Loudness (dBFS)",
            "date": "Date Created",
        }

        self.table.setRowCount(len(self.metadata))
        for row, (k, v) in enumerate(self.metadata.items()):
            display_key = key_labels.get(k, k.replace("_", " ").title())

            if isinstance(v, dict) and "year" in v:
                display_val = f"{v.get('year')}-{v.get('month'):02d}-{v.get('day'):02d} {v.get('hour'):02d}:{v.get('minute'):02d}"
            elif isinstance(v, float):
                display_val = f"{v:.3f}"
            else:
                display_val = str(v)

            item_key = QTableWidgetItem(display_key)
            item_key.setFlags(Qt.ItemFlag.ItemIsEnabled |
                              Qt.ItemFlag.ItemIsSelectable)

            item_val = QTableWidgetItem(display_val)
            item_val.setFlags(Qt.ItemFlag.ItemIsEnabled |
                              Qt.ItemFlag.ItemIsSelectable)

            self.table.setItem(row, 0, item_key)
            self.table.setItem(row, 1, item_val)

        layout.addWidget(self.table)

        # Editable Personal Notes Section
        notes_header = QLabel("📝 Personal Capture Notes:")
        notes_header.setObjectName("NotesHeader")
        layout.addWidget(notes_header)

        self.notes_input = QPlainTextEdit()
        self.notes_input.setObjectName("NotesInput")
        self.notes_input.setPlaceholderText(
            "Enter your custom notes for this profile (e.g. 'Great for Les Paul bridge pickup')...")
        self.notes_input.setPlainText(self.user_notes)
        self.notes_input.setMaximumHeight(80)
        layout.addWidget(self.notes_input)

        # Buttons
        btn_layout = QHBoxLayout()
        copy_btn = QPushButton("📋 Copy Raw JSON")
        copy_btn.clicked.connect(self.copy_metadata)

        save_notes_btn = QPushButton("💾 Save Notes")
        save_notes_btn.setObjectName("SaveNotesBtn")
        save_notes_btn.clicked.connect(self.on_save_notes_clicked)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(copy_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_notes_btn)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def on_save_notes_clicked(self):
        new_notes = self.notes_input.toPlainText().strip()
        self.notes_saved.emit(new_notes)

    def copy_metadata(self):
        text_str = json.dumps(self.metadata, indent=2)
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(text_str)
