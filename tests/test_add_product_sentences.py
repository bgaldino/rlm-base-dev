"""The Add Product To Quote sentences agree across the class, its Flow and the agent.

The quoting agent decides whether to retry an add from the sentence it gets back, so three files
must agree: RLM_AI_AddProductToQuoteService.cls (which returns the sentences), the
RLM_AI_Add_Product_To_Quote Flow (whose fault path returns its own copy of the uncertain sentence,
never the fault message) and the agent's instructions (which quote parts of two sentences).

No org, no network. Run:  python tests/test_add_product_sentences.py
"""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGENTS = REPO / "unpackaged" / "post_agents"
SERVICE = AGENTS / "classes" / "RLM_AI_AddProductToQuoteService.cls"
FLOW = AGENTS / "flows" / "RLM_AI_Add_Product_To_Quote.flow-meta.xml"
AGENT = AGENTS / "aiAuthoringBundles" / "RLM_Quoting_Assistant" / "RLM_Quoting_Assistant.agent"
NS = {"f": "http://soap.sforce.com/2006/04/metadata"}


def apex_constant(name):
    match = re.search(r"static final String " + name + r"\s*=\s*'((?:[^'\\]|\\.)*)';",
                      SERVICE.read_text(encoding="utf-8"))
    if match is None:
        raise AssertionError(f"{name} not found in {SERVICE.name}")
    return apex_unescape(match.group(1))


# Apex string-literal escapes: \uXXXX, the letters below, and any other escaped character
# standing for itself (\' and \\).
APEX_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f"}


def _decode_escape(match):
    if match.group(1) is not None:
        return chr(int(match.group(1), 16))
    return APEX_ESCAPES.get(match.group(2), match.group(2))


def apex_unescape(literal):
    """The text an Apex string literal stands for, as the Flow XML holds it decoded."""
    return re.sub(r"\\(?:u([0-9a-fA-F]{4})|(.))", _decode_escape, literal)


def add_product_instruction():
    """The agent's instruction bullet for adding a product: the line that starts with it."""
    lines = [line for line in AGENT.read_text(encoding="utf-8").splitlines()
             if line.lstrip().startswith("- Add a product to the quote ->")]
    if len(lines) != 1:
        raise AssertionError(f"expected one add-product instruction in {AGENT.name}, found {len(lines)}")
    return lines[0]


def fault_assignment(name):
    root = ET.parse(FLOW).getroot()
    for assignment in root.findall("f:assignments", NS):
        if assignment.findtext("f:name", namespaces=NS) == name:
            return {
                item.findtext("f:assignToReference", namespaces=NS): item.find("f:value", NS)
                for item in assignment.findall("f:assignmentItems", NS)
            }
    raise AssertionError(f"assignment {name} not found in {FLOW.name}")


class AddProductSentences(unittest.TestCase):
    def test_apex_escapes_are_decoded(self):
        self.assertEqual("it's \\ ok\n", apex_unescape(r"it\'s \\ ok\n"))
        self.assertEqual("caf\u00e9", apex_unescape(r"caf\u00e9"))

    def test_the_flow_fault_path_returns_the_uncertain_sentence(self):
        root = ET.parse(FLOW).getroot()
        fault_targets = {fc.findtext("f:targetReference", namespaces=NS)
                         for fc in root.iter("{%s}faultConnector" % NS["f"])}
        self.assertEqual({"AssignError"}, fault_targets)
        items = fault_assignment("AssignError")
        self.assertEqual(apex_constant("ADD_UNCERTAIN_MESSAGE"),
                         items["errorMessage"].findtext("f:stringValue", namespaces=NS))
        self.assertEqual("false", items["isSuccess"].findtext("f:booleanValue", namespaces=NS))

    def test_the_flow_never_returns_the_fault_message(self):
        self.assertNotIn("$Flow.FaultMessage", FLOW.read_text(encoding="utf-8"))

    def test_the_add_product_instruction_quotes_parts_of_the_sentences_the_class_returns(self):
        agent = add_product_instruction()
        for constant, quoted in [("ADD_UNCERTAIN_MESSAGE", "may not have been added"),
                                 ("ACTION_UNAVAILABLE_MESSAGE", "cannot be added to quotes here yet")]:
            with self.subTest(constant=constant):
                self.assertIn(quoted, apex_constant(constant))
                self.assertIn(quoted, agent)


if __name__ == "__main__":
    unittest.main()
