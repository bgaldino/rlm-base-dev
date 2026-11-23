"""Capture guard: refuse a capture that is not the article, before it is written.

A refresh overwrites each captured file with what the portal serves now. Two
failure shapes slip through the fetch-level checks (HTTP status, empty body,
missing H1) and used to land in the corpus as if they were content:

* **Placeholder**: the Help portal answers a retired or unknown article id with
  a rendered page whose H1 and first line say "We couldn't find the page you're
  looking for." It has an H1 and a body, so nothing flags it. The 2026-11-23
  264 refresh wrote it over 4 articles (two Help articles, two release notes)
  and recorded them as captured.
* **Truncated stub**: the atlas content API serves a page cut to its heading
  and first lines (the 264.0 source of the Decision Table Definitions POST page
  is 1.5 KB against 17.2 KB at the prior capture). The converter is faithful, so
  the capture was a correct copy of a bad source.

Both are detected here from the captured text alone (stdlib, no browser), so the
rules are unit-testable offline. See ``scripts/doc_snapshot/README.md`` ->
"Capture guard" for the evidence behind each threshold.
"""

import re
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Placeholder (portal not-found page)
# ---------------------------------------------------------------------------

# Compared after folding curly quotes, case and runs of whitespace.
_NOT_FOUND_LEADS = (
    "we couldn't find the page you're looking for",   # seen 2026-11-23, 4 captures
    "we looked high and low",                          # seen earlier, ind.dro_* page
)
# Boilerplate the not-found page carries below its headline.
_NOT_FOUND_MARKERS = (
    "searching for something? agentforce can help",
    "may we also suggest",
)
# A real article can quote a marker; a placeholder is short. Two markers on a
# short body is a placeholder even if the portal rewords the headline.
_PLACEHOLDER_MAX_BODY_CHARS = 1500


def _fold(text: str) -> str:
    text = (text or "").replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", text).strip().lower()


def placeholder_reason(title: Optional[str], body: Optional[str]) -> Optional[str]:
    """Why ``title``/``body`` is the portal's not-found page, or None.

    Signals (any one refuses): the title leads with a known not-found headline;
    the first non-empty body line does (the portal repeats the headline as H1
    and as the first line); or the body is short and carries two of the
    not-found boilerplate markers.
    """
    folded_title = _fold(title)
    for lead in _NOT_FOUND_LEADS:
        if folded_title.startswith(lead):
            return f"portal not-found page (title is {title.strip()!r})"
    text = body or ""
    first = next((ln for ln in text.splitlines() if ln.strip()), "")
    folded_first = _fold(first)
    for lead in _NOT_FOUND_LEADS:
        if folded_first.startswith(lead):
            return "portal not-found page (body opens with the not-found headline)"
    folded_body = _fold(text)
    hits = [m for m in _NOT_FOUND_MARKERS if m in folded_body]
    if len(hits) >= 2 and len(text) <= _PLACEHOLDER_MAX_BODY_CHARS:
        return "portal not-found page (body carries the not-found boilerplate)"
    return None


# ---------------------------------------------------------------------------
# Truncated stub (shrinkage against the prior capture)
# ---------------------------------------------------------------------------

# Refuse when the new body keeps under this share of the prior body's
# characters AND under SHRINK_WORD_RATIO of its words. Requiring both keeps a
# reformat (table pipes, link syntax) that changes size but not content from
# tripping the guard; a real truncation drops both.
SHRINK_CHAR_RATIO = 0.5
SHRINK_WORD_RATIO = 0.6
# Below this prior size a page is a one-line note whose ratio is noise (a
# 479-char page that now reads "Reserved for internal use." is a real edit).
SHRINK_MIN_PRIOR_CHARS = 500

_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
_ATTRIBUTION = re.compile(r"\n---\n\n> \*\*Source attribution.*\Z", re.S)
_H1 = re.compile(r"\A\s*# [^\n]*\n")
# Preview banner the 262-era captures carried at the top of every dev-guide page.
_PREVIEW_NOTE = re.compile(r"\A\s*Note: This release is in preview\.[^\n]*\n")
_WORD = re.compile(r"\w+")


def body_of(captured_file_text: str) -> str:
    """The article body of a captured file: no frontmatter, H1, banner or footer."""
    text = _FRONTMATTER.sub("", captured_file_text, count=1)
    text = _ATTRIBUTION.sub("", text, count=1)
    text = _PREVIEW_NOTE.sub("", text, count=1)
    text = _H1.sub("", text, count=1)
    return text.strip()


def _words(text: str) -> int:
    return len(_WORD.findall(text))


def shrink_reason(prior_body: Optional[str], new_body: str) -> Optional[str]:
    """Why ``new_body`` is a truncated stub of ``prior_body``, or None."""
    prior = (prior_body or "").strip()
    new = (new_body or "").strip()
    if len(prior) < SHRINK_MIN_PRIOR_CHARS:
        return None
    char_ratio = len(new) / len(prior)
    prior_words = _words(prior)
    word_ratio = _words(new) / prior_words if prior_words else 1.0
    if char_ratio < SHRINK_CHAR_RATIO and word_ratio < SHRINK_WORD_RATIO:
        return (
            f"shrank to {char_ratio:.0%} of the prior capture's characters and "
            f"{word_ratio:.0%} of its words ({len(prior):,} -> {len(new):,} chars)"
        )
    return None


def refusal_reason(
    title: Optional[str],
    body: str,
    prior_file_text: Optional[str],
    accept_shrinkage: bool = False,
) -> Optional[str]:
    """Why a capture must not be written, or None when it is safe to write.

    A placeholder is never overridable. Shrinkage is refused unless
    ``accept_shrinkage`` (the operator has read the page and the loss is real).
    """
    reason = placeholder_reason(title, body)
    if reason:
        return reason
    if accept_shrinkage or not prior_file_text:
        return None
    return shrink_reason(body_of(prior_file_text), body)


def report_refusals(logger, refused: List[Tuple[str, str]]) -> None:
    """Log every refused page at the end of a capture, with the way out."""
    if not refused:
        return
    logger.warning(
        f"Refused {len(refused)} capture(s); the prior file and manifest size were kept:"
    )
    for page_id, reason in sorted(refused):
        logger.warning(f"  {page_id}: {reason}")
    logger.warning(
        "If a shrunken page is the real new text, re-run with --accept-shrinkage. "
        "A not-found page is never written: the id was retired or moved."
    )


def report_orphans(logger, orphaned: List[str], noun: str) -> None:
    """Log errored pages the current table of contents no longer lists.

    Salesforce moves pages between guides and retires others (18 asset and
    order object pages left the 264.0 developer guide for the Object Reference).
    Such a page keeps erroring on every refresh; this names it so it can be
    retired or marked moved instead of read as a transient fetch failure.
    """
    if not orphaned:
        return
    logger.warning(
        f"{len(orphaned)} errored {noun}(s) are no longer in the current table of "
        "contents (moved or retired upstream); their earlier capture was kept. "
        "Retire them or mark them moved:"
    )
    for page_id in sorted(orphaned):
        logger.warning(f"  {page_id}")
