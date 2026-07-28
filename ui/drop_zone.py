from pathlib import Path
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class DropZone(QFrame):
    """Interactive drag-and-drop widget for accepting .nam files."""

    file_dropped = pyqtSignal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel("Drag & Drop Neural Amp Modeler (.nam) File")
        self.title.setObjectName("DropTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle = QLabel(
            "Extracts physical hardware (amps, cabs, pedals, mics) & searches physical gear"
        )
        self.subtitle.setObjectName("DropSubtitle")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)

        self.setMinimumSize(QSize(400, 110))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".nam"):
                    event.acceptProposedAction()
                    self.setProperty("dragOver", "true")
                    self.style().unpolish(self)
                    self.style().polish(self)
                    return
        event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.setProperty("dragOver", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragOver", "false")
        self.style().unpolish(self)
        self.style().polish(self)

        for url in event.mimeData().urls():
            file_path = Path(url.toLocalFile())
            if file_path.suffix.lower() == ".nam":
                self.file_dropped.emit(file_path)
                event.acceptProposedAction()
                return
