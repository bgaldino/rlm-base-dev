#!/usr/bin/env python3
"""Offline tests for scripts/ux/ (UX assembly + drift tooling). sf is stubbed."""

import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.ux import _sf, ux_tool  # noqa: E402
from scripts.ux._context import UxContext, UxError, UxOptionError  # noqa: E402
from scripts.ux._deploy import deploy  # noqa: E402
from scripts.ux._flags import (  # noqa: E402
    UX_KNOWN_FLAGS,
    parse_flag_overrides,
    resolve_features,
)
from scripts.ux._retrieve import UxRetriever  # noqa: E402

QUOTE_PAGE = "RLM_Quote_Record_Page.flexipage-meta.xml"


# ── helpers ──────────────────────────────────────────────────────────────────

def _ctx(features=None):
    import logging

    resolved, api_version = resolve_features(REPO_ROOT)
    resolved.update(features or {})
    return UxContext(
        repo_root=REPO_ROOT, features=resolved, api_version=api_version,
        logger=logging.getLogger("test_ux"),
    )


class FakeSf:
    """Stands in for subprocess.run inside scripts.ux._sf; records every call."""

    def __init__(self, payload, on_call=None, stdout=None):
        self.payload = payload
        self.on_call = on_call
        self.stdout = stdout
        self.calls = []

    def __call__(self, cmd, **kwargs):
        self.calls.append((cmd, kwargs))
        if self.on_call:
            self.on_call(cmd)
        out = self.stdout if self.stdout is not None else json.dumps(self.payload)
        return subprocess.CompletedProcess(cmd, 0, stdout=out, stderr="")


def _arg(cmd, flag):
    return cmd[cmd.index(flag) + 1]


@pytest.fixture(scope="module")
def assembled(tmp_path_factory):
    """Assemble the real templates once; tests copy it before mutating."""
    out = tmp_path_factory.mktemp("ux_assembled")
    assert ux_tool.main(["assemble", "--output-path", str(out)]) == 0
    return out


@pytest.fixture
def org_state(assembled, tmp_path):
    dest = tmp_path / "org"
    shutil.copytree(assembled, dest)
    return dest


# ── flags ────────────────────────────────────────────────────────────────────

def test_parse_flag_overrides_accepts_known_flags():
    name = UX_KNOWN_FLAGS[0]
    assert parse_flag_overrides([f"{name}=false"]) == {name: False}
    assert parse_flag_overrides([f"{name}=TRUE"]) == {name: True}


@pytest.mark.parametrize("bad", ["not_a_flag=true", "billing_ui", "=true", "billing_ui=treu", "billing_ui="])
def test_parse_flag_overrides_rejects_bad_input(bad):
    with pytest.raises(UxOptionError):
        parse_flag_overrides([bad])


def test_resolve_features_precedence(tmp_path):
    name = UX_KNOWN_FLAGS[0]
    defaults, _ = resolve_features(REPO_ROOT)
    manifest = tmp_path / "assembly_manifest.json"
    manifest.write_text(json.dumps({"feature_flags": {name: not defaults[name], "bogus": True}}))

    from_manifest, _ = resolve_features(REPO_ROOT, manifest_path=manifest)
    assert from_manifest[name] is (not defaults[name])
    assert "bogus" not in from_manifest

    overridden, _ = resolve_features(REPO_ROOT, {name: defaults[name]}, manifest_path=manifest)
    assert overridden[name] is defaults[name]


def test_flags_command_prints_overrides(capsys):
    name = UX_KNOWN_FLAGS[0]
    assert ux_tool.main(["flags", "--flag", f"{name}=false"]) == 0
    assert json.loads(capsys.readouterr().out)[name] is False


def test_unknown_flag_exits_with_error():
    assert ux_tool.main(["flags", "--flag", "nope=true"]) == ux_tool.EXIT_ERROR


def test_missing_manifest_exits_with_error(tmp_path):
    rc = ux_tool.main(["flags", "--flags-from-manifest", str(tmp_path / "missing.json")])
    assert rc == ux_tool.EXIT_ERROR


# ── assemble + diff ──────────────────────────────────────────────────────────

def test_assemble_writes_manifest(assembled):
    manifest = json.loads((assembled / "assembly_manifest.json").read_text())
    assert manifest["assembled"]
    assert (assembled / "flexipages" / QUOTE_PAGE).exists()


