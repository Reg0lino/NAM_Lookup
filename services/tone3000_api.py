import re
import requests
from core.config_manager import get_api_key, load_config

TONE3000_BASE_URL = "https://www.tone3000.com/api/v1"


def sanitize_search_term(raw_term: str) -> str:
    """Strips noise words, knob settings, and creator tags."""
    cleaned = raw_term.replace("_", " ").replace("-", " ")

    patterns = [
        r"(?i)\b(bass|mid|treble|gain|volume|vol|presence|depth)\s*\d+\b",
        r"(?i)\b(eq\s*flat|flat\s*eq|no\s*boost|treble\s*boost|clean\s*ss)\b",
        r"(?i)\b(full[\s-]*rig|di|direct|cap|normal|bright|crunch|clean|overdrive)\b",
        r"(?i)\bjp[\s_]*is[\s_]*out[\s_]*of[\s_]*tune\b",
        r"(?i)\b(v\d+|final|raw|test)\b",
    ]

    for p in patterns:
        cleaned = re.sub(p, " ", cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if cleaned else raw_term


def query_tone3000(search_term: str, logger=None) -> dict:
    """Standard Tone3000 search using sanitized term."""
    def log(msg):
        if logger:
            logger(f"[Tone3000API] {msg}")

    config = load_config()
    if not config.get("enable_tone3000", True):
        log("Integration disabled in config. Skipping API query.")
        return {"matched": False, "reason": "Disabled", "candidates": []}

    api_key = get_api_key("tone3000_api_key")
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    sanitized = sanitize_search_term(search_term)
    log(f"Raw query: '{search_term}' -> Sanitized: '{sanitized}'")

    return _execute_tone3000_search(sanitized, headers, log)


def query_tone3000_deep_breakdown(search_term: str, logger=None) -> dict:
    """Deep search testing individual phrases and collecting candidate hits."""
    def log(msg):
        if logger:
            logger(f"[Tone3000DeepSearch] {msg}")

    config = load_config()
    api_key = get_api_key("tone3000_api_key")
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    sanitized = sanitize_search_term(search_term)
    phrases = [p.strip() for p in re.split(
        r"[,._\-]", search_term) if len(p.strip()) > 2]
    candidates = [sanitized] + phrases

    all_found_candidates = []
    matched_result = None

    for query in candidates:
        if not query:
            continue
        log(f"Testing deep query: '{query}'...")
        res = _execute_tone3000_search(query, headers, log)

        if res.get("candidate_titles"):
            all_found_candidates.extend(res["candidate_titles"])

        if res.get("matched") and not matched_result:
            matched_result = res

    if matched_result:
        matched_result["candidates"] = list(set(all_found_candidates))
        return matched_result

    clean_fallback = sanitized.replace(" ", "+")
    return {
        "matched": False,
        "web_url": f"https://www.tone3000.com/search?q={clean_fallback}",
        "candidates": list(set(all_found_candidates)),
    }


def _execute_tone3000_search(query_term: str, headers: dict, log_fn) -> dict:
    result = {
        "matched": False,
        "tone_id": None,
        "title": "",
        "web_url": f"https://www.tone3000.com/search?q={query_term.replace(' ', '+')}",
        "makes_and_models": [],
        "tags": [],
        "gears": "",
        "description": "",
        "candidate_titles": [],
    }

    try:
        search_url = f"{TONE3000_BASE_URL}/tones/search"
        params = {"q": query_term, "limit": 5}

        response = requests.get(
            search_url, headers=headers, params=params, timeout=5)

        if response.status_code != 200:
            search_url = f"{TONE3000_BASE_URL}/tones"
            params = {"query": query_term, "limit": 5}
            response = requests.get(
                search_url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            items = data.get("items") or data.get("tones") or (
                data if isinstance(data, list) else [])

            if items and len(items) > 0:
                result["candidate_titles"] = [
                    t.get("title", "") for t in items if t.get("title")]

                tone = items[0]
                tone_id = tone.get("id") or tone.get("tone_id")

                result["matched"] = True
                result["tone_id"] = tone_id
                result["title"] = tone.get("title") or tone.get("name", "")
                result["web_url"] = f"https://www.tone3000.com/tones/{tone_id}" if tone_id else result["web_url"]
                result["makes_and_models"] = tone.get("makes_and_models", [])
                result["tags"] = tone.get("tags", [])
                result["gears"] = tone.get("gears") or tone.get("category", "")
                result["description"] = tone.get("description", "")

                log_fn(
                    f"Matched tone_id={tone_id}, Title: '{result['title']}'")

    except Exception as e:
        log_fn(f"Exception during Tone3000 request: {e}")

    return result
