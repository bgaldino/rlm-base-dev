from __future__ import annotations

import pytest

from scripts.build_harness.tui.dotenv_local import DotenvError, load


def _exports(text: str, environ: dict[str, str] | None = None) -> dict[str, str]:
    exports, _ = load(text, environ or {})
    return exports


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ('KEY="/path/to/Chrome" # managed build', "/path/to/Chrome"),
        ("KEY=/path/to/chrome # managed build", "/path/to/chrome"),
        ("KEY='/path/with spaces' # note", "/path/with spaces"),
        ('export KEY="/opt/chrome"', "/opt/chrome"),
        ('KEY = "/opt/chrome"', "/opt/chrome"),
        ("KEY: /opt/chrome", "/opt/chrome"),
        ("  KEY=value  ", "value"),
        ("KEY=", ""),
    ],
)
def test_accepts_the_line_forms_direnv_accepts(line: str, expected: str) -> None:
    assert _exports(line) == {"KEY": expected}


def test_skips_comments_and_blank_lines() -> None:
    assert _exports("# heading\n\n   \n  # indented\r\nKEY=1\r\n") == {"KEY": "1"}


def test_expands_like_direnv() -> None:
    text = "\n".join(
        [
            'BASE="$HOME/cft"',
            'BINARY="${BASE}/Chrome for Testing"',
            "FALLBACK=${MISSING:-/default/path}",
            "LITERAL='$HOME/not expanded'",
            'ESCAPED="a\\"b\\nc"',
            "DOLLAR=cost$",
        ]
    )
    assert _exports(text, {"HOME": "/Users/me"}) == {
        "BASE": "/Users/me/cft",
        "BINARY": "/Users/me/cft/Chrome for Testing",
        "FALLBACK": "/default/path",
        "LITERAL": "$HOME/not expanded",
        "ESCAPED": 'a"b\nc',
        "DOLLAR": "cost$",
    }


def test_environment_wins_even_when_empty_and_feeds_later_lines() -> None:
    environ = {"BASE": "/from/shell", "CHROME_BINARY": ""}
    text = 'BASE="/from/file"\nCHROME_BINARY="/file/chrome"\nDRIVER="$BASE/driver"'
    assert _exports(text, environ) == {"DRIVER": "/from/shell/driver"}


def test_command_substitution_is_skipped_not_run() -> None:
    exports, warnings = load('EVIL="$(rm -rf ~)"\nTICK=`id`\nOK=1', {})
    assert exports == {"OK": "1"}
    assert warnings == [
        "skipping EVIL: .env.local cannot run commands",
        "skipping TICK: .env.local cannot run commands",
    ]


def test_single_quoted_command_text_is_literal() -> None:
    assert _exports("NOTE='$(not run)'") == {"NOTE": "$(not run)"}


def test_one_invalid_line_rejects_the_whole_file() -> None:
    with pytest.raises(DotenvError, match="line 2"):
        load('GOOD="1"\nthis is not dotenv\n', {})


def test_dotted_keys_parse_but_are_not_exported() -> None:
    exports, warnings = load("app.name=demo\nKEY=1", {})
    assert exports == {"KEY": "1"}
    assert warnings == ["skipping app.name: not a valid shell variable name"]