def test_assemble_deploy_needs_target_org(tmp_path):
    rc = ux_tool.main(["assemble", "--output-path", str(tmp_path), "--deploy"])
    assert rc == ux_tool.EXIT_ERROR


@pytest.mark.parametrize("command", ["diff", "writeback"])
def test_missing_org_state_is_an_error(command, tmp_path):
    (tmp_path / "flexipages").mkdir()
    assert ux_tool.main([command, "--output-path", str(tmp_path)]) == ux_tool.EXIT_ERROR
    assert ux_tool.main([command, "--output-path", str(tmp_path / "nope")]) == ux_tool.EXIT_ERROR


@pytest.mark.parametrize("name", ["RLM_Nope.flexipage-meta.xml", "RLM_Nope.layout-meta.xml"])
def test_assemble_unknown_name_is_an_error(name, tmp_path):
    rc = ux_tool.main(["assemble", "--name", name, "--output-path", str(tmp_path)])
    assert rc == ux_tool.EXIT_ERROR
    assert not (tmp_path / "assembly_manifest.json").exists()


def test_writeback_unknown_name_is_an_error(org_state):
    rc = ux_tool.main(["writeback", "--name", "RLM_Nope.flexipage-meta.xml", "--output-path", str(org_state)])
    assert rc == ux_tool.EXIT_ERROR


def test_writeback_name_type_mismatch_is_an_error(org_state):
    rc = ux_tool.main([
        "writeback", "--name", QUOTE_PAGE, "--type", "layouts", "--output-path", str(org_state),
    ])
    assert rc == ux_tool.EXIT_ERROR


def test_diff_against_own_assembly_is_clean(org_state):
    rc = ux_tool.main(["diff", "--output-path", str(org_state), "--fail-on-drift"])
    assert rc == 0
    report = json.loads((org_state / "drift_report.json").read_text())
    assert report["summary"]["drifted"] == 0


def test_diff_detects_removed_region(org_state, tmp_path):
    page = org_state / "flexipages" / QUOTE_PAGE
    xml = page.read_text()
    trimmed, n = re.subn(r"<flexiPageRegions>.*?</flexiPageRegions>\s*", "", xml, count=1, flags=re.S)
    assert n == 1
    page.write_text(trimmed)

    report_file = tmp_path / "report.json"
    rc = ux_tool.main([
        "diff", "--output-path", str(org_state), "--report-file", str(report_file),
        "--fail-on-drift",
    ])
    assert rc == ux_tool.EXIT_DRIFT
    assert json.loads(report_file.read_text())["summary"]["drifted"] == 1
    # Without --fail-on-drift drift is reported but not an error.
    assert ux_tool.main(["diff", "--output-path", str(org_state)]) == 0


# ── retrieve (sf project retrieve start, stubbed) ────────────────────────────

def _retrieve_payload(status="Succeeded", messages=None):
    return {"status": 0, "result": {"status": status, "messages": messages or []}}


def _write_retrieved(pages):
    def on_call(cmd):
        target = Path(_arg(cmd, "--target-metadata-dir")) / "unpackaged" / "flexipages"
        target.mkdir(parents=True, exist_ok=True)
        for name in pages:
            (target / f"{name}.flexipage").write_text(f"<FlexiPage>{name}</FlexiPage>")
    return on_call


def test_retrieve_uses_sf_cli_and_writes_source_names(monkeypatch, tmp_path):
    (tmp_path / "flexipages").mkdir()
    stale = tmp_path / "flexipages" / "RLM_Stale.flexipage-meta.xml"
    stale.write_text("<old/>")
    fake = FakeSf(_retrieve_payload(), on_call=_write_retrieved(["RLM_Quote_Record_Page"]))
    monkeypatch.setattr(_sf.subprocess, "run", fake)

    count = UxRetriever(_ctx(), "my-scratch").run(tmp_path)

    assert count == 1
    assert (tmp_path / "flexipages" / QUOTE_PAGE).read_text() == (
        "<FlexiPage>RLM_Quote_Record_Page</FlexiPage>"
    )
    assert not stale.exists(), "a full retrieve clears stale pages"
    (cmd, kwargs), = fake.calls
    assert cmd[:4] == ["sf", "project", "retrieve", "start"]
    assert _arg(cmd, "--target-org") == "my-scratch"
    assert "--unzip" in cmd and cmd[-1] == "--json"
    assert "FlexiPage:RLM_Quote_Record_Page" in cmd
    assert kwargs["cwd"] == str(REPO_ROOT)
    assert not any("token" in part.lower() for part in cmd)


