import urllib.parse
import webbrowser
from core.config_manager import load_config


def build_search_url(query: str, include_exclusions: bool = True, demo_mode: bool = False) -> str:
    """Builds a Google search URL, appending DEMO and negative operators if requested."""
    clean_query = query.strip()

    if demo_mode:
        clean_query = f"{clean_query} DEMO"

    if include_exclusions:
        config = load_config()
        operators = config.get(
            "negative_search_operators",
            '-NAM -Neural -"Neural Amp Modeler" -ToneHunt -Tone3000 -capture -preset',
        )
        full_query = f"{clean_query} {operators}"
    else:
        full_query = clean_query

    encoded_query = urllib.parse.quote_plus(full_query)
    return f"https://www.google.com/search?q={encoded_query}"


def build_youtube_search_url(query: str, demo_mode: bool = False) -> str:
    """Builds a YouTube video search URL for gear reviews and demos."""
    clean_query = query.strip()
    full_query = f"{clean_query} demo review" if not demo_mode else f"{clean_query} DEMO review"
    encoded_query = urllib.parse.quote_plus(full_query)
    return f"https://www.youtube.com/results?search_query={encoded_query}"


def open_in_browser(url: str) -> bool:
    """Opens a URL in the default system browser."""
    try:
        return webbrowser.open(url)
    except Exception as e:
        print(f"[SearchBuilder] Failed to open URL '{url}': {e}")
        return False


def execute_gear_search(query: str, search_engine: str = "Google", demo_mode: bool = False):
    """Unified search launcher. Routes to YouTube or Google based on search_engine setting."""
    if search_engine.lower() == "youtube":
        url = build_youtube_search_url(query, demo_mode=demo_mode)
    else:
        url = build_search_url(
            query, include_exclusions=True, demo_mode=demo_mode)

    open_in_browser(url)
