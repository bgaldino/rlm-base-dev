#!/usr/bin/env python3
"""Generate customer-branded Lightning Experience Theme metadata.

Creates three deployable metadata artifacts from a customer logo (**URL** or **local file**),
brand color, and company name:

  1. ContentAsset   — the logo image resized/letterboxed to 600×120 PNG
  2. BrandingSet    — brand color + BRAND_IMAGE pointing at the ContentAsset
  3. LightningExperienceTheme — SLDS v2 theme referencing the BrandingSet

Output lands in unpackaged/post_customer_demo/branding/ and can be deployed
with ``sf project deploy start``.

NOTE: Salesforce has **no API for activating** a LightningExperienceTheme.
After deploy, the user must manually activate the theme at
<org-url>/lightning/setup/ThemingAndBranding/home.

Requires: ``pip install Pillow requests``
"""

from __future__ import annotations

import argparse
import io
import re
import textwrap
from pathlib import Path
from urllib.parse import urlparse

try:
    from PIL import Image
except ImportError:
    raise SystemExit(
        "Pillow is required for image processing.\n"
        "Install it:  pip install Pillow   (or:  pip install -r requirements-branding.txt)"
    )

try:
    import requests
except ImportError:
    requests = None  # optional when using --logo-path only

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "unpackaged" / "post_customer_demo" / "branding"

BRAND_IMAGE_WIDTH = 600
BRAND_IMAGE_HEIGHT = 120
BRAND_IMAGE_SIZE = (BRAND_IMAGE_WIDTH, BRAND_IMAGE_HEIGHT)

MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024  # 10 MB download cap (before processing)


def _slugify(value: str) -> str:
    """Lower-case alphanumeric slug for directory/file naming."""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return slug or "customer"


def _api_name(value: str) -> str:
    """Produce a valid Salesforce API name (alphanumeric + underscore, starts with letter)."""
    clean = re.sub(r"[^A-Za-z0-9_]", "_", value).strip("_")
    if not clean:
        raise ValueError("API name cannot be empty after sanitization.")
    if not re.match(r"^[A-Za-z]", clean):
        clean = f"RLM_{clean}"
    return clean[:240]


def _validate_hex_color(color: str) -> str:
    """Normalize and validate a hex color string."""
    color = color.strip()
    if not color.startswith("#"):
        color = f"#{color}"
    if not re.match(r"^#[0-9A-Fa-f]{6}$", color):
        raise ValueError(
            f"Invalid hex color '{color}'. Expected format: #RRGGBB (e.g. #0176D3)"
        )
    return color.upper()


def _download_logo(url: str) -> bytes:
    """Download logo image bytes from a public URL."""
    if requests is None:
        raise SystemExit(
            "The 'requests' package is required for --logo-url.\n"
            "Install it:  pip install requests\n"
            "Or use --logo-path with a local image file instead."
        )
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    payload = response.content
    if not payload:
        raise ValueError(f"Downloaded logo from {url} is empty.")
    if len(payload) > MAX_DOWNLOAD_BYTES:
        raise ValueError(
            f"Downloaded logo is {len(payload):,} bytes, exceeds {MAX_DOWNLOAD_BYTES:,} byte limit."
        )
    return payload


def _load_logo_from_path(path: Path) -> bytes:
    """Read logo image bytes from a local file (PNG, JPEG, etc.)."""
    if not path.is_file():
        raise FileNotFoundError(f"Logo file not found: {path}")
    payload = path.read_bytes()
    if not payload:
        raise ValueError(f"Logo file is empty: {path}")
    if len(payload) > MAX_DOWNLOAD_BYTES:
        raise ValueError(
            f"Logo file is {len(payload):,} bytes, exceeds {MAX_DOWNLOAD_BYTES:,} byte limit."
        )
    return payload


