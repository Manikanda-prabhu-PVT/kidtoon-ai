import pytest

from app.story import load_story, save_story, validate_story


def make_valid_story() -> dict:
    return {
        "title": "Test Story",
        "characters": [{"name": "Ruby", "type": "rabbit", "description": "A rabbit"}],
        "scenes": [
            {"scene_number": 1, "description": "A forest", "narration": "Hello"}
        ],
    }


def test_load_sample_story():
    story = load_story("data/sample_story.json")
    assert story["title"] == "The Lost Little Bird"
    assert len(story["scenes"]) == 3


def test_validate_accepts_valid_story():
    validate_story(make_valid_story())  # should not raise


def test_validate_rejects_missing_title():
    story = make_valid_story()
    del story["title"]
    with pytest.raises(ValueError, match="title"):
        validate_story(story)


def test_validate_rejects_empty_scenes():
    story = make_valid_story()
    story["scenes"] = []
    with pytest.raises(ValueError, match="at least one scene"):
        validate_story(story)


def test_save_then_load_returns_same_story(tmp_path):
    story = make_valid_story()
    file_path = tmp_path / "out" / "story.json"
    save_story(story, file_path)
    assert load_story(file_path) == story