def test_retrieve_single_page_keeps_other_files(monkeypatch, tmp_path):
    (tmp_path / "flexipages").mkdir()
    other = tmp_path / "flexipages" / "RLM_Order_Record_Page.flexipage-meta.xml"
    other.write_text("<keep/>")
    fake = FakeSf(_retrieve_payload(), on_call=_write_retrieved(["RLM_Quote_Record_Page"]))
    monkeypatch.setattr(_sf.subprocess, "run", fake)

    assert UxRetriever(_ctx(), "my-scratch").run(tmp_path, QUOTE_PAGE) == 1
    assert other.read_text() == "<keep/>"
    cmd = fake.calls[0][0]
    assert [c for c in cmd if c.startswith("FlexiPage:")] == ["FlexiPage:RLM_Quote_Record_Page"]


def test_single_page_retrieve_the_org_lacks_clears_the_stale_copy(monkeypatch, tmp_path):
    (tmp_path / "flexipages").mkdir()
    stale = tmp_path / "flexipages" / QUOTE_PAGE
    stale.write_text("<old/>")
    monkeypatch.setattr(_sf.subprocess, "run", FakeSf(_retrieve_payload(), on_call=_write_retrieved([])))

    assert UxRetriever(_ctx(), "my-scratch").run(tmp_path, QUOTE_PAGE) == 0
    assert not stale.exists()


def test_failed_retrieve_leaves_existing_files(monkeypatch, tmp_path):
    (tmp_path / "flexipages").mkdir()
    existing = tmp_path / "flexipages" / QUOTE_PAGE
    existing.write_text("<keep/>")
    fake = FakeSf({"status": 1, "name": "NamedOrgNotFoundError", "message": "No authorization"})
    monkeypatch.setattr(_sf.subprocess, "run", fake)

    with pytest.raises(UxError, match="NamedOrgNotFoundError"):
        UxRetriever(_ctx(), "nope").run(tmp_path)
    assert existing.read_text() == "<keep/>"


def test_retrieve_rejects_wrong_suffix():
    with pytest.raises(UxOptionError):
        UxRetriever(_ctx(), "my-scratch").run(Path("/tmp"), "RLM_Quote_Record_Page.layout-meta.xml")


def test_retrieve_cli_requires_target_org():
    with pytest.raises(SystemExit):
        ux_tool.main(["retrieve"])


def test_capture_drift_cli(monkeypatch, org_state):
    """capture-drift = retrieve (stubbed: the org returns the assembled pages) then diff."""
    pages = {f.name: f.read_text() for f in (org_state / "flexipages").glob("*.flexipage-meta.xml")}

    def on_call(cmd):
        target = Path(_arg(cmd, "--target-metadata-dir")) / "unpackaged" / "flexipages"
        target.mkdir(parents=True)
        for name, xml in pages.items():
            (target / name.replace("-meta.xml", "")).write_text(xml)

    monkeypatch.setattr(_sf.subprocess, "run", FakeSf(_retrieve_payload(), on_call=on_call))
    rc = ux_tool.main([
        "capture-drift", "--target-org", "my-scratch", "--output-path", str(org_state),
        "--fail-on-drift",
    ])
    assert rc == 0
    report = json.loads((org_state / "drift_report.json").read_text())
    assert report["summary"]["drifted"] == 0
    assert report["summary"]["in_sync"] == len(pages)


# ── deploy (sf project deploy start, stubbed) ────────────────────────────────

def test_deploy_success(monkeypatch, tmp_path):
    fake = FakeSf({"status": 0, "result": {"status": "Succeeded", "numberComponentsDeployed": 3}})
    monkeypatch.setattr(_sf.subprocess, "run", fake)

    result = deploy(tmp_path, "my-scratch", cwd=REPO_ROOT)

    assert result["numberComponentsDeployed"] == 3
    cmd, kwargs = fake.calls[0]
    assert cmd[:4] == ["sf", "project", "deploy", "start"]
    assert _arg(cmd, "--source-dir") == str(tmp_path)
    assert _arg(cmd, "--target-org") == "my-scratch"
    assert kwargs["cwd"] == str(REPO_ROOT)


