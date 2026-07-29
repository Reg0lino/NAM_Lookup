from datetime import datetime
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
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

from core.cache_manager import (
    clear_cache,
    get_recent_history,
    update_cache_entry_notes_and_favorite,
)
from core.config_manager import load_config, save_config, get_api_key
from core.search_builder import execute_gear_search
from ui.drop_zone import DropZone
from ui.hardware_chips import HardwareChipsContainer
from ui.worker_thread import HardwareAnalysisWorker


class MainWindow(QMainWindow):
    """Main application window powered by Groq Llama 3.3 and Tone3000."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NAM Hardware Finder")
        self.setMinimumSize(820, 720)

        self.current_file_path = None
        self.current_notes = ""
        self.current_is_favorite = False
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
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # 1. Drop Zone Widget
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self.process_file)
        self.drop_zone.clicked.connect(self.browse_for_file)
        main_layout.addWidget(self.drop_zone)

        # 2. Status Label
        self.status_label = QLabel(
            "Status: Ready (Drag & drop or click box to open a .nam file)")
        self.status_label.setObjectName("StatusLabel")
        main_layout.addWidget(self.status_label)

        # 3. Capture Filter & History Bar
        history_layout = QHBoxLayout()
        history_layout.addWidget(QLabel("🔍 Filter Captures:"))

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText(
            "Type fuzzy search (e.g. 'badland', '5150')...")
        self.filter_input.setToolTip(
            "Type fuzzy keywords (e.g., 'badland', '5150') to filter recent captures in real-time")
        self.filter_input.textChanged.connect(self.refresh_history_dropdown)
        history_layout.addWidget(self.filter_input)

        self.fav_only_checkbox = QCheckBox("⭐ Favorites Only")
        self.fav_only_checkbox.setToolTip(
            "Filter dropdown list to show exclusively favorited captures")
        self.fav_only_checkbox.stateChanged.connect(
            self.refresh_history_dropdown)
        history_layout.addWidget(self.fav_only_checkbox)

        history_layout.addWidget(QLabel("🕒 History:"))
        self.history_combo = QComboBox()
        self.history_combo.setMinimumWidth(220)
        self.history_combo.setToolTip(
            "Select a previously analyzed capture to restore its search queries, metadata, and notes")
        self.history_combo.currentIndexChanged.connect(
            self.on_history_selected)
        history_layout.addWidget(self.history_combo)

        main_layout.addLayout(history_layout)

        # 4. Primary Search Query Box with Engine Switch & DEMO Toggle
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Primary Hardware Search Query...")
        self.search_input.setToolTip(
            "Editable combined search query containing all identified hardware components")
        self.search_input.returnPressed.connect(self.on_search_clicked)

        # Engine Switch Button (Google vs YouTube)
        self.engine_toggle_btn = QPushButton("🔍 Engine: Google")
        self.engine_toggle_btn.setToolTip(
            "Switch target search engine between Google (for physical gear web results) and YouTube (for video/audio reviews)")
        self.engine_toggle_btn.setCheckable(True)
        self.engine_toggle_btn.clicked.connect(self.on_engine_toggle_changed)

        # DEMO Toggle Button
        self.demo_toggle_btn = QPushButton("🎥 DEMO: OFF")
        self.demo_toggle_btn.setToolTip(
            "Toggle DEMO mode ON to automatically append 'DEMO' to all gear search queries")
        self.demo_toggle_btn.setCheckable(True)
        self.demo_toggle_btn.clicked.connect(self.on_demo_toggle_changed)

        self.search_btn = QPushButton("Search Gear")
        self.search_btn.setObjectName("PrimaryButton")
        self.search_btn.setToolTip(
            "Executes a web search for the entire primary search string using the active search engine")
        self.search_btn.clicked.connect(self.on_search_clicked)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.engine_toggle_btn)
        search_layout.addWidget(self.demo_toggle_btn)
        search_layout.addWidget(self.search_btn)
        main_layout.addLayout(search_layout)

        # 5. Hardware Action Chips Container (3 Rows)
        self.chips_container = HardwareChipsContainer()
        self.chips_container.deep_search_requested.connect(
            self.trigger_deep_tone3000_search)
        self.chips_container.favorite_toggled.connect(self.on_favorite_toggled)
        self.chips_container.notes_updated.connect(self.on_notes_saved)
        main_layout.addWidget(self.chips_container)

        # 6. Inline Personal User Notes Bar
        notes_layout = QHBoxLayout()
        notes_layout.addWidget(QLabel("📝 Personal Notes:"))
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText(
            "Add custom notes (e.g. 'Great rhythm tone on Les Paul bridge pickup')...")
        self.notes_input.setToolTip(
            "Custom personal notes saved locally for this capture profile")
        self.notes_input.returnPressed.connect(self.save_current_notes)
        notes_layout.addWidget(self.notes_input)

        save_notes_btn = QPushButton("💾 Save")
        save_notes_btn.setToolTip("Save personal notes for this capture")
        save_notes_btn.clicked.connect(self.save_current_notes)
        notes_layout.addWidget(save_notes_btn)
        main_layout.addLayout(notes_layout)

        # 7. Config / Settings Group Box
        settings_group = QGroupBox("Groq & App Settings")
        settings_layout = QVBoxLayout(settings_group)

        groq_layout = QHBoxLayout()
        groq_layout.addWidget(QLabel("Groq API Key:"))
        self.groq_key_input = QLineEdit()
        self.groq_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.groq_key_input.setPlaceholderText(
            "Enter Groq API key (gsk_...)...")
        self.groq_key_input.setToolTip(
            "Enter your free Groq API Key from console.groq.com")
        groq_layout.addWidget(self.groq_key_input)

        test_keys_btn = QPushButton("⚡ Test Groq Key")
        test_keys_btn.setToolTip("Test API connection to Groq Llama 3.3 model")
        test_keys_btn.clicked.connect(self.test_api_connection)
        groq_layout.addWidget(test_keys_btn)

        settings_layout.addLayout(groq_layout)

        bottom_settings = QHBoxLayout()
        self.cache_checkbox = QCheckBox("Enable Local Caching")
        self.cache_checkbox.setToolTip(
            "Store analysis results locally in cache.json to avoid repeating API calls")
        self.t3k_checkbox = QCheckBox("Enable Tone3000 Search")
        self.t3k_checkbox.setToolTip(
            "Lookup capture metadata online on Tone3000")

        clear_cache_btn = QPushButton("🗑️ Clear Cache")
        clear_cache_btn.setToolTip("Wipe local response cache in cache.json")
        clear_cache_btn.clicked.connect(self.on_clear_cache_clicked)

        save_btn = QPushButton("Save Settings")
        save_btn.setToolTip("Save configuration to config.json")
        save_btn.clicked.connect(self.save_settings_from_ui)

        bottom_settings.addWidget(self.cache_checkbox)
        bottom_settings.addWidget(self.t3k_checkbox)
        bottom_settings.addWidget(clear_cache_btn)
        bottom_settings.addStretch()
        bottom_settings.addWidget(save_btn)

        settings_layout.addLayout(bottom_settings)
        main_layout.addWidget(settings_group)

        # 8. Debug Console Section
        debug_header = QHBoxLayout()
        self.toggle_debug_btn = QPushButton("🛠️ Toggle Debug Console")
        self.toggle_debug_btn.setToolTip(
            "Expand/collapse live event and API logs console")
        self.toggle_debug_btn.setCheckable(True)
        self.toggle_debug_btn.setChecked(True)
        self.toggle_debug_btn.clicked.connect(self.toggle_debug_console)

        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.setToolTip("Clear text from debug console")
        clear_logs_btn.clicked.connect(self.clear_logs)

        copy_logs_btn = QPushButton("Copy Logs")
        copy_logs_btn.setToolTip("Copy debug console output to clipboard")
        copy_logs_btn.clicked.connect(self.copy_logs)

        debug_header.addWidget(self.toggle_debug_btn)
        debug_header.addStretch()
        debug_header.addWidget(clear_logs_btn)
        debug_header.addWidget(copy_logs_btn)
        main_layout.addLayout(debug_header)

        self.debug_console = QPlainTextEdit()
        self.debug_console.setObjectName("DebugConsole")
        self.debug_console.setReadOnly(True)
        self.debug_console.setMaximumHeight(130)
        main_layout.addWidget(self.debug_console)

    def browse_for_file(self):
        config = load_config()
        initial_dir = config.get(
            "last_open_directory", r"I:\Assorted Synth & DAW\!NAM")

        if not Path(initial_dir).exists():
            initial_dir = str(Path.home())

        file_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Select Neural Amp Modeler (.nam) File",
            initial_dir,
            "NAM Files (*.nam);;All Files (*)",
        )

        if file_path_str:
            file_path = Path(file_path_str)
            config["last_open_directory"] = str(file_path.parent.resolve())
            save_config(config)
            self.process_file(file_path)

    def update_engine_btn_style(self):
        """Updates Engine switch button styling (Blue for Google, Red for YouTube)."""
        if self.engine_toggle_btn.isChecked():
            self.engine_toggle_btn.setText("▶️ Engine: YouTube")
            self.engine_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #991B1B;
                    border: 1px solid #DC2626;
                    color: #FFFFFF;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 6px 14px;
                }
                QPushButton:hover { background-color: #DC2626; }
            """)
        else:
            self.engine_toggle_btn.setText("🔍 Engine: Google")
            self.engine_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E293B;
                    border: 1px solid #0284C7;
                    color: #38BDF8;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 6px 14px;
                }
                QPushButton:hover { background-color: #0284C7; color: #FFFFFF; }
            """)

    def on_engine_toggle_changed(self):
        self.update_engine_btn_style()
        engine = "YouTube" if self.engine_toggle_btn.isChecked() else "Google"
        self.log_debug(f"Search Engine switched to: {engine}")
        self.save_settings_from_ui()

    def update_demo_btn_style(self):
        if self.demo_toggle_btn.isChecked():
            self.demo_toggle_btn.setText("🎥 DEMO: ON")
            self.demo_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #D97706;
                    border: 1px solid #F59E0B;
                    color: #FFFFFF;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 6px 14px;
                }
                QPushButton:hover { background-color: #F59E0B; }
            """)
        else:
            self.demo_toggle_btn.setText("🎥 DEMO: OFF")
            self.demo_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2D2D2D;
                    border: 1px solid #3D3D3D;
                    color: #A0A0A0;
                    border-radius: 6px;
                    padding: 6px 14px;
                }
                QPushButton:hover { background-color: #383838; color: #FFFFFF; }
            """)

    def on_demo_toggle_changed(self):
        self.update_demo_btn_style()
        is_on = self.demo_toggle_btn.isChecked()
        self.log_debug(f"DEMO Mode toggled: {'ON' if is_on else 'OFF'}")
        self.save_settings_from_ui()

    def get_current_search_engine(self) -> str:
        return "YouTube" if self.engine_toggle_btn.isChecked() else "Google"

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
        filter_text = self.filter_input.text().strip()
        fav_only = self.fav_only_checkbox.isChecked()

        self.history_combo.blockSignals(True)
        self.history_combo.clear()
        self.history_items = get_recent_history(
            filter_text=filter_text, favorites_only=fav_only)

        if not self.history_items:
            self.history_combo.addItem("No Matching Captures")
            self.history_combo.setEnabled(False)
        else:
            self.history_combo.setEnabled(True)
            label_suffix = "Favorites" if fav_only else "History"
            self.history_combo.addItem(
                f"-- Select {label_suffix} ({len(self.history_items)}) --")
            for item in self.history_items:
                fname = item.get("filename", "Unknown")
                ts = item.get("timestamp", "")
                is_fav = item.get("is_favorite", False)
                fav_star = "⭐ " if is_fav else ""
                label = f"{fav_star}{fname} ({ts[11:16]})" if ts else f"{fav_star}{fname}"
                self.history_combo.addItem(label)

        self.history_combo.blockSignals(False)

    def on_history_selected(self, index: int):
        if index <= 0 or not self.history_items:
            return

        selected_entry = self.history_items[index - 1]
        fname = selected_entry.get("filename", "")
        fpath_str = selected_entry.get("file_path", "")
        if fpath_str:
            self.current_file_path = Path(fpath_str)

        extraction = selected_entry.get("extraction", {})
        self.current_notes = selected_entry.get("user_notes", "")
        self.current_is_favorite = selected_entry.get("is_favorite", False)

        self.notes_input.setText(self.current_notes)
        self.log_debug(f"Loaded '{fname}' from Cache History.")
        self.status_label.setText(
            f"Status: Loaded '{fname}' from Cache History.")

        primary_search = extraction.get("primary_search", "")
        self.search_input.setText(primary_search)

        components = extraction.get("hardware_components", [])
        candidate_terms = extraction.get("candidate_terms", [])
        internal_metadata = extraction.get("internal_metadata", {})
        tone3000_url = extraction.get("tone3000_url", "")

        self.chips_container.render_chips(
            components,
            candidate_terms,
            tone3000_url,
            extraction.get("tone3000_matched", False),
            internal_metadata,
            fname,
            user_notes=self.current_notes,
            is_favorite=self.current_is_favorite,
            search_engine_provider=self.get_current_search_engine,
            demo_mode_provider=lambda: self.demo_toggle_btn.isChecked(),
        )

    def on_favorite_toggled(self, is_fav: bool):
        self.current_is_favorite = is_fav
        if self.current_file_path:
            update_cache_entry_notes_and_favorite(
                self.current_file_path, is_favorite=is_fav)
            fav_str = "added to ⭐ Favorites" if is_fav else "removed from Favorites"
            self.log_debug(
                f"Capture '{self.current_file_path.name}' {fav_str}.")
            self.refresh_history_dropdown()

    def save_current_notes(self):
        notes_text = self.notes_input.text().strip()
        self.on_notes_saved(notes_text)

    def on_notes_saved(self, notes_text: str):
        self.current_notes = notes_text
        self.notes_input.setText(notes_text)
        if self.current_file_path:
            update_cache_entry_notes_and_favorite(
                self.current_file_path, user_notes=notes_text)
            self.log_debug(f"Saved notes for '{self.current_file_path.name}'.")
            self.status_label.setText("Status: Personal notes saved.")
            self.refresh_history_dropdown()

    def _load_settings_into_ui(self):
        config = load_config()
        self.groq_key_input.setText(config.get("groq_api_key", ""))
        self.cache_checkbox.setChecked(config.get("enable_cache", True))
        self.t3k_checkbox.setChecked(config.get("enable_tone3000", True))

        is_demo_on = config.get("enable_demo_mode", False)
        self.demo_toggle_btn.setChecked(is_demo_on)
        self.update_demo_btn_style()

        engine_setting = config.get("search_engine", "Google")
        is_yt = engine_setting.lower() == "youtube"
        self.engine_toggle_btn.setChecked(is_yt)
        self.update_engine_btn_style()

    def save_settings_from_ui(self):
        config = load_config()
        config["groq_api_key"] = self.groq_key_input.text().strip()
        config["enable_cache"] = self.cache_checkbox.isChecked()
        config["enable_tone3000"] = self.t3k_checkbox.isChecked()
        config["enable_demo_mode"] = self.demo_toggle_btn.isChecked()
        config["search_engine"] = self.get_current_search_engine()

        if save_config(config):
            self.status_label.setText("Status: Settings saved successfully.")

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
        internal_metadata = result.get("internal_metadata", {})
        tone3000_url = result.get("tone3000_url", "")
        matched = result.get("tone3000_matched", False)

        self.current_notes = result.get("user_notes", "")
        self.current_is_favorite = result.get("is_favorite", False)
        self.notes_input.setText(self.current_notes)

        filename = self.current_file_path.name if self.current_file_path else ""

        self.chips_container.render_chips(
            components,
            candidate_terms,
            tone3000_url,
            matched,
            internal_metadata,
            filename,
            user_notes=self.current_notes,
            is_favorite=self.current_is_favorite,
            search_engine_provider=self.get_current_search_engine,
            demo_mode_provider=lambda: self.demo_toggle_btn.isChecked(),
        )

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
            execute_gear_search(
                query,
                search_engine=self.get_current_search_engine(),
                demo_mode=self.demo_toggle_btn.isChecked(),
            )
