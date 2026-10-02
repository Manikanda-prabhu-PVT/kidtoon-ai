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


if __name__ == "__main__":
    main()