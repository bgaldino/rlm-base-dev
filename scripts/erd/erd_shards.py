#!/usr/bin/env python3
"""erd_shards.py - per-domain shards of docs/erds/erd-data.json.

`docs/erds/data/` is the reviewable source: one shard per domain (objects only, each with a
provenance stamp), `relationships.json`, and `_meta.json` (release metadata plus the object
order). `docs/erds/erd-data.json` is the composed output that `query_erd.py`, `build_erds.py`
and the tests read; it is committed so those consumers do not change. Writers call `save()`,
which rewrites the composed file and the shards together. `check()` fails when they disagree.

    python scripts/erd/erd_shards.py split    # (re)write shards from erd-data.json
    python scripts/erd/erd_shards.py compose  # (re)write erd-data.json from the shards
    python scripts/erd/erd_shards.py check    # shape + composition + equality, exit 1 on any failure

Every other `*.json` in the data directory is a domain shard: `{provenance, objects}`.
"""

import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
ERD_DIR = REPO / "docs" / "erds"
ERD_PATH = ERD_DIR / "erd-data.json"
DATA_DIR = ERD_DIR / "data"
META, RELS = "_meta.json", "relationships.json"
RESERVED = {META, RELS}
STAMP_KEYS = ("release", "apiVersion", "verifiedOn", "method", "coreSourceValidated")


def dumps(data) -> str:
    """The one serialization used for every ERD JSON file."""
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def shard_name(domain_short: str) -> str:
    return domain_short.lower().replace(" ", "-") + ".json"


def stats_for(erd: dict) -> dict:
    objs = erd["objects"]
    return {
        "totalObjects": len(objs),
        "totalRelationships": len(erd["relationships"]),
        "totalFields": sum(len(o.get("fields", {})) for o in objs.values()),
        "domains": sorted({o.get("domain", "Unknown") for o in objs.values()}),
    }


def default_stamp(meta: dict) -> dict:
    return {
        "release": meta.get("release", ""),
        "apiVersion": meta.get("apiVersion", ""),
        "verifiedOn": meta.get("lastRefreshedOn", ""),
        "method": "describe extraction from fresh ent-shape orgs; custom fields excluded",
        "coreSourceValidated": False,
    }


def split(erd: dict, old_shards: dict = None, verified: dict = None) -> dict:
    """Return {filename: content}. A shard whose objects changed since `old_shards` gets
    `verified` (e.g. {"release": "264", "apiVersion": "68.0"}) and today's date in its stamp."""
    old_shards = old_shards or {}
    meta = erd["metadata"]
    out = {META: {"metadata": meta, "objectOrder": list(erd["objects"])},
           RELS: {"relationships": erd["relationships"]}}
    groups = {}
    for name, obj in erd["objects"].items():
        groups.setdefault(shard_name(obj.get("domainShort") or obj.get("domain", "unknown")), {})[name] = obj
    for fname, objs in sorted(groups.items()):
        old = old_shards.get(fname)
        stamp = dict(old["provenance"]) if old else default_stamp(meta)
        if verified and (old is None or old["objects"] != objs):
            stamp.update(verified)
            stamp["verifiedOn"] = date.today().isoformat()
        out[fname] = {"provenance": stamp, "objects": objs}
    return out


def read_shards(data_dir: Path = DATA_DIR) -> dict:
    return {p.name: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(data_dir.glob("*.json"))}


def compose(shards: dict) -> dict:
    meta = shards[META]
    objects = {}
    for fname, s in shards.items():
        if fname in RESERVED:
            continue
        for name, obj in s["objects"].items():
            if name in objects:
                raise ValueError(f"object {name} appears in more than one shard")
            objects[name] = obj
    ordered = {n: objects[n] for n in meta["objectOrder"] if n in objects}
    ordered.update({n: o for n, o in objects.items() if n not in ordered})
    erd = {"metadata": meta["metadata"], "objects": ordered,
           "relationships": list(shards[RELS]["relationships"])}
    erd["stats"] = stats_for(erd)
    return {k: erd[k] for k in ("metadata", "stats", "objects", "relationships")}


def save(erd: dict, path: Path = ERD_PATH, verified: dict = None) -> None:
    """Write erd-data.json and, for the canonical path, the shards it composes from."""
    erd["stats"] = stats_for(erd)
    path = Path(path)
    if path.resolve() == ERD_PATH.resolve():
        DATA_DIR.mkdir(exist_ok=True)
        old = read_shards() if (DATA_DIR / META).exists() else {}
        new = split(erd, {n: s for n, s in old.items() if n not in RESERVED}, verified)
        for stale in set(old) - set(new):
            (DATA_DIR / stale).unlink()
        for fname, content in new.items():
            (DATA_DIR / fname).write_text(dumps(content), encoding="utf-8")
    path.write_text(dumps(erd), encoding="utf-8")


def shape_problems(shards: dict) -> list:
    """Explicit key checks: _meta has metadata + objectOrder, relationships has a list, and
    every domain shard has a full provenance stamp and an objects map."""
    out = []
    if "metadata" not in shards.get(META, {}) or not shards[META].get("objectOrder"):
        out.append(f"{META}: needs metadata and a non-empty objectOrder")
    if not isinstance(shards.get(RELS, {}).get("relationships"), list):
        out.append(f"{RELS}: needs a relationships list")
    for fname, s in shards.items():
        if fname in RESERVED:
            continue
        missing = [k for k in STAMP_KEYS if k not in s.get("provenance", {})]
        if missing:
            out.append(f"{fname}: provenance missing {', '.join(missing)}")
        if not isinstance(s.get("objects"), dict):
            out.append(f"{fname}: needs an objects map")
    return out


def check() -> list:
    """Return a list of problems; empty means shards are well formed, compose and equal erd-data.json."""
    shards = read_shards()
    problems = shape_problems(shards)
    if problems:
        return problems
    try:
        composed = compose(shards)
    except ValueError as e:
        return problems + [str(e)]
    if composed != json.loads(ERD_PATH.read_text(encoding="utf-8")):
        problems.append("compose(shards) != erd-data.json; run `erd_shards.py compose` or `split`")
    elif dumps(composed) != ERD_PATH.read_text(encoding="utf-8"):
        problems.append("erd-data.json is not byte-identical to the composed output")
    return problems


def main(argv=None) -> int:
    cmd = (argv or sys.argv[1:] or ["check"])[0]
    if cmd == "split":
        save(json.loads(ERD_PATH.read_text(encoding="utf-8")))
    elif cmd == "compose":
        ERD_PATH.write_text(dumps(compose(read_shards())), encoding="utf-8")
    elif cmd == "check":
        problems = check()
        for p in problems:
            print("FAIL:", p)
        print("ERD shards OK" if not problems else f"{len(problems)} problem(s)")
        return 1 if problems else 0
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
