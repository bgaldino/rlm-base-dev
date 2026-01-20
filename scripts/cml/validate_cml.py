import argparse
import csv
import os
import re
import sys

CML_DIR = os.path.dirname(__file__)

TYPE_RE = re.compile(r"^\s*type\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*([A-Za-z_][A-Za-z0-9_]*))?\s*(\{|;)\s*$")
DEFINE_RE = re.compile(r"^\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\s+\[(.*)\]\s*$")
RELATION_RE = re.compile(
    r"^\s*relation\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([A-Za-z_][A-Za-z0-9_]*)"
)
ORDER_RE = re.compile(r"order\s*\(([^)]*)\)")
FIELD_RE = re.compile(
    r"^\s*(?:@\(.*\)\s*)*(string|int|boolean|decimal(?:\(\d+\))?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^;]+);"
)
DEFAULT_RE = re.compile(r"defaultValue\s*=\s*(\"[^\"]*\"|[^,\)]+)")
RANGE_RE = re.compile(r"\[\s*(\d+)\s*\.\.\s*(\d+)\s*\]")


def split_list_values(raw):
    values = []
    for part in raw.split(","):
        part = part.strip()
        if part.startswith('"') and part.endswith('"'):
            part = part[1:-1]
        values.append(part)
    return [v for v in values if v != ""]


def parse_define(line):
    match = DEFINE_RE.match(line)
    if not match:
        return None
    name = match.group(1)
    raw_vals = match.group(2).strip()
    values = split_list_values(raw_vals) if raw_vals else []
    return name, values


def parse_default_value(annotation_text):
    match = DEFAULT_RE.search(annotation_text)
    if not match:
        return None
    raw = match.group(1).strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    return raw


def validate_file(path):
    issues = []
    types = {}
    abstract_types = set()
    child_types = set()
    defines = {}
    relations = []
    type_order_refs = []
    pending_annotations = []

    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    for line_no, line in enumerate(lines, start=1):
        define_parsed = parse_define(line)
        if define_parsed:
            defines[define_parsed[0]] = define_parsed[1]
            continue

        type_match = TYPE_RE.match(line)
        if type_match:
            type_name = type_match.group(1)
            base_name = type_match.group(2)
            body_token = type_match.group(3)
            if type_name in types:
                issues.append(
                    (
                        "error",
                        line_no,
                        f"Duplicate type definition '{type_name}'.",
                    )
                )
            types[type_name] = base_name
            if base_name:
                child_types.add(base_name)
            if body_token == ";":
                abstract_types.add(type_name)
            continue

        relation_match = RELATION_RE.match(line)
        if relation_match:
            rel_name, rel_type = relation_match.groups()
            relations.append((line_no, rel_name, rel_type))
            order_match = ORDER_RE.search(line)
            if order_match:
                order_list = [
                    item.strip()
                    for item in order_match.group(1).split(",")
                    if item.strip()
                ]
                for order_type in order_list:
                    type_order_refs.append((line_no, order_type))
            continue

        if line.strip().startswith("@("):
            pending_annotations.append(line.strip())
            continue

        field_match = FIELD_RE.match(line)
        if field_match:
            field_type, field_name, raw_rhs = field_match.groups()
            annotation_text = " ".join(pending_annotations + [line])
            pending_annotations = []

            default_value = parse_default_value(annotation_text)
            if default_value is None:
                continue

            rhs = raw_rhs.strip()
            values = None
            range_match = RANGE_RE.search(rhs)
            if rhs.startswith("[") and rhs.endswith("]"):
                values = split_list_values(rhs[1:-1])
            elif rhs in defines:
                values = defines[rhs]

            if field_type.startswith("string"):
                if values is not None and default_value not in values:
                    issues.append(
                        (
                            "warning",
                            line_no,
                            f"Default '{default_value}' not in enum for '{field_name}'.",
                        )
                    )
            elif field_type.startswith("int") or field_type.startswith("decimal"):
                if range_match:
                    low, high = int(range_match.group(1)), int(range_match.group(2))
                    try:
                        numeric_default = int(float(default_value))
                        if numeric_default < low or numeric_default > high:
                            issues.append(
                                (
                                    "warning",
                                    line_no,
                                    f"Default '{default_value}' outside range for '{field_name}'.",
                                )
                            )
                    except ValueError:
                        issues.append(
                            (
                                "warning",
                                line_no,
                                f"Default '{default_value}' is not numeric for '{field_name}'.",
                            )
                        )
            continue

        if line.strip() and not line.strip().startswith("//"):
            pending_annotations = []

    for line_no, rel_name, rel_type in relations:
        if rel_type not in types:
            issues.append(
                (
                    "error",
                    line_no,
                    f"Relation '{rel_name}' references missing type '{rel_type}'.",
                )
            )

    for line_no, order_type in type_order_refs:
        if order_type not in types:
            issues.append(
                (
                    "warning",
                    line_no,
                    f"Order list references missing type '{order_type}'.",
                )
            )

    for type_name, base_name in types.items():
        if base_name and base_name not in types:
            issues.append(
                (
                    "warning",
                    None,
                    f"Type '{type_name}' extends missing base '{base_name}'.",
                )
            )

    leaf_types = {t for t in types if t not in child_types and t not in abstract_types}
    return issues, types, relations, leaf_types


