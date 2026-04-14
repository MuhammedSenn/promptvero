"""Tests for promptvero.storage.Storage."""

import pytest

from promptvero.exceptions import PromptNotFoundError, VersionNotFoundError
from promptvero.storage import Storage


def test_save_creates_file(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "You are a helpful assistant")
    assert (tmp_path / "system" / "v1.txt").exists()


def test_save_increments_version(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    v1 = s.save("system", "first content")
    v2 = s.save("system", "second content")
    assert v1 == "v1"
    assert v2 == "v2"


def test_save_creates_history_json(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    assert (tmp_path / "system" / "history.json").exists()


def test_get_latest_returns_last_saved(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "first content")
    s.save("system", "second content")
    assert s.get("system") == "second content"


def test_get_specific_version(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "first content")
    s.save("system", "second content")
    assert s.get("system", version="v1") == "first content"


def test_get_raises_prompt_not_found(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    with pytest.raises(PromptNotFoundError):
        s.get("nonexistent")


def test_get_raises_version_not_found(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    with pytest.raises(VersionNotFoundError):
        s.get("system", version="v99")


def test_history_returns_correct_count(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "first")
    s.save("system", "second")
    s.save("system", "third")
    assert len(s.history("system")) == 3


def test_history_dict_has_required_keys(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    item = s.history("system")[0]
    assert "version" in item
    assert "timestamp" in item


def test_diff_added_lines(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "line one")
    s.save("system", "line one\nline two")
    result = s.diff("system", "v1", "v2")
    assert "line two" in result["added"]


def test_diff_removed_lines(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "line one\nline two")
    s.save("system", "line one")
    result = s.diff("system", "v1", "v2")
    assert "line two" in result["removed"]


def test_set_main_creates_main_json(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    s.set_main("system", "v1")
    assert (tmp_path / "system" / "main.json").exists()


def test_set_main_raises_for_nonexistent_version(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    with pytest.raises(VersionNotFoundError):
        s.set_main("system", "v99")


def test_get_main_returns_correct_version(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "first")
    s.save("system", "second")
    s.set_main("system", "v1")
    assert s.get_main("system") == "v1"


def test_get_main_returns_none_when_not_set(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    assert s.get_main("system") is None


def test_list_prompts_returns_all_names(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    s.save("analyzer", "content")
    names = s.list_prompts()
    assert "system" in names
    assert "analyzer" in names


def test_list_prompts_returns_sorted(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("zebra", "content")
    s.save("alpha", "content")
    names = s.list_prompts()
    assert names == sorted(names)


def test_next_version_no_collision_after_gap(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "first")
    s.save("system", "second")
    s.save("system", "third")
    (tmp_path / "system" / "v2.txt").unlink()
    next_version = s.save("system", "fourth")
    assert next_version == "v4"


def test_delete_version_removes_file(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    s.delete_version("system", "v1")
    assert not (tmp_path / "system" / "v1.txt").exists()


def test_delete_version_removes_history_entry(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "first")
    s.save("system", "second")
    s.delete_version("system", "v1")
    history = s.history("system")
    assert len(history) == 1
    assert history[0]["version"] == "v2"


def test_delete_version_clears_main_if_deleted(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    s.set_main("system", "v1")
    s.delete_version("system", "v1")
    assert s.get_main("system") is None


def test_delete_version_raises_for_nonexistent(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    with pytest.raises(VersionNotFoundError):
        s.delete_version("system", "v99")


def test_delete_prompt_removes_directory(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    s.delete_prompt("system")
    assert not (tmp_path / "system").exists()


def test_delete_prompt_raises_when_not_found(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    with pytest.raises(PromptNotFoundError):
        s.delete_prompt("nonexistent")


def test_history_does_not_contain_content(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "hello world")
    item = s.history("system")[0]
    assert "content" not in item
