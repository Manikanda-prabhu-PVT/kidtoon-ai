from pathlib import Path

from app.story import load_story, validate_story


def clean_prompt(prompt: str) -> str:
    """Remove extra spaces from the user's story idea.

    Raises ValueError if the prompt is empty.
    """
    cleaned = prompt.strip()
    if not cleaned:
        raise ValueError("Story prompt cannot be empty")
    return cleaned


def main() -> None:
    user_prompt = "   A cute rabbit and baby elephant help a lost bird find its mother.   "
    story_idea = clean_prompt(user_prompt)
    print("KidToon AI is ready!")
    print(f"Story idea received: {story_idea}")

    story_path = Path(__file__).resolve().parent.parent / "data" / "sample_story.json"
    story = load_story(story_path)
    validate_story(story)

    names = [character["name"] for character in story["characters"]]
    print(f"Story title: {story['title']}")
    print(f"Characters: {', '.join(names)}")
    print(f"Number of scenes: {len(story['scenes'])}")
    for scene in story["scenes"]:
        print(f"  Scene {scene['scene_number']}: {scene['narration']}")


if __name__ == "__main__":
    main()