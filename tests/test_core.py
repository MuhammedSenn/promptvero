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


def test_set_main_and_get_main(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first content")
    p.save("second content")
    p.set_main("v1")
    assert p.get_main() == "first content"


def test_get_main_returns_pinned_version_not_latest(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first content")
    p.save("second content")
    p.save("third content")
    p.set_main("v1")
    assert p.get_main() == "first content"
    assert p.get() == "third content"


def test_set_main_can_be_updated(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first content")
    p.save("second content")
    p.set_main("v1")
    p.set_main("v2")
    assert p.get_main() == "second content"


def test_get_main_raises_when_not_set(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("content")
    with pytest.raises(PromptNotFoundError):
        p.get_main()


def test_log_is_main_flag(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first content")
    p.save("second content")
    p.set_main("v1")
    history = p.log()
    assert history[0]["is_main"] is True
    assert history[1]["is_main"] is False


def test_log_is_main_false_when_no_main_set(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("content")
    history = p.log()
    assert history[0]["is_main"] is False


def test_changes_returns_string(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("line one")
    p.save("line one\nline two")
    result = p.changes()
    assert isinstance(result, str)
    assert "line two" in result


def test_changes_shows_added_and_removed(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("line one\nline two")
    p.save("line one\nline three")
    result = p.changes("v1", "v2")
    assert "line three" in result
    assert "line two" in result


def test_show_returns_string(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("hello world")
    result = p.show()
    assert isinstance(result, str)
    assert "hello world" in result


def test_show_contains_main_tag(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("content")
    p.set_main("v1")
    result = p.show("v1")
    assert "[main]" in result


def test_show_no_main_tag_when_not_main(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first content")
    p.save("second content")
    p.set_main("v1")
    result = p.show("v2")
    assert "[main]" not in result


def test_list_all_returns_prompt_names(tmp_path):
    Prompt("system", base_dir=str(tmp_path)).save("content")
    Prompt("analyzer", base_dir=str(tmp_path)).save("content")
    names = Prompt.list_all(base_dir=str(tmp_path))
    assert "system" in names
    assert "analyzer" in names


def test_delete_version(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first")
    p.save("second")
    p.delete_version("v1")
    assert len(p.log()) == 1
    assert p.get() == "second"


def test_delete_version_clears_main(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("content")
    p.set_main("v1")
    p.delete_version("v1")
    with pytest.raises(PromptNotFoundError):
        p.get_main()


def test_delete_prompt_removes_all(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first")
    p.save("second")
    p.delete_prompt()
    assert "system" not in Prompt.list_all(base_dir=str(tmp_path))


def test_delete_prompt_raises_when_not_found(tmp_path):
    p = Prompt("system", base_dir=str(tmp_path))
    with pytest.raises(PromptNotFoundError):
        p.delete_prompt()


def test_list_all_returns_sorted(tmp_path):
    Prompt("zebra", base_dir=str(tmp_path)).save("content")
    Prompt("alpha", base_dir=str(tmp_path)).save("content")
    names = Prompt.list_all(base_dir=str(tmp_path))
    assert names == sorted(names)
