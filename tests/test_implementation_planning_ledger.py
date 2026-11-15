"""Tests for .cursor/skills/implementation-planning/scripts/ledger.py (standard library only).

    python tests/test_implementation_planning_ledger.py

Builds a synthetic plan and blind plan shaped like the template, then checks every
origin, recording, re-init and the scorecard, and that each refusal can happen.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = (Path(__file__).resolve().parent.parent
          / ".cursor/skills/implementation-planning/scripts/ledger.py")

BLIND = """# Example on Revenue Cloud — Build Plan

## 1. Goal and definition of done

| # | Step | Verify |
|---|---|---|
| 1 | Price | Pricing-1 |

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

| Spike | Rules | Expected |
|---|---|---|
| X-01 | R-02 | ignored |

| # | Case | Decision |
|---|---|---|
| Pricing-3 | Round | D2 |

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
        (self.dir / "plan.md").write_text(PLAN, encoding="utf-8")
        (self.dir / "blind.md").write_text(BLIND, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_ledger(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], cwd=self.dir,
                              capture_output=True, text=True)

    def ledger(self):
        return json.loads((self.dir / "verification/ledger.json").read_text(encoding="utf-8"))["items"]

    def init(self, *extra):
        p = self.run_ledger("init", "--plan", "plan.md", "--blind", "blind.md", "--intake", "D1", *extra)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p

    def fresh_init(self):
        """init on a new ledger, so a row can't be there only because an earlier init kept it."""
        (self.dir / "verification/ledger.json").unlink(missing_ok=True)
        return self.init()

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
        self.run_ledger("init", "--plan", "plan.md")  # a plain re-init keeps it
        self.assertEqual(self.ledger()["decision:D2"]["origin"], "owner")
        self.run_ledger("init", "--plan", "plan.md", "--owner", "D1")  # intake moved to owner
        self.assertEqual(self.ledger()["decision:D1"]["origin"], "owner")
        self.run_ledger("report")
        card = (self.dir / "verification/scorecard.md").read_text(encoding="utf-8")
        self.assertIn("Excluded (intake or owner): 2.", card)
        self.run_ledger("truth")
        tr = json.loads((self.dir / "verification/truth.json").read_text(encoding="utf-8"))
        self.assertNotIn("decision:D2", tr)

    def test_blind_plan_is_remembered_across_inits(self):
        self.init()
        self.run_ledger("init", "--plan", "plan.md", "--owner", "D2")
        items = self.ledger()
        self.assertEqual((items["decision:D3"]["origin"], items["decision:D4"]["origin"]), ("edited", "added"))
        self.assertIn("At the end", items["decision:D3"]["blind_prediction"])

    def test_blind_path_is_relative_and_survives_a_moved_folder(self):
        self.init()
        meta = json.loads((self.dir / "verification/ledger.json").read_text(encoding="utf-8"))["meta"]
        self.assertEqual((meta["blind"], meta["plan"]), (str(Path("..") / "blind.md"), str(Path("..") / "plan.md")))
        moved = self.dir / "moved"
        moved.mkdir()
        for name in ("plan.md", "blind.md", "verification"):
            src = self.dir / name
            (shutil.copytree if src.is_dir() else shutil.copy)(src, moved / name)
        (self.dir / "blind.md").unlink()  # only the moved copy can answer now

        def run_moved():
            return subprocess.run([sys.executable, "-I", str(SCRIPT), "init", "--plan", "plan.md"],
                                  cwd=moved, capture_output=True, text=True)
        p = run_moved()
        self.assertEqual(p.returncode, 0, p.stderr)
        items = json.loads((moved / "verification/ledger.json").read_text(encoding="utf-8"))["items"]
        self.assertEqual(items["decision:D3"]["origin"], "edited")
        self.assertIn("At the end", items["decision:D3"]["blind_prediction"])
        (moved / "blind.md").unlink()
        p = run_moved()
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("pass --blind", p.stderr)

    def test_rebuild_drops_only_unrecorded_rows_gone_from_the_plan(self):
        self.init()
        self.run_ledger("record", "D3", "affirmed", "x")
        (self.dir / "plan.md").write_text(PLAN.replace("| D2 | Which band edge? | Inclusive |\n", "")
                                          .replace("| D3 | Round where? | Per line |\n", ""), encoding="utf-8")
        self.run_ledger("init", "--plan", "plan.md")
        self.assertIn("decision:D2", self.ledger())
        p = self.run_ledger("init", "--plan", "plan.md", "--rebuild")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn("decision:D2", self.ledger())
        self.assertEqual(self.ledger()["decision:D3"]["outcome"], "affirmed")

    def test_unknown_intake_id_warns_and_missing_plan_fails(self):
        p = self.init("--intake", "R-01")
        self.assertIn("not decision rows", p.stderr)
        self.assertIn("R-01", p.stderr)
        p = self.run_ledger("init", "--plan", "missing.md")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("cannot read", p.stderr)

    def test_fenced_tables_are_not_read_as_rows(self):
        fence = ("```bash\n| Spike | Rules | Must hit | Smallest case | Read first |\n|---|---|---|---|---|\n"
                 "| X-9 | R-02 | 1 | a | b |\n```\n\n")
        plan = PLAN.replace("| Spike | Rules |", fence + "| Spike | Rules |", 1)
        (self.dir / "plan.md").write_text(plan, encoding="utf-8")
        p = self.init()
        self.assertEqual(sorted(k for k in self.ledger() if k.startswith("spike:")), ["spike:S-1"])
        dfence = "```\n| # | Decision |\n|---|---|\n| D9 | fenced |\n```\n\n"
        (self.dir / "plan.md").write_text(PLAN.replace("## 2. Decisions\n", "## 2. Decisions\n\n" + dfence), encoding="utf-8")
        self.init()
        self.assertIn("decision:D2", self.ledger())
        self.assertNotIn("decision:D9", self.ledger())
        tilde = "~~~\n| # | Decision |\n|---|---|\n| D9 | fenced |\n~~~\n\n"
        (self.dir / "plan.md").write_text(PLAN.replace("## 2. Decisions\n", "## 2. Decisions\n\n" + tilde), encoding="utf-8")
        self.init()
        self.assertNotIn("decision:D9", self.ledger())

    def test_fence_length_and_unclosed_fence(self):
        nested = "````md\n```\n| # | Decision |\n|---|---|\n| D9 | fenced |\n```\n````\n\n"
        (self.dir / "plan.md").write_text(PLAN.replace("## 2. Decisions\n", "## 2. Decisions\n\n" + nested),
                                          encoding="utf-8")
        self.init()
        self.assertIn("decision:D2", self.ledger())
        self.assertNotIn("decision:D9", self.ledger())
        (self.dir / "plan.md").write_text(PLAN.replace("**P3 Catalog", "```\n**P3 Catalog"), encoding="utf-8")
        p = self.run_ledger("init", "--plan", "plan.md")
        self.assertIn("never closed", p.stderr)
        self.assertIn("opened at line", p.stderr)

    def test_row_syntax_variants(self):
        plan = (PLAN.replace("|---|---|---|---|", "|-|-|-|-|")
                    .replace("| R-03 | Repo (inferred); Live (b) on renewal | Formula | exact |",
                             "| R-03 | Repo | Formula ||"))
        (self.dir / "plan.md").write_text(plan, encoding="utf-8")
        self.init()
        pred = self.ledger()["rule:R-03"]["prediction"]
        self.assertEqual(pred["Exact vs source?"], "")
        self.assertEqual(pred["Native feature and fallback"], "Formula")

    def test_missing_table_error_names_the_cause(self):
        (self.dir / "plan.md").write_text(PLAN.replace("| Rule | Decided by |", "| ID | Decided by |"), encoding="utf-8")
        p = self.run_ledger("init", "--plan", "plan.md")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("starts with 'Rule'", p.stderr)

    def test_parser_edge_cases(self):
        # a rule after a table with no blank line before a horizontal rule is kept
        plan = PLAN.replace("| R-03 | Repo (inferred); Live (b) on renewal | Formula | exact |\n",
                            "| R-03 | Repo (inferred); Live (b) on renewal | Formula | exact |\n---\n")
        (self.dir / "plan.md").write_text(plan, encoding="utf-8")
        self.fresh_init()
        self.assertIn("rule:R-03", self.ledger())
        # a row with too many cells warns instead of silently losing its columns
        plan = PLAN.replace("| R-01 | **Repo** |", "| R-01 | **Repo** | extra |")
        (self.dir / "plan.md").write_text(plan, encoding="utf-8")
        p = self.fresh_init()
        self.assertIn("R-01 has 5 cells under 4 columns", p.stderr)
        # inline triple-backtick code is not a fence
        plan = PLAN.replace("What D2 changes:", "```x``` is inline.\n\nWhat D2 changes:")
        (self.dir / "plan.md").write_text(plan, encoding="utf-8")
        p = self.fresh_init()
        self.assertNotIn("never closed", p.stderr)
        self.assertIn("rule:R-03", self.ledger())

    def test_bold_header_cells(self):
        plan = (PLAN.replace("| Spike | Rules | Must hit |", "| **Spike** | Rules | **Must hit** |")
                .replace("| Rule | Decided by |", "| `Rule` | Decided by |")
                .replace("| # | Decision |", "| **#** | Decision |"))
        (self.dir / "plan.md").write_text(plan, encoding="utf-8")
        self.init()
        self.assertTrue({"decision:D2", "rule:R-01", "spike:S-1"} <= set(self.ledger()))

    def test_short_row_pads_to_the_header(self):
        plan = PLAN.replace("| R-03 | Repo (inferred); Live (b) on renewal | Formula | exact |\n",
                            "| R-03 | Repo (inferred); Live (b) on renewal | Formula | exact |\n| R-04 | Live (c) | Formula |\n")
        (self.dir / "plan.md").write_text(plan, encoding="utf-8")
        p = self.init()
        self.assertNotIn("cells under", p.stderr)
        self.assertEqual(self.ledger()["rule:R-04"]["prediction"]["Decided by"], "Live (c)")
        self.assertEqual(self.ledger()["rule:R-04"]["prediction"]["Exact vs source?"], "")
        # the same row written padded is not a change on a plain re-init, nor from the blind plan
        (self.dir / "plan.md").write_text(plan.replace("| R-04 | Live (c) | Formula |",
                                                       "| R-04 | Live (c) | Formula | |"), encoding="utf-8")
        p = self.run_ledger("init", "--plan", "plan.md")
        self.assertNotIn("changed in the plan", p.stderr)
        (self.dir / "blind.md").write_text(plan, encoding="utf-8")
        self.init("--rebuild")
        self.assertEqual(self.ledger()["rule:R-04"]["origin"], "blind")

    def test_spike_tables_anywhere_and_escaped_pipes(self):
        late = ("\n| Spike | Rules | Must hit | Smallest case | Read first |\n|---|---|---|---|---|\n"
                "| S-2 Renewal value | R-02 | `a\\b\\|\\bb` | One line | `x` |\n")
        (self.dir / "plan.md").write_text(PLAN + late, encoding="utf-8")
        self.init()
        self.assertEqual(self.ledger()["spike:S-2"]["prediction"]["Must hit"], "`a\\b|\\bb`")
        self.assertNotIn("G-1", json.dumps(self.ledger()))  # a "Check | Must hit" table is no spike

    def test_rules_in_several_tables(self):
        (self.dir / "plan.md").write_text(PLAN.replace(
            "| R-02 | Live (c) | Amendment | exact |\n",
            "\nPricing rules:\n\n| Rule | Decided by | Native feature and fallback | Exact vs source? |\n"
            "|---|---|---|---|\n| R-02 | Live (c) | Amendment | exact |\n"), encoding="utf-8")
        self.init()
        self.assertEqual(sorted(k for k in self.ledger() if k.startswith("rule:")),
                         ["rule:R-01", "rule:R-02", "rule:R-03"])

    def test_intake_origin_is_kept_until_rebuild(self):
        self.run_ledger("init", "--plan", "plan.md", "--intake", "D1,D4")
        self.run_ledger("record", "D4", "affirmed", "x")
        (self.dir / "plan.md").write_text(PLAN.replace("| D4 | Added later? | Yes |\n", ""), encoding="utf-8")
        p = self.run_ledger("init", "--plan", "plan.md", "--rebuild", "--intake", "D1,D4")
        self.assertNotIn("ignored", p.stderr)
        self.run_ledger("init", "--plan", "plan.md")  # no list: the origin is kept
        item = self.ledger()["decision:D4"]
        self.assertEqual((item["origin"], item["outcome"]), ("intake", "affirmed"))
        self.run_ledger("init", "--plan", "plan.md", "--rebuild", "--intake", "D1")  # a mistaken D4 undone
        item = self.ledger()["decision:D4"]
        self.assertEqual((item["origin"], item["outcome"]), ("blind", "affirmed"))

    def test_list_naming_a_row_that_rebuild_drops_is_warned(self):
        self.init()
        (self.dir / "plan.md").write_text(PLAN.replace("| D4 | Added later? | Yes |\n", ""), encoding="utf-8")
        p = self.run_ledger("init", "--plan", "plan.md", "--rebuild", "--intake", "D4")
        self.assertIn("ignored: D4", p.stderr)
        self.assertNotIn("decision:D4", self.ledger())

    def test_duplicate_warnings_name_the_file(self):
        (self.dir / "blind.md").write_text(BLIND.replace("| R-02 |", "| R-01 | **Repo** | Volume tiers | exact |\n| R-02 |"),
                                           encoding="utf-8")
        p = self.run_ledger("init", "--plan", "plan.md", "--blind", "blind.md")
        self.assertIn("blind.md: R-01 appears twice", p.stderr)

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
        self.assertEqual(self.run_ledger("init", "--plan", "plan.md", "--intake", "D2-D1").returncode, 1)

    def test_zero_padded_range(self):
        spec = importlib.util.spec_from_file_location("ledger", SCRIPT)
        ledger = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ledger)
        self.assertEqual(ledger.id_set("D08-D10,D2"), {"D08", "D09", "D10", "D2"})

    def test_non_ascii_evidence_round_trips(self):
        self.init()
        p = self.run_ledger("record", "R-01", "affirmed", "margin ≥ 20% — goldens pass")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(self.ledger()["rule:R-01"]["evidence"][-1]["evidence"],
                         "margin ≥ 20% — goldens pass")
        raw = (self.dir / "verification/ledger.json").read_text(encoding="utf-8")
        self.assertIn("margin ≥ 20% — goldens pass", raw)  # written as the characters, not \\u escapes
        self.assertFalse((self.dir / "verification/ledger.json.tmp").exists())

    def test_record_and_reinit_keep_outcomes_and_frozen_prediction(self):
        self.init()
        p = self.run_ledger("record", "R-02", "refuted", "org x: 90.00",
                            "--skill", "asset-lifecycle-changes: claim")
        self.assertEqual(p.returncode, 0, p.stderr)
        (self.dir / "plan.md").write_text(PLAN.replace("| R-02 | Live (c) | Amendment |",
                                                       "| R-02 | Live (c) | Rewritten |"), encoding="utf-8")
        p = self.run_ledger("init", "--plan", "plan.md")
        self.assertIn("rule:R-02 changed in the plan", p.stderr)
        item = self.ledger()["rule:R-02"]
        self.assertEqual(item["outcome"], "refuted")
        self.assertEqual(item["prediction"]["Native feature and fallback"], "Amendment")
        p = self.run_ledger("init", "--plan", "plan.md", "--rebuild")
        self.assertIn("rule:R-02 prediction replaced", p.stderr)
        item = self.ledger()["rule:R-02"]
        self.assertEqual((item["outcome"], item["prediction"]["Native feature and fallback"]),
                         ("refuted", "Rewritten"))
        self.assertEqual(self.ledger()["decision:D1"]["origin"], "blind")  # no list given now

    def test_refusals(self):
        self.init()
        p = self.run_ledger("record", "R-99", "affirmed", "x")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("unknown id R-99", p.stderr)
        p = self.run_ledger("init", "--plan", "plan.md", "--intake", "D1-D2", "--owner", "D2")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("in both --intake and --owner: D2", p.stderr)
        self.assertNotEqual(self.run_ledger("record", "R-01", "pending", "x").returncode, 0)
        path = self.dir / "verification/ledger.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["items"]["spike:D2"] = dict(data["items"]["decision:D2"], kind="spike")
        path.write_text(json.dumps(data), encoding="utf-8")
        p = self.run_ledger("record", "D2", "affirmed", "x")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ambiguous", p.stderr)
        self.assertEqual(self.run_ledger("record", "decision:D2", "affirmed", "x").returncode, 0)
        empty = self.dir / "empty"
        empty.mkdir()
        p = subprocess.run([sys.executable, "-I", str(SCRIPT), "report"], cwd=empty,
                           capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("run init first", p.stderr)
        (self.dir / "verification/ledger.json").write_text("{", encoding="utf-8")
        p = self.run_ledger("report")
        self.assertIn("not valid JSON", p.stderr)

    def test_hyphenated_decided_by_header_is_scored(self):
        (self.dir / "plan.md").write_text(PLAN.replace("| Rule | Decided by |", "| Rule | Decided-by |"), encoding="utf-8")
        self.init()
        self.run_ledger("report")
        self.assertNotIn("(none)", (self.dir / "verification/scorecard.md").read_text(encoding="utf-8"))

    def test_partly_bold_decided_by_cell_keeps_its_label(self):
        plan = (PLAN.replace("| R-01 | **Repo** |", "| R-01 | **Repo** (inferred) |")
                .replace("| Repo (inferred); Live (b) on renewal |", "| Live (b) |"))
        (self.dir / "plan.md").write_text(plan, encoding="utf-8")
        self.init()
        self.run_ledger("report")
        self.assertIn("| Repo (inferred) |", (self.dir / "verification/scorecard.md").read_text(encoding="utf-8"))

    def test_labels_join_in_one_order(self):
        plan = PLAN.replace("| Repo (inferred); Live (b) on renewal |", "| Live (b) on renewal; Repo (inferred) |")
        (self.dir / "plan.md").write_text(plan, encoding="utf-8")
        self.init()
        self.run_ledger("report")
        self.assertIn("| Repo (inferred) + Live | 1 |", (self.dir / "verification/scorecard.md").read_text(encoding="utf-8"))

    def test_report(self):
        self.init()
        self.run_ledger("record", "R-01", "affirmed", "goldens pass")
        self.run_ledger("record", "D3", "modified", "rounded per line")
        self.run_ledger("record", "D3", "modified", "later gate, same result")
        self.run_ledger("record", "R-02", "refuted", "90.00", "--path", "fallback", "--skill", "s: c")
        self.run_ledger("record", "R-03", "affirmed", "first look")
        self.run_ledger("record", "R-03", "modified", "second look")
        p = self.run_ledger("report")
        self.assertEqual(p.returncode, 0, p.stderr)
        card = (self.dir / "verification/scorecard.md").read_text(encoding="utf-8")
        self.assertIn("| rule | blind | 3 | 1 | 1 | 1 | 0 | 0 |", card)  # R-03: the latest record wins
        self.assertIn("| decision | edited | 1 | 0 | 1 | 0 | 0 | 0 |", card)
        self.assertIn("Excluded (intake or owner): 1.", card)
        self.assertIn("| Repo | 1 | 1 |", card)
        self.assertIn("| Repo (inferred) + Live | 1 |", card)
        self.assertIn("**rule:R-02** (blind): refuted. 90.00 Path: fallback.", card)
        self.assertIn("**rule:R-02** (refuted): s: c", card)
        self.assertIn("second look", card)
        self.assertNotIn("first look", card)
        self.assertIn("later gate, same result", card)
        self.assertNotIn("rounded per line", card)
        self.assertEqual([k for k in self.ledger() if k.startswith("spike:")], ["spike:S-1"])

    def test_truth_and_score(self):
        self.init()
        self.run_ledger("record", "R-01", "affirmed", "ok")
        self.run_ledger("record", "R-02", "refuted", "90.00", "--path", "fallback",
                        "--skill", "s: c")
        self.run_ledger("record", "R-03", "modified", "per line")
        self.run_ledger("record", "S-1", "inconclusive", "not run")
        self.run_ledger("record", "D1", "affirmed", "intake, excluded")
        p = self.run_ledger("truth")
        self.assertEqual(p.returncode, 0, p.stderr)
        tr = json.loads((self.dir / "verification/truth.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(tr), ["rule:R-01", "rule:R-02", "rule:R-03", "spike:S-1"])
        self.assertEqual(tr["rule:R-02"]["path_taken"], ["fallback"])
        self.assertEqual(tr["rule:R-02"]["measured"], ["90.00"])
        self.assertEqual(tr["rule:R-02"]["skill_claim"], ["s: c"])
        self.assertEqual(tr["rule:R-01"]["skill_claim"], [])

        judged = {"rule:R-01": {"label": "hit"}, "rule:R-02": {"label": "hedged", "where": "S-9"},
                  "rule:R-03": {"label": "hit"},
                  "spike:S-1": {"label": "absent", "why": "dropped"}}
        (self.dir / "j.json").write_text(json.dumps(judged), encoding="utf-8")
        p = self.run_ledger("score", "j.json", "r2")
        self.assertEqual(p.returncode, 0, p.stderr)
        out = (self.dir / "verification/regen-scores.md").read_text(encoding="utf-8")
        self.assertIn("| measured plan (baseline) | 1 | 1 | 2 | 0 | 2/4 |", out)
        self.assertIn("| r2 | 2 | 1 | 0 | 1 | 3/4 |", out)
        self.assertIn("**spike:S-1** (spike, was inconclusive): absent", out)
        judged["rule:R-01"]["label"] = "miss"
        (self.dir / "j.json").write_text(json.dumps(judged), encoding="utf-8")
        p = self.run_ledger("score", "j.json", "r2")
        self.assertEqual(p.returncode, 0, p.stderr)
        out = (self.dir / "verification/regen-scores.md").read_text(encoding="utf-8")
        self.assertEqual(out.count("## r2"), 1)
        self.assertIn("| r2 | 1 | 1 | 1 | 1 | 2/4 |", out)

    def test_score_refuses_incomplete_or_bad_judgments(self):
        self.init()
        self.run_ledger("record", "R-01", "affirmed", "ok")
        p = self.run_ledger("score", "j.json", "r2")
        self.assertIn("run truth first", p.stderr)
        self.run_ledger("truth")
        (self.dir / "j.json").write_text(json.dumps({"rule:R-02": {"label": "hit"}}), encoding="utf-8")
        p = self.run_ledger("score", "j.json", "r2")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("missing ['rule:R-01']", p.stderr)
        (self.dir / "j.json").write_text(json.dumps({"rule:R-01": {"label": "hit"}, "rule:R-09": {"label": "hit"}}),
                                         encoding="utf-8")
        p = self.run_ledger("score", "j.json", "r2")
        self.assertIn("extra ['rule:R-09']", p.stderr)
        (self.dir / "j.json").write_text(json.dumps([{"label": "hit"}]), encoding="utf-8")
        p = self.run_ledger("score", "j.json", "r2")
        self.assertIn("expected a JSON object", p.stderr)
        (self.dir / "j.json").write_text(json.dumps({"rule:R-01": {"label": "close"}}), encoding="utf-8")
        p = self.run_ledger("score", "j.json", "r2")
        self.assertIn("bad labels", p.stderr)
        self.assertFalse((self.dir / "verification/regen-scores.md").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
