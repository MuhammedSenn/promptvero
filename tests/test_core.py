"""Tests for promptvero.core.Prompt."""

import pytest

from promptvero.core import Prompt
from promptvero.exceptions import PromptNotFoundError


def test_save_and_get(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("You are an expert")
    assert p.get() == "You are an expert"


def test_save_returns_version_string(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    version = p.save("content")
    assert version == "v1"


def test_save_from_file(tmp_path):
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("You are an expert", encoding="utf-8")
    p = Prompt("system", base_dir=str(tmp_path))
    version = p.save_from_file(str(prompt_file))
    assert version == "v1"
    assert p.get() == "You are an expert"


def test_save_from_missing_file_raises(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    with pytest.raises(PromptNotFoundError):
        p.save_from_file("nonexistent/path/file.md")


def test_log_returns_history(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("v1 content")
    p.save("v2 content")
    assert len(p.log()) == 2


def test_diff_returns_correct_keys(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("line one")
    p.save("line one\nline two")
    diff = p.diff("v1", "v2")
    assert "added" in diff
    assert "removed" in diff
    assert "unchanged" in diff


def test_checkout_correct_version(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first version")
    p.save("second version")
    assert p.checkout("v1") == "first version"


def test_two_prompts_independent(tmp_path):
    p1 = Prompt("system", base_dir=str(tmp_path))
    p2 = Prompt("analyzer", base_dir=str(tmp_path))
    p1.save("system content")
    p2.save("analyzer content")
    assert p1.get() == "system content"
    assert p2.get() == "analyzer content"


def test_multiple_instances_share_storage(tmp_path):
    p1 = Prompt("system", base_dir=str(tmp_path))
    p1.save("first content")
    p2 = Prompt("system", base_dir=str(tmp_path))
    assert p2.get() == "first content"
