"""Tests for promptvero.cli."""

import sys

import pytest

from promptvero.cli import main
from promptvero.core import Prompt


def run_cli(args: list[str], base_dir: str) -> tuple[str, str, int]:
    """Run the CLI with given args and return (stdout, stderr, exit_code)."""
    argv = ["pv", "--base-dir", base_dir] + args
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(sys, "argv", argv)
        try:
            main()
            return "", "", 0
        except SystemExit as e:
            return "", "", int(e.code or 0)


def test_list_empty(tmp_path, capsys):
    run_cli(["list"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "No prompts saved yet." in out


def test_list_shows_prompt_names(tmp_path, capsys):
    Prompt("system", base_dir=str(tmp_path)).save("content")
    run_cli(["list"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "system" in out


def test_save_from_file(tmp_path, capsys):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("hello world", encoding="utf-8")
    run_cli(["save", "system", str(prompt_file)], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "v1" in out
    assert Prompt("system", base_dir=str(tmp_path)).get() == "hello world"


def test_save_missing_file_exits_with_error(tmp_path, capsys):
    _, _, code = run_cli(
        ["save", "system", str(tmp_path / "missing.txt")], base_dir=str(tmp_path)
    )
    err = capsys.readouterr().err
    assert code == 1
    assert "Error" in err


def test_log_shows_versions(tmp_path, capsys):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first")
    p.save("second")
    run_cli(["log", "system"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "v1" in out
    assert "v2" in out


def test_log_shows_main_tag(tmp_path, capsys):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first")
    p.set_main("v1")
    run_cli(["log", "system"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "[main]" in out


def test_log_empty(tmp_path, capsys):
    Prompt("system", base_dir=str(tmp_path)).save("x")
    run_cli(["log", "system"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "v1" in out


def test_show_latest(tmp_path, capsys):
    Prompt("system", base_dir=str(tmp_path)).save("hello world")
    run_cli(["show", "system"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "hello world" in out


def test_show_specific_version(tmp_path, capsys):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first")
    p.save("second")
    run_cli(["show", "system", "v1"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "first" in out


def test_changes_output(tmp_path, capsys):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("line one")
    p.save("line one\nline two")
    run_cli(["changes", "system"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "line two" in out


def test_set_main(tmp_path, capsys):
    Prompt("system", base_dir=str(tmp_path)).save("content")
    run_cli(["set-main", "system", "v1"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "v1" in out
    assert "main" in out


def test_set_main_invalid_version_exits_with_error(tmp_path, capsys):
    Prompt("system", base_dir=str(tmp_path)).save("content")
    _, _, code = run_cli(
        ["set-main", "system", "v99"], base_dir=str(tmp_path)
    )
    err = capsys.readouterr().err
    assert code == 1
    assert "Error" in err


def test_get_main(tmp_path, capsys):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("main content")
    p.set_main("v1")
    run_cli(["get-main", "system"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "main content" in out


def test_get_main_not_set_exits_with_error(tmp_path, capsys):
    Prompt("system", base_dir=str(tmp_path)).save("content")
    _, _, code = run_cli(["get-main", "system"], base_dir=str(tmp_path))
    err = capsys.readouterr().err
    assert code == 1
    assert "Error" in err


def test_delete_version(tmp_path, capsys):
    p = Prompt("system", base_dir=str(tmp_path))
    p.save("first")
    p.save("second")
    run_cli(["delete", "system", "v1"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "v1" in out
    assert len(p.log()) == 1


def test_delete_version_invalid_exits_with_error(tmp_path, capsys):
    Prompt("system", base_dir=str(tmp_path)).save("content")
    _, _, code = run_cli(
        ["delete", "system", "v99"], base_dir=str(tmp_path)
    )
    err = capsys.readouterr().err
    assert code == 1
    assert "Error" in err


def test_delete_prompt(tmp_path, capsys):
    Prompt("system", base_dir=str(tmp_path)).save("content")
    run_cli(["delete-prompt", "system"], base_dir=str(tmp_path))
    out = capsys.readouterr().out
    assert "system" in out
    assert "system" not in Prompt.list_all(base_dir=str(tmp_path))


def test_delete_prompt_invalid_exits_with_error(tmp_path, capsys):
    _, _, code = run_cli(
        ["delete-prompt", "nonexistent"], base_dir=str(tmp_path)
    )
    err = capsys.readouterr().err
    assert code == 1
    assert "Error" in err
