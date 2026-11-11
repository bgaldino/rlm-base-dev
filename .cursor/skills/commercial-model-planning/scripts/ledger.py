#!/usr/bin/env python3
"""Verification ledger: how a build affirms or refutes its plan's predictions.

Part of the commercial-model-planning skill (SKILL.md, step 9). Standard library only.
Run it from the folder that holds the plan; paths are relative to the current folder.

    python3 ledger.py init --plan plan.md [--blind <blind plan>] [--intake D1-D6] [--owner D7,D8]
    python3 ledger.py record <ID> <outcome> "<evidence>" [--path "<what was built>"]
                             [--skill "<skill/file: claim>"] [--blind-right yes|no]
    python3 ledger.py report

Every prediction is one row of the plan. Each section is found by a heading or a bold
label (a line starting "**") that contains its marker, ignoring case; every such section
is read (one heading per area works), and only tables whose header identifies the kind
count, so a passing mention elsewhere adds nothing. init fails if no rule or decision
rows are found:
  rule      tables under "Rule decision record" whose first header cell starts "Rule"
  decision  tables under "2. Decisions" whose first header cell is "#" (so a table of
            what each choice changes is not read as decisions)
  spike     tables under "P2 Live spikes" with a "must hit" column
Other tables in a section, such as the next phase's under a label, are skipped.
The first cell of a row is its ID. Override the markers with --rules, --decisions, --spikes.

Origins (set by init):
  blind    the row is in the blind plan unchanged
  edited   the row is in the blind plan but was changed before the build (blind text kept)
  added    the row is not in the blind plan
  intake   a decision the build owner gave at intake (--intake): not a prediction
  owner    a decision a person settled after the blind plan, the source owner or the
           build owner (--owner): not a prediction
With no blind plan, every row not named by --intake or --owner is "blind". Intake and
owner items are excluded from accuracy. --blind, --intake and --owner are remembered, so
a later init needs only --plan.

Outcomes (set by record), judged against what the item predicts (a rule's native
feature, a decision's recommendation, a spike's must-hit at its enforcement point; a
rule with two decided-by values takes the worse of its parts): affirmed (held, goldens pass),
modified (held with different values or configuration), refuted (failed; a fallback or
another route was used), inconclusive. New items are pending.

init keeps every recorded outcome and, for rows already in the ledger, the row it first
recorded, so the blind measurement survives later plan revisions. Origins are worked out
again on every init, so a decision moved to --owner after the plan was written leaves
the accuracy count. --rebuild re-reads every row from the plan (outcomes are still kept).
"""
import argparse
import json
import re
import sys
from pathlib import Path

OUTCOMES = ("pending", "affirmed", "modified", "refuted", "inconclusive")
ORIGINS = ("blind", "edited", "added", "intake", "owner")
KINDS = ("rule", "decision", "spike")
DEFAULT_MARKERS = {
    "rule": "Rule decision record",
    "decision": "2. Decisions",
    "spike": "P2 Live spikes",
}
LABELS = ("Repo (inferred)", "Build (custom)", "Repo", "Snapshot", "Live")


def heading_level(line):
    m = re.match(r"(#{1,6}) ", line)
    return len(m.group(1)) if m else 0


def section_lines(lines, marker):
    """The plan's lines that lie in any section for `marker`, others blanked (so tables in
    different sections never join). A section starts at a heading or bold label (a line
    starting "**") that holds the marker, ignoring case. A heading ends at the next heading
    of the same or a higher level; a label ends at the next heading or the next label
    (the next phase), while bulleted bold lines ("- **Gate:**") stay inside it.
    Overlapping sections are read once."""
    want = marker.lower()
    keep = set()
    for start, line in enumerate(lines):
        level = heading_level(line)
        if want not in line.lower() or not (level or line.startswith("**")):
            continue
        for i in range(start + 1, len(lines)):
            h = heading_level(lines[i])
            if h and (not level or h <= level):
                break
            if not level and lines[i].startswith("**"):
                break
            keep.add(i)
    return [l if i in keep else "" for i, l in enumerate(lines)]


def cells(line):
    parts = line.strip().strip("|").replace("\\|", "\0").split("|")
    return [p.replace("\0", "|").strip() for p in parts]


