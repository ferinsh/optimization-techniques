
import json
import os
from pathlib import Path


def load_settings(save_path):
    path = Path(save_path)

    if not path.exists():
        return {
            "graphical_method": {},
            "simplex_method": {},
        }

    with path.open("r", encoding="utf-8") as file:
        settings = json.load(file)

    if not isinstance(settings, dict):
        raise ValueError("Settings file must contain a JSON object.")

    # Migrate the original graphical-only format, where the graphical fields
    # were stored directly at the top level of the JSON file.
    if "graphical_method" not in settings and any(
        key in settings for key in ("sense", "c1", "c2", "constraints")
    ):
        settings["graphical_method"] = {
            key: settings.pop(key)
            for key in ("sense", "c1", "c2", "constraints")
            if key in settings
        }

    settings.setdefault("graphical_method", {})
    settings.setdefault("simplex_method", {})

    return settings


def save_method_state(save_path, method, method_state):
    if method not in ("graphical_method", "simplex_method"):
        raise ValueError(f"Unknown settings section: {method}")

    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    settings = load_settings(path)
    settings[method] = method_state

    temp_path = Path(str(path) + ".tmp")

    try:
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4)

        os.replace(temp_path, path)

    except (OSError, TypeError, ValueError):
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def load_method_state(save_path, method):
    settings = load_settings(save_path)
    state = settings.get(method, {})

    if not isinstance(state, dict):
        raise ValueError(f"Invalid settings for {method}.")

    return state
