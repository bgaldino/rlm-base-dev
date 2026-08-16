"""Audit the ERD-derived counts in docs against `docs/erds/erd-data.json`.

Every "N objects / N,NNN fields / NNN relationships" figure in the ERD docs is
hand-copied out of `erd-data.json`, and nothing regenerates them. The headline
triple is swept when the ERD is refreshed — it went 4,190 -> 4,252 fields at 264
and all seven citations were updated — but the **per-domain** counts underneath it
never were, and the sweep does not look at them.

What that cost, measured on the 264 ERD (263 objects):

    Domain Overview table in revenue-cloud-data-model/SKILL.md
      8 of its 9 rows disagreed with the data; the Objects column summed to
      185 against an actual 263, so the table understated the model by 78
      objects while sitting directly under a correct "263 objects" headline.

    domains/*.md headlines
      7 of the 9 disagreed. Only `configurator.md` (4) and `usage.md` (23)
      were right.

15 numbers, not the 13 first counted: the lower tally came from reading Usage
Mgmt's 22 as correct, which it is only if you exclude the `(Core Object)`
variants — the reading this file rejects three paragraphs down. A count is wrong
under the definition you publish, not under the one that flatters it.

The drift is **not** uniformly stale-low, which is why "add the new objects"
would not have found it: `rates.md` and the table both claim 15 Rate Management
objects where the data has 11, an over-claim that predates the 264 refresh — as
in fact every one of these errors does. The per-domain counts in `erd-data.json`
are byte-identical at `release/262`; only `totalFields` moved. So the refresh did
not stale these numbers. They had never been right, and had simply stopped
describing anything measurable. The Approvals row is the clearest
case: it claims 1 object and names `ApprovalSubmission`, while the domain holds 3
and `ApprovalSubmission` is the one tagged with a *different* label
(`Advanced Approvals`).

So this check pins each count to a definition rather than to whatever was true
when someone last counted by hand.

**The definition, stated once here because the docs cannot agree on it
implicitly.** A domain's object count is every object in `erd-data.json` whose
domain resolves to that domain, *including* the `(Core Object)` variants. That is
the only reading under which the per-domain counts sum to the 263 the headline
claims — excluding core objects yields 239, which matches no published figure.
`Advanced Approvals` folds into `Approvals`, mirroring `get_short_domain` in
`scripts/erd/build_erds.py`, which maps that label to the short name "Approvals".
Note the plain label `Approvals` is *not* a `DOMAIN_MAP` key at all — it reaches
the same short name through that function's fallback, which is the subject of
pack 148. Two operations get from 14 raw labels to the documented **9**: stripping
the 4 `(Core Object)` suffixes (14 -> 10), then this fold (10 -> 9).

Six directions are checked, because these fail independently:

1. **`erd-data.json` agrees with itself** — its `stats` block vs the objects,
   fields and relationships actually present. Everything else trusts `stats`
   only after this passes, so a stale generator cannot certify the docs.
2. **Every headline triple matches the totals**, and **every site still states
   one.** The distinctive "N objects, N fields, N relationships" phrasing. The
   second half is the load-bearing half: the first version of this layer asked
   only whether *any* site matched, so a file that reworded its citation — or was
   renamed — left the audit while the run reported clean. Verified: wrong numbers
   in a reworded `scripts/ai/README.md` passed 33/33.
3. **The Statistics block matches the totals.** `docs/erds/README.md` restates all
   three figures plus the domain count as a bullet list, which the triple pattern
   cannot match — so that file was audited at its three prose citations while four
   bullets in it went unchecked.
4. **Every Domain Overview row matches its domain.** Catches the 8 wrong rows.
5. **Every `domains/*.md` headline matches its domain.** Catches the 7 wrong ones.
6. **The taxonomy is closed and complete** — every domain label in the data folds
   into one of the documented domains, all of them appear in the table, the rows
   sum to the total, every "across N domains" claim matches how many the data
   actually folds to, and the table and the `domains/*.md` set cover the *same*
   domains. This is the direction that catches the *next* refresh rather than this
   one: a new domain label, or a domain silently dropped from the table, is
   invisible to checks 4 and 5 because they only audit rows that exist. The
   two-map agreement is here for the same reason — a domain with a table row but
   no sub-file is invisible to check 5, which iterates the file map, so nothing
   else would name it. The pinned count does move, but it says "something left the
   audit" and prompts you to raise EXPECTED_CHECKS, which would accept the
   unaudited domain. A smoke alarm is not a diagnosis.

Two things the pattern deliberately cannot do. It cannot tell the ERD triple from
the org-describe pair, so a doc phrasing that as "254 objects, 3,913 fields, 0
relationships" would fail here — loudly, printing both sides, so the diagnosis is
immediate. And a citation wrapped across more than WINDOW lines escapes the
pattern; that is now a failure of its site's `_states_the_triple` check rather
than a silent skip.
"""

