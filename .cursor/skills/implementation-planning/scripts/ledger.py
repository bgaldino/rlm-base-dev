#!/usr/bin/env python3
"""Verification ledger: how a build affirms or refutes its plan's predictions.

Part of the implementation-planning skill (SKILL.md step 9). Standard library only.
Run from the folder that holds the plan, by the script's full path in the Foundations clone
(.cursor/skills/implementation-planning/scripts/ledger.py). The ledger defaults to
verification/ledger.json under that folder; --ledger PATH (before the command) moves it:

    python3 ledger.py [--ledger PATH] init --plan plan-as-approved.md [--blind <blind plan>] [--intake D1-D6] [--owner D7,D8] [--rebuild]
    python3 ledger.py record <ID> <outcome> "<evidence>" [--path "<what was built>"] [--skill "<file: claim>"]
    python3 ledger.py report     # writes scorecard.md next to the ledger
    python3 ledger.py truth      # writes truth.json: measured items, predicted vs measured
    python3 ledger.py score <judgments.json> <label>   # tallies a judged regeneration

Items are table rows of the plan (plan-template.md), the first cell being the ID. Every table
line starts with "|". A table is recognised by its header, wherever it sits in the plan (fenced
code blocks are ignored):
  decision  first column "#" and second column "Decision"
  rule      first column starting "Rule", and a "Decided by" column
  spike     first column starting "Spike", and a "Must hit" column
init fails if it finds no rule or decision rows.

Origin: blind (unchanged from the blind plan), edited (its blind text kept), added,
intake or owner (given to the planner; not counted for accuracy). With no blind plan,
everything else is blind. --blind is remembered (by its path relative to the ledger's
folder). --intake and --owner set the origin of the rows they name; a row keeps that origin
until a later list names it again.

Outcome: affirmed, modified (held with different values or configuration), refuted
(failed), inconclusive (not tested). New items are pending.

Re-running init adds new rows and keeps outcomes and each row's recorded text, so the
blind measurement survives plan revisions; --rebuild re-reads the rows (and prints each
replaced prediction's previous text). A row no
longer in the plan is kept by init; --rebuild drops it if it is still pending with no evidence.

Scoring a later blind regeneration: its IDs won't match this plan's, so a fresh judge
reads the regenerated plan with truth.json and labels every item in it (the measured ones,
not intake or owner rows):
  hit     the plan predicts the measured result (route, value or behavior)
  hedged  the plan doesn't assert it, but routes it to a live measurement that would find it
  miss    the plan asserts what the build refuted or changed
  absent  the plan doesn't address it
judgments.json: {"<truth key>": {"label": "...", "where": "<plan section or ID>", "why": "<one line>"}}
score writes regen-scores.md next to the ledger, one section per label, with the
measured plan's own baseline (affirmed = hit, modified or refuted = miss,
inconclusive = hedged) beside the regeneration.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

OUTCOMES = ("pending", "affirmed", "modified", "refuted", "inconclusive")
KINDS = ("rule", "decision", "spike")
LABELS = ("Repo (inferred)", "Build (custom)", "Repo", "Snapshot", "Live")


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        sys.exit(f"{path}: cannot read ({e})")


def cells(line):
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    parts = s.replace("\\|", "\0").split("|")
    return [p.replace("\0", "|").strip() for p in parts]


def row_key(line):
    """A row's cells without trailing blanks, so a short row equals the same row padded."""
    row = cells(line)
    while row and not row[-1]:
        row.pop()
    return row


def is_separator(line):
    return bool(re.fullmatch(r"\|\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?", line.strip()))


def clean_id(cell):
    """The row's ID: the whole first cell, or its first word when that word holds a digit
    ("S-1 Amendment value" -> "S-1"). A cell listing several IDs ("A-01, A-02") is kept whole."""
    text = re.sub(r"[*`]", "", cell).strip()
    first = text.split(" ", 1)[0]
    if "," not in text and re.search(r"\d", first):
        return first
    return text


DECIDED_BY = re.compile(r"decided.by", re.I)
TABLE_TEST = {
    "decision": lambda h: h[0] == "#" and len(h) > 1 and h[1].lower() == "decision",
    "rule": lambda h: h[0].lower().startswith("rule") and any(DECIDED_BY.search(c) for c in h),
    "spike": lambda h: h[0].lower().startswith("spike") and any(re.search(r"must.hit", c, re.I) for c in h),
}


