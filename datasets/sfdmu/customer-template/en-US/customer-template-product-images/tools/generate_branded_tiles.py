#!/usr/bin/env python3
"""Generate brand-colored product tile Static Resources for a customer demo.

Reads `sku-contract.yaml` and, for every SKU with `image_required: true`, writes a
512x512 SVG Static Resource (payload + `-meta.xml`) into
`unpackaged/post_customer_demo/staticresources/`, then projects the matching
`DisplayUrl` values onto this plan's `Product2.csv`.

The tiles are self-contained SVG: solid brand-color background, the product name,
the SKU, and a logo band. No external references — Salesforce renders static
resource images in secure static mode, which blocks cross-resource fetches.

Two modes:

    # 1. Wordmark placeholder logo (only needed once, or when the brand color changes)
    .venv/bin/python <this script> --emit-logo-placeholder

    # 2. Tiles + Product2.csv (re-run after dropping in a real logo)
    .venv/bin/python <this script> --logo-path <tools/assets/sfdc-logo.png>

Swapping in the real customer logo is a one-file change: overwrite
`tools/assets/<prefix>-logo.png`, re-run mode 2, and re-run
`prepare_customer_branding.py` with the same path.

Requires: PyYAML (always), Pillow (only for --emit-logo-placeholder).
"""

from __future__ import annotations

import argparse
import base64
import csv
import re
import textwrap
import xml.sax.saxutils as xml_utils
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit(
        "PyYAML is required.\n"
        "Install it:  .venv/bin/python -m pip install pyyaml"
    )

PLAN_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[6]
DEFAULT_CONTRACT = PLAN_DIR.parent / "sku-contract.yaml"
DEFAULT_STATICRESOURCES = REPO_ROOT / "unpackaged" / "post_customer_demo" / "staticresources"
DEFAULT_CSV = PLAN_DIR / "Product2.csv"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

TILE_SIZE = 512
LOGO_BAND = (56, 48, 400, 108)  # x, y, w, h of the white logo band inside a tile


def _api_name(value: str) -> str:
    """Salesforce API name: alphanumeric + underscore, starting with a letter."""
    clean = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")
    if not re.match(r"^[A-Za-z]", clean):
        clean = f"r_{clean}"
    return clean[:240]


def _sku_slug(sku: str, prefix: str) -> str:
    body = re.sub(rf"^{re.escape(prefix)}[-_]?", "", sku, flags=re.IGNORECASE)
    return _api_name(body.lower())


def _rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if not re.match(r"^[0-9A-Fa-f]{6}$", h):
        raise ValueError(f"Invalid hex color '{hex_color}'. Expected #RRGGBB.")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _shade(hex_color: str, factor: float) -> str:
    r, g, b = (min(255, int(c * factor)) for c in _rgb(hex_color))
    return f"#{r:02X}{g:02X}{b:02X}"


def _logo_data_uri(logo_path: Path | None) -> str:
    if logo_path is None:
        return ""
    suffix = logo_path.suffix.lower()
    content_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }.get(suffix, "image/png")
    encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
    return xml_utils.escape(f"data:{content_type};base64,{encoded}", entities={'"': "&quot;"})


def _logo_band_markup(data_uri: str, customer_name: str, brand: str) -> str:
    """White band at the top of a tile: the real logo if present, else a wordmark."""
    x, y, w, h = LOGO_BAND
    band = (
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#FFFFFF"/>\n'
    )
    if data_uri:
        return band + (
            f'  <image x="{x + 20}" y="{y + 14}" width="{w - 40}" height="{h - 28}" '
            f'preserveAspectRatio="xMidYMid meet" href="{data_uri}"/>\n'
        )
    return band + (
        f'  <text x="{TILE_SIZE / 2}" y="{y + h / 2}" text-anchor="middle" '
        f'dominant-baseline="central" font-family="Helvetica, Arial, sans-serif" '
        f'font-size="46" font-weight="700" fill="{brand}">'
        f"{xml_utils.escape(customer_name)}</text>\n"
    )


