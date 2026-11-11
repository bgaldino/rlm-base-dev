"""Tests for .cursor/skills/commercial-model-planning/scripts/ledger.py (standard library only).

    python tests/test_commercial_model_planning_ledger.py

Builds a synthetic plan and blind plan in the template's section names, then checks every
origin, recording, re-init and the scorecard, and that each refusal can happen.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = (Path(__file__).resolve().parent.parent
          / ".cursor/skills/commercial-model-planning/scripts/ledger.py")

BLIND = """# Example on Revenue Cloud — Build Plan

## 1. Goal and definition of done

- The Rule decision record below is the record.
**The record:** the Rule decision record in section 3.

## 2. Decisions

| # | Decision | Recommendation |
|---|---|---|
| D1 | **DECIDED 2026-01-01: demo.** What is it for? | Sets done |
| D2 | Which band edge? | Inclusive |
| D3 | Round where? | At the end |

What D2 changes:

| Choice | Total |
|---|---|
| Inclusive | 100.00 |
| Exclusive | 90.00 |

## 3. Architecture: source mapped to Revenue Cloud

### 3.10 Rule decision record

| Rule | Decided by | Native feature and fallback | Exact vs source? |
|---|---|---|---|
| R-01 | **Repo** | Volume tiers | exact |
| R-02 | Live (c) | Amendment | exact |
| R-03 | Repo (inferred); Live (b) on renewal | Formula | exact |

### 3.11 Knowledge source per area

| Area | Decided by |
|---|---|
| pricing | Repo |

## 5. Phases, gates, skills

| Phase | Typical content |
|---|---|
| P2 Live spikes | Only the Live rules |
| P3 Catalog | Plans |

**P0 Environment**

**Skills:** `build-harness`

**P2 Live spikes** (each on its own org)

- **Skills:** `asset-lifecycle-changes`

| Spike | Rules | Must hit | Smallest case | Read first |
|---|---|---|---|---|
| S-1 Amendment value | R-02 | 100.00 | One line | `asset-lifecycle-changes` |

**P3 Catalog, then configuration**

| Not | a spike |
|---|---|
| X-01 | ignored |

| Check | Must hit |
|---|---|
| G-1 | a gate check, not a spike |
"""

PLAN = (BLIND
        .replace("| D3 | Round where? | At the end |",
                 "| D3 | Round where? | Per line |\n| D4 | Added later? | Yes |")
        .replace("| S-1 Amendment value | R-02 | 100.00 |", "| S-1 Amendment value | R-02 | 120.00 |"))


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "plan.md").write_text(PLAN)
        (self.dir / "blind.md").write_text(BLIND)

    def tearDown(self):
        self.tmp.cleanup()

    def run_ledger(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], cwd=self.dir,
                              capture_output=True, text=True)

    def ledger(self):
        return json.loads((self.dir / "verification/ledger.json").read_text())["items"]

    def init(self, *extra):
        p = self.run_ledger("init", "--plan", "plan.md", "--blind", "blind.md", "--intake", "D1", *extra)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p

    def test_origins(self):
        self.init()
        origin = {k: v["origin"] for k, v in self.ledger().items()}
        self.assertEqual(origin, {
            "decision:D1": "intake", "decision:D2": "blind", "decision:D3": "edited",
            "decision:D4": "added", "rule:R-01": "blind", "rule:R-02": "blind",
            "rule:R-03": "blind", "spike:S-1": "edited"})
        items = self.ledger()
        self.assertIn("At the end", items["decision:D3"]["blind_prediction"])
        self.assertIsNone(items["decision:D2"]["blind_prediction"])
        self.assertEqual(items["spike:S-1"]["prediction"]["Must hit"], "120.00")

    def test_owner_set_after_the_plan_leaves_accuracy(self):
        self.init()
        self.run_ledger("record", "D2", "affirmed", "x")
        self.run_ledger("init", "--plan", "plan.md", "--owner", "D2")
        item = self.ledger()["decision:D2"]
        self.assertEqual((item["origin"], item["outcome"]), ("owner", "affirmed"))
        self.run_ledger("init", "--plan", "plan.md", "--owner", "")
        self.assertEqual(self.ledger()["decision:D2"]["origin"], "blind")

    def test_heading_case_and_mentions(self):
        (self.dir / "plan.md").write_text(PLAN.replace("### 3.10 Rule decision record",
                                                       "### 3.10 Rule Decision Record"))
        self.init()
        self.assertEqual(sorted(self.ledger()), [
            "decision:D1", "decision:D2", "decision:D3", "decision:D4",
            "rule:R-01", "rule:R-02", "rule:R-03", "spike:S-1"])

    def test_missing_rule_record_fails(self):
        (self.dir / "plan.md").write_text(PLAN.replace("### 3.10 Rule decision record", "### 3.10 Rules"))
        p = self.run_ledger("init", "--plan", "plan.md")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("no rule rows", p.stderr)
        self.assertFalse((self.dir / "verification/ledger.json").exists())

    def test_empty_spike_section_reads_no_other_phase(self):
        start = PLAN.index("**P2 Live spikes**")
        end = PLAN.index("**P3 Catalog")
        plan = PLAN[:start] + "**P2 Live spikes** None: no rule is Live.\n\n" + PLAN[end:]
        (self.dir / "plan.md").write_text(plan.replace("| Not | a spike |", "| Item | Content |"))
        p = self.run_ledger("init", "--plan", "plan.md")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("no spike rows", p.stderr)
        self.assertFalse([k for k in self.ledger() if k.startswith("spike:")])

    def test_rules_in_several_tables(self):
        (self.dir / "plan.md").write_text(PLAN.replace(
            "| R-02 | Live (c) | Amendment | exact |\n",
            "\nPricing rules:\n\n| Rule | Decided by | Native feature and fallback | Exact vs source? |\n"
            "|---|---|---|---|\n| R-02 | Live (c) | Amendment | exact |\n"))
        self.init()
        self.assertEqual(sorted(k for k in self.ledger() if k.startswith("rule:")),
                         ["rule:R-01", "rule:R-02", "rule:R-03"])

    def test_rule_record_under_one_heading_per_area(self):
        plan = PLAN.replace("| R-02 | Live (c) | Amendment | exact |\n",
                            "\n#### Rule decision record: lifecycle\n\n"
                            "| Rule | Decided by | Native feature and fallback | Exact vs source? |\n"
                            "|---|---|---|---|\n| R-02 | Live (c) | Amendment | exact |\n")
        (self.dir / "plan.md").write_text(plan)
        p = self.init()
        self.assertNotIn("appears twice", p.stderr)
        self.assertEqual(sorted(k for k in self.ledger() if k.startswith("rule:")),
                         ["rule:R-01", "rule:R-02", "rule:R-03"])

    def test_without_blind_every_row_is_blind(self):
        p = self.run_ledger("init", "--plan", "plan.md")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual({v["origin"] for v in self.ledger().values()}, {"blind"})

    def test_ranges(self):
        p = self.run_ledger("init", "--plan", "plan.md", "--intake", "D1-D2", "--owner", "D4")
        self.assertEqual(p.returncode, 0, p.stderr)
        origin = {k: v["origin"] for k, v in self.ledger().items()}
        self.assertEqual((origin["decision:D1"], origin["decision:D2"], origin["decision:D4"]),
                         ("intake", "intake", "owner"))

    def test_record_and_reinit_keep_outcomes_and_frozen_prediction(self):
        self.init()
        p = self.run_ledger("record", "R-02", "refuted", "org x: 90.00",
                            "--skill", "asset-lifecycle-changes: claim")
        self.assertEqual(p.returncode, 0, p.stderr)
        (self.dir / "plan.md").write_text(PLAN.replace("| R-02 | Live (c) | Amendment |",
                                                       "| R-02 | Live (c) | Rewritten |"))
        self.run_ledger("init", "--plan", "plan.md")
        item = self.ledger()["rule:R-02"]
        self.assertEqual(item["outcome"], "refuted")
        self.assertEqual(item["prediction"]["Native feature and fallback"], "Amendment")
        self.run_ledger("init", "--plan", "plan.md", "--rebuild")
        item = self.ledger()["rule:R-02"]
        self.assertEqual((item["outcome"], item["prediction"]["Native feature and fallback"]),
                         ("refuted", "Rewritten"))
        self.assertEqual(self.ledger()["decision:D1"]["origin"], "intake")  # --intake remembered

    def test_refusals(self):
        self.init()
        self.assertNotEqual(self.run_ledger("record", "R-99", "affirmed", "x").returncode, 0)
        self.assertNotEqual(self.run_ledger("record", "R-01", "pending", "x").returncode, 0)
        self.assertNotEqual(self.run_ledger("record", "R-01", "affirmed", "x", "--blind-right", "yes").returncode, 0)
        self.assertEqual(self.ledger()["rule:R-01"]["outcome"], "pending")
        p = subprocess.run([sys.executable, "-I", str(SCRIPT), "report"], cwd=tempfile.gettempdir(),
                           capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)

    def test_report(self):
        self.init()
        self.run_ledger("record", "R-01", "affirmed", "goldens pass")
        self.run_ledger("record", "D3", "modified", "rounded per line", "--blind-right", "yes")
        self.run_ledger("record", "D3", "modified", "later gate, same result")
        self.run_ledger("record", "R-02", "refuted", "90.00", "--path", "fallback", "--skill", "s: c")
        p = self.run_ledger("report")
        self.assertEqual(p.returncode, 0, p.stderr)
        card = (self.dir / "verification/scorecard.md").read_text()
        self.assertIn("| rule | blind | 3 | 1 | 0 | 1 | 0 | 1 |", card)
        self.assertIn("| decision | edited | 1 | 0 | 1 | 0 | 0 | 0 |", card)
        self.assertIn("Excluded (intake or owner): 1.", card)
        self.assertIn("Yes 1, no 0, not recorded 0.", card)
        self.assertIn("| Repo | 1 | 1 |", card)
        self.assertIn("| Repo (inferred) + Live | 1 |", card)
        self.assertIn("**rule:R-02** (blind): refuted. 90.00 Path: fallback.", card)
        self.assertIn("**rule:R-02** (refuted): s: c", card)
        self.assertNotIn("X-01", json.dumps(self.ledger()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
