"""
Extract all mustache tokens from a .docx or .pptx template.

Parses paragraphs/tables (Word: document, headers, footers; PowerPoint:
slides, slide masters/layouts) for:
  - {{field}} — simple value tokens
  - {{#Section}} / {{/Section}} — repeating block boundaries
  - {{IMG_name}} — dynamic image tokens

Outputs a structured report useful for validating alignment between
a template and its Transform ODT output keys.

Usage:
  python scripts/docgen/docgen_template_extract_tokens.py /path/to/template.docx
  python scripts/docgen/docgen_template_extract_tokens.py /path/to/template.pptx
  python scripts/docgen/docgen_template_extract_tokens.py /path/to/template.docx --json
  python scripts/docgen/docgen_template_extract_tokens.py /path/to/template.docx --validate-transform RLMQuoteProposalTransform --org dev-scratch
"""
import argparse
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _soql import soql_escape


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
TOKEN_RE = re.compile(r"\{\{([^}]+)\}\}")


def extract_paragraphs_from_word_xml(xml_content):
    root = ET.fromstring(xml_content)
    paragraphs = []
    for para in root.iter(f"{{{WORD_NS}}}p"):
        runs = []
        for t in para.iter(f"{{{WORD_NS}}}t"):
            if t.text:
                runs.append(t.text)
        if runs:
            paragraphs.append("".join(runs))
    return paragraphs


def extract_paragraphs_from_drawingml_xml(xml_content):
    root = ET.fromstring(xml_content)
    paragraphs = []
    for para in root.iter(f"{{{DRAWING_NS}}}p"):
        runs = []
        for t in para.iter(f"{{{DRAWING_NS}}}t"):
            if t.text:
                runs.append(t.text)
        if runs:
            paragraphs.append("".join(runs))
    return paragraphs


def _select_parts(namelist, file_type):
    if file_type == "pptx":
        return [
            name for name in namelist
            if name.endswith(".xml") and name.startswith("ppt/slides/slide")
        ]
    return [
        name for name in namelist
        if name.endswith(".xml") and (
            "document" in name
            or "header" in name
            or "footer" in name
        )
    ]


