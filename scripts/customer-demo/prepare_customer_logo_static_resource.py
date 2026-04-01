#!/usr/bin/env python3
"""Prepare a customer logo Static Resource for demo product images.

This script downloads a logo from a public URL and writes a square SVG Static
Resource wrapper that can be deployed to Salesforce and referenced as:
  /resource/<StaticResourceName>
"""

from __future__ import annotations

import argparse
import base64
import re
import textwrap
import xml.sax.saxutils as xml_utils
from pathlib import Path
from urllib.parse import urlparse

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "unpackaged" / "post_customer_demo" / "staticresources"

CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}

MAX_BYTES = 2 * 1024 * 1024


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return slug or "customer"


def _safe_resource_name(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]", "_", value).strip("_")
    if not clean:
        raise ValueError("Static resource name cannot be empty after sanitization.")
    if not re.match(r"^[A-Za-z]", clean):
        clean = f"RLM_{clean}"
    return clean[:240]


def _guess_content_type(url: str, header_type: str | None) -> str:
    if header_type:
        ct = header_type.split(";")[0].strip().lower()
        if ct.startswith("image/"):
            return ct
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in CONTENT_TYPES:
        return CONTENT_TYPES[suffix]
    return "image/png"


def _download_logo(url: str) -> tuple[bytes, str]:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    payload = response.content
    if not payload:
        raise ValueError(f"Downloaded logo from {url} is empty.")
    if len(payload) > MAX_BYTES:
        raise ValueError(
            f"Downloaded logo is {len(payload)} bytes, which exceeds {MAX_BYTES} bytes."
        )
    return payload, _guess_content_type(url, response.headers.get("Content-Type"))


def _svg_static_resource(payload: bytes, content_type: str) -> str:
    data_uri = f"data:{content_type};base64,{base64.b64encode(payload).decode('ascii')}"
    escaped_data_uri = xml_utils.escape(data_uri, entities={'"': "&quot;"})
    return textwrap.dedent(
        f"""\
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="Customer logo">
          <rect width="512" height="512" fill="#ffffff"/>
          <image x="0" y="0" width="512" height="512" preserveAspectRatio="xMidYMid meet" href="{escaped_data_uri}"/>
        </svg>
        """
    )


def _metadata_xml(description: str) -> str:
    escaped_description = xml_utils.escape(description)
    return textwrap.dedent(
        f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <StaticResource xmlns="http://soap.sforce.com/2006/04/metadata">
            <cacheControl>Public</cacheControl>
            <contentType>image/svg+xml</contentType>
            <description>{escaped_description}</description>
        </StaticResource>
        """
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Download a customer logo and generate Salesforce Static Resource files "
            "for customer demo product images."
        )
    )
    parser.add_argument("--company-name", required=True, help="Company/customer name.")
    parser.add_argument("--logo-url", required=True, help="Public URL to logo image.")
    parser.add_argument(
        "--resource-name",
        default="",
        help=(
            "Optional static resource API name. Default: "
            "RLM_customer_<company_slug>_logo_sq"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Directory where staticresource files are written. Default: {DEFAULT_OUTPUT_DIR}",
    )
    args = parser.parse_args()

    company_slug = _slugify(args.company_name)
    resource_name = _safe_resource_name(
        args.resource_name or f"RLM_customer_{company_slug}_logo_sq"
    )
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    payload, payload_content_type = _download_logo(args.logo_url)
    svg_body = _svg_static_resource(payload, payload_content_type)
    description = f"Customer demo square logo for {args.company_name}"

    resource_file = output_dir / resource_name
    metadata_file = output_dir / f"{resource_name}.resource-meta.xml"
    resource_file.write_text(svg_body, encoding="utf-8")
    metadata_file.write_text(_metadata_xml(description), encoding="utf-8")

    print(f"Wrote: {resource_file}")
    print(f"Wrote: {metadata_file}")
    print(f"DisplayUrl value: /resource/{resource_name}")


if __name__ == "__main__":
    main()