def read_dataset_associations(dataset_dir):
    esc_path = os.path.join(dataset_dir, "ExpressionSetConstraintObj.csv")
    if not os.path.exists(esc_path):
        return {}

    associations_by_model = {}
    with open(esc_path, newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            model_name = row.get("ExpressionSet.Name", "").strip()
            if not model_name:
                continue
            tag = row.get("ConstraintModelTag", "").strip()
            tag_type = row.get("ConstraintModelTagType", "").strip().lower()
            if not tag or not tag_type:
                continue
            entry = associations_by_model.setdefault(model_name, {"type": set(), "port": set()})
            if tag_type == "type":
                entry["type"].add(tag)
            elif tag_type == "port":
                entry["port"].add(tag)
    return associations_by_model


def infer_expression_set_name(cml_path, dataset_dirs):
    cml_name = os.path.splitext(os.path.basename(cml_path))[0]
    for dataset_dir in dataset_dirs:
        expr_path = os.path.join(dataset_dir, "ExpressionSet.csv")
        if not os.path.exists(expr_path):
            continue
        with open(expr_path, newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                name = (row.get("Name") or "").strip()
                if name:
                    return name
    return cml_name


def main():
    parser = argparse.ArgumentParser(description="Validate CML structure and associations.")
    parser.add_argument("--cml-dir", default=CML_DIR, help="Directory containing .cml files.")
    parser.add_argument("--dataset-dir", action="append", default=[], help="SFDMU dataset directory containing ExpressionSetConstraintObj.csv.")
    parser.add_argument("--expression-set-name", default="", help="Override Expression Set name for association checks.")
    args = parser.parse_args()

    cml_dir = args.cml_dir
    dataset_dirs = args.dataset_dir
    expression_set_override = args.expression_set_name.strip()

    cml_files = [
        os.path.join(cml_dir, name)
        for name in os.listdir(cml_dir)
        if name.endswith(".cml")
    ]

    if not cml_files:
        print("No .cml files found.")
        return 1

    all_issues = {}
    association_issues = {}
    associations = {}
    for dataset_dir in dataset_dirs:
        associations.update(read_dataset_associations(dataset_dir))

    for path in sorted(cml_files):
        issues, types, relations, leaf_types = validate_file(path)
        if issues:
            all_issues[path] = issues

        if dataset_dirs:
            model_name = expression_set_override or infer_expression_set_name(path, dataset_dirs)
            assoc = associations.get(model_name, {"type": set(), "port": set()})
            assoc_issues = []

            relation_names = {rel_name for _, rel_name, _ in relations}
            for rel_name in sorted(relation_names):
                if rel_name not in assoc["port"]:
                    assoc_issues.append(("warning", None, f"Missing port association for relation '{rel_name}' in '{model_name}'."))

            for type_name in sorted(leaf_types):
                if type_name not in assoc["type"]:
                    assoc_issues.append(("warning", None, f"Missing type association for leaf type '{type_name}' in '{model_name}'."))

            for tag in sorted(assoc["type"]):
                if tag not in types:
                    assoc_issues.append(("warning", None, f"Type association '{tag}' not found in CML types for '{model_name}'."))

            for tag in sorted(assoc["port"]):
                if tag not in relation_names:
                    assoc_issues.append(("warning", None, f"Port association '{tag}' not found in CML relations for '{model_name}'."))

            if assoc_issues:
                association_issues[path] = assoc_issues

    if not all_issues and not association_issues:
        print("✅ No structural issues found in CML files.")
        return 0

    print("⚠️  CML validation results:")
    for path, issues in all_issues.items():
        rel_path = os.path.relpath(path, cml_dir)
        print(f"\n{rel_path}:")
        for severity, line_no, message in issues:
            if line_no:
                print(f"  - [{severity}] L{line_no}: {message}")
            else:
                print(f"  - [{severity}] {message}")

    for path, issues in association_issues.items():
        rel_path = os.path.relpath(path, cml_dir)
        print(f"\n{rel_path} (associations):")
        for severity, line_no, message in issues:
            if line_no:
                print(f"  - [{severity}] L{line_no}: {message}")
            else:
                print(f"  - [{severity}] {message}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
