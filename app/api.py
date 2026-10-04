from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.main import clean_prompt
from app.story import load_story, validate_story

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_STORY_PATH = BASE_DIR.parent / "data" / "sample_story.json"
INDEX_PAGE = BASE_DIR / "static" / "index.html"

app = FastAPI(title="KidToon AI")


class StoryRequest(BaseModel):
    prompt: str


@app.get("/")
def home() -> FileResponse:
    return FileResponse(INDEX_PAGE)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/story/sample")
def get_sample_story() -> dict:
    story = load_story(SAMPLE_STORY_PATH)
    validate_story(story)
    return story


@app.post("/story/generate")
def generate_story(request: StoryRequest) -> dict:
    try:
        idea = clean_prompt(request.prompt)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    story = load_story(SAMPLE_STORY_PATH)  # placeholder until Step 4
    story["prompt"] = idea
    return story