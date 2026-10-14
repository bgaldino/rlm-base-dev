"""Read ``.env.local`` the way direnv's ``dotenv`` does, for ``./tui-cci``.

A port of direnv's parser (github.com/direnv/go-dotenv ``parse.go``, itself a
port of bkeepers/dotenv), so a file that loads through the tracked ``.envrc``
loads the same way when ``./tui-cci`` is launched from a shell that never
exported it. Accepted lines: comments, ``export KEY=value``, whitespace around
``=``, ``KEY: value``, single/double/unquoted values and a trailing ``# note``.
Single-quoted values are literal; other values expand ``$VAR``, ``${VAR}`` and
``${VAR:-default}`` from earlier keys in the file, then the environment. As in
direnv, one invalid line rejects the whole file.

Two deliberate differences from direnv:

* A variable already present in the environment -- even one exported empty --
  keeps its value, and later lines expand against that value.
* A value containing ``$(`` or a backtick is skipped with a warning rather than
  exported as mangled text, since nothing here runs commands.

Run as a script, it writes ``KEY\\0VALUE\\0`` pairs to stdout for the launcher
to export, and warnings to stderr.
"""

from __future__ import annotations

import os
import re
import sys
from collections.abc import Callable, Mapping
from pathlib import Path

# go-dotenv's LINE regexp after its own comment and whitespace stripping.
_LINE = re.compile(
    r"\A\s*(?:|#.*|(?:export\s+)?([\w.]+)(?:\s*=\s*|:\s+?)"
    r"""('(?:\'|[^'])*'|"(?:\"|[^"])*"|[^\s#\n]+)?\s*(?:\#.*)?)\Z"""
)
_LINE_BREAK = re.compile(r"\r\n|\r|\n")
_ESCAPE = re.compile(r"\\([^$])")
_SHELL_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_ALNUM = re.compile(r"[A-Za-z0-9_]*")
_SHELL_SPECIAL = frozenset("*#$@!?-0123456789")


class DotenvError(ValueError):
    """A line direnv would reject too, which stops the whole file loading."""


def _shell_name(text: str) -> tuple[str, int]:
    """Go's ``os.getShellName``: the name after a ``$`` and how much it spans."""
    if text[0] == "{":
        if len(text) > 2 and text[1] in _SHELL_SPECIAL and text[2] == "}":
            return text[1], 3
        end = text.find("}", 1)
        if end == 1:
            return "", 2
        if end == -1:
            return "", 1
        return text[1:end], end + 1
    if text[0] in _SHELL_SPECIAL:
        return text[0], 1
    name = _ALNUM.match(text).group()
    return name, len(name)


def _expand(value: str, lookup: Callable[[str], str]) -> str:
    """Go's ``os.Expand``: bad ``${`` syntax is dropped, a bare ``$`` is kept."""
    out: list[str] = []
    i = 0
    while i < len(value):
        if value[i] != "$" or i + 1 >= len(value):
            out.append(value[i])
            i += 1
            continue
        name, width = _shell_name(value[i + 1 :])
        if name:
            out.append(lookup(name))
        elif width == 0:
            out.append("$")
        i += 1 + width
    return "".join(out)


def load(data: str, environ: Mapping[str, str]) -> tuple[dict[str, str], list[str]]:
    """Return the variables to export and any warnings.

    Raises ``DotenvError`` when a line is not valid dotenv.
    """
    parsed: list[tuple[str, str]] = []
    for number, line in enumerate(_LINE_BREAK.split(data), start=1):
        match = _LINE.match(line)
        if match is None:
            raise DotenvError(f"line {number} is not valid dotenv")
        if match.group(1):
            parsed.append((match.group(1), match.group(2) or ""))

    effective: dict[str, str] = {}

    def lookup(name: str) -> str:
        key, has_default, default = name.partition(":-")
        if key in effective:
            return effective[key]
        value = environ.get(key, "")
        return default if has_default and not value else value

    exports: dict[str, str] = {}
    warnings: list[str] = []
    for key, raw in parsed:
        if key in environ:
            effective[key] = environ[key]
            continue
        if not _SHELL_IDENTIFIER.match(key):
            warnings.append(f"skipping {key}: not a valid shell variable name")
            continue
        value = raw
        if len(raw) > 1 and raw[0] == raw[-1] == "'":
            value = raw[1:-1]
        elif len(raw) > 1:
            if raw[0] == raw[-1] == '"':
                value = raw[1:-1].replace("\\n", "\n").replace("\\r", "\r")
                value = _ESCAPE.sub(r"\1", value)
            if "$(" in value or "`" in value:
                warnings.append(f"skipping {key}: .env.local cannot run commands")
                continue
            value = _expand(value, lookup)
        effective[key] = value
        exports[key] = value
    return exports, warnings


def main(argv: list[str]) -> int:
    data = Path(argv[1]).read_text(encoding="utf-8", errors="surrogateescape")
    try:
        exports, warnings = load(data, os.environ)
    except DotenvError as exc:
        print(f"[tui-cci] not loading .env.local: {exc}", file=sys.stderr)
        return 0
    for warning in warnings:
        print(f"[tui-cci] {warning}", file=sys.stderr)
    out = sys.stdout.buffer
    for key, value in exports.items():
        out.write(key.encode() + b"\0" + value.encode("utf-8", "surrogateescape") + b"\0")
    out.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
