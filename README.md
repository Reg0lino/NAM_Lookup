# 🎸 NAM Hardware Finder

**NAM Hardware Finder** is a lightweight Python desktop application (PyQt6) designed for guitarists, bassists, and audio engineers using Neural Amp Modeler (`.nam`).

It analyzes dropped `.nam` capture files, identifies underlying physical gear (amplifiers, cabinets, overdrive pedals, microphones), and launches targeted web searches (or YouTube video reviews) for the physical hardware while automatically filtering out digital capture site clutter (`ToneHunt`, `Tone3000`, NAM forums, etc.).

---

## 📥 Downloads (For Guitarists & End Users)

Download the latest version from the **[GitHub Releases Page](../../releases/latest)**:

- **`NAM_Hardware_Finder_Setup.exe`** (Recommended Windows Installer with Start Menu & Desktop Shortcuts)
- **`NAM_Hardware_Finder_Portable.zip`** (Portable version — extract and run `run_app.bat`)

---

## ✨ Features

- **⚡ Blazing Fast Extraction (Groq AI):** Powered by Groq’s `llama-3.3-70b-versatile` for sub-second context-aware hardware extractions from chaotic creator filenames.
- **🔍 Dual Search Engines (Google & YouTube):**
  - **Google Engine:** Searches Google for physical hardware while appending negative search exclusions (`-NAM -Neural -ToneHunt...`).
  - **YouTube Engine:** Searches YouTube directly for video/audio reviews and gear demos.
- **🎥 DEMO Mode Switch:** Toggle DEMO mode ON to automatically append `"DEMO"` to all gear search queries.
- **🎯 Bass vs. Guitar Context Awareness:** Detects bass profiles (`SVT`, `Ampeg`, `Darkglass`, `Bass`) vs. guitar profiles and formats queries with targeted terms (`guitar cabinet`, `bass cabinet`, `guitar amplifier`, `microphone`).
- **📡 Tone3000 Integration & Deep Search:**
  - **Sanitized Search Query:** Strips knob settings (`Bass 6 Mid 5`) and creator handles before querying Tone3000.
  - **🔍 Deep Tone3000 Search:** Multi-pass phrase search that breaks down complex titles and fetches online metadata.
- **📄 Embedded Metadata Inspector:** Click `[ 📄 View NAM Metadata ]` to view all internal JSON attributes (`gear_make`, `gear_model`, `author`, `dBu levels`, `creation date`) in a clean table modal.
- **📝 Personal Notes System:** Add custom notes to any profile (e.g. *"Great rhythm tone on Les Paul bridge pickup"*), saved locally for future reference.
- **⭐ Favorites System:** Star your favorite captures and filter your history list with one click.
- **🕒 Fuzzy Search History:** Filter your capture history live as you type (stripping brackets `[]`, underscores `_`, and hyphens `-`).
- **📁 Click-to-Browse with Folder Memory:** Click the drop zone to open files directly, automatically remembering your last browsed folder.
- **🛠️ Live Debug Console:** Real-time log stream showing exact local JSON parses, Tone3000 API requests, and Groq AI responses.

---

## 🚀 Developer Setup (Running from Source)

### Prerequisites
- **Python 3.10+**
- A free **Groq API Key** (obtainable from [console.groq.com](https://console.groq.com))

### Installation & Run

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/nam-hardware-finder.git
   cd nam-hardware-finder
   ```

2. **Create and Activate Virtual Environment:**
   ```powershell
   python -m venv venv
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch Application:**
   ```bash
   python main.py
   ```

---

## 📁 Project Structure

```text
nam-hardware-finder/
├── config.json              # Local settings & API key storage (gitignored)
├── cache.json               # Local extraction history, notes, & response cache
├── requirements.txt         # Python dependencies
├── installer.iss            # Inno Setup installer compilation script
├── LICENSE                  # MIT License
├── README.md                # Project documentation
├── run_app.bat              # Windows Desktop launcher batch script
├── main.py                  # Application entry point
│
├── .github/
│   └── workflows/
│       └── release.yml      # GitHub Actions automated release pipeline
│
├── core/                    # System & Configuration Utilities
│   ├── config_manager.py    # Setting management & API key handling
│   ├── cache_manager.py     # Hash caching & Recent Captures history manager
│   └── search_builder.py    # Formats exclusion search URLs & launches browser
│
├── services/                # API & Processing Pipeline
│   ├── nam_parser.py        # Reads local .nam JSON files & metadata
│   ├── tone3000_api.py      # Query sanitization & Tone3000 search engine
│   └── groq_service.py      # Llama 3.3 hardware extraction service
│
└── ui/                      # PyQt6 User Interface
    ├── main_window.py       # Primary GUI layout & event handlers
    ├── drop_zone.py         # Clickable drag-and-drop file widget
    ├── hardware_chips.py    # Dynamic action chips & candidate term buttons
    ├── metadata_dialog.py   # Embedded JSON metadata inspector modal
    ├── styles.py            # Dark theme QSS stylesheet
    └── worker_thread.py     # Background QThread handler
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.