def _resize_logo_to_brand_image(raw_bytes: bytes, bg_color: str = "#FFFFFF") -> bytes:
    """Resize and letterbox a logo image to 600×120 PNG.

    The source image is scaled to fit within 600×120 while preserving aspect
    ratio, then centered on a solid-color canvas. Output is always PNG/RGBA.
    """
    src = Image.open(io.BytesIO(raw_bytes))
    src = src.convert("RGBA")

    src_w, src_h = src.size
    scale = min(BRAND_IMAGE_WIDTH / src_w, BRAND_IMAGE_HEIGHT / src_h)
    new_w = max(1, int(src_w * scale))
    new_h = max(1, int(src_h * scale))

    resized = src.resize((new_w, new_h), Image.LANCZOS)

    bg_rgb = tuple(int(bg_color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    canvas = Image.new("RGBA", BRAND_IMAGE_SIZE, (*bg_rgb, 255))

    paste_x = (BRAND_IMAGE_WIDTH - new_w) // 2
    paste_y = (BRAND_IMAGE_HEIGHT - new_h) // 2
    canvas.paste(resized, (paste_x, paste_y), resized)

    buf = io.BytesIO()
    canvas.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Metadata generators
# ---------------------------------------------------------------------------

def _content_asset_meta_xml(asset_name: str) -> str:
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <ContentAsset xmlns="http://soap.sforce.com/2006/04/metadata">
            <isVisibleByExternalUsers>false</isVisibleByExternalUsers>
            <language>en_US</language>
            <masterLabel>{asset_name}</masterLabel>
            <relationships>
                <workspace>
                    <access>INFERRED</access>
                    <isManagingWorkspace>true</isManagingWorkspace>
                    <name>sfdc_asset_company_assets</name>
                </workspace>
            </relationships>
            <versions>
                <version>
                    <number>1</number>
                    <pathOnClient>{asset_name}.png</pathOnClient>
                </version>
            </versions>
        </ContentAsset>
    """)


def _branding_set_xml(branding_set_label: str, brand_color: str, asset_name: str) -> str:
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <BrandingSet xmlns="http://soap.sforce.com/2006/04/metadata">
            <brandingSetProperty>
                <propertyName>BRAND_COLOR</propertyName>
                <propertyValue>{brand_color}</propertyValue>
            </brandingSetProperty>
            <brandingSetProperty>
                <propertyName>HEADER_BACKGROUND_COLOR</propertyName>
                <propertyValue>#FFFFFF</propertyValue>
            </brandingSetProperty>
            <brandingSetProperty>
                <propertyName>BRAND_IMAGE</propertyName>
                <propertyValue>/file-asset/{asset_name}?v=1</propertyValue>
            </brandingSetProperty>
            <brandingSetProperty>
                <propertyName>BANNER_IMAGE</propertyName>
                <propertyValue></propertyValue>
            </brandingSetProperty>
            <brandingSetProperty>
                <propertyName>GROUPS_BANNER_IMAGE</propertyName>
                <propertyValue></propertyValue>
            </brandingSetProperty>
            <brandingSetProperty>
                <propertyName>GROUP_IMAGE</propertyName>
                <propertyValue></propertyValue>
            </brandingSetProperty>
            <brandingSetProperty>
                <propertyName>PROFILE_BANNER_IMAGE</propertyName>
                <propertyValue></propertyValue>
            </brandingSetProperty>
            <brandingSetProperty>
                <propertyName>USER_IMAGE</propertyName>
                <propertyValue></propertyValue>
            </brandingSetProperty>
            <brandingSetProperty>
                <propertyName>OVERRIDE_LOADING_PAGE</propertyName>
                <propertyValue>false</propertyValue>
            </brandingSetProperty>
            <masterLabel>{branding_set_label}</masterLabel>
        </BrandingSet>
    """)


def _theme_xml(theme_label: str, branding_set_api_name: str) -> str:
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <LightningExperienceTheme xmlns="http://soap.sforce.com/2006/04/metadata">
            <defaultBrandingSet>{branding_set_api_name}</defaultBrandingSet>
            <designSystemVersion>SLDS_v2</designSystemVersion>
            <masterLabel>{theme_label}</masterLabel>
            <shouldOverrideLoadingImage>false</shouldOverrideLoadingImage>
        </LightningExperienceTheme>
    """)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a customer-branded Lightning Experience Theme "
            "(ContentAsset + BrandingSet + LightningExperienceTheme) "
            "for customer demo onboarding."
        )
    )
    parser.add_argument("--company-name", required=True, help="Customer/company name for the theme label.")
    logo_src = parser.add_mutually_exclusive_group(required=True)
    logo_src.add_argument(
        "--logo-url",
        help="Public URL to a logo image (any size; resized to 600x120).",
    )
    logo_src.add_argument(
        "--logo-path",
        help="Path to a local logo file (PNG, JPEG, etc.); relative paths resolve from repo root.",
    )
    parser.add_argument("--brand-color", required=True, help="Hex brand color (e.g. #0176D3).")
    parser.add_argument(
        "--bg-color",
        default="#FFFFFF",
        help="Hex background color for letterboxing (default: #FFFFFF white).",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory. Default: {DEFAULT_OUTPUT_DIR}",
    )
    args = parser.parse_args()

    company_slug = _slugify(args.company_name)
    brand_color = _validate_hex_color(args.brand_color)
    bg_color = _validate_hex_color(args.bg_color)

    asset_name = _api_name(f"RLM_customer_{company_slug}_brand")
    branding_set_api = _api_name(f"LEXTHEMING{company_slug}SLDSv2")
    branding_set_label = f"{args.company_name} SLDSv2"
    theme_api = _api_name(f"{company_slug}SLDSv2")
    theme_label = f"{args.company_name} SLDSv2"

    output_dir = Path(args.output_dir).resolve()

    # --- Load and process logo ---
    if args.logo_path:
        logo_path = Path(args.logo_path)
        if not logo_path.is_absolute():
            logo_path = (REPO_ROOT / logo_path).resolve()
        print(f"Loading logo from {logo_path} ...")
        raw_bytes = _load_logo_from_path(logo_path)
    else:
        print(f"Downloading logo from {args.logo_url} ...")
        raw_bytes = _download_logo(args.logo_url)

    src_img = Image.open(io.BytesIO(raw_bytes))
    print(f"  Source image:  {src_img.size[0]}x{src_img.size[1]} {src_img.format or 'unknown'}")

    print(f"  Resizing to:   {BRAND_IMAGE_WIDTH}x{BRAND_IMAGE_HEIGHT} PNG (letterbox bg: {bg_color})")
    png_bytes = _resize_logo_to_brand_image(raw_bytes, bg_color)
    print(f"  Output size:   {len(png_bytes):,} bytes")

    # --- ContentAsset ---
    asset_dir = output_dir / "contentassets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    asset_file = asset_dir / f"{asset_name}.asset"
    asset_meta_file = asset_dir / f"{asset_name}.asset-meta.xml"
    asset_file.write_bytes(png_bytes)
    asset_meta_file.write_text(_content_asset_meta_xml(asset_name), encoding="utf-8")
    print(f"  ContentAsset:  {asset_file}")
    print(f"  ContentAsset:  {asset_meta_file}")

    # --- BrandingSet ---
    bs_dir = output_dir / "brandingSets"
    bs_dir.mkdir(parents=True, exist_ok=True)
    bs_file = bs_dir / f"{branding_set_api}.brandingSet-meta.xml"
    bs_file.write_text(_branding_set_xml(branding_set_label, brand_color, asset_name), encoding="utf-8")
    print(f"  BrandingSet:   {bs_file}")

    # --- LightningExperienceTheme ---
    theme_dir = output_dir / "lightningExperienceThemes"
    theme_dir.mkdir(parents=True, exist_ok=True)
    theme_file = theme_dir / f"{theme_api}.lightningExperienceTheme-meta.xml"
    theme_file.write_text(_theme_xml(theme_label, branding_set_api), encoding="utf-8")
    print(f"  Theme:         {theme_file}")

    # --- Summary ---
    print()
    print("=" * 60)
    print(f"  Theme label:       {theme_label}")
    print(f"  Brand color:       {brand_color}")
    print(f"  Brand image:       /file-asset/{asset_name}?v=1")
    print(f"  Image spec:        {BRAND_IMAGE_WIDTH}x{BRAND_IMAGE_HEIGHT} PNG")
    print(f"  Deploy directory:  {output_dir}")
    print()
    print("  NEXT STEPS:")
    print(f"    1. Deploy:   cci task run deploy_customer_demo_branding --org <alias>")
    print(f"    2. Activate: Open your org's Themes and Branding page:")
    print(f"       <org-url>/lightning/setup/ThemingAndBranding/home")
    print(f"       Find '{theme_label}' → click dropdown → Activate")
    print("=" * 60)


if __name__ == "__main__":
    main()
