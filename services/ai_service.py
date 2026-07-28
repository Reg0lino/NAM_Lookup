from pathlib import Path
from core.config_manager import load_config
from services.gemini_service import extract_hardware_with_gemini
from services.groq_service import extract_hardware_with_groq


def extract_hardware(
    file_path: Path, nam_data: dict, tone3000_data: dict, logger=None
) -> dict:
    """Unified entry point for AI extraction with automatic provider failover."""
    def log(msg):
        if logger:
            logger(f"[AIService] {msg}")

    config = load_config()
    provider = config.get("ai_provider", "Groq")

    log(f"Primary AI Provider selected: {provider}")

    # Try Primary Provider
    if provider == "Groq":
        try:
            return extract_hardware_with_groq(file_path, nam_data, tone3000_data, logger=logger)
        except Exception as e:
            log(f"⚠️ Groq primary failed ({e}). Attempting Gemini failover...")
            try:
                return extract_hardware_with_gemini(file_path, nam_data, tone3000_data, logger=logger)
            except Exception as ge:
                log(f"❌ Gemini failover also failed ({ge}).")
    else:
        try:
            return extract_hardware_with_gemini(file_path, nam_data, tone3000_data, logger=logger)
        except Exception as e:
            log(f"⚠️ Gemini primary failed ({e}). Attempting Groq failover...")
            try:
                return extract_hardware_with_groq(file_path, nam_data, tone3000_data, logger=logger)
            except Exception as gre:
                log(f"❌ Groq failover also failed ({gre}).")

    # Fallback if both providers failed
    fallback_query = nam_data.get("stem_name", "").replace("_", " ")
    return {
        "error": "Both AI providers failed.",
        "primary_search": fallback_query,
        "hardware_components": [
            {"type": "Audio Hardware", "query": fallback_query}
        ],
        "tone3000_url": tone3000_data.get("web_url", ""),
        "tone3000_matched": tone3000_data.get("matched", False),
    }