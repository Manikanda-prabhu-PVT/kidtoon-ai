import json
import os
import time

from dotenv import load_dotenv

from app.story import validate_story

load_dotenv()

DEFAULT_MODEL = "gemini-flash-latest"
TRANSIENT_CODES = (429, 500, 502, 503, 504)

PROMPT_TEMPLATE = """You are a children's story writer for ages 3 to 7.
Write a short, gentle, happy story based on this idea:
"{idea}"

Return ONLY valid JSON (no markdown, no extra text) in exactly this format:
{
  "title": "...",
  "characters": [
    {"name": "...", "type": "...", "description": "..."}
  ],
  "scenes": [
    {"scene_number": 1, "description": "...", "narration": "...", "characters": ["name"]}
  ]
}

Rules:
- Exactly {scene_count} scenes, numbered from 1.
- "description" says what we SEE in the scene (for an illustrator).
- "narration" is 1 or 2 simple sentences that will be read aloud.
- Character descriptions must be visual (colors, clothes, size) so pictures stay consistent.
- In each scene, "characters" may only use names listed in the top-level "characters".
"""


class LLMError(Exception):
    """Raised when the LLM call fails or returns a bad story."""


def call_with_retry(func, attempts=3, delay=2.0, sleep=time.sleep):
    """Call func(). If the service is temporarily busy, wait and try again."""
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except Exception as error:
            code = getattr(error, "code", None)
            if code not in TRANSIENT_CODES or attempt == attempts:
                raise
            sleep(delay * attempt)


def build_prompt(idea: str, scene_count: int = 4) -> str:
    return PROMPT_TEMPLATE.replace("{idea}", idea).replace("{scene_count}", str(scene_count))


def parse_story(text: str) -> dict:
    """Turn the LLM's text into a validated story dict."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        story = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise LLMError(f"LLM did not return valid JSON: {error}") from error

    if not isinstance(story, dict):
        raise LLMError("LLM returned JSON, but it is not a story object")

    try:
        validate_story(story)
    except ValueError as error:
        raise LLMError(f"LLM returned an invalid story: {error}") from error
    return story


def call_gemini(prompt: str) -> str:
    """Send the prompt to Gemini and return the raw text answer."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMError("GEMINI_API_KEY is not set. Add it to your .env file.")

    from google import genai
    from google.genai import types

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    try:
        client = genai.Client(api_key=api_key)
        response = call_with_retry(
            lambda: client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.8,
                ),
            )
        )
    except Exception as error:
        raise LLMError(f"Gemini call failed: {error}") from error

    if not response.text:
        raise LLMError("Gemini returned an empty answer")
    return response.text


def generate_story(idea: str, call_llm=call_gemini) -> dict:
    """Idea in, validated story out. call_llm can be swapped in tests."""
    text = call_llm(build_prompt(idea))
    return parse_story(text)


if __name__ == "__main__":
    result = generate_story("A cute rabbit and baby elephant help a lost bird find its mother.")
    print("Title:", result["title"])
    for scene in result["scenes"]:
        print(f"  Scene {scene['scene_number']}: {scene['narration']}")