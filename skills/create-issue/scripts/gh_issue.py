#!/usr/bin/env python3
"""Small, fail-closed wrapper around the authenticated GitHub CLI.

This script intentionally delegates authentication and API details to `gh` and
never accepts tokens as arguments. It emits JSON for read/verify operations so
an agent can inspect results without scraping human-formatted output.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


class CliError(RuntimeError):
    """A safe, user-facing command failure."""


TYPE_LABELS = ("bug", "feature", "enhancement")
SCHEDULING_LABEL_RE = re.compile(
    r"^(?:parallel:(?:candidate|risky|blocked)|depends-on:\d+|area:[a-z0-9][a-z0-9._-]*)$"
)


def run(command: list[str], *, capture: bool = True) -> str:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=capture,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        raise CliError(f"Required executable is unavailable: {command[0]}") from exc
    if completed.returncode:
        detail = (completed.stderr or completed.stdout).strip()
        raise CliError(f"Command failed ({completed.returncode}): {' '.join(command)}\n{detail}")
    return (completed.stdout or "").strip()


def require_gh() -> None:
    if shutil.which("gh") is None:
        raise CliError("GitHub CLI 'gh' is not installed or not on PATH")


def parse_remote(remote: str) -> str:
    value = remote.strip()
    if value.startswith("git@"):
        match = re.match(r"git@([^:]+):(.+?)(?:\.git)?$", value)
        if not match:
            raise CliError(f"Cannot parse Git remote: {value}")
        host, path = match.groups()
    else:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https", "ssh", "git"} or not parsed.hostname:
            raise CliError(f"Cannot parse Git remote: {value}")
        host, path = parsed.hostname, parsed.path.lstrip("/")
        if path.endswith(".git"):
            path = path[:-4]
    path = path.strip("/")
    if path.count("/") != 1 or any(not part for part in path.split("/")):
        raise CliError(f"Remote is not an owner/repository pair: {value}")
    if host.lower() not in {"github.com", "www.github.com"} and ".github." not in host.lower():
        raise CliError(f"Remote host is not recognized as GitHub: {host}")
    return f"{host}/{path}"


def repo_from_git(remote: str) -> str:
    if remote:
        return parse_remote(remote)
    candidates: list[str] = []
    for name in ("origin", "upstream"):
        try:
            candidates.append(run(["git", "remote", "get-url", name]))
        except CliError:
            pass
    errors: list[str] = []
    for candidate in candidates:
        try:
            return parse_remote(candidate)
        except CliError as exc:
            errors.append(str(exc))
    if errors:
        raise CliError("No GitHub remote was found; " + errors[0])
    raise CliError("No Git remote was found; specify the intended repository explicitly")


def repo_arg(value: str | None) -> str:
    return value or repo_from_git("")


def json_command(args: list[str]) -> object:
    raw = run(args)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CliError(f"Expected JSON from gh but received: {raw[:300]}") from exc


def add_repo(args: list[str], repo: str) -> list[str]:
    return [*args, "--repo", repo]


def command_repo(args: argparse.Namespace) -> object:
    return {"repository": repo_from_git(args.remote or "")}


def command_auth(args: argparse.Namespace) -> object:
    repo = repo_arg(args.repo)
    host = repo.split("/", 1)[0]
    run(["gh", "auth", "status", "--hostname", host])
    return {"repository": repo, "host": host, "authenticated": True}


def command_list(args: argparse.Namespace) -> object:
    repo = repo_arg(args.repo)
    command = ["gh", "issue", "list", "--state", args.state, "--limit", str(args.limit), "--json", "number,title,body,state,url,labels"]
    if args.search:
        command += ["--search", args.search]
    return json_command(add_repo(command, repo))


def command_view(args: argparse.Namespace) -> object:
    repo = repo_arg(args.repo)
    command = ["gh", "issue", "view", str(args.number), "--json", "number,title,body,state,url,labels"]
    return json_command(add_repo(command, repo))


def command_labels(args: argparse.Namespace) -> object:
    repo = repo_arg(args.repo)
    command = ["gh", "label", "list", "--limit", "100", "--json", "name,description,color"]
    return json_command(add_repo(command, repo))


def command_ensure_label(args: argparse.Namespace) -> object:
    repo = repo_arg(args.repo)
    labels = command_labels(argparse.Namespace(repo=repo))
    if any(item.get("name") == args.label for item in labels):
        return {"repository": repo, "label": args.label, "created": False}
    command = ["gh", "label", "create", args.label, "--description", args.description, "--color", args.color]
    run(add_repo(command, repo))
    return {"repository": repo, "label": args.label, "created": True}


def body_args(args: argparse.Namespace) -> list[str]:
    path = Path(args.body_file)
    if not path.is_file():
        raise CliError(f"Body file does not exist: {path}")
    return ["--body-file", str(path)]


def validate_metadata_labels(labels: list[str]) -> list[str]:
    invalid = [label for label in labels if not SCHEDULING_LABEL_RE.fullmatch(label)]
    if invalid:
        raise CliError(
            "Unsupported scheduling label(s): " + ", ".join(invalid)
        )
    return labels


def review_finding_errors(document: object) -> list[str]:
    if not isinstance(document, dict):
        return ["review finding must be a JSON object"]
    errors: list[str] = []
    if document.get("source_mode") != "review-finding":
        errors.append("source_mode must be review-finding")
    for key in (
        "authoritative_expectation",
        "material_consequence",
        "bounded_remedy",
    ):
        if not isinstance(document.get(key), str) or not document[key].strip():
            errors.append(f"{key} must be non-empty")
    evidence = document.get("direct_evidence")
    if not isinstance(evidence, list) or not evidence or not all(
        isinstance(item, str) and item.strip() for item in evidence
    ):
        errors.append("direct_evidence must contain repository evidence")
    if document.get("confidence") != "high":
        errors.append("confidence must be high")
    if document.get("prd_edd_semantic_change_required") is not False:
        errors.append("PRD/EDD semantic decision must not be required")
    duplicate = document.get("duplicate_search")
    if not isinstance(duplicate, dict) or duplicate.get("open") is not True or duplicate.get("closed") is not True:
        errors.append("duplicate search must cover open and closed Issues")
    elif duplicate.get("equivalent_issue") is not None:
        errors.append("an equivalent Issue already exists")
    return errors


def command_check_review_finding(args: argparse.Namespace) -> object:
    path = Path(args.finding_file)
    if not path.is_file():
        raise CliError(f"Finding file does not exist: {path}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CliError(f"Finding file is not valid UTF-8 JSON: {path}: {exc}") from exc
    errors = review_finding_errors(document)
    if errors:
        raise CliError("Review finding is ineligible: " + "; ".join(errors))
    return {"source_mode": "review-finding", "eligible": True}


def command_create(args: argparse.Namespace) -> object:
    repo = repo_arg(args.repo)
    metadata = validate_metadata_labels(args.metadata_label)
    command = ["gh", "issue", "create", "--title", args.title, *body_args(args), "--label", args.label]
    for label in metadata:
        command += ["--label", label]
    output = run(add_repo(command, repo))
    url = output.splitlines()[-1].strip() if output else ""
    return {
        "repository": repo,
        "operation": "created",
        "type": args.label,
        "scheduling_labels": metadata,
        "url": url,
    }


def command_comment(args: argparse.Namespace) -> object:
    repo = repo_arg(args.repo)
    command = ["gh", "issue", "comment", str(args.number), *body_args(args)]
    run(add_repo(command, repo))
    return {"repository": repo, "operation": "commented", "number": args.number}


def command_edit(args: argparse.Namespace) -> object:
    repo = repo_arg(args.repo)
    command = ["gh", "issue", "edit", str(args.number), *body_args(args)]
    run(add_repo(command, repo))
    return {"repository": repo, "operation": "updated", "number": args.number}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--repo", help="[HOST/]OWNER/REPO; defaults to the Git remote")
    sub = root.add_subparsers(dest="command", required=True)

    repo = sub.add_parser("repo", help="resolve the current Git remote")
    repo.add_argument("--remote", help="explicit remote URL")
    repo.set_defaults(func=command_repo)

    auth = sub.add_parser("auth", help="verify gh authentication")
    auth.set_defaults(func=command_auth)

    listing = sub.add_parser("list", help="list Issues for duplicate detection")
    listing.add_argument("--state", choices=("open", "closed", "all"), default="all")
    listing.add_argument("--search", help="GitHub issue search query")
    listing.add_argument("--limit", type=int, default=100)
    listing.set_defaults(func=command_list)

    view = sub.add_parser("view", help="fetch one Issue")
    view.add_argument("number", type=int)
    view.set_defaults(func=command_view)

    labels = sub.add_parser("labels", help="list repository labels")
    labels.set_defaults(func=command_labels)

    ensure = sub.add_parser("ensure-label", help="create one missing minimal label")
    ensure.add_argument("label")
    ensure.add_argument("--description", default="Issue type")
    ensure.add_argument("--color", default="ededed")
    ensure.set_defaults(func=command_ensure_label)

    finding = sub.add_parser(
        "check-review-finding",
        help="validate the autonomous review-finding gate without writing",
    )
    finding.add_argument("--finding-file", required=True)
    finding.set_defaults(func=command_check_review_finding)

    for name, func, help_text in (("create", command_create, "create one Issue"), ("comment", command_comment, "append a comment"), ("edit", command_edit, "replace one Issue body")):
        item = sub.add_parser(name, help=help_text)
        if name == "create":
            item.add_argument("--title", required=True)
            item.add_argument("--label", required=True, choices=TYPE_LABELS)
            item.add_argument(
                "--metadata-label",
                action="append",
                default=[],
                help="optional scheduling hint such as parallel:risky or area:payments",
            )
        else:
            item.add_argument("number", type=int)
        item.add_argument("--body-file", required=True)
        item.set_defaults(func=func)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command != "repo":
            require_gh()
        result = args.func(args)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except CliError as exc:
        print(f"create-issue backend error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
