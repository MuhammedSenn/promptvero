"""Command-line interface for promptvero."""

import argparse
import sys

from promptvero.core import Prompt
from promptvero.exceptions import PromptVeroError


def cmd_list(args: argparse.Namespace) -> None:
    names = Prompt.list_all(base_dir=args.base_dir)
    if not names:
        print("No prompts saved yet.")
        return
    for name in names:
        print(name)


def cmd_save(args: argparse.Namespace) -> None:
    p = Prompt(args.name, base_dir=args.base_dir)
    version = p.save_from_file(args.file)
    print(f"Saved {args.name} as {version}")


def cmd_log(args: argparse.Namespace) -> None:
    p = Prompt(args.name, base_dir=args.base_dir)
    history = p.log()
    if not history:
        print("No versions found.")
        return
    for entry in history:
        main_tag = "  [main]" if entry["is_main"] else ""
        print(f"{entry['version']}  |  {entry['timestamp']}{main_tag}")


def cmd_show(args: argparse.Namespace) -> None:
    p = Prompt(args.name, base_dir=args.base_dir)
    print(p.show(version=args.version))


def cmd_changes(args: argparse.Namespace) -> None:
    p = Prompt(args.name, base_dir=args.base_dir)
    print(p.changes(v1=args.v1, v2=args.v2))


def cmd_set_main(args: argparse.Namespace) -> None:
    p = Prompt(args.name, base_dir=args.base_dir)
    p.set_main(args.version)
    print(f"Set {args.version} as main for '{args.name}'")


def cmd_get_main(args: argparse.Namespace) -> None:
    p = Prompt(args.name, base_dir=args.base_dir)
    print(p.get_main())


def cmd_delete(args: argparse.Namespace) -> None:
    p = Prompt(args.name, base_dir=args.base_dir)
    p.delete_version(args.version)
    print(f"Deleted {args.version} from '{args.name}'")


def cmd_delete_prompt(args: argparse.Namespace) -> None:
    p = Prompt(args.name, base_dir=args.base_dir)
    p.delete_prompt()
    print(f"Deleted prompt '{args.name}'")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pv",
        description="Git-like version control for LLM prompts.",
    )
    parser.add_argument(
        "--base-dir",
        default=".promptvero",
        metavar="DIR",
        help="Root directory for prompt storage (default: .promptvero)",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    sub.add_parser("list", help="List all saved prompts")

    p_save = sub.add_parser("save", help="Save a file as a new prompt version")
    p_save.add_argument("name", help="Prompt name")
    p_save.add_argument("file", help="Path to the file to save")

    p_log = sub.add_parser("log", help="Show version history for a prompt")
    p_log.add_argument("name", help="Prompt name")

    p_show = sub.add_parser("show", help="Show the content of a prompt version")
    p_show.add_argument("name", help="Prompt name")
    p_show.add_argument(
        "version", nargs="?", default=None, help="Version (default: latest)"
    )

    p_changes = sub.add_parser("changes", help="Show what changed between two versions")
    p_changes.add_argument("name", help="Prompt name")
    p_changes.add_argument(
        "v1", nargs="?", default=None, help="Base version (default: second-to-last)"
    )
    p_changes.add_argument(
        "v2", nargs="?", default=None, help="Target version (default: latest)"
    )

    p_set_main = sub.add_parser("set-main", help="Mark a version as the main prompt")
    p_set_main.add_argument("name", help="Prompt name")
    p_set_main.add_argument("version", help="Version to mark as main (e.g. v2)")

    p_get_main = sub.add_parser(
        "get-main", help="Print the content of the main version"
    )
    p_get_main.add_argument("name", help="Prompt name")

    p_delete = sub.add_parser("delete", help="Delete a specific version")
    p_delete.add_argument("name", help="Prompt name")
    p_delete.add_argument("version", help="Version to delete (e.g. v2)")

    p_delete_prompt = sub.add_parser(
        "delete-prompt", help="Delete a prompt and all its versions"
    )
    p_delete_prompt.add_argument("name", help="Prompt name")

    return parser


COMMANDS = {
    "list": cmd_list,
    "save": cmd_save,
    "log": cmd_log,
    "show": cmd_show,
    "changes": cmd_changes,
    "set-main": cmd_set_main,
    "get-main": cmd_get_main,
    "delete": cmd_delete,
    "delete-prompt": cmd_delete_prompt,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        COMMANDS[args.command](args)
    except PromptVeroError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