import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lines a wrapped citation may span. Widening this only moves the boundary, so it is
# the per-site assertion below — not this number — that makes an escaped citation
# loud: a citation that wraps past WINDOW fails its file's `_states_the_triple`
# check, and if the file has others, the pinned total check count catches the loss.
WINDOW = 3

# The count this file reports when the docs and the data agree. Pinned so that a
# citation, row, headline or whole file leaving the audit shows up as a smaller
# number instead of as "all checks passed" — the failure mode the per-site guards
# above exist to prevent, and the reason `tests/test_branch_scope.py` pins its own.
EXPECTED_CHECKS = 51

ERD_DATA = os.path.join(REPO_ROOT, "docs", "erds", "erd-data.json")
SKILL = os.path.join(
    REPO_ROOT, ".cursor", "skills", "revenue-cloud-data-model", "SKILL.md"
)
DOMAINS_DIR = os.path.join(
    REPO_ROOT, ".cursor", "skills", "revenue-cloud-data-model", "domains"
)

# Files that cite the headline triple. Each is checked wherever the phrasing appears.
# All four docs the schema-validation skill names as restating the figures, so the
# one that got missed in the 262->264 sweep (`scripts/ai/README.md`, which left
# `query_erd.py stats` printing 264 numbers under a 262 README) is gated too.
TRIPLE_SITES = [
    os.path.join(REPO_ROOT, "docs", "erds", "README.md"),
    SKILL,
    os.path.join(REPO_ROOT, ".cursor", "skills", "schema-validation", "SKILL.md"),
    os.path.join(REPO_ROOT, "scripts", "ai", "README.md"),
]

# domains/<file>.md -> the domain label it documents, after folding.
FILE_TO_DOMAIN = {
    "pcm": "Product Catalog Management",
    "pricing": "Salesforce Pricing",
    "rates": "Rate Management",
    "configurator": "Product Configurator",
    "transactions": "Transaction Management",
    "dro": "Dynamic Revenue Orchestrator",
    "usage": "Usage Management",
    "billing": "Billing",
    "approvals": "Approvals",
}

# Domain Overview row label -> domain label. The table uses short names.
ROW_TO_DOMAIN = {
    "PCM": "Product Catalog Management",
    "Pricing": "Salesforce Pricing",
    "Rate Management": "Rate Management",
    "Configurator": "Product Configurator",
    "Transaction Mgmt": "Transaction Management",
    "DRO": "Dynamic Revenue Orchestrator",
    "Usage Mgmt": "Usage Management",
    "Billing": "Billing",
    "Approvals": "Approvals",
}

_passed = _total = 0


def check(label, cond, detail=""):
    global _passed, _total
    _total += 1
    if cond:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}  {detail}")


def fold(raw):
    """Collapse a raw erd-data.json domain label to a documented domain.

    Mirrors `DOMAIN_MAP` in scripts/erd/build_erds.py: the `(Core Object)`
    variants are the same domain as their base, and `Advanced Approvals` is
    displayed as `Approvals`.
    """
    base = raw.replace(" (Core Object)", "").strip()
    return "Approvals" if base == "Advanced Approvals" else base


def load():
    with open(ERD_DATA) as f:
        erd = json.load(f)
    objects = erd.get("objects", {})
    per_domain = {}
    for obj in objects.values():
        domain = fold(obj.get("domain", "?"))
        per_domain[domain] = per_domain.get(domain, 0) + 1
    totals = {
        "objects": len(objects),
        "fields": sum(len(o.get("fields", [])) for o in objects.values()),
        "relationships": len(erd.get("relationships", [])),
    }
    return erd, totals, per_domain


