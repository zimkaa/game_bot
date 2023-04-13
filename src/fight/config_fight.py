import json
import os
from pathlib import Path
from typing import Any


def get_fight_config(file_name: str) -> list[dict[str, Any]]:
    dir_path = Path(__file__).parent.resolve()
    file_path = os.path.join(dir_path, "settings", f"{file_name}.json")
    with open(file_path, "r", encoding="utf8") as file:
        fight_config: list[dict] = json.loads(file.read())
    return fight_config
