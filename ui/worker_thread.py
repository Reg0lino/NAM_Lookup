from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

from services.groq_service import extract_hardware_with_groq
from services.nam_parser import parse_nam_file
from services.tone3000_api import query_tone3000, query_tone3000_deep_breakdown


class HardwareAnalysisWorker(QThread):
    """Background worker thread for processing .nam files and API calls."""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    log_message = pyqtSignal(str)

    def __init__(self, file_path: Path, deep_mode: bool = False):
        super().__init__()
        self.file_path = file_path
        self.deep_mode = deep_mode

    def run(self):
        def logger(msg):
            self.log_message.emit(msg)

        try:
            logger(
                f"Starting analysis for: {self.file_path.name} (Deep Mode: {self.deep_mode})")

            # Step 1: Parse local .nam JSON
            nam_data = parse_nam_file(self.file_path)
            logger(
                f"[NAMParser] Stem: '{nam_data.get('stem_name')}', Folder: '{nam_data.get('parent_folder')}'")

            # Step 2: Query Tone3000 API
            if self.deep_mode:
                tone3000_data = query_tone3000_deep_breakdown(
                    nam_data.get("stem_name", ""), logger=logger)
            else:
                tone3000_data = query_tone3000(
                    nam_data.get("stem_name", ""), logger=logger)

            # Step 3: Extract hardware using Groq
            result = extract_hardware_with_groq(
                self.file_path, nam_data, tone3000_data, force_refresh=self.deep_mode, logger=logger
            )

            self.finished.emit(result)

        except Exception as e:
            logger(f"[WorkerError] {e}")
            self.error.emit(str(e))
