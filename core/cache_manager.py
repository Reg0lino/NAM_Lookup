import hashlib
import json
import os
import re
from datetime import datetime
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


CACHE_FILE = get_app_dir() / "cache.json"


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


def _get_cache_key(file_path: Path) -> str:
    """Creates a unique cache key combining filename and file hash."""
    file_hash = _get_file_hash(file_path)
    return f"{file_path.name}_{file_hash}"


def normalize_search_string(text: str) -> str:
    """Strips brackets [], underscores _, hyphens -, and extra spaces for fuzzy matching."""
    if not text:
        return ""
    cleaned = re.sub(r"[\[\]\(\)_\-\.]", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
    return cleaned


def get_cached_result(file_path: Path) -> dict | None:
    """Retrieves cached extraction result for a file if key matches."""
    if not CACHE_FILE.exists():
        return None

    cache_key = _get_cache_key(file_path)
    file_hash = _get_file_hash(file_path)

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

            entry = cache_data.get(cache_key) or cache_data.get(file_hash)
            if entry and isinstance(entry, dict) and "extraction" in entry:
                result = entry["extraction"]
                result["is_favorite"] = entry.get("is_favorite", False)
                result["user_notes"] = entry.get("user_notes", "")
                return result
            return entry if isinstance(entry, dict) else None
    except Exception as e:
        print(f"[CacheManager] Error reading cache: {e}")
        return None


def save_to_cache(file_path: Path, result_data: dict) -> bool:
    """Saves extraction result with filename, timestamp, favorites, and notes into cache.json."""
    cache_key = _get_cache_key(file_path)

    cache_data = {}
    is_favorite = False
    user_notes = ""

    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                if cache_key in cache_data:
                    is_favorite = cache_data[cache_key].get(
                        "is_favorite", False)
                    user_notes = cache_data[cache_key].get("user_notes", "")
        except Exception:
            cache_data = {}

    cache_data[cache_key] = {
        "filename": file_path.name,
        "file_path": str(file_path.resolve()),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_favorite": result_data.get("is_favorite", is_favorite),
        "user_notes": result_data.get("user_notes", user_notes),
        "extraction": result_data,
    }

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=4)
        return True
    except Exception as e:
        print(f"[CacheManager] Error writing cache: {e}")
        return False


def update_cache_entry_notes_and_favorite(
    file_path: Path, user_notes: str = None, is_favorite: bool = None
) -> bool:
    """Updates notes and/or favorite status for an existing cache entry."""
    if not CACHE_FILE.exists():
        return False

    cache_key = _get_cache_key(file_path)

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

        if cache_key not in cache_data:
            return False

        if user_notes is not None:
            cache_data[cache_key]["user_notes"] = user_notes
            if "extraction" in cache_data[cache_key]:
                cache_data[cache_key]["extraction"]["user_notes"] = user_notes

        if is_favorite is not None:
            cache_data[cache_key]["is_favorite"] = is_favorite
            if "extraction" in cache_data[cache_key]:
                cache_data[cache_key]["extraction"]["is_favorite"] = is_favorite

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=4)
        return True

    except Exception as e:
        print(f"[CacheManager] Error updating notes/favorite: {e}")
        return False


def get_recent_history(filter_text: str = "", favorites_only: bool = False) -> list:
    """Returns cached entries filtered by fuzzy search text and/or favorites flag."""
    if not CACHE_FILE.exists():
        return []

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

        norm_filter = normalize_search_string(filter_text)
        history = []

        for key, entry in cache_data.items():
            if not isinstance(entry, dict) or "extraction" not in entry:
                continue

            entry_is_fav = entry.get("is_favorite", False)
            if favorites_only and not entry_is_fav:
                continue

            fname = entry.get("filename", "")
            notes = entry.get("user_notes", "")
            extraction = entry.get("extraction", {})
            primary_search = extraction.get("primary_search", "")

            if norm_filter:
                combined_targets = f"{fname} {notes} {primary_search}"
                norm_target = normalize_search_string(combined_targets)
                if norm_filter not in norm_target:
                    continue

            history.append({
                "cache_key": key,
                "filename": fname,
                "file_path": entry.get("file_path", ""),
                "timestamp": entry.get("timestamp", ""),
                "is_favorite": entry_is_fav,
                "user_notes": notes,
                "extraction": extraction,
            })

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
