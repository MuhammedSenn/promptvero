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
    assert "content" in item


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


def test_checkout_returns_correct_content(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "first")
    s.save("system", "second")
    assert s.checkout("system", "v1") == "first"


def test_version_not_found_raises_on_checkout(tmp_path):
    s = Storage(base_dir=str(tmp_path))
    s.save("system", "content")
    with pytest.raises(VersionNotFoundError):
        s.checkout("system", "v99")