def test_deploy_reports_component_failures(monkeypatch, tmp_path):
    failure = {"componentType": "FlexiPage", "fullName": "RLM_X", "problem": "bad region"}
    payload = {"status": 1, "result": {"status": "Failed", "details": {"componentFailures": failure}}}
    monkeypatch.setattr(_sf.subprocess, "run", FakeSf(payload))

    with pytest.raises(UxError, match="FlexiPage/RLM_X: bad region"):
        deploy(tmp_path, "my-scratch")


def test_deploy_reports_cli_error(monkeypatch, tmp_path):
    payload = {"status": 1, "name": "MissingPackageDirectoryError", "message": "not in project"}
    monkeypatch.setattr(_sf.subprocess, "run", FakeSf(payload))

    with pytest.raises(UxError, match="MissingPackageDirectoryError"):
        deploy(tmp_path, "my-scratch")


def test_deploy_non_json_output(monkeypatch, tmp_path):
    monkeypatch.setattr(_sf.subprocess, "run", FakeSf(None, stdout="Error: boom"))
    with pytest.raises(UxError, match="non-JSON"):
        deploy(tmp_path, "my-scratch")


def test_deploy_needs_target_and_directory(tmp_path):
    with pytest.raises(UxOptionError):
        deploy(tmp_path, "")
    with pytest.raises(UxOptionError):
        deploy(tmp_path / "missing", "my-scratch")


def test_sf_missing(monkeypatch, tmp_path):
    def raise_missing(cmd, **kwargs):
        raise FileNotFoundError("sf")

    monkeypatch.setattr(_sf.subprocess, "run", raise_missing)
    with pytest.raises(UxError, match="sf command not found"):
        deploy(tmp_path, "my-scratch")


# ── writeback (against a temp copy of templates/, never the real one) ───────

PERSONA_PATCH = Path("templates/flexipages/patches/personas/RLM_Quote_Record_Page.yml")
PERSONA_RULE = re.compile(
    r"\s*<visibilityRule>\s*<criteria>\s*<leftValue>\{!\$User\.Profile\.Name\}</leftValue>"
    r"\s*<operator>NE</operator>\s*<rightValue>RLM Sales Representative</rightValue>"
    r"\s*</criteria>\s*</visibilityRule>"
)


def _snapshot(root):
    return {
        p.relative_to(root): p.read_bytes()
        for p in (root / "templates").rglob("*") if p.is_file()
    }


@pytest.fixture(scope="module")
def pristine_repo(tmp_path_factory):
    """templates/ + cumulusci.yml and their assembled output, built once."""
    root = tmp_path_factory.mktemp("ux_repo") / "repo"
    root.mkdir()
    shutil.copytree(REPO_ROOT / "templates", root / "templates")
    shutil.copy2(REPO_ROOT / "cumulusci.yml", root / "cumulusci.yml")
    assert ux_tool.main(["assemble", "--repo-root", str(root), "--output-path", str(root / "out")]) == 0
    return root