def _tile_svg(product_name: str, sku: str, customer_name: str, brand: str,
              data_uri: str) -> str:
    lines = textwrap.wrap(product_name, width=17) or [product_name]
    lines = lines[:3]
    font_size = 46 if len(max(lines, key=len)) <= 15 else 40
    line_height = font_size + 12
    block_top = 300 - (len(lines) - 1) * line_height / 2

    tspans = "".join(
        f'<tspan x="{TILE_SIZE / 2}" y="{block_top + i * line_height}">'
        f"{xml_utils.escape(line)}</tspan>"
        for i, line in enumerate(lines)
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TILE_SIZE} {TILE_SIZE}" '
        f'width="{TILE_SIZE}" height="{TILE_SIZE}" role="img" '
        f'aria-label="{xml_utils.escape(product_name)}">\n'
        f'  <rect width="{TILE_SIZE}" height="{TILE_SIZE}" fill="{brand}"/>\n'
        f"{_logo_band_markup(data_uri, customer_name, brand)}"
        f'  <text text-anchor="middle" font-family="Helvetica, Arial, sans-serif" '
        f'font-size="{font_size}" font-weight="600" fill="#FFFFFF">{tspans}</text>\n'
        f'  <text x="{TILE_SIZE / 2}" y="432" text-anchor="middle" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="24" '
        f'fill="#FFFFFF" fill-opacity="0.85">{xml_utils.escape(sku)}</text>\n'
        f'  <rect y="{TILE_SIZE - 24}" width="{TILE_SIZE}" height="24" '
        f'fill="{_shade(brand, 0.72)}"/>\n'
        f"</svg>\n"
    )


def _logo_svg(customer_name: str, brand: str, bg: str, data_uri: str) -> str:
    """Square customer mark — generic fallback image and real-logo smoke test."""
    body = (
        f'  <image x="56" y="56" width="400" height="400" '
        f'preserveAspectRatio="xMidYMid meet" href="{data_uri}"/>\n'
        if data_uri
        else (
            f'  <text x="{TILE_SIZE / 2}" y="{TILE_SIZE / 2}" text-anchor="middle" '
            f'dominant-baseline="central" font-family="Helvetica, Arial, sans-serif" '
            f'font-size="56" font-weight="700" fill="{brand}">'
            f"{xml_utils.escape(customer_name)}</text>\n"
        )
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TILE_SIZE} {TILE_SIZE}" '
        f'width="{TILE_SIZE}" height="{TILE_SIZE}" role="img" '
        f'aria-label="{xml_utils.escape(customer_name)} logo">\n'
        f'  <rect width="{TILE_SIZE}" height="{TILE_SIZE}" fill="{bg}"/>\n'
        f"{body}"
        f'  <rect y="{TILE_SIZE - 24}" width="{TILE_SIZE}" height="24" fill="{brand}"/>\n'
        f"</svg>\n"
    )


def _resource_meta_xml(description: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<StaticResource xmlns="http://soap.sforce.com/2006/04/metadata">\n'
        "    <cacheControl>Public</cacheControl>\n"
        "    <contentType>image/svg+xml</contentType>\n"
        f"    <description>{xml_utils.escape(description)}</description>\n"
        "</StaticResource>\n"
    )


