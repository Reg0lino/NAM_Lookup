from datetime import datetime
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.cache_manager import clear_cache, get_recent_history
from core.config_manager import load_config, save_config, get_api_key
from core.search_builder import execute_hardware_search
from ui.drop_zone import DropZone
from ui.hardware_chips import HardwareChipsContainer
from ui.worker_thread import HardwareAnalysisWorker


class MainWindow(QMainWindow):
    """Main application window powered by Groq Llama 3.3 and Tone3000."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NAM Hardware Finder")
        self.setMinimumSize(740, 640)

        self.current_file_path = None
        self.worker = None
        self.history_items = []

        self._init_ui()
        self._load_settings_into_ui()
        self.refresh_history_dropdown()
        self.log_debug("Application started. Powered by Groq AI.")

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # 1. Drop Zone Widget
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self.process_file)
        main_layout.addWidget(self.drop_zone)

        # 2. Status Indicator & History Dropdown Row
        history_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Ready (Drag and drop a .nam file)")
        self.status_label.setObjectName("StatusLabel")
        history_layout.addWidget(self.status_label)
        history_layout.addStretch()

        history_layout.addWidget(QLabel("🕒 Recent Captures:"))
        self.history_combo = QComboBox()
        self.history_combo.setMinimumWidth(220)
        self.history_combo.currentIndexChanged.connect(
            self.on_history_selected)
        history_layout.addWidget(self.history_combo)

        main_layout.addLayout(history_layout)

        # 3. Primary Search Query Box
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Primary Hardware Search Query...")
        self.search_input.returnPressed.connect(self.on_search_clicked)

        self.search_btn = QPushButton("Search All Gear")
        self.search_btn.setObjectName("PrimaryButton")
        self.search_btn.clicked.connect(self.on_search_clicked)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        main_layout.addLayout(search_layout)

        # 4. Hardware Action Chips Container
        self.chips_container = HardwareChipsContainer()
        self.chips_container.deep_search_requested.connect(
            self.trigger_deep_tone3000_search)
        main_layout.addWidget(self.chips_container)

        # 5. Config / Settings Group Box
        settings_group = QGroupBox("Groq & App Settings")
        settings_layout = QVBoxLayout(settings_group)

        # Groq Key Input
        groq_layout = QHBoxLayout()
        groq_layout.addWidget(QLabel("Groq API Key:"))
        self.groq_key_input = QLineEdit()
        self.groq_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.groq_key_input.setPlaceholderText(
            "Enter Groq API key (gsk_...)...")
        groq_layout.addWidget(self.groq_key_input)

        test_keys_btn = QPushButton("⚡ Test Groq Key")
        test_keys_btn.clicked.connect(self.test_api_connection)
        groq_layout.addWidget(test_keys_btn)

        settings_layout.addLayout(groq_layout)

        # Toggles, Clear Cache, Save Settings
        bottom_settings = QHBoxLayout()
        self.cache_checkbox = QCheckBox("Enable Local Caching")
        self.t3k_checkbox = QCheckBox("Enable Tone3000 Search")

        clear_cache_btn = QPushButton("🗑️ Clear Cache")
        clear_cache_btn.clicked.connect(self.on_clear_cache_clicked)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings_from_ui)

        bottom_settings.addWidget(self.cache_checkbox)
        bottom_settings.addWidget(self.t3k_checkbox)
        bottom_settings.addWidget(clear_cache_btn)
        bottom_settings.addStretch()
        bottom_settings.addWidget(save_btn)

        settings_layout.addLayout(bottom_settings)
        main_layout.addWidget(settings_group)

        # 6. Debug Console Section
        debug_header = QHBoxLayout()
        self.toggle_debug_btn = QPushButton("🛠️ Toggle Debug Console")
        self.toggle_debug_btn.setCheckable(True)
        self.toggle_debug_btn.setChecked(True)
        self.toggle_debug_btn.clicked.connect(self.toggle_debug_console)

        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.clicked.connect(self.clear_logs)

        copy_logs_btn = QPushButton("Copy Logs")
        copy_logs_btn.clicked.connect(self.copy_logs)

        debug_header.addWidget(self.toggle_debug_btn)
        debug_header.addStretch()
        debug_header.addWidget(clear_logs_btn)
        debug_header.addWidget(copy_logs_btn)
        main_layout.addLayout(debug_header)

        self.debug_console = QPlainTextEdit()
        self.debug_console.setObjectName("DebugConsole")
        self.debug_console.setReadOnly(True)
        self.debug_console.setMaximumHeight(140)
        main_layout.addWidget(self.debug_console)

    def log_debug(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.debug_console.appendPlainText(f"[{timestamp}] {message}")

    def toggle_debug_console(self):
        is_visible = self.toggle_debug_btn.isChecked()
        self.debug_console.setVisible(is_visible)

    def clear_logs(self):
        self.debug_console.clear()

    def copy_logs(self):
        self.debug_console.selectAll()
        self.debug_console.copy()
        self.status_label.setText("Status: Logs copied to clipboard.")

    def refresh_history_dropdown(self):
        self.history_combo.blockSignals(True)
        self.history_combo.clear()
        self.history_items = get_recent_history()

        if not self.history_items:
            self.history_combo.addItem("No Recent Captures")
            self.history_combo.setEnabled(False)
        else:
            self.history_combo.setEnabled(True)
            self.history_combo.addItem(
                f"-- Select History ({len(self.history_items)}) --")
            for item in self.history_items:
                fname = item.get("filename", "Unknown")
                ts = item.get("timestamp", "")
                label = f"{fname} ({ts[11:16]})" if ts else fname
                self.history_combo.addItem(label)

        self.history_combo.blockSignals(False)

    def on_history_selected(self, index: int):
        if index <= 0 or not self.history_items:
            return

        selected_entry = self.history_items[index - 1]
        fname = selected_entry.get("filename", "")
        extraction = selected_entry.get("extraction", {})

        self.log_debug(f"Loaded '{fname}' from Cache History.")
        self.status_label.setText(
            f"Status: Loaded '{fname}' from Cache History.")

        primary_search = extraction.get("primary_search", "")
        self.search_input.setText(primary_search)

        components = extraction.get("hardware_components", [])
        candidate_terms = extraction.get("candidate_terms", [])
        tone3000_url = extraction.get("tone3000_url", "")

        self.chips_container.render_chips(
            components, candidate_terms, tone3000_url, extraction.get(
                "tone3000_matched", False)
        )

    def _load_settings_into_ui(self):
        config = load_config()
        self.groq_key_input.setText(config.get("groq_api_key", ""))
        self.cache_checkbox.setChecked(config.get("enable_cache", True))
        self.t3k_checkbox.setChecked(config.get("enable_tone3000", True))

    def save_settings_from_ui(self):
        config = load_config()
        config["groq_api_key"] = self.groq_key_input.text().strip()
        config["enable_cache"] = self.cache_checkbox.isChecked()
        config["enable_tone3000"] = self.t3k_checkbox.isChecked()

        if save_config(config):
            self.status_label.setText("Status: Settings saved successfully.")
            self.log_debug("Settings saved.")

    def on_clear_cache_clicked(self):
        if clear_cache():
            self.status_label.setText("Status: Cache cleared successfully.")
            self.log_debug("Local cache.json cleared.")
            self.refresh_history_dropdown()

    def test_api_connection(self):
        self.save_settings_from_ui()
        self.log_debug("--- TESTING GROQ API KEY ---")

        groq_key = get_api_key("groq_api_key")
        if not groq_key:
            self.log_debug("❌ Groq Test: No API Key entered.")
        else:
            try:
                import requests
                headers = {"Authorization": f"Bearer {groq_key}",
                           "Content-Type": "application/json"}
                data = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": "Ping"}],
                    "max_tokens": 5
                }
                res = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=5)
                if res.status_code == 200:
                    self.log_debug("🟢 Groq Test PASS! API Key active.")
                else:
                    self.log_debug(
                        f"❌ Groq Test FAIL ({res.status_code}): {res.text}")
            except Exception as e:
                self.log_debug(f"❌ Groq Test FAIL: {e}")

    def process_file(self, file_path: Path, deep_mode: bool = False):
        self.current_file_path = file_path
        self.status_label.setText(f"Status: Analyzing '{file_path.name}'...")
        self.chips_container.clear_chips()

        self.log_debug(
            f"--- PROCESSING FILE: {file_path.name} (Deep Mode: {deep_mode}) ---")

        self.worker = HardwareAnalysisWorker(file_path, deep_mode=deep_mode)
        self.worker.log_message.connect(self.log_debug)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def trigger_deep_tone3000_search(self):
        if self.current_file_path:
            self.process_file(self.current_file_path, deep_mode=True)
        else:
            self.status_label.setText("Status: No active file to deep search.")

    def on_analysis_finished(self, result: dict):
        if "error" in result and not result.get("primary_search"):
            self.status_label.setText(f"Error: {result['error']}")
            return

        primary_search = result.get("primary_search", "")
        self.search_input.setText(primary_search)

        components = result.get("hardware_components", [])
        candidate_terms = result.get("candidate_terms", [])
        tone3000_url = result.get("tone3000_url", "")
        matched = result.get("tone3000_matched", False)

        self.chips_container.render_chips(
            components, candidate_terms, tone3000_url, matched)

        match_info = "Tone3000 Matched" if matched else "Groq Extraction"
        self.status_label.setText(
            f"Status: Complete ({match_info}). {len(components)} hardware component(s) identified."
        )
        self.refresh_history_dropdown()

    def on_analysis_error(self, err_msg: str):
        self.status_label.setText(f"Status: Error during analysis - {err_msg}")
        self.log_debug(f"❌ Error: {err_msg}")

    def on_search_clicked(self):
        query = self.search_input.text().strip()
        if query:
            execute_hardware_search(query)