@pytest.fixture
def repo_copy(pristine_repo, tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(pristine_repo, root)
    return root, root / "out"


def _apply_drift(root, out):
    return ux_tool.main([
        "apply-drift", "--repo-root", str(root), "--output-path", str(out),
        "--no-backup", "--fail-on-drift",
    ])


def test_writeback_dry_run_changes_nothing(repo_copy):
    root, out = repo_copy
    before = _snapshot(root)
    assert ux_tool.main(["writeback", "--repo-root", str(root), "--output-path", str(out)]) == 0
    assert _snapshot(root) == before


def test_apply_drift_without_drift_leaves_templates_unchanged(repo_copy):
    """Regression: a no-op apply used to bake the persona visibilityRule into the
    base and delete its patch file (insert_after_xml of a bare element)."""
    root, out = repo_copy
    before = _snapshot(root)
    assert _apply_drift(root, out) == 0
    assert _snapshot(root) == before


def test_apply_drift_removes_dropped_insert_after_xml_patch(repo_copy):
    root, out = repo_copy
    page = out / "flexipages" / QUOTE_PAGE
    xml, n = PERSONA_RULE.subn("", page.read_text(), count=1)
    assert n == 1
    page.write_text(xml)
    base = root / "templates" / "flexipages" / "base" / QUOTE_PAGE
    base_before = base.read_bytes()

    assert _apply_drift(root, out) == 0
    assert not (root / PERSONA_PATCH).exists()
    assert base.read_bytes() == base_before


def test_apply_drift_reports_drift_writeback_cannot_resolve(repo_copy):
    """A page the templates produce but the org lacks stays templates_only. The
    diff must see the org state, not the reassembled output (which has the page)."""
    root, out = repo_copy
    (out / "flexipages" / QUOTE_PAGE).unlink()

    assert _apply_drift(root, out) == ux_tool.EXIT_DRIFT
    report = json.loads((out / "drift_report.json").read_text())
    assert report["summary"]["templates_only"] == 1
    assert (out / "flexipages" / QUOTE_PAGE).exists(), "output is reassembled afterwards"


def test_apply_drift_leaves_layout_templates_alone(repo_copy):
    """Regression: retrieve fetches no layouts, so apply-drift used to write the
    assembled (here constraints=false) layouts over the feature layout templates."""
    root, out = repo_copy
    assert ux_tool.main([
        "assemble", "--repo-root", str(root), "--output-path", str(out),
        "--flag", "constraints=false",
    ]) == 0
    layouts = {p: p.read_bytes() for p in (root / "templates" / "layouts").rglob("*") if p.is_file()}
    _apply_drift(root, out)
    assert {p: p.read_bytes() for p in layouts} == layouts


def test_apply_drift_drops_insert_action_patch_the_org_lacks(repo_copy):
    """An org without any of a patch's actions loses that insert_action patch."""
    root, out = repo_copy
    patch = root / "templates" / "flexipages" / "patches" / "approvals" / QUOTE_PAGE.replace(".flexipage-meta.xml", ".yml")
    page = out / "flexipages" / QUOTE_PAGE
    xml, n = re.subn(
        r"\s*<valueListItems>\s*<value>Quote\.RLM_Submit_for_Approval</value>\s*</valueListItems>",
        "", page.read_text(),
    )
    assert n == 1
    page.write_text(xml)

    _apply_drift(root, out)
    import yaml

    remaining = yaml.safe_load(patch.read_text())["patches"]
    assert not [p for p in remaining if p["type"] == "insert_action"]


def test_reverse_insert_action_keeps_template_actions_and_targets_anchor_list():
    from scripts.ux._writeback import _reverse_insert_action

    ns = "http://soap.sforce.com/2006/04/metadata"

    def action_list(*names):
        items = "".join(f"<valueListItems><value>{n}</value></valueListItems>" for n in names)
        return (
            "<componentInstanceProperties><name>actionNames</name>"
            f"<valueList>{items}</valueList></componentInstanceProperties>"
        )

    org = ET.fromstring(
        f'<FlexiPage xmlns="{ns}"><a>{action_list("Other", "A")}</a>'
        f'<b>{action_list("Anchor", "A", "B")}</b></FlexiPage>'
    )
    patch = {"after": "Anchor", "actions": ["A", "B"]}

    # The template already has B, so the forward patch never inserted it.
    assert _reverse_insert_action(org, patch, keep={"B"}) is True
    values = [v.text for v in org.iter(f"{{{ns}}}value")]
    assert values == ["Other", "A", "Anchor", "B"]
    assert _reverse_insert_action(org, patch, keep={"B"}) is False


def test_insert_action_keeps_dict_entries():
    from scripts.ux._writeback import UxWriteback

    ns = "http://soap.sforce.com/2006/04/metadata"
    org = ET.fromstring(
        f'<FlexiPage xmlns="{ns}"><itemInstances><componentInstance>'
        "<componentInstanceProperties><name>actionNames</name><valueList>"
        "<valueListItems><value>Keep</value></valueListItems>"
        "</valueList></componentInstanceProperties>"
        "</componentInstance></itemInstances></FlexiPage>"
    )
    keep = {"name": "Keep", "visibility": [{"leftValue": "x", "operator": "EQUAL", "rightValue": "y"}]}
    patch = {"actions": [keep, "Gone"]}
    assert UxWriteback._extract_insert_actions(None, org, org, patch) == [keep]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
