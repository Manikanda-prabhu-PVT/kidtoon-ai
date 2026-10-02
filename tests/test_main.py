import pytest

from app.main import clean_prompt


def test_clean_prompt_removes_extra_spaces():
    assert clean_prompt("   A rabbit and an elephant   ") == "A rabbit and an elephant"


def test_clean_prompt_rejects_empty_text():
    with pytest.raises(ValueError):
        clean_prompt("     ")