def num(text):
    """`4,252` -> 4252, and a comma-only cell -> None rather than a traceback.

    `[\\d,]+` matches `,`, which `int("")` turns into an uncaught ValueError — a
    crash where the point of this file is to report a `[FAIL]`.
    """
    digits = text.replace(",", "")
    return int(digits) if digits.isdigit() else None


def rel(path):
    return os.path.relpath(path, REPO_ROOT)


def domain_overview_rows():
    """Parse the Domain Overview table: [(lineno, row label, claimed count)]."""
    rows = []
    with open(SKILL) as f:
        lines = f.read().split("\n")
    in_table = False
    for lineno, line in enumerate(lines, 1):
        if line.startswith("## Domain Overview"):
            in_table = True
            continue
        if in_table:
            # Any heading ends the section, not just `## `. A `###` subsection would
            # otherwise let rows of a *different* table into this one's audit.
            if line.startswith("#"):
                break
            m = re.match(r"\|\s*\*\*([^*|]+)\*\*\s*\|\s*([\d,]+)\+?\s*\|", line)
            if m:
                rows.append((lineno, m.group(1).strip(), num(m.group(2))))
    return rows


def main():
    erd, totals, per_domain = load()

    print("=" * 116)
    print("erd-data.json internal consistency")
    stats = erd.get("stats", {})
    for key, stat_key in (
        ("objects", "totalObjects"),
        ("fields", "totalFields"),
        ("relationships", "totalRelationships"),
    ):
        check(
            f"stats.{stat_key}_matches_content",
            stats.get(stat_key) == totals[key],
            f"stats says {stats.get(stat_key)}, content has {totals[key]} — "
            "regenerate the ERD rather than editing the stats block",
        )

    print()
    print("headline triples")
    # Matched over a 3-line sliding window, not per line, because two of these four
    # citations are wrapped mid-phrase — `scripts/ai/README.md` breaks between "263"
    # and "objects". A per-line pattern reported both files clean while auditing
    # neither. The optional qualifier before "relationship" is for the same reason:
    # that file says "674 verified relationship edges", not "674 relationships".
    triple = re.compile(
        r"([\d,]+)\s+objects,\s+([\d,]+)\s+(?:platform\s+)?fields,\s+"
        r"([\d,]+)\s+(?:\w+\s+)?relationships?"
    )
    want = (totals["objects"], totals["fields"], totals["relationships"])
    triples = 0
    for path in TRIPLE_SITES:
        # Per site, not in aggregate. A global "did anything match?" only fires when
        # every site drops out at once, so one file rewording its citation — or being
        # renamed — took itself out of the audit while the run reported clean. Both
        # were demonstrated on `scripts/ai/README.md`, which is *also* the file the
        # last sweep already missed once and the only one whose citation wraps.
        if not os.path.isfile(path):
            check(f"{rel(path)}_exists", False,
                  "a site that restates the figures is missing — remove it from "
                  "TRIPLE_SITES deliberately or fix the path; skipping it silently is "
                  "how a file leaves the audit")
            continue
        with open(path) as f:
            lines = f.read().split("\n")
        here = 0
        for i, line in enumerate(lines):
            window = " ".join(lines[i:i + WINDOW])
            for m in triple.finditer(window):
                # Count a match only where it starts, so overlapping windows do not
                # report the same citation three times.
                if m.start() >= len(line) + 1:
                    continue
                here += 1
                got = (num(m.group(1)), num(m.group(2)), num(m.group(3)))
                check(
                    f"{rel(path)}:{i + 1}_triple",
                    got == want,
                    f"doc says {got}, erd-data.json has {want}",
                )
        triples += here
        check(f"{rel(path)}_states_the_triple", here > 0,
              f"no citation in {rel(path)} matched the triple pattern — it was "
              f"reworded, or wrapped across more than {WINDOW} lines, and this file "
              "stopped being audited")

    print()
    print("Statistics block")
    # `docs/erds/README.md` restates all three totals *and* the domain count as a
    # bullet list, which the triple pattern cannot match — so the file was audited at
    # three prose citations while four bullets in it went unchecked. Found by review.
    stat_bullets = {
        "Total Objects": totals["objects"],
        "Total Fields": totals["fields"],
        "Total Relationships": totals["relationships"],
        "Total Domains": len(per_domain),
    }
    readme = os.path.join(REPO_ROOT, "docs", "erds", "README.md")
    with open(readme) as f:
        readme_lines = f.read().split("\n")
    for label, expected in stat_bullets.items():
        hits = [
            (i + 1, num(m.group(1)))
            for i, line in enumerate(readme_lines)
            for m in [re.match(rf"-\s+\*\*{label}:\*\*\s+([\d,]+)", line)]
            if m
        ]
        # Absence is a failure, not a skip: these bullets are the densest restatement
        # of the figures in the repo, so a reworded label must not quietly drop them.
        check(f"statistics_{label.replace(' ', '_').lower()}_present", len(hits) == 1,
              f"expected exactly 1 `- **{label}:** N` bullet in {rel(readme)}, "
              f"found {len(hits)}")
        for lineno, claimed in hits:
            check(f"{rel(readme)}:{lineno}_{label.replace(' ', '_').lower()}",
                  claimed == expected,
                  f"bullet says {claimed}, erd-data.json has {expected}")

    print()
    print("Domain Overview table")
    rows = domain_overview_rows()
    check("domain_overview_table_parsed", len(rows) == len(ROW_TO_DOMAIN),
          f"parsed {len(rows)} rows, expected {len(ROW_TO_DOMAIN)} — a row stopped "
          "matching, so it left the audit silently")
    seen = set()
    for lineno, label, claimed in rows:
        domain = ROW_TO_DOMAIN.get(label)
        if domain is None:
            check(f"row_{label}_is_a_known_domain", False,
                  f"{rel(SKILL)}:{lineno} row **{label}** maps to no domain — add it "
                  "to ROW_TO_DOMAIN or fix the label")
            continue
        seen.add(domain)
        actual = per_domain.get(domain, 0)
        check(
            f"row_{label}_count",
            claimed == actual,
            f"{rel(SKILL)}:{lineno} claims {claimed}, {domain} has {actual}",
        )
    # `None` skipped, not summed: `num()` returns it for a malformed cell, and
    # `sum()` over it raises TypeError *before* this check or the pinned count can
    # report — a traceback in place of a `[FAIL]`. The row's own comparison above
    # already fails on `None`, so dropping it here loses no signal.
    counted = [c for _, _, c in rows if c is not None]
    check("domain_overview_row_sum", sum(counted) == totals["objects"],
          f"rows sum to {sum(counted)}, total is {totals['objects']} — a domain is "
          "missing from the table or double-counted")

    print()
    print("domains/*.md headlines")
    # The trailing `+` is deliberate: `pricing.md` read "14+ objects" against an
    # actual 27, and a pattern without it skipped the file and reported "no count
    # to audit" — a wrong number hiding behind a blind spot in the audit meant to
    # catch it. An approximate count is still a claim, so it is still checked.
    headline = re.compile(r"\b([\d,]+)\+?\s+(?:core\s+)?objects?\b")
    for stem, domain in sorted(FILE_TO_DOMAIN.items()):
        path = os.path.join(DOMAINS_DIR, f"{stem}.md")
        if not os.path.isfile(path):
            check(f"{stem}.md_exists", False, f"{rel(path)} is missing")
            continue
        # Scoped to the preamble — everything before the first `## ` section — rather
        # than to a fixed line budget. These files also state *data-plan* object counts
        # further down (`approvals.md`: "2 objects across 2 objectSets"), so a fixed
        # window that the front matter outgrew would start checking the wrong number
        # instead of reporting a missing one.
        with open(path) as f:
            head = []
            for line in f.read().split("\n"):
                if line.startswith("## "):
                    break
                head.append(line)
        found = None
        for lineno, line in enumerate(head, 1):
            m = headline.search(line)
            if m and num(m.group(1)) is not None:
                found = (lineno, num(m.group(1)))
                break
        actual = per_domain.get(domain, 0)
        if found is None:
            # Failed, not noted. Every one of these files states its object count,
            # so absence means a headline was deleted or reworded past the pattern —
            # and a *noted* absence still exits 0, which is how a deleted count
            # leaves the audit while the run reports clean. Demonstrated: the note
            # form survived the mutation that removed dro.md's count.
            check(f"{stem}.md_states_a_count", False,
                  f"{rel(path)} states no object count in its preamble — a headline "
                  "was deleted or reworded, taking it out of this audit")
            continue
        lineno, claimed = found
        check(
            f"{stem}.md_headline",
            claimed == actual,
            f"{rel(path)}:{lineno} claims {claimed}, {domain} has {actual}",
        )

    print()
    print("taxonomy is closed and complete")
    documented = set(ROW_TO_DOMAIN.values())
    unknown = sorted(d for d in per_domain if d not in documented)
    check("every_data_domain_is_documented", not unknown,
          f"erd-data.json carries domain(s) no doc covers: {unknown} — a new domain "
          "needs a table row, a domains/*.md, and a DOMAIN_MAP entry")
    missing = sorted(documented - seen)
    check("every_documented_domain_has_a_row", not missing,
          f"documented domain(s) absent from the Domain Overview table: {missing}")
    # The two maps must agree, asserted directly. A domain that reaches the data and
    # the table but never gets a `domains/*.md` is invisible to the headline layer,
    # which iterates FILE_TO_DOMAIN — so nothing here would have named it. The pinned
    # count does move, but it reports "a citation, row, headline or file left the
    # audit" and prompts you to raise EXPECTED_CHECKS, which is precisely the wrong
    # action: bumping it accepts an unaudited domain. A smoke alarm is not a diagnosis.
    only_row = sorted(set(ROW_TO_DOMAIN.values()) - set(FILE_TO_DOMAIN.values()))
    only_file = sorted(set(FILE_TO_DOMAIN.values()) - set(ROW_TO_DOMAIN.values()))
    check("table_and_sub_files_cover_the_same_domains",
          not only_row and not only_file,
          f"in the table with no domains/*.md: {only_row}; with a sub-file but no "
          f"table row: {only_file} — every domain needs both")
    # Against the DATA, not against a literal. `len(set(ROW_TO_DOMAIN.values())) == 9`
    # was the first version and it audited nothing: both sides were constants in this
    # file, so it could not fail. The quantity that actually moves is the number of
    # folded domains in erd-data.json, and what it must agree with is the "across N
    # domains" the docs claim — so both are read from their sources.
    raw_labels = len(set(o.get("domain", "?") for o in erd["objects"].values()))
    check("documented_domains_match_the_data",
          len(documented) == len(per_domain),
          f"{len(documented)} domains documented, {len(per_domain)} in the data "
          f"({raw_labels} raw labels before folding)")
    claim = re.compile(r"across\s+([\d,]+)\s+domains")
    claims = 0
    for path in TRIPLE_SITES:
        if not os.path.isfile(path):
            continue
        with open(path) as f:
            for lineno, line in enumerate(f.read().split("\n"), 1):
                for m in claim.finditer(line):
                    claims += 1
                    check(f"{rel(path)}:{lineno}_domain_count",
                          num(m.group(1)) == len(per_domain),
                          f"doc says {num(m.group(1))} domains, the data folds to "
                          f"{len(per_domain)}")
    check("domain_count_is_claimed_somewhere", claims > 0,
          "no doc states `across N domains` — the phrasing changed and this direction "
          "stopped auditing anything")

    # Counted like any other check, so the summary cannot read "N/N passed" next to a
    # non-zero exit. `ran` is sampled before the call, so the pin does not count itself.
    print()
    ran = _total
    check("check_count_is_pinned", ran == EXPECTED_CHECKS,
          f"ran {ran} checks, expected {EXPECTED_CHECKS} — a citation, row, headline "
          "or file left the audit; if the change was deliberate, update "
          "EXPECTED_CHECKS")

    print("=" * 116)
    print(
        f"{_passed}/{_total} checks passed  ({totals['objects']} objects / "
        f"{totals['fields']:,} fields / {totals['relationships']} relationships "
        f"across {len(per_domain)} domains, {triples} triple citations)"
    )
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
