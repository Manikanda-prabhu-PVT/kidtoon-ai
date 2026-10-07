import json

import pytest

from app.llm import LLMError, build_prompt, call_with_retry, generate_story, parse_story

VALID_STORY = {
    "title": "Test Story",
    "characters": [{"name": "Ruby", "type": "rabbit", "description": "A white rabbit"}],
    "scenes": [
        {"scene_number": 1, "description": "A forest", "narration": "Hello", "characters": ["Ruby"]}
    ],
}


class FakeApiError(Exception):
    def __init__(self, code):
        super().__init__(f"error {code}")
        self.code = code


def test_build_prompt_contains_idea_and_scene_count():
    prompt = build_prompt("a brave turtle", scene_count=5)
    assert "a brave turtle" in prompt
    assert "Exactly 5 scenes" in prompt


def test_parse_story_accepts_plain_json():
    story = parse_story(json.dumps(VALID_STORY))
    assert story["title"] == "Test Story"


def test_parse_story_strips_code_fences():
    text = "```json\n" + json.dumps(VALID_STORY) + "\n```"
    assert parse_story(text)["title"] == "Test Story"


def test_parse_story_rejects_invalid_json():
    with pytest.raises(LLMError, match="valid JSON"):
        parse_story("this is not json")


def test_parse_story_rejects_missing_field():
    broken = {"title": "No scenes", "characters": []}
    with pytest.raises(LLMError, match="scenes"):
        parse_story(json.dumps(broken))


def test_generate_story_uses_the_llm_function():
    fake_answer = json.dumps(VALID_STORY)
    story = generate_story("a rabbit", call_llm=lambda prompt: fake_answer)
    assert story["title"] == "Test Story"


def test_retry_succeeds_after_temporary_errors():
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise FakeApiError(503)
        return "ok"

    result = call_with_retry(flaky, attempts=3, sleep=lambda seconds: None)
    assert result == "ok"
    assert len(calls) == 3


def test_retry_gives_up_after_all_attempts():
    calls = []

    def always_busy():
        calls.append(1)
        raise FakeApiError(503)

    with pytest.raises(FakeApiError):
        call_with_retry(always_busy, attempts=3, sleep=lambda seconds: None)
    assert len(calls) == 3


def test_retry_does_not_retry_bad_key_errors():
    calls = []

    def bad_key():
        calls.append(1)
        raise FakeApiError(403)

    with pytest.raises(FakeApiError):
        call_with_retry(bad_key, attempts=3, sleep=lambda seconds: None)
    assert len(calls) == 1