import hashlib
import json
from datetime import datetime
from pathlib import Path

CACHE_FILE = Path("cache.json")


def _get_file_hash(file_path: Path) -> str:
    """Generates an MD5 hash of the given file content."""
    hasher = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"[CacheManager] Error hashing file {file_path}: {e}")
        return ""


def get_cached_result(file_path: Path) -> dict | None:
    """Retrieves cached extraction result for a file if hash matches."""
    if not CACHE_FILE.exists():
        return None

    file_hash = _get_file_hash(file_path)
    if not file_hash:
        return None

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
            entry = cache_data.get(file_hash)
            if entry and "extraction" in entry:
                return entry["extraction"]
            return entry  # Fallback for old cache format
    except Exception as e:
        print(f"[CacheManager] Error reading cache: {e}")
        return None


def save_to_cache(file_path: Path, result_data: dict) -> bool:
    """Saves extraction result with filename and timestamp into cache.json."""
    file_hash = _get_file_hash(file_path)
    if not file_hash:
        return False

    cache_data = {}
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
        except Exception:
            cache_data = {}

    cache_data[file_hash] = {
        "filename": file_path.name,
        "file_path": str(file_path.resolve()),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "extraction": result_data,
    }

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=4)
        return True
    except Exception as e:
        print(f"[CacheManager] Error writing cache: {e}")
        return False


def get_recent_history() -> list:
    """Returns a list of all cached entries sorted by most recent timestamp."""
    if not CACHE_FILE.exists():
        return []

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

        history = []
        for file_hash, entry in cache_data.items():
            if isinstance(entry, dict) and "extraction" in entry:
                history.append({
                    "hash": file_hash,
                    "filename": entry.get("filename", "Unknown File"),
                    "file_path": entry.get("file_path", ""),
                    "timestamp": entry.get("timestamp", ""),
                    "extraction": entry.get("extraction", {}),
                })

        # Sort by timestamp descending
        history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return history
    except Exception as e:
        print(f"[CacheManager] Error reading history: {e}")
        return []


def clear_cache() -> bool:
    """Clears all cached entries from cache.json."""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
        return True
    except Exception as e:
        print(f"[CacheManager] Error clearing cache: {e}")
        return False
