# 🎸 NAM Hardware Finder v1.0.3

Neural Amp Modeler (`.nam`) captures are downloaded from countless creators, forums, and repositories, but **there is no common naming convention** for these files. Many captures have chaotic, cryptic filenames (e.g. `Full-Rig-Peavey-5150-No-boost-Mesa-OS-SM57---jp_is_out_of_tune.nam`) or lack complete internal metadata, making it frustrating to figure out what physical amplifiers, speaker cabinets, or microphones were actually used.

**NAM Hardware Finder** solves this by using high-speed AI to instantly analyze `.nam` filenames, parent folder context, and embedded tags to extract the exact underlying physical gear. It gives you 1-click access to Google hardware specs and YouTube video reviews while filtering out as much digital preset clutter as possible.

This application works best with a **FREE** Groq Llama 3.3 API. See below for directions on quickly getting that API. 

Note: This is **NOT GROK**, This is a different site that hosts a FREE Llama build for small tasks like this.


*YES, I used **Google Gemini 3.6** to hurry this along, but the app is solid.*

---

## 📥 Download Assets

Download your preferred version under **Assets** on the **[GitHub Releases Page](../../releases/latest)**:

- **`NAM_Hardware_Finder_Setup.exe`** — Recommended Windows Installer (Includes Start Menu & Desktop Shortcuts).
- **`NAM_Hardware_Finder_Portable.zip`** — Portable version (Extract anywhere and run `run_app.bat` or `NAM_Hardware_Finder.exe`).

If Windows hits you with a Defender Smart Screen, hit more info, then run.
---

## 🔥 Features Summary

- **⚡ Blazing Fast AI Extraction (Groq Llama 3.3):** Sub-second context-aware hardware extractions from chaotic creator filenames.
- **🔍 Dual Search Engine Switch (Google vs. YouTube):**
  - **Google Mode:** Searches for physical hardware specifications while automatically excluding digital capture sites (`-NAM -Neural -ToneHunt...`).
  - **YouTube Mode:** Searches YouTube directly for video/audio gear reviews and demos (`demo review`).
- **🎥 DEMO Mode Switch:** Toggle DEMO mode ON to automatically append `"DEMO"` to all gear search queries.
- **🎯 Targeted Bass vs. Guitar Context Rules:** Detects bass profiles vs. guitar profiles and formats search queries with targeted terms (`guitar cabinet`, `bass cabinet`, `guitar amplifier`, `microphone`).
- **📡 Tone3000 Integration & Deep Search:**
  - **Sanitized Search Query:** Strips knob settings (`Bass 6 Mid 5`) and creator handles before querying Tone3000.
  - **🔍 Deep Tone3000 Search:** Multi-pass phrase search that breaks down complex titles and fetches online metadata.
- **📄 Embedded JSON Metadata Inspector:** Click `[ 📄 View NAM Metadata ]` to view all internal JSON attributes (`gear_make`, `gear_model`, `author`, `dBu levels`, `date created`) in a clean table modal.
- **📝 Personal Capture Notes:** Save custom notes to any profile (e.g. *"Great rhythm tone on Les Paul bridge pickup"*), saved locally in your cache for future reference.
- **⭐ Favorites & Fuzzy Search Filter:** Star your favorite captures and filter your history list in real time as you type (stripping brackets `[]`, underscores `_`, and hyphens `-`).
- **📁 Click-to-Browse with Folder Memory:** Click the drop zone box to open files directly, remembering your last browsed folder location.
- **🛠️ Live Debug Console:** Real-time log stream showing exact local JSON parses, Tone3000 API requests, and AI responses.

---

## 🚀 1-Minute Quick Start Guide

1. Get a **free Groq API Key** in 30 seconds from [console.groq.com](https://console.groq.com).
2. Launch **NAM Hardware Finder**.
3. Paste your Groq key into the **Groq & App Settings** field at the bottom and click **`⚡ Test Groq Key`**.
4. Click **`Save Settings`**.
5. Drag and drop any `.nam` file or click the box to browse!

---

## 🛠️ Developer Setup (Running from Source)

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
├── icon.ico                 # 256x256 Application Icon
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
