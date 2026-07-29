import json
from pathlib import Path


def parse_nam_file(file_path: Path, logger=None) -> dict:
    """
    Parses a local .nam file (which is internally formatted as JSON).
    Extracts filename, parent folder context, and all embedded JSON metadata.
    """
    def log(msg):
        if logger:
            logger(f"[NAMParser] {msg}")

    path_obj = Path(file_path)

    result = {
        "filename": path_obj.name,
        "stem_name": path_obj.stem,
        "parent_folder": path_obj.parent.name,
        "internal_metadata": {},
        "raw_json_available": False,
    }

    if not path_obj.exists() or not path_obj.is_file():
        log(f"File not found: {file_path}")
        return result

    try:
        with open(path_obj, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            result["raw_json_available"] = True

            # NAM files store metadata under 'metadata' dict or root level
            metadata = data.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}

            # Extract standard + extended NAM metadata fields
            extracted_meta = {
                "model_name": metadata.get("model_name") or data.get("model_name", ""),
                "gear": metadata.get("gear") or data.get("gear", ""),
                "author": metadata.get("author") or data.get("author", ""),
                "mode": metadata.get("mode") or data.get("mode", ""),
                "dataset_name": metadata.get("dataset_name") or data.get("dataset_name", ""),
                "loudness": metadata.get("loudness") or data.get("loudness", ""),
                "input_level_dbu": metadata.get("input_level_dbu") or data.get("input_level_dbu", ""),
                "output_level_dbu": metadata.get("output_level_dbu") or data.get("output_level_dbu", ""),
                "date": metadata.get("date") or data.get("date", ""),
            }

            # Filter out empty or None values
            cleaned_meta = {k: v for k, v in extracted_meta.items() if v != "" and v is not None}

            # Capture any extra custom metadata dictionary keys
            for k, v in metadata.items():
                if k not in cleaned_meta and v is not None and v != "":
                    cleaned_meta[k] = v

            result["internal_metadata"] = cleaned_meta

            if cleaned_meta:
                log(f"Embedded Metadata Found -> {cleaned_meta}")
            else:
                log("No embedded JSON metadata found in file.")

    except Exception as e:
        log(f"Could not parse internal JSON for {path_obj.name}: {e}")

    return result