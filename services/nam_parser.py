import json
from pathlib import Path


def parse_nam_file(file_path: Path) -> dict:
    """
    Parses a local .nam file (which is internally formatted as JSON).
    Extracts filename, parent folder context, and internal metadata.
    """
    path_obj = Path(file_path)

    result = {
        "filename": path_obj.name,
        "stem_name": path_obj.stem,
        "parent_folder": path_obj.parent.name,
        "internal_metadata": {},
        "raw_json_available": False,
    }

    if not path_obj.exists() or not path_obj.is_file():
        return result

    try:
        with open(path_obj, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            result["raw_json_available"] = True

            # Extract fields from root JSON or nested 'metadata' key
            metadata = data.get("metadata", {})
            if isinstance(metadata, dict):
                result["internal_metadata"] = {
                    "model_name": metadata.get("model_name")
                    or data.get("model_name", ""),
                    "author": metadata.get("author") or data.get("author", ""),
                    "gear": metadata.get("gear") or data.get("gear", ""),
                    "mode": metadata.get("mode") or data.get("mode", ""),
                    "dataset_name": metadata.get("dataset_name")
                    or data.get("dataset_name", ""),
                }
            else:
                # Handle root-level metadata if present
                result["internal_metadata"] = {
                    "model_name": data.get("model_name", ""),
                    "author": data.get("author", ""),
                    "gear": data.get("gear", ""),
                }

    except Exception as e:
        print(
            f"[NAMParser] Could not parse internal JSON for {path_obj.name}: {e}")

    return result
