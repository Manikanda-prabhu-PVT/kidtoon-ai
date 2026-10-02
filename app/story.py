import json
from pathlib import Path


def load_story(file_path) -> dict:
    """Read a story from a JSON file and return it as a dictionary."""
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_story(story: dict, file_path) -> None:
    """Write a story dictionary to a JSON file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(story, file, indent=2, ensure_ascii=False)


def validate_story(story: dict) -> None:
    """Check that the story has all required fields.

    Raises ValueError with a clear message if something is missing.
    """
    for key in ["title", "characters", "scenes"]:
        if key not in story:
            raise ValueError(f"Story is missing '{key}'")

    if not story["scenes"]:
        raise ValueError("Story must have at least one scene")

    for index, scene in enumerate(story["scenes"], start=1):
        for key in ["scene_number", "description", "narration"]:
            if key not in scene:
                raise ValueError(f"Scene {index} is missing '{key}'")