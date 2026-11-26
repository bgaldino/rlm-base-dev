#!/usr/bin/env python3
"""erd_shards.py - per-domain shards of docs/erds/erd-data.json.

`docs/erds/data/` is the reviewable source: one shard per domain (objects only, each with a
provenance stamp), `relationships.json`, and `_meta.json` (release metadata plus the object
order). `docs/erds/erd-data.json` is the composed output that `query_erd.py`, `build_erds.py`
and the tests read; it is committed so those consumers do not change. Writers call `save()`,
which rewrites the composed file and the shards together. `check()` fails when they disagree.

    python scripts/erd/erd_shards.py split    # (re)write shards from erd-data.json
    python scripts/erd/erd_shards.py compose  # (re)write erd-data.json from the shards
    python scripts/erd/erd_shards.py check    # schema + composition + equality, exit 1 on any failure

Composition invariant: an internal overlay shard (any extra `*.json` in the data directory
other than the ones above, named `overlay-*.json`) may add objects, fields and relationships but
may never redefine a public key; `compose` raises on a contradiction.
"""

import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
ERD_DIR = REPO / "docs" / "erds"
ERD_PATH = ERD_DIR / "erd-data.json"
DATA_DIR = ERD_DIR / "data"
SCHEMA_PATH = DATA_DIR / "erd-shard.schema.json"
META, RELS = "_meta.json", "relationships.json"
RESERVED = {META, RELS, SCHEMA_PATH.name}


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
            for p in sorted(data_dir.glob("*.json")) if p.name != SCHEMA_PATH.name}


def compose(shards: dict) -> dict:
    meta = shards[META]
    objects, rels = {}, list(shards[RELS]["relationships"])
    parts = {n: s for n, s in shards.items() if n not in RESERVED}
    public = {n: s for n, s in parts.items() if not n.startswith("overlay-")}
    overlays = {n: s for n, s in parts.items() if n.startswith("overlay-")}
    for s in public.values():
        for name, obj in s["objects"].items():
            if name in objects:
                raise ValueError(f"object {name} appears in more than one shard")
            objects[name] = obj
    for fname, s in overlays.items():
        for name, obj in s["objects"].items():
            base = objects.setdefault(name, {k: v for k, v in obj.items() if k != "fields"} | {"fields": {}})
            for k, v in obj.items():
                if k == "fields":
                    for f, fv in v.items():
                        if f in base["fields"] and base["fields"][f] != fv:
                            raise ValueError(f"{fname} redefines public field {name}.{f}")
                        base["fields"][f] = fv
                elif k in base and base[k] != v:
                    raise ValueError(f"{fname} redefines public key {name}.{k}")
                else:
                    base[k] = v
        rels.extend(r for r in s.get("relationships", []) if r not in rels)
    ordered = {n: objects[n] for n in meta["objectOrder"] if n in objects}
    ordered.update({n: o for n, o in objects.items() if n not in ordered})
    erd = {"metadata": meta["metadata"], "objects": ordered, "relationships": rels}
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
        for stale in set(old) - set(new) - {n for n in old if n.startswith("overlay-")}:
            (DATA_DIR / stale).unlink()
        for fname, content in new.items():
            (DATA_DIR / fname).write_text(dumps(content), encoding="utf-8")
    path.write_text(dumps(erd), encoding="utf-8")


def validate(instance, schema, where="$") -> list:
    """Minimal JSON Schema subset (type, required, properties, additionalProperties, items,
    enum, minItems, pattern) - enough for erd-shard.schema.json without a dependency."""
    import re
    types = {"object": dict, "array": list, "string": str, "boolean": bool, "integer": int}
    errs = []
    t = schema.get("type")
    if t and not isinstance(instance, types[t]):
        return [f"{where}: expected {t}"]
    if "enum" in schema and instance not in schema["enum"]:
        errs.append(f"{where}: {instance!r} not in {schema['enum']}")
    if "pattern" in schema and isinstance(instance, str) and not re.search(schema["pattern"], instance):
        errs.append(f"{where}: {instance!r} does not match {schema['pattern']}")
    if isinstance(instance, dict):
        for r in schema.get("required", []):
            if r not in instance:
                errs.append(f"{where}: missing {r}")
        props = schema.get("properties", {})
        for k, v in instance.items():
            if k in props:
                errs += validate(v, props[k], f"{where}.{k}")
            elif isinstance(schema.get("additionalProperties"), dict):
                errs += validate(v, schema["additionalProperties"], f"{where}.{k}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{where}: unexpected key {k}")
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errs.append(f"{where}: fewer than {schema['minItems']} items")
        if "items" in schema:
            for i, v in enumerate(instance):
                errs += validate(v, schema["items"], f"{where}[{i}]")
    return errs


def check() -> list:
    """Return a list of problems; empty means shards validate, compose and equal erd-data.json."""
    problems = []
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    shards = read_shards()
    for fname, s in shards.items():
        kind = "meta" if fname == META else "relationships" if fname == RELS else "domain"
        problems += [f"{fname} {e}" for e in validate(s, schema["definitions"][kind], "$")]
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