def table_rows(lines, kind, name=""):
    """{id: (header cells, row cells, raw line)} for the body rows of every table whose
    header (bold and code marks dropped) passes the kind's TABLE_TEST."""
    rows = {}
    header = None
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            header = None
            continue
        if is_separator(line):
            continue
        if i + 1 < len(lines) and is_separator(lines[i + 1]):
            header = [re.sub(r"[*`]", "", c).strip() for c in cells(line)]
            continue
        if not header or not TABLE_TEST[kind](header):
            continue
        row = cells(line)
        iid = clean_id(row[0]) if row else ""
        if not iid:
            continue
        if len(row) < len(header):  # GFM: a short row has blank trailing cells
            row = row + [""] * (len(header) - len(row))
        elif len(row) > len(header):
            print(f"warning: {name + ': ' if name else ''}{iid} has {len(row)} cells under "
                  f"{len(header)} columns (an unescaped '|' in a cell?); its cells are kept "
                  "without column names", file=sys.stderr)
        if iid in rows:
            print(f"warning: {name + ': ' if name else ''}{iid} appears twice; keeping the "
                  "first row", file=sys.stderr)
            continue
        rows[iid] = (header, row, line.strip())
    return rows


def unfenced(lines, name):
    """The lines with fenced code blocks (and their fences) blanked, so a fenced table is not
    read as plan rows. A fence closes on a line of the same character at least as long as the
    opening one, with nothing after it."""
    out, fence, opened = [], None, 0
    for n, line in enumerate(lines, 1):
        m = re.match(r"\s*(`{3,}|~{3,})", line)
        if fence is None and m and not (m.group(1)[0] == "`" and "`" in line[m.end():]):
            fence, opened = m.group(1), n
        elif fence is not None and re.fullmatch(rf"\s*{fence[0]}{{{len(fence)},}}\s*", line):
            fence = None
            out.append("")
            continue
        out.append("" if fence is not None else line)
    if fence is not None:
        print(f"warning: {name}: the code fence opened at line {opened} is never closed; "
              "the rest of the plan is ignored", file=sys.stderr)
    return out


NEEDS = {"decision": "a table whose first column is '#' and second column 'Decision'",
         "rule": "a table whose first column starts with 'Rule' and that has a 'Decided by' column",
         "spike": "a table whose first column starts with 'Spike' and that has a 'Must hit' column"}


def items(text, name):
    lines = unfenced(text.splitlines(), name)
    found = {}
    for kind in KINDS:
        found[kind] = table_rows(lines, kind, name=name)
        if not found[kind]:
            msg = f"{name}: no {kind} rows; the plan needs {NEEDS[kind]}"
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
            if lo > hi:
                sys.exit(f"reversed range {part!r}; write the lower id first")
            width = len(m.group(2)) if m.group(2).startswith("0") else 0
            out |= {f"{prefix}{n:0{width}d}" for n in range(lo, hi + 1)}
        else:
            out.add(part)
    return out


def prediction(header, row):
    if len(header) == len(row):
        return dict(zip(header[1:], row[1:]))
    return {"cells": row[1:]}


def read_json(path):
    try:
        return json.loads(read_text(path))
    except ValueError as e:
        sys.exit(f"{path}: not valid JSON ({e}); restore it from a backup or version control")


def write_text(path, text):
    """Write through a temporary file so an interrupted write leaves the old copy whole."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def load(path):
    if not path.exists():
        sys.exit(f"no ledger at {path}; run init first")
    return read_json(path)


def save(path, ledger):
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text(path, json.dumps(ledger, indent=1, ensure_ascii=False) + "\n")


def relative(path, folder):
    """The path relative to the ledger's folder, so the ledger survives a moved folder."""
    try:
        return os.path.relpath(Path(path).resolve(), folder)
    except ValueError:  # another drive on Windows
        return str(Path(path).resolve())


def droppable(item):
    """A row that has left the plan and that --rebuild may drop: nothing was recorded on it."""
    return item["outcome"] == "pending"


