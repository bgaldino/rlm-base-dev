#!/usr/bin/env python3
"""
Retrieve the running user's App Launcher order and write it to the repo for new builds.

The default org's running user must have set their app order (Setup > App Menu, or
personalized in the App Launcher). This script:
  1. Queries UserAppMenuCustomization (SortOrder, ApplicationId) for the running user
  2. Maps each ApplicationId to (name, type) via AppMenuItem
  3. Writes unpackaged/post_tso_appmenu/appMenus/AppSwitcher.appMenu-meta.xml

No deploy is performed. Use the output in builds (e.g. deploy_post_tso_app_menu when tso=true).
Target orgs must have the same apps or the file may need trimming for that org.

Run with default org set:
  python scripts/sync_appmenu_from_user.py
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


def _run_sf_query(query: str) -> str:
    result = subprocess.run(
        ["sf", "data", "query", "--query", query, "--result-format", "csv"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"sf data query failed: {result.stderr or result.stdout}")
    return result.stdout


def _parse_csv(csv_text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(csv_text.strip().splitlines())
    return list(reader)


def _app_menu_name_and_type(row: dict[str, str]) -> tuple[str, str]:
    """Map AppMenuItem row to (menu name, menu type) for AppMenu metadata."""
    name = (row.get("NAME") or row.get("Name") or "").strip()
    type_ = (row.get("TYPE") or row.get("Type") or "").strip()
    ns = (row.get("NAMESPACEPREFIX") or row.get("NamespacePrefix") or "").strip()

    if type_ == "TabSet":
        if ns == "standard":
            return ("standard__" + name, "CustomApplication")
        if ns:
            return (ns + "__" + name, "CustomApplication")
        return (name, "CustomApplication")
    if type_ == "ConnectedApplication":
        return (name, "ConnectedApp")
    if type_ == "Network":
        return (name, "Network")
    return (name, "CustomApplication")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    out_path = repo_root / "unpackaged" / "post_tso_appmenu" / "appMenus" / "AppSwitcher.appMenu-meta.xml"

    print("Querying running user's App Launcher order (UserAppMenuCustomization)...")
    custom_csv = _run_sf_query(
        "SELECT ApplicationId, SortOrder FROM UserAppMenuCustomization ORDER BY SortOrder"
    )
    custom_rows = _parse_csv(custom_csv)
    if not custom_rows:
        print("No UserAppMenuCustomization records found. Has this user set their App Launcher order?", file=sys.stderr)
        return 1

    print("Querying AppMenuItem for ApplicationId -> Name, Type...")
    items_csv = _run_sf_query(
        "SELECT ApplicationId, Name, Type, NamespacePrefix FROM AppMenuItem WHERE Type IN ('TabSet','ConnectedApplication','Network')"
    )
    items_rows = _parse_csv(items_csv)
    app_id_to_name_type = {}
    for r in items_rows:
        aid = (r.get("APPLICATIONID") or r.get("ApplicationId") or "").strip()
        if aid:
            app_id_to_name_type[aid] = _app_menu_name_and_type(r)

    ordered_entries = []
    for r in custom_rows:
        aid = (r.get("APPLICATIONID") or r.get("ApplicationId") or "").strip()
        name_type = app_id_to_name_type.get(aid)
        if name_type:
            ordered_entries.append(name_type)
        else:
            print(f"Warning: ApplicationId {aid} not found in AppMenuItem, skipping.", file=sys.stderr)

    if not ordered_entries:
        print("No app menu entries could be resolved.", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<AppMenu xmlns="http://soap.sforce.com/2006/04/metadata">',
    ]
    for name, type_ in ordered_entries:
        name_escaped = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines.append("    <appMenuItems>")
        lines.append(f"        <name>{name_escaped}</name>")
        lines.append(f"        <type>{type_}</type>")
        lines.append("    </appMenuItems>")
    lines.append("</AppMenu>")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {len(ordered_entries)} app menu items to {out_path} (your manual order; no deploy).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