def extract_tokens_from_template(template_path):
    tokens = {
        "fields": [],
        "sections_open": [],
        "sections_close": [],
        "images": [],
        "all": [],
    }

    suffix = Path(template_path).suffix.lower().lstrip(".")
    file_type = "pptx" if suffix == "pptx" else "docx"
    paragraph_extractor = (
        extract_paragraphs_from_drawingml_xml if file_type == "pptx"
        else extract_paragraphs_from_word_xml
    )

    try:
        with zipfile.ZipFile(template_path, "r") as z:
            parts = _select_parts(z.namelist(), file_type)

            all_text = ""
            for part in parts:
                content = z.read(part)
                paragraphs = paragraph_extractor(content)
                all_text += "\n".join(paragraphs) + "\n"

    except zipfile.BadZipFile:
        print(f"ERROR: '{template_path}' is not a valid .docx/.pptx file", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: File not found: '{template_path}'", file=sys.stderr)
        sys.exit(1)

    seen = set()
    for match in TOKEN_RE.finditer(all_text):
        token = match.group(1)
        if token in seen:
            continue
        seen.add(token)
        tokens["all"].append(token)

        if token.startswith("#"):
            tokens["sections_open"].append(token[1:])
        elif token.startswith("/"):
            tokens["sections_close"].append(token[1:])
        elif token.startswith("IMG_"):
            tokens["images"].append(token)
        else:
            tokens["fields"].append(token)

    return tokens


def validate_against_transform(tokens, odt_name, org):
    escaped_name = soql_escape(odt_name)
    query = f"SELECT Id FROM OmniDataTransform WHERE Name = '{escaped_name}'"
    result = subprocess.run(
        ["sf", "data", "query", "-q", query, "--target-org", org, "--json"],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(result.stdout)
        records = data["result"]["records"]
    except (json.JSONDecodeError, KeyError):
        print(f"ERROR: Could not find Transform ODT '{odt_name}'", file=sys.stderr)
        return None

    if not records:
        print(f"ERROR: Transform ODT '{odt_name}' not found", file=sys.stderr)
        return None

    odt_id = records[0]["Id"]
    escaped_id = soql_escape(odt_id)
    query = (
        f"SELECT OutputFieldName, OutputObjectName, FormulaExpression "
        f"FROM OmniDataTransformItem WHERE OmniDataTransformationId = '{escaped_id}'"
    )
    result = subprocess.run(
        ["sf", "data", "query", "-q", query, "--target-org", org, "--json"],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(result.stdout)
        items = data["result"]["records"]
    except (json.JSONDecodeError, KeyError):
        print(f"ERROR: Could not query Transform items", file=sys.stderr)
        return None

    transform_outputs = set()
    for item in items:
        out = item.get("OutputFieldName")
        if out and out != "Formula":
            transform_outputs.add(out)
            if ":" in out:
                transform_outputs.add(out.split(":")[0])
        obj = item.get("OutputObjectName")
        if obj and obj not in ("json", "Formula"):
            transform_outputs.add(obj)

    template_expects = set(tokens["fields"] + tokens["images"])
    for section in tokens["sections_open"]:
        template_expects.add(section)

    missing = template_expects - transform_outputs
    extra = transform_outputs - template_expects

    return {
        "missing_in_transform": sorted(missing),
        "extra_in_transform": sorted(extra),
        "aligned": sorted(template_expects & transform_outputs),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract mustache tokens from a .docx or .pptx template"
    )
    parser.add_argument("template", help="Path to .docx or .pptx template file")
    parser.add_argument(
        "--json", action="store_true", dest="json_output", help="Output as JSON"
    )
    parser.add_argument(
        "--validate-transform",
        metavar="ODT_NAME",
        help="Compare tokens against a Transform ODT's output keys",
    )
    parser.add_argument("--org", help="SF CLI target org (required with --validate-transform)")
    args = parser.parse_args()

    tokens = extract_tokens_from_template(args.template)

    if args.json_output:
        print(json.dumps(tokens, indent=2))
        return

    print(f"Template: {args.template}")
    print(f"Total unique tokens: {len(tokens['all'])}")

    if tokens["fields"]:
        print(f"\nField tokens ({len(tokens['fields'])}):")
        for t in sorted(tokens["fields"]):
            print(f"  {{{{ {t} }}}}")

    if tokens["sections_open"]:
        print(f"\nSection blocks ({len(tokens['sections_open'])}):")
        for t in sorted(tokens["sections_open"]):
            matched = t in tokens["sections_close"]
            status = "✓ closed" if matched else "✗ UNCLOSED"
            print(f"  {{{{#{t}}}}} ... {{{{/{t}}}}}  [{status}]")

    unclosed = set(tokens["sections_open"]) - set(tokens["sections_close"])
    unopened = set(tokens["sections_close"]) - set(tokens["sections_open"])
    if unclosed:
        print(f"\n⚠ Unclosed sections: {sorted(unclosed)}")
    if unopened:
        print(f"\n⚠ Close without open: {sorted(unopened)}")

    if tokens["images"]:
        print(f"\nImage tokens ({len(tokens['images'])}):")
        for t in sorted(tokens["images"]):
            print(f"  {{{{ {t} }}}}")

    if args.validate_transform:
        if not args.org:
            print("\nERROR: --org required with --validate-transform", file=sys.stderr)
            sys.exit(1)

        print(f"\n--- Validating against Transform: {args.validate_transform} ---")
        result = validate_against_transform(tokens, args.validate_transform, args.org)
        if result:
            if result["aligned"]:
                print(f"  ✓ Aligned ({len(result['aligned'])}): {result['aligned']}")
            if result["missing_in_transform"]:
                print(
                    f"  ✗ Template expects but Transform doesn't provide "
                    f"({len(result['missing_in_transform'])}): "
                    f"{result['missing_in_transform']}"
                )
            if result["extra_in_transform"]:
                print(
                    f"  ℹ Transform provides but template doesn't use "
                    f"({len(result['extra_in_transform'])}): "
                    f"{result['extra_in_transform']}"
                )


if __name__ == "__main__":
    main()