def init(args):
    ledger_path = Path(args.ledger)
    old = read_json(ledger_path) if ledger_path.exists() else {"meta": {}, "items": {}}
    meta = old.get("meta", {})
    intake, owner = id_set(args.intake), id_set(args.owner)
    ledger_dir = ledger_path.resolve().parent
    if args.blind:
        blind_file = Path(args.blind).resolve()
        blind_path = relative(blind_file, ledger_dir)
    else:
        blind_path = meta.get("blind")
        blind_file = ledger_dir / blind_path if blind_path else None
        if blind_file and not blind_file.exists():
            sys.exit(f"remembered blind plan {blind_file} not found; pass --blind")
    plan = items(read_text(args.plan), args.plan)
    blind = items(read_text(blind_file), str(blind_file)) if blind_file else None
    known = set(plan["decision"]) | {v["id"] for v in old["items"].values() if v["kind"] == "decision"
                                     and not (args.rebuild and droppable(v))}
    unknown = sorted((intake | owner) - known)
    if unknown:
        print(f"warning: not decision rows in the plan, so ignored: {', '.join(unknown)}", file=sys.stderr)

    ledger = {"meta": {"plan": relative(args.plan, ledger_dir), "blind": blind_path}, "items": {}}

    def origin_of(kind, iid, line, prev):
        if kind == "decision" and iid in intake:
            return "intake"
        if kind == "decision" and iid in owner:
            return "owner"
        if prev and prev["origin"] in ("intake", "owner"):
            return prev["origin"]
        if blind is None:
            return "blind"
        if iid not in blind[kind]:
            return "added"
        return "blind" if row_key(blind[kind][iid][2]) == row_key(line) else "edited"

    def entry(kind, iid, line, pred, prev):
        origin = origin_of(kind, iid, line, prev)
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
            if prev and row_key(prev["line"]) != row_key(raw):
                if args.rebuild:
                    print(f"warning: {key} prediction replaced; previous text was: {prev['line']}",
                          file=sys.stderr)
                else:
                    print(f"warning: {key} changed in the plan since it was recorded; kept as "
                          "recorded (--rebuild re-reads it)", file=sys.stderr)
            if prev and not args.rebuild:
                ledger["items"][key] = entry(kind, iid, prev["line"], prev["prediction"], prev)
            else:
                ledger["items"][key] = entry(kind, iid, raw, prediction(header, row), prev)
    for key, prev in old["items"].items():
        if key not in seen:
            if args.rebuild and droppable(prev):
                print(f"warning: {key} is no longer in the plan and has nothing recorded; dropped",
                      file=sys.stderr)
                continue
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
    item["outcome"] = args.outcome
    item["evidence"].append(entry)
    save(ledger_path, ledger)
    print(f"{key}: {args.outcome}")


def label(item):
    by = next((v for k, v in item["prediction"].items() if DECIDED_BY.search(k)), "")
    by = re.sub(r"[*`]", "", by)  # **Repo** (inferred) is one label
    found = []
    for m in re.finditer(r"(?<!\w)(?:" + "|".join(re.escape(x) for x in LABELS) + r")(?!\w)", by):
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
    refuted = []
    for key, v in ledger["items"].items():
        if v["outcome"] in ("refuted", "modified") and v["evidence"]:
            last = v["evidence"][-1]
            refuted.append(f"- **{key}** ({v['origin']}): {v['outcome']}. {last.get('evidence', '')}"
                           + (f" Path: {last['path_taken']}." if "path_taken" in last else ""))
    lines += refuted or ["None."]

    claims = [(key, e) for key, v in ledger["items"].items() for e in v["evidence"] if "skill_claim" in e]
    lines += ["", "## Skill claims to settle", ""]
    lines += [f"- **{key}** ({e['outcome']}): {e['skill_claim']}" for key, e in claims] or ["None recorded."]
    write_text(out_path, "\n".join(lines) + "\n")
    print(f"wrote {out_path}")


JUDGE_LABELS = ("hit", "hedged", "miss", "absent")
BASELINE = {"affirmed": "hit", "modified": "miss", "refuted": "miss", "inconclusive": "hedged"}


def truth(args):
    ledger_path = Path(args.ledger)
    ledger = load(ledger_path)
    out = {}
    for key, v in ledger["items"].items():
        if v["origin"] in ("intake", "owner") or v["outcome"] == "pending":
            continue
        ev = v["evidence"]
        out[key] = {"kind": v["kind"], "origin": v["origin"], "outcome": v["outcome"],
                    "predicted": v["prediction"],
                    "measured": [e.get("evidence", "") for e in ev],
                    "path_taken": [e["path_taken"] for e in ev if "path_taken" in e],
                    "skill_claim": [e["skill_claim"] for e in ev if "skill_claim" in e]}
    out_path = ledger_path.with_name("truth.json")
    write_text(out_path, json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(out)} measured items written to {out_path}")


