import json
import os
from pathlib import Path

def get_app_dir() -> Path:
    """Returns %APPDATA%/NAM_Hardware_Finder for user settings & cache."""
    appdata = os.getenv("APPDATA")
    if appdata:
        path = Path(appdata) / "NAM_Hardware_Finder"
    else:
        path = Path.home() / ".nam_hardware_finder"
    path.mkdir(parents=True, exist_ok=True)
    return path


CONFIG_FILE = get_app_dir() / "config.json"

DEFAULT_CONFIG = {
    "groq_api_key": "",
    "groq_model": "llama-3.3-70b-versatile",
    "tone3000_api_key": "",
    "enable_tone3000": True,
    "enable_cache": True,
    "enable_demo_mode": False,
    "search_engine": "Google",
    "last_open_directory": r"I:\Assorted Synth & DAW\!NAM",
    "negative_search_operators": '-NAM -Neural -"Neural Amp Modeler" -ToneHunt -Tone3000 -capture -preset',
}


def load_config() -> dict:
    """Loads configuration from AppData config.json. Creates default if missing."""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception as e:
        print(f"[ConfigManager] Error loading config: {e}. Reverting to defaults.")
        return DEFAULT_CONFIG.copy()


def save_config(config_data: dict) -> bool:
    """Saves given configuration dictionary to AppData config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        print(f"[ConfigManager] Error saving config to {CONFIG_FILE}: {e}")
        return False


def get_api_key(key_name: str) -> str:
    """Helper to fetch a specific API key."""
    env_val = os.getenv(key_name.upper())
    if env_val:
        return env_val
    config = load_config()
    return config.get(key_name, "")