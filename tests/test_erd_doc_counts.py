"""Audit the ERD-derived counts in docs against `docs/erds/erd-data.json`.

Every "N objects / N,NNN fields / NNN relationships" figure in the ERD docs is
hand-copied out of `erd-data.json`, and nothing regenerates them. The headline
triple is swept when the ERD is refreshed — it went 4,190 -> 4,252 fields at 264
and all five citations were updated — but the **per-domain** counts underneath it
never were, and the sweep does not look at them.

What that cost, measured on the 264 ERD (263 objects):

    Domain Overview table in revenue-cloud-data-model/SKILL.md
      7 of its 9 rows disagreed with the data; the Objects column summed to
      185 against an actual 263, so the table understated the model by 78
      objects while sitting directly under a correct "263 objects" headline.

    domains/*.md headlines
      6 of the 8 that carry a count disagreed. Only `configurator.md` (4) and
      `usage.md` (23) were right.

The drift is **not** uniformly stale-low, which is why "add the new objects"
would not have found it: `rates.md` and the table both claim 15 Rate Management
objects where the data has 11, an over-claim that predates the 264 refresh.
These numbers had simply stopped describing anything measurable — 6 of 9 matched
neither the ERD nor the file's own object table. The Approvals row is the clearest
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
`Advanced Approvals` folds into `Approvals`, mirroring `DOMAIN_MAP` in
`scripts/erd/build_erds.py`, which maps that label to the short name "Approvals";
the same folding is what makes the documented **9** domains out of 14 raw labels.

Five directions are checked, because these fail independently:

1. **`erd-data.json` agrees with itself** — its `stats` block vs the objects,
   fields and relationships actually present. Everything else trusts `stats`
   only after this passes, so a stale generator cannot certify the docs.
2. **Every headline triple matches the totals.** The distinctive
   "N objects, N fields, N relationships" phrasing, wherever it appears.
3. **Every Domain Overview row matches its domain.** Catches the 7 wrong rows.
4. **Every `domains/*.md` headline matches its domain.** Catches the 6 wrong ones.
5. **The taxonomy is closed and complete** — every domain label in the data folds
   into one of the 9 documented domains, all 9 appear in the table, and the rows
   sum to the total. This is the direction that catches the *next* refresh rather
   than this one: a new domain label, or a domain silently dropped from the table,
   is invisible to checks 3 and 4 because they only audit rows that exist.
"""

import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    """`4,252` -> 4252."""
    return int(text.replace(",", ""))


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
            if line.startswith("## "):
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
    triples = 0
    for path in TRIPLE_SITES:
        if not os.path.isfile(path):
            continue
        with open(path) as f:
            lines = f.read().split("\n")
        for i, line in enumerate(lines):
            window = " ".join(lines[i:i + 3])
            for m in triple.finditer(window):
                # Count a match only where it starts, so overlapping windows do not
                # report the same citation three times.
                if m.start() >= len(line) + 1:
                    continue
                triples += 1
                got = (num(m.group(1)), num(m.group(2)), num(m.group(3)))
                want = (totals["objects"], totals["fields"], totals["relationships"])
                check(
                    f"{rel(path)}:{i + 1}_triple",
                    got == want,
                    f"doc says {got}, erd-data.json has {want}",
                )
    check("headline_triple_found", triples > 0,
          "no citation matched the triple pattern — the phrasing changed and this "
          "direction stopped auditing anything")

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
    check("domain_overview_row_sum", sum(c for _, _, c in rows) == totals["objects"],
          f"rows sum to {sum(c for _, _, c in rows)}, total is {totals['objects']} — "
          "a domain is missing from the table or double-counted")

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
        with open(path) as f:
            head = f.read().split("\n")[:12]
        found = None
        for lineno, line in enumerate(head, 1):
            m = headline.search(line)
            if m:
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
                  f"{rel(path)} states no object count in its first 12 lines — a "
                  "headline was deleted or reworded, taking it out of this audit")
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
    check("domain_count_matches_docs", len(documented) == 9,
          f"{len(documented)} documented domains, but the docs say 9 across "
          f"{len(set(o.get('domain', '?') for o in erd['objects'].values()))} raw labels")

    print("=" * 116)
    print(
        f"{_passed}/{_total} checks passed  ({totals['objects']} objects / "
        f"{totals['fields']:,} fields / {totals['relationships']} relationships "
        f"across {len(per_domain)} domains)"
    )
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