def is_separator(line):
    return bool(re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?", line.strip()))


def clean_id(cell):
    """The row's ID: the whole first cell, or its first word when that word holds a digit
    ("L-01 Regional route" -> "L-01"). A cell listing several IDs ("A-01, A-02") is kept whole."""
    text = re.sub(r"[*`]", "", cell).strip()
    first = text.split(" ", 1)[0]
    if "," not in text and re.search(r"\d", first):
        return first
    return text


TABLE_TEST = {
    "decision": lambda h: h[0] == "#",
    "rule": lambda h: h[0].lower().startswith("rule"),
    "spike": lambda h: any(re.search(r"must.hit", c, re.I) for c in h),
}


def table_rows(lines, kind):
    """{id: (header cells, row cells, raw line)} for the body rows of every table whose
    header passes the kind's TABLE_TEST."""
    rows = {}
    header = None
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            header = None
            continue
        if is_separator(line):
            continue
        if i + 1 < len(lines) and is_separator(lines[i + 1]):
            header = cells(line)
            continue
        if not header or not TABLE_TEST[kind](header):
            continue
        row = cells(line)
        iid = clean_id(row[0]) if row else ""
        if not iid:
            continue
        if iid in rows:
            print(f"warning: {iid} appears twice; keeping the first row", file=sys.stderr)
            continue
        rows[iid] = (header or [], row, line.strip())
    return rows


def items(text, markers, name):
    lines = text.splitlines()
    found = {}
    for kind in KINDS:
        found[kind] = table_rows(section_lines(lines, markers[kind]), kind)
        if not found[kind]:
            msg = f"{name}: no {kind} rows under a heading or bold label containing '{markers[kind]}'"
            if kind == "spike":
                print(f"warning: {msg}", file=sys.stderr)
            else:
                sys.exit(f"error: {msg}")
    return found


def id_set(spec):
    """'D1-D3,D7' -> {'D1', 'D2', 'D3', 'D7'}."""
    out = set()
    for part in filter(None, (p.strip() for p in (spec or "").split(","))):
        m = re.fullmatch(r"([A-Za-z]*-?)(\d+)-\1?(\d+)", part)
        if m:
            prefix, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
            width = len(m.group(2)) if m.group(2).startswith("0") else 0
            out |= {f"{prefix}{n:0{width}d}" for n in range(lo, hi + 1)}
        else:
            out.add(part)
    return out


def norm(line):
    return re.sub(r"\s+", " ", line).strip()


def prediction(header, row):
    if len(header) == len(row):
        return dict(zip(header[1:], row[1:]))
    return {"cells": row[1:]}


def load(path):
    if not path.exists():
        sys.exit(f"no ledger at {path}; run init first")
    return json.loads(path.read_text())


def save(path, ledger):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n")


def init(args):
    ledger_path = Path(args.ledger)
    old = json.loads(ledger_path.read_text()) if ledger_path.exists() else {"meta": {}, "items": {}}
    meta = old.get("meta", {})
    markers = {k: getattr(args, k + "s") or meta.get("markers", {}).get(k) or DEFAULT_MARKERS[k]
               for k in KINDS}
    intake = id_set(args.intake) if args.intake is not None else set(meta.get("intake", []))
    owner = id_set(args.owner) if args.owner is not None else set(meta.get("owner", []))
    blind_path = args.blind or meta.get("blind")
    plan = items(Path(args.plan).read_text(), markers, args.plan)
    blind = items(Path(blind_path).read_text(), markers, blind_path) if blind_path else None

    ledger = {"meta": {"plan": args.plan, "blind": blind_path, "markers": markers,
                       "intake": sorted(intake), "owner": sorted(owner)},
              "items": {}}
    def origin_of(kind, iid, line):
        if kind == "decision" and iid in intake:
            return "intake"
        if kind == "decision" and iid in owner:
            return "owner"
        if blind is None:
            return "blind"
        if iid not in blind[kind]:
            return "added"
        return "blind" if norm(blind[kind][iid][2]) == norm(line) else "edited"

    def entry(kind, iid, line, pred, prev):
        origin = origin_of(kind, iid, line)
        return {
            "kind": kind,
            "id": iid,
            "origin": origin,
            "line": line,
            "prediction": pred,
            "blind_prediction": blind[kind][iid][2] if origin == "edited" else None,
            "outcome": prev["outcome"] if prev else "pending",
            "evidence": prev["evidence"] if prev else [],
        }

    seen = set()
    for kind in KINDS:
        for iid, (header, row, raw) in plan[kind].items():
            key = f"{kind}:{iid}"
            seen.add(key)
            prev = old["items"].get(key)
            if prev and not args.rebuild:
                ledger["items"][key] = entry(kind, iid, prev["line"], prev["prediction"], prev)
            else:
                ledger["items"][key] = entry(kind, iid, raw, prediction(header, row), prev)
    for key, prev in old["items"].items():
        if key not in seen:
            print(f"warning: {key} is no longer in the plan; kept as recorded", file=sys.stderr)
            ledger["items"][key] = entry(prev["kind"], prev["id"], prev["line"], prev["prediction"], prev)
    save(ledger_path, ledger)
    counts = {k: sum(1 for v in ledger["items"].values() if v["kind"] == k) for k in KINDS}
    print(f"{len(ledger['items'])} items in {ledger_path}: "
          + ", ".join(f"{n} {k}s" for k, n in counts.items()))


def find(ledger, iid):
    if iid in ledger["items"]:
        return iid
    keys = [k for k, v in ledger["items"].items() if v["id"] == iid]
    if len(keys) == 1:
        return keys[0]
    if keys:
        sys.exit(f"{iid} is ambiguous: use one of {keys}")
    sys.exit(f"unknown id {iid}")


def record(args):
    ledger_path = Path(args.ledger)
    ledger = load(ledger_path)
    key = find(ledger, args.id)
    entry = {"outcome": args.outcome, "evidence": args.evidence}
    if args.path:
        entry["path_taken"] = args.path
    if args.skill:
        entry["skill_claim"] = args.skill
    item = ledger["items"][key]
    if args.blind_right:
        if item["origin"] != "edited":
            sys.exit(f"--blind-right applies only to an edited item; {key} is {item['origin']}")
        entry["blind_right"] = args.blind_right
    item["outcome"] = args.outcome
    item["evidence"].append(entry)
    save(ledger_path, ledger)
    print(f"{key}: {args.outcome}")


def label(item):
    by = next((v for k, v in item["prediction"].items() if "decided by" in k.lower()), "")
    by = re.sub(r"[*`]", "", by)
    found = []
    for m in re.finditer("|".join(re.escape(x) for x in LABELS), by):
        if m.group(0) not in found:
            found.append(m.group(0))
    return " + ".join(found) or "(none)"


def report(args):
    ledger_path = Path(args.ledger)
    ledger = load(ledger_path)
    values = list(ledger["items"].values())
    out_path = ledger_path.with_name("scorecard.md")
    lines = ["# Verification scorecard", "",
             f"Generated by `ledger.py report` from `{ledger_path.name}`. Do not edit by hand. "
             "Intake and owner items are excluded from accuracy: the planner was given them.", "",
             "| Kind | Origin | Items | " + " | ".join(o.capitalize() for o in OUTCOMES[1:]) + " | Pending |",
             "|---|---|---|" + "---|" * len(OUTCOMES)]
    for k in KINDS:
        for o in ("blind", "edited", "added"):
            sel = [v for v in values if v["kind"] == k and v["origin"] == o]
            if sel:
                n = [sum(1 for v in sel if v["outcome"] == x) for x in OUTCOMES[1:] + ("pending",)]
                lines.append(f"| {k} | {o} | {len(sel)} | " + " | ".join(map(str, n)) + " |")
    excluded = [v for v in values if v["origin"] in ("intake", "owner")]
    lines += ["", f"Excluded (intake or owner): {len(excluded)}."]

    edited = [v for v in values if v["origin"] == "edited" and v["evidence"]]
    verdicts = [next((e["blind_right"] for e in reversed(v["evidence"]) if "blind_right" in e), None)
                for v in edited]
    if edited:
        lines += ["", "## Edited items: would the blind text have held?", "",
                  f"Yes {verdicts.count('yes')}, no {verdicts.count('no')}, "
                  f"not recorded {sum(1 for x in verdicts if x is None)}."]

    labels = {}
    for v in values:
        if v["kind"] == "rule":
            labels.setdefault(label(v), []).append(v["outcome"])
    if labels:
        lines += ["", "## Rules by knowledge source", "",
                  "| Decided by | Rules | " + " | ".join(o.capitalize() for o in OUTCOMES[1:]) + " | Pending |",
                  "|---|---|" + "---|" * len(OUTCOMES)]
        for lab, outs in sorted(labels.items()):
            lines.append(f"| {lab} | {len(outs)} | "
                         + " | ".join(str(outs.count(x)) for x in OUTCOMES[1:] + ("pending",)) + " |")

    lines += ["", "## Refuted or modified", ""]
    for key, v in ledger["items"].items():
        if v["outcome"] in ("refuted", "modified") and v["evidence"]:
            last = v["evidence"][-1]
            lines.append(f"- **{key}** ({v['origin']}): {v['outcome']}. {last.get('evidence', '')}"
                         + (f" Path: {last['path_taken']}." if "path_taken" in last else ""))

    claims = [(key, e) for key, v in ledger["items"].items() for e in v["evidence"] if "skill_claim" in e]
    lines += ["", "## Skill claims to settle", ""]
    lines += [f"- **{key}** ({e['outcome']}): {e['skill_claim']}" for key, e in claims] or ["None recorded."]
    out_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--ledger", default="verification/ledger.json",
                   help="ledger file (default: verification/ledger.json); the scorecard is written beside it")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="build or update the ledger from the plan")
    i.add_argument("--plan", required=True, help="the plan the build follows")
    i.add_argument("--blind", help="the blind plan, as generated before any edit (remembered)")
    i.add_argument("--intake", help="decision IDs given at intake, e.g. D1-D6 (remembered)")
    i.add_argument("--owner", help="decision IDs the source owner settled, e.g. D7,D8 (remembered)")
    for k in KINDS:
        i.add_argument(f"--{k}s", help=f"text that marks the {k} section (default: '{DEFAULT_MARKERS[k]}')")
    i.add_argument("--rebuild", action="store_true", help="re-read every prediction from the plan")
    i.set_defaults(func=init)

    r = sub.add_parser("record", help="record a build outcome for one item")
    r.add_argument("id", help="item ID, or kind:ID when two kinds share an ID")
    r.add_argument("outcome", choices=OUTCOMES[1:])
    r.add_argument("evidence", help="org, record ids, values")
    r.add_argument("--path", help="what was built, when it differs from the prediction")
    r.add_argument("--skill", help="the skill file and claim a refutation traces to")
    r.add_argument("--blind-right", choices=("yes", "no"),
                   help="for an edited item: would the blind text have held?")
    r.set_defaults(func=record)

    sub.add_parser("report", help="write the scorecard").set_defaults(func=report)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
