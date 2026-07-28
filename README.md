
# 🎸 NAM Hardware Finder

**NAM Hardware Finder** is a lightweight Python desktop application (PyQt6) designed for guitarists, bassists, and audio engineers using Neural Amp Modeler (`.nam`).

It analyzes dropped `.nam` capture files, identifies the underlying physical gear (amplifiers, cabinets, overdrive pedals, microphones), and launches targeted web searches for the physical hardware while automatically filtering out digital capture/preset clutter (`ToneHunt`, `Tone3000`, NAM forums, etc.).

---

## ✨ Features

- **⚡ Blazing Fast Extraction (Groq AI):** Powered by Groq’s `llama-3.3-70b-versatile` for sub-second context-aware hardware extractions from chaotic creator filenames.
- **🎯 Context-Aware Search Precision:**
  - Detects **Bass** vs. **Guitar** context from parent folders and filenames.
  - Automatically appends search target terms (`guitar cabinet`, `bass cabinet`, `guitar amplifier`, `microphone`) to prevent generic web search results.
- **📡 Tone3000 Integration & Deep Search:**
  - **Sanitized Search Query:** Strips knob settings (`Bass 6 Mid 5`) and creator handles before querying Tone3000.
  - **🔍 Deep Tone3000 Search:** Multi-pass phrase search that breaks down complex titles and fetches online metadata.
  - **🌐 Direct Web Shortcut:** One-click button to jump directly to matched Tone3000 capture pages.
- **🕒 Cache History Dropdown:** Access all previously analyzed `.nam` captures with **0ms latency** from the "Recent Captures" menu without making new API calls.
- **🛠️ Live Debug Console:** Real-time log stream showing exact local JSON parses, Tone3000 API requests, and Groq AI responses.
- **🌙 Modern Dark Theme:** Sleek slate/charcoal PyQt6 interface with non-blocking `QThread` execution for zero UI freezes.

---

## 📁 Project Structure

```text
nam-hardware-finder/
├── config.json              # Local settings & API key storage (gitignored)
├── cache.json               # Local extraction history & response cache
├── requirements.txt         # Python dependencies
├── .gitignore               # Excludes virtual environments, caches, and config
├── README.md                # Project documentation
├── run_app.bat              # Windows Desktop launcher batch script
├── main.py                  # Application entry point
│
├── core/                    # System & Configuration Utilities
│   ├── config_manager.py    # Setting management & API key handling
│   ├── cache_manager.py     # Hash caching & Recent Captures history manager
│   └── search_builder.py    # Formats exclusion search URLs & launches browser
│
├── services/                # API & Processing Pipeline
│   ├── nam_parser.py        # Reads local .nam JSON files & metadata
│   ├── tone3000_api.py      # Query sanitization & Tone3000 search engine
│   ├── groq_service.py      # Llama 3.3 hardware extraction service
│   └── ai_service.py        # Pipeline orchestrator
│
└── ui/                      # PyQt6 User Interface
    ├── main_window.py       # Primary GUI layout & event handlers
    ├── drop_zone.py         # Drag-and-drop file widget
    ├── hardware_chips.py    # Dynamic action chips & candidate term buttons
    ├── styles.py            # Dark theme QSS stylesheet
    └── worker_thread.py     # Background QThread handler
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- **Python 3.10+**
- A free **Groq API Key** (obtainable instantly from [console.groq.com](https://console.groq.com))

### Setup Instructions

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

## ⚙️ App Configuration

1. Launch the application.
2. Enter your **Groq API Key** (`gsk_...`) in the **Groq & App Settings** box at the bottom.
3. Click **`⚡ Test Groq Key`** to verify your connection.
4. Click **`Save Settings`**.

---

## 💡 How To Use

1. **Drag and drop** any `.nam` file into the top drop zone.
2. The application extracts hardware items and displays **Primary Hardware Chips** (`[ 🔊 Peavey 5150 guitar amplifier ]`, `[ 📢 Mesa OS guitar cabinet ]`, `[ 🎙️ Shure SM57 microphone ]`).
3. **Candidate Terms Row:** Click any candidate badge (`[ 🔎 Vox AC30 Top Boost ]`) to run a speculative Google search.
4. **History Dropdown:** Select any previously dropped file from `[ 🕒 Recent Captures ]` to load its results instantly from local cache.
5. **Targeted Web Searches:** Click any chip to search Google for physical hardware while excluding digital capture site clutter (`-NAM -Neural -Tone3000 -ToneHunt ...`).

---

📄 License

MIT License