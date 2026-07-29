import json
import requests
from pathlib import Path

from core.cache_manager import get_cached_result, save_to_cache
from core.config_manager import get_api_key, load_config

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_INSTRUCTION = """
You are an expert audio gear assistant specializing in guitar and bass amplifiers, speaker cabinets, effect pedals, and microphones.
Your task is to extract individual physical hardware pieces from Neural Amp Modeler (.nam) filenames, parent folder context, internal metadata, and online Tone3000 details.

CRITICAL INSTRUCTIONS FOR EMBEDDED METADATA:
- If internal_metadata contains 'gear_make' and 'gear_model' (e.g., gear_make: "Marshall", gear_model: "68 Purple Plexi"), ALWAYS combine them into the primary hardware query (e.g., "Marshall 68 Purple Plexi guitar amplifier").
- If 'gear_make' or 'gear_model' is missing, fallback to parsing the filename stem.

CRITICAL QUERY FORMATTING RULES:
1. ALWAYS split multiple pieces of hardware into SEPARATE objects in "hardware_components".
2. BASS VS GUITAR CONTEXT DETECTION:
   - Inspect parent folder name, filename, and metadata for bass indicators ('bass', 'svt', 'ampeg', 'darkglass', 'b15', 'sansamp', 'sub').
   - If BASS context is detected:
     * For Cabinets: Append "bass cabinet" (e.g., "Ampeg 8x10 bass cabinet")
     * For Amplifiers: Append "bass amplifier" (e.g., "Ampeg SVT bass amplifier")
   - If GUITAR context is detected (or default):
     * For Cabinets: Append "guitar cabinet" (e.g., "Mesa OS 4x12 guitar cabinet")
     * For Amplifiers: Append "guitar amplifier" (e.g., "Marshall 68 Purple Plexi guitar amplifier", "Peavey 5150 guitar amplifier")

3. MICROPHONE FORMATTING:
   - Append "microphone" if not already present (e.g., "Shure SM57 microphone").

4. STRIP non-hardware metadata (knob settings, volume/EQ levels, capture flags like DI/Full-Rig).

Return valid JSON with schema:
{
  "primary_search": "Marshall 68 Purple Plexi guitar amplifier",
  "hardware_components": [
    {"type": "Guitar Amplifier", "query": "Marshall 68 Purple Plexi guitar amplifier"}
  ],
  "candidate_terms": [
    "Marshall Purple Plexi",
    "Tone Junkie Plexi"
  ]
}
"""


def extract_hardware_with_groq(
    file_path: Path, nam_data: dict, tone3000_data: dict, force_refresh: bool = False, logger=None
) -> dict:
    """Extracts hardware components using Groq's fast Llama-3.3 API."""
    def log(msg):
        if logger:
            logger(f"[GroqService] {msg}")

    config = load_config()
    model_name = config.get("groq_model", "llama-3.3-70b-versatile")

    if not force_refresh and config.get("enable_cache", True):
        cached = get_cached_result(file_path)
        if cached:
            log(f"Cache hit for '{file_path.name}'. Returning stored result.")
            return cached

    api_key = get_api_key("groq_api_key")
    if not api_key:
        log("ERROR: Groq API Key missing!")
        return {
            "error": "Groq API Key missing. Please set it in Settings.",
            "primary_search": nam_data.get("stem_name", ""),
            "hardware_components": [],
            "candidate_terms": [],
            "internal_metadata": nam_data.get("internal_metadata", {}),
        }

    payload_context = {
        "filename": nam_data.get("filename"),
        "parent_folder": nam_data.get("parent_folder"),
        "internal_metadata": nam_data.get("internal_metadata", {}),
        "tone3000_online_details": {
            "matched": tone3000_data.get("matched", False),
            "makes_and_models": tone3000_data.get("makes_and_models", []),
            "tags": tone3000_data.get("tags", []),
            "category": tone3000_data.get("gears", ""),
            "description": tone3000_data.get("description", ""),
            "candidate_titles": tone3000_data.get("candidates", []),
        },
    }

    # Word 'json' is explicitly required in user prompt for Groq json_object format
    user_prompt = f"Extract physical hardware from context and return valid json:\n{json.dumps(payload_context, indent=2)}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
    }

    log(f"Calling Groq API model '{model_name}'...")
    response = requests.post(
        GROQ_ENDPOINT, headers=headers, json=data, timeout=10)

    if response.status_code != 200:
        log(f"Groq API Error {response.status_code}: {response.text}")
        fallback_query = nam_data.get("stem_name", "").replace("_", " ")
        return {
            "error": f"Groq Error {response.status_code}",
            "primary_search": fallback_query,
            "hardware_components": [{"type": "Audio Hardware", "query": fallback_query}],
            "candidate_terms": [],
            "internal_metadata": nam_data.get("internal_metadata", {}),
            "tone3000_url": tone3000_data.get("web_url", ""),
            "tone3000_matched": tone3000_data.get("matched", False),
        }

    res_json = response.json()
    content_str = res_json["choices"][0]["message"]["content"]
    log(f"🟢 Groq Success! Output: {content_str.strip()}")

    extracted_json = json.loads(content_str)
    extracted_json["tone3000_url"] = tone3000_data.get("web_url", "")
    extracted_json["tone3000_matched"] = tone3000_data.get("matched", False)
    extracted_json["internal_metadata"] = nam_data.get("internal_metadata", {})

    t3k_candidates = tone3000_data.get("candidates", [])
    if t3k_candidates:
        existing = extracted_json.get("candidate_terms", [])
        extracted_json["candidate_terms"] = list(
            set(existing + t3k_candidates[:4]))

    if config.get("enable_cache", True):
        save_to_cache(file_path, extracted_json)
        log("Saved result to local cache.json.")

    return extracted_json