def _write_resource(out_dir: Path, name: str, svg: str, description: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{name}.resource").write_text(svg, encoding="utf-8")
    (out_dir / f"{name}.resource-meta.xml").write_text(
        _resource_meta_xml(description), encoding="utf-8"
    )


def emit_logo_placeholder(customer_name: str, brand: str, bg: str, dest: Path) -> None:
    """Write a 1200x240 wordmark PNG to stand in until a real logo arrives."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise SystemExit(
            "Pillow is required for --emit-logo-placeholder.\n"
            "Install it:  .venv/bin/python -m pip install Pillow"
        )

    width, height = 1200, 240
    canvas = Image.new("RGBA", (width, height), (*_rgb(bg), 255))
    draw = ImageDraw.Draw(canvas)

    font = None
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        if Path(candidate).is_file():
            font = ImageFont.truetype(candidate, 128)
            break
    if font is None:
        font = ImageFont.load_default(size=128)

    box = draw.textbbox((0, 0), customer_name, font=font)
    draw.text(
        ((width - (box[2] - box[0])) / 2 - box[0], (height - (box[3] - box[1])) / 2 - box[1] - 14),
        customer_name,
        font=font,
        fill=(*_rgb(brand), 255),
    )
    draw.rectangle([(width / 2 - 220, height - 46), (width / 2 + 220, height - 34)],
                   fill=(*_rgb(brand), 255))

    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, format="PNG", optimize=True)
    print(f"Wrote placeholder logo: {dest}  ({width}x{height} PNG)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate brand-colored product tile static resources from the SKU contract."
    )
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument(
        "--logo-path",
        default="",
        help="Local logo image embedded into every tile. Omit for a wordmark placeholder.",
    )
    parser.add_argument("--staticresources-dir", default=str(DEFAULT_STATICRESOURCES))
    parser.add_argument("--csv", default=str(DEFAULT_CSV))
    parser.add_argument(
        "--emit-logo-placeholder",
        action="store_true",
        help="Write assets/<prefix>-logo.png wordmark and exit (requires Pillow).",
    )
    args = parser.parse_args()

    contract = yaml.safe_load(Path(args.contract).read_text(encoding="utf-8"))
    customer = contract["customer"]["name"]
    experience = contract.get("experience", {})
    brand = experience.get("brand_color", "#0176D3").upper()
    bg = experience.get("bg_color", "#FFFFFF").upper()
    prefix = experience.get("static_resource_prefix") or contract["customer"]["prefix"].lower()
    sku_prefix = contract["customer"]["prefix"]

    if args.emit_logo_placeholder:
        emit_logo_placeholder(customer, brand, bg, ASSETS_DIR / f"{prefix}-logo.png")
        return

    logo_path = Path(args.logo_path) if args.logo_path else None
    if logo_path and not logo_path.is_absolute():
        logo_path = (REPO_ROOT / logo_path).resolve()
    if logo_path and not logo_path.is_file():
        raise SystemExit(f"Logo file not found: {logo_path}")
    data_uri = _logo_data_uri(logo_path)

    out_dir = Path(args.staticresources_dir)
    _write_resource(
        out_dir,
        _api_name(f"{prefix}_logo_sq"),
        _logo_svg(customer, brand, bg, data_uri),
        f"Customer demo square logo for {customer}",
    )

    rows = []
    for sku in contract["skus"]:
        if not sku.get("image_required"):
            continue
        resource_name = _api_name(f"{prefix}_tile_{_sku_slug(sku['sku'], sku_prefix)}")
        _write_resource(
            out_dir,
            resource_name,
            _tile_svg(sku["name"], sku["sku"], customer, brand, data_uri),
            f"{customer} demo product tile for {sku['sku']}",
        )
        rows.append(
            {
                "DisplayUrl": f"/resource/{resource_name}",
                "Name": sku["name"],
                "StockKeepingUnit": sku["sku"],
            }
        )

    rows.sort(key=lambda r: r["StockKeepingUnit"])
    with open(args.csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["DisplayUrl", "Name", "StockKeepingUnit"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Logo source:   {logo_path or 'none (wordmark placeholder rendered in SVG)'}")
    print(f"Tiles written: {len(rows)} -> {out_dir}")
    print(f"CSV written:   {args.csv}")
    for row in rows:
        print(f"  {row['StockKeepingUnit']:<20} {row['DisplayUrl']}")


if __name__ == "__main__":
    main()
