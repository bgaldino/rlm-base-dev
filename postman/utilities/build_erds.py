#!/usr/bin/env python3
"""
build_erds.py — Patch the interactive ERD HTML with updated entity data.

Reads docs/erds/erd-data.json and patches the embedded D= data block in
docs/erds/revenue-cloud-erd.html with the current entity inventory and
relationships. Preserves the existing HTML/CSS/JS template.

Can also add new entities and relationships to erd-data.json.

Usage:
    # Regenerate HTML from erd-data.json
    python3 postman/utilities/build_erds.py

    # Verify current state without modifying
    python3 postman/utilities/build_erds.py --verify

Output: docs/erds/revenue-cloud-erd.html (patched in place)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Domain → sidebar short names and colors matching the HTML template
# Colors chosen for WCAG AA contrast on both dark (#0f172a) and light (#f8fafc)
# backgrounds, and pairwise distinguishability (min 1.5:1 between any two domains).
DOMAIN_MAP = {
    "Product Catalog Management": {"short": "PCM", "color": "#42a5f5"},
    "Product Catalog Management (Core Object)": {"short": "PCM", "color": "#42a5f5"},
    "Salesforce Pricing": {"short": "Pricing", "color": "#ab47bc"},
    "Rate Management": {"short": "Rates", "color": "#ec407a"},
    "Product Configurator": {"short": "Configurator", "color": "#26c6da"},
    "Transaction Management": {"short": "Transactions", "color": "#ffa726"},
    "Transaction Management (Core Object)": {"short": "Transactions", "color": "#ffa726"},
    "Advanced Approvals": {"short": "Approvals", "color": "#8d6e63"},
    "Dynamic Revenue Orchestrator": {"short": "DRO", "color": "#66bb6a"},
    "Usage Management": {"short": "Usage", "color": "#5c6bc0"},
    "Usage Management (Core Object)": {"short": "Usage", "color": "#5c6bc0"},
    "Billing": {"short": "Billing", "color": "#ef5350"},
    "Billing (Core Object)": {"short": "Billing", "color": "#ef5350"},
}


def get_short_domain(raw_domain: str) -> str:
    """Map raw domain name to sidebar-friendly short name."""
    info = DOMAIN_MAP.get(raw_domain)
    if info:
        return info["short"]
    # Fallback: strip (Core Object) and use as-is
    return raw_domain.replace(" (Core Object)", "").strip()


def get_color(raw_domain: str) -> str:
    """Map raw domain name to hex color."""
    info = DOMAIN_MAP.get(raw_domain)
    return info["color"] if info else "#999999"


def erd_data_to_html_nodes(erd_data: dict) -> list:
    """Convert erd-data.json objects into HTML-compatible node format.

    HTML node format:
        {id, dom, std, fc, rf: [{n, t, d, r?}], df: [{n, t, d}], c}
    """
    nodes = []
    objects = erd_data.get("objects", {})

    for name, obj in objects.items():
        raw_domain = obj.get("domain", "Unknown")
        short_dom = get_short_domain(raw_domain)
        color = get_color(raw_domain)
        fields = obj.get("fields", {})
        is_standard = "(Core Object)" in raw_domain or name in (
            "Account", "Contact", "Contract", "Quote", "QuoteLineItem",
            "Order", "OrderItem", "Asset", "Product2", "PriceBook2",
            "PriceBookEntry", "FulfillmentOrder", "FulfillmentOrderLineItem",
        )

        # Separate relationship fields from data fields
        rf = []  # relationship fields
        df = []  # data fields
        if isinstance(fields, dict):
            for fname, fdata in fields.items():
                if isinstance(fdata, dict) and fdata.get("refersTo"):
                    rf.append({
                        "n": fname,
                        "t": fdata.get("relationshipType", "reference"),
                        "d": (fdata.get("description", "") or "")[:200],
                        "r": fdata["refersTo"],
                    })
                elif isinstance(fdata, dict):
                    entry = {
                        "n": fname,
                        "t": fdata.get("type", ""),
                        "d": (fdata.get("description", "") or "")[:200],
                    }
                    df.append(entry)
                else:
                    # Simple field with no metadata
                    df.append({"n": fname, "t": "", "d": ""})
        elif isinstance(fields, int):
            # Just a count, no detail
            pass

        fc = (len(rf) + len(df)) if (rf or df) else (fields if isinstance(fields, int) else 0)

        nodes.append({
            "id": name,
            "dom": short_dom,
            "std": is_standard,
            "fc": fc,
            "rf": rf,
            "df": df,
            "c": color,
        })

    return nodes


def erd_data_to_html_links(erd_data: dict, node_ids: set) -> list:
    """Convert erd-data.json relationships into HTML-compatible link format."""
    links = []
    seen = set()
    for rel in erd_data.get("relationships", []):
        src, tgt, field = rel["source"], rel["target"], rel["field"]
        if src in node_ids and tgt in node_ids:
            key = (src, tgt, field)
            if key not in seen:
                links.append({"source": src, "target": tgt, "field": field})
                seen.add(key)
    return links


def patch_html(html_path: str, nodes: list, links: list) -> bool:
    """Replace the D= data block in the HTML file."""
    with open(html_path, "r") as f:
        html = f.read()

    # Find D= block boundaries
    marker = "const D="
    start = html.find(marker)
    if start == -1:
        print("Error: could not find 'const D=' in HTML", file=sys.stderr)
        return False
    start += len(marker)

    # Use json.JSONDecoder to consume ALL JSON blocks between "const D="
    # and the next JS statement.  Previous buggy patches may have left
    # multiple concatenated JSON objects (e.g. {…}{…}{…}).  We need to
    # skip past every one of them so the replacement is clean.
    try:
        decoder = json.JSONDecoder()
        remaining = html[start:]
        pos = 0
        while pos < len(remaining):
            # Skip whitespace
            while pos < len(remaining) and remaining[pos] in ' \t\r\n':
                pos += 1
            if pos >= len(remaining) or remaining[pos] != '{':
                break
            _, offset = decoder.raw_decode(remaining[pos:])
            pos += offset
        if pos == 0:
            raise json.JSONDecodeError("No JSON found", html, start)
        end = start + pos
    except json.JSONDecodeError as e:
        print(f"Error: could not parse existing JSON block: {e}", file=sys.stderr)
        return False

    D = {"nodes": nodes, "links": links}
    new_json = json.dumps(D, separators=(",", ":"))

    new_html = html[:start] + new_json + html[end:]

    with open(html_path, "w") as f:
        f.write(new_html)

    return True


def verify(html_path: str):
    """Parse and verify the current HTML data."""
    with open(html_path, "r") as f:
        html = f.read()

    marker = "const D="
    start = html.find(marker) + len(marker)
    decoder = json.JSONDecoder()
    D, _ = decoder.raw_decode(html[start:])
    ids = {n["id"] for n in D["nodes"]}

    print(f"Nodes: {len(D['nodes'])}")
    print(f"Links: {len(D['links'])}")
    print(f"Domains: {sorted(set(n['dom'] for n in D['nodes']))}")

    critical = [
        "QuoteLineItem", "OrderItem", "Account", "Quote", "Order",
        "Asset", "Product2", "PriceBookEntry", "Invoice", "BillingSchedule",
    ]
    print("\nCritical objects:")
    for name in critical:
        lc = sum(1 for l in D["links"] if l["source"] == name or l["target"] == name)
        print(f"  {'✓' if name in ids else '✗'} {name} ({lc} links)")


def main():
    base = Path(__file__).parent.parent.parent  # repo root
    data_file = base / "docs" / "erds" / "erd-data.json"
    html_file = base / "docs" / "erds" / "revenue-cloud-erd.html"

    if not data_file.exists():
        data_file = Path("docs/erds/erd-data.json")
        html_file = Path("docs/erds/revenue-cloud-erd.html")

    if "--verify" in sys.argv:
        if not html_file.exists():
            print(f"Error: {html_file} not found", file=sys.stderr)
            return 1
        verify(str(html_file))
        return 0

    if not data_file.exists():
        print(f"Error: {data_file} not found", file=sys.stderr)
        return 1
    if not html_file.exists():
        print(f"Error: {html_file} not found (the HTML template must exist)", file=sys.stderr)
        return 1

    print(f"Loading {data_file}...")
    with open(data_file) as f:
        erd_data = json.load(f)

    print("Converting to HTML format...")
    nodes = erd_data_to_html_nodes(erd_data)
    node_ids = {n["id"] for n in nodes}
    links = erd_data_to_html_links(erd_data, node_ids)

    print(f"  {len(nodes)} nodes, {len(links)} links")

    print(f"Patching {html_file}...")
    if patch_html(str(html_file), nodes, links):
        print(f"✓ Patched successfully")
        verify(str(html_file))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