def score(args):
    ledger_path = Path(args.ledger)
    truth_path = ledger_path.with_name("truth.json")
    if not truth_path.exists():
        sys.exit(f"no truth file at {truth_path}; run truth first")
    tr = read_json(truth_path)
    judged = read_json(args.judgments)
    if not isinstance(judged, dict):
        sys.exit(f"{args.judgments}: expected a JSON object of {{truth key: {{label, where, why}}}}")
    missing, extra = sorted(set(tr) - set(judged)), sorted(set(judged) - set(tr))
    if missing or extra:
        sys.exit(f"judgments must cover exactly the measured items; missing {missing}, extra {extra}")
    bad = sorted(k for k, j in judged.items() if not isinstance(j, dict) or j.get("label") not in JUDGE_LABELS)
    if bad:
        sys.exit(f"bad labels for {bad}; use one of {JUDGE_LABELS}")

    def tally(label_of):
        return {lab: sum(1 for k in tr if label_of(k) == lab) for lab in JUDGE_LABELS}
    new = tally(lambda k: judged[k]["label"])
    base = tally(lambda k: BASELINE[tr[k]["outcome"]])
    n = len(tr)

    def row(name, t):
        return (f"| {name} | {t['hit']} | {t['hedged']} | {t['miss']} | {t['absent']} | "
                f"{t['hit'] + t['hedged']}/{n} |")
    block = [f"## {args.label}", "",
             f"Judged from `{Path(args.judgments).name}` against `{truth_path.name}` ({n} measured items).", "",
             "| | Hit | Hedged | Miss | Absent | First-time accurate (hit + hedged) |",
             "|---|---|---|---|---|---|",
             row("measured plan (baseline)", base), row(args.label, new), "",
             "Still missed or absent:", ""]
    still = [k for k in tr if judged[k]["label"] in ("miss", "absent")]
    block += [f"- **{k}** ({tr[k]['kind']}, was {tr[k]['outcome']}): {judged[k]['label']} at "
              f"{judged[k].get('where') or '—'}. {judged[k].get('why', '')}".rstrip() for k in still] or ["None."]
    out_path = ledger_path.with_name("regen-scores.md")
    old = (out_path.read_text(encoding="utf-8") if out_path.exists() else
           "# Regeneration scores\n\nGenerated by `ledger.py score`. Do not edit by hand. Each "
           "regeneration is judged against the build's measured outcomes.\n\n")
    old = re.sub(rf"## {re.escape(args.label)}\n.*?(?=\n## |\Z)", "", old, flags=re.S).rstrip() + "\n\n"
    write_text(out_path, old + "\n".join(block) + "\n")
    print(f"{args.label}: hit {new['hit']}, hedged {new['hedged']}, miss {new['miss']}, "
          f"absent {new['absent']} of {n} (baseline hit + hedged {base['hit'] + base['hedged']})")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ledger", default="verification/ledger.json",
                   help="ledger file (default: verification/ledger.json); the scorecard is written beside it")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="build or update the ledger from the plan")
    i.add_argument("--plan", required=True, help="the plan as approved: a frozen copy (SKILL.md step 9)")
    i.add_argument("--blind", help="the blind plan, as generated before any edit (remembered)")
    i.add_argument("--intake", help="decision IDs given at intake, e.g. D1-D6 (sticks to those rows)")
    i.add_argument("--owner", help="decision IDs a person settled after the blind plan, e.g. D7,D8 "
                   "(sticks to those rows)")
    i.add_argument("--rebuild", action="store_true", help="re-read every prediction from the plan")
    i.set_defaults(func=init)

    r = sub.add_parser("record", help="record a build outcome for one item")
    r.add_argument("id", help="item ID, or kind:ID when two kinds share an ID")
    r.add_argument("outcome", choices=OUTCOMES[1:])
    r.add_argument("evidence", help="org, record ids, values")
    r.add_argument("--path", help="what was built, when it differs from the prediction")
    r.add_argument("--skill", help="the skill file and claim a refutation traces to")
    r.set_defaults(func=record)

    sub.add_parser("report", help="write the scorecard").set_defaults(func=report)
    sub.add_parser("truth", help="write truth.json: measured items (not intake or owner), predicted vs measured"
                   ).set_defaults(func=truth)
    sc = sub.add_parser("score", help="tally a judged regeneration into regen-scores.md")
    sc.add_argument("judgments", help="JSON of {truth key: {label, where, why}}")
    sc.add_argument("label", help="the regeneration's name, e.g. r2; a rerun replaces its section")
    sc.set_defaults(func=score)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
