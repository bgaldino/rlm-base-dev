"""Salesforce metadata XML helpers shared by assembly, diff and writeback."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator, List, Optional

# Salesforce metadata XML namespace
SF_NS = "http://soap.sforce.com/2006/04/metadata"
SF_NS_TAG = f"{{{SF_NS}}}"

# Register default namespace so ElementTree serializes without ns0: prefix
ET.register_namespace("", SF_NS)


def write_xml(root: ET.Element, dest: Path) -> None:
    """Write an ElementTree Element to a file with XML declaration."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space="    ")
    tree = ET.ElementTree(root)
    tree.write(str(dest), encoding="unicode", xml_declaration=True)
    # ElementTree uses single quotes and writes encoding="us-ascii" in the
    # declaration when using encoding="unicode". Fix both to match Salesforce
    # convention: double quotes, UTF-8, and trailing newline.
    text = dest.read_text(encoding="utf-8")
    # Normalize the XML declaration to Salesforce convention (double quotes).
    # ET may produce: version='1.0', encoding='us-ascii'|'utf-8'|'UTF-8'
    text = text.replace("<?xml version='1.0'", '<?xml version="1.0"')
    for sq_enc in ("encoding='us-ascii'", "encoding='utf-8'", "encoding='UTF-8'"):
        if sq_enc in text:
            text = text.replace(sq_enc, 'encoding="UTF-8"')
            break
    # Re-encode quotes as &quot; inside <value> elements containing escaped
    # HTML (&lt;) or JSON ([{/{"}).  ET unescapes &quot; on parse since raw "
    # is valid in XML text, but Salesforce metadata expects &quot; in these
    # contexts (HTML attribute quotes, JSON property names/values).
    def _requote_value(m):
        content = m.group(2)
        if "&lt;" in content or content.lstrip().startswith(("[{", '{"')):
            content = content.replace('"', "&quot;")
        return m.group(1) + content + m.group(3)

    text = re.sub(r"(<value>)(.*?)(</value>)", _requote_value, text)
    if not text.endswith("\n"):
        text += "\n"
    dest.write_text(text, encoding="utf-8")


def indented_text(root: ET.Element) -> str:
    """Indent ``root`` in place and return its serialization."""
    ET.indent(root, space="    ")
    return ET.tostring(root, encoding="unicode")


def normalize_xml(element: ET.Element) -> str:
    """Canonical string for XML comparison — strips whitespace between tags."""
    return re.sub(r">\s+<", "><", ET.tostring(element, encoding="unicode")).strip()


def parse_fragment(xml_fragment: str) -> ET.Element:
    """Parse sibling elements in the SF namespace under a ``<wrapper>`` root."""
    return ET.fromstring(f'<wrapper xmlns="{SF_NS}">{xml_fragment}</wrapper>')


def find_elem(parent: ET.Element, local_name: str) -> Optional[ET.Element]:
    return parent.find(f"{SF_NS_TAG}{local_name}")


def findall_elem(parent: ET.Element, local_name: str) -> List[ET.Element]:
    return parent.findall(f"{SF_NS_TAG}{local_name}")


def child_text(parent: ET.Element, local_name: str) -> Optional[str]:
    """Text of the first ``local_name`` child, or None."""
    el = find_elem(parent, local_name)
    return el.text if el is not None else None


def local_tag(el: ET.Element) -> str:
    """Tag name without its namespace."""
    return el.tag.rsplit("}", 1)[-1]


def make_elem(local_name: str, text: Optional[str] = None) -> ET.Element:
    el = ET.Element(f"{SF_NS_TAG}{local_name}")
    if text is not None:
        el.text = text
    return el


def sub_elem(parent: ET.Element, local_name: str, text: Optional[str] = None) -> ET.Element:
    el = ET.SubElement(parent, f"{SF_NS_TAG}{local_name}")
    if text is not None:
        el.text = text
    return el


# ---------------------------------------------------------------------------
# componentInstanceProperties valueLists
# ---------------------------------------------------------------------------


def _property_value_list(ci_props: ET.Element, prop_name: str) -> Optional[ET.Element]:
    if child_text(ci_props, "name") != prop_name:
        return None
    return find_elem(ci_props, "valueList")


def value_lists(root: ET.Element, prop_name: str) -> Iterator[ET.Element]:
    """Every ``valueList`` of a ``prop_name`` componentInstanceProperties, in document order."""
    for ci_props in root.iter(f"{SF_NS_TAG}componentInstanceProperties"):
        vlist = _property_value_list(ci_props, prop_name)
        if vlist is not None:
            yield vlist


def component_value_list(root: ET.Element, identifier: str, prop_name: str) -> Optional[ET.Element]:
    """The ``prop_name`` valueList of the component ``identifier``; None if absent."""
    for ci in root.iter(f"{SF_NS_TAG}componentInstance"):
        if child_text(ci, "identifier") != identifier:
            continue
        for ci_props in findall_elem(ci, "componentInstanceProperties"):
            if child_text(ci_props, "name") == prop_name:
                return find_elem(ci_props, "valueList")
    return None


def value_items(vlist: ET.Element) -> List[ET.Element]:
    return findall_elem(vlist, "valueListItems")


def item_value(item: ET.Element) -> Optional[str]:
    """``<value>`` text of a valueListItems element."""
    return child_text(item, "value")


def list_values(vlist: ET.Element) -> List[str]:
    """Non-empty values of a valueList, in order."""
    return [v for v in map(item_value, value_items(vlist)) if v]


def make_value_item(value: str) -> ET.Element:
    item = make_elem("valueListItems")
    sub_elem(item, "value", value)
    return item


def remove_values(vlist: ET.Element, values) -> bool:
    """Remove every item whose value is in ``values``; True if any was removed."""
    removed = [item for item in value_items(vlist) if item_value(item) in values]
    for item in removed:
        vlist.remove(item)
    return bool(removed)
