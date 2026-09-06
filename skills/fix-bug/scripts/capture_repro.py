#!/usr/bin/env python3
"""Run a reproduction command and append exact evidence to a JSON record."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a command without a shell, capture stdout/stderr/exit status, and "
            "append the result to a JSON evidence file."
        )
    )
    parser.add_argument("--output", required=True, type=Path, help="JSON evidence file")
    parser.add_argument("--label", required=True, help="Short evidence label")
    parser.add_argument("--cwd", type=Path, help="Working directory (defaults to current directory)")
    parser.add_argument("--timeout", type=float, default=300.0, help="Timeout in seconds")
    parser.add_argument(
        "--expect-exit",
        help="Optional expected exit: zero, nonzero, or an integer. A match returns 0.",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command after --")
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("provide a command after --")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    if args.expect_exit not in (None, "zero", "nonzero"):
        try:
            int(args.expect_exit)
        except ValueError:
            parser.error("--expect-exit must be zero, nonzero, or an integer")
    return args


def expectation_met(expected: str | None, exit_code: int | None, timed_out: bool) -> bool | None:
    if expected is None:
        return None
    if timed_out or exit_code is None:
        return False
    if expected == "zero":
        return exit_code == 0
    if expected == "nonzero":
        return exit_code != 0
    return exit_code == int(expected)


def load_document(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": 1, "records": []}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON evidence from {path}: {exc}") from exc
    if document.get("schema_version") != 1 or not isinstance(document.get("records"), list):
        raise ValueError(f"unsupported evidence document in {path}")
    return document


def write_atomic(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        delete=False,
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temp_path = Path(handle.name)
    try:
        with handle:
            json.dump(document, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def main() -> int:
    args = parse_args()
    cwd = (args.cwd or Path.cwd()).resolve()
    if not cwd.is_dir():
        print(f"capture_repro: working directory does not exist: {cwd}", file=sys.stderr)
        return 2

    started = dt.datetime.now(dt.timezone.utc)
    began = time.monotonic()
    timed_out = False
    exit_code: int | None = None
    stdout = ""
    stderr = ""
    try:
        completed = subprocess.run(
            args.command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=args.timeout,
            shell=False,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
    except OSError as exc:
        stderr = f"{type(exc).__name__}: {exc}"
        exit_code = 127

    matched = expectation_met(args.expect_exit, exit_code, timed_out)

    record = {
        "label": args.label,
        "captured_at_utc": started.isoformat(),
        "duration_seconds": round(time.monotonic() - began, 6),
        "cwd": str(cwd),
        "command": args.command,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "expected_exit": args.expect_exit,
        "expectation_met": matched,
        "stdout": stdout,
        "stderr": stderr,
    }

    try:
        document = load_document(args.output)
        document["records"].append(record)
        write_atomic(args.output.resolve(), document)
    except (OSError, ValueError) as exc:
        print(f"capture_repro: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(record, ensure_ascii=False))
    if args.expect_exit is not None:
        return 0 if matched else 1
    if timed_out:
        return 124
    return exit_code if exit_code is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
