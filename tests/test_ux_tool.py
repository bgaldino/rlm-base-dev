#!/usr/bin/env python3
"""Offline tests for scripts/ux/ (UX assembly + drift tooling). sf is stubbed."""

import copy
import json
import logging
import re
import shutil
import subprocess
import sys
import types
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
from scripts.ux._retrieve import retrieve  # noqa: E402

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
    manifest.write_text(json.dumps({"feature_flags": {**defaults, name: not defaults[name], "bogus": True}}))

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


def _features_for(argv):
    import logging

    args = ux_tool._build_parser().parse_args(argv)
    return ux_tool._make_context(args, logging.getLogger("test_ux")).features


def test_org_commands_default_to_manifest_flags(tmp_path):
    name = UX_KNOWN_FLAGS[0]
    defaults, _ = resolve_features(REPO_ROOT)
    out = ["--output-path", str(tmp_path)]
    assert _features_for(["diff", *out])[name] is defaults[name], "no manifest: cumulusci.yml"

    (tmp_path / "assembly_manifest.json").write_text(
        json.dumps({"feature_flags": {**defaults, name: not defaults[name]}})
    )
    for command in sorted(ux_tool.MANIFEST_COMMANDS):
        extra = ["--target-org", "x"] if command in ("retrieve", "capture-drift") else []
        assert _features_for([command, *out, *extra])[name] is (not defaults[name]), command
    assert _features_for(["diff", *out, "--flag", f"{name}={defaults[name]}"])[name] is defaults[name]
    assert _features_for(["assemble", *out])[name] is defaults[name], "assemble ignores the manifest"


@pytest.mark.parametrize("content", [
    "{not json", "[]", '{"feature_flags": true}', '{"feature_flags": []}',
    '{"feature_flags": false}', '{"feature_flags": null}', '{"partial": true}', "{}",
])
def test_corrupt_manifest_exits_with_error(tmp_path, content):
    (tmp_path / "flexipages").mkdir()
    (tmp_path / "assembly_manifest.json").write_text(content)
    assert ux_tool.main(["diff", "--output-path", str(tmp_path)]) == ux_tool.EXIT_ERROR


@pytest.mark.parametrize("value", ["treu", None, 2, [], "yes"])
def test_manifest_flag_values_must_be_boolean(tmp_path, value):
    """An unrecognized value must not silently read as false."""
    defaults, _ = resolve_features(REPO_ROOT)
    name = UX_KNOWN_FLAGS[0]
    manifest = tmp_path / "assembly_manifest.json"
    manifest.write_text(json.dumps({"feature_flags": {**defaults, name: value}}))
    if value == "yes":
        assert resolve_features(REPO_ROOT, manifest_path=manifest)[0][name] is True
        return
    with pytest.raises(UxOptionError, match=name):
        resolve_features(REPO_ROOT, manifest_path=manifest)


def test_manifest_missing_a_known_flag_is_rejected(tmp_path):
    """A missing flag must not silently take its cumulusci.yml default."""
    defaults, _ = resolve_features(REPO_ROOT)
    name = UX_KNOWN_FLAGS[0]
    manifest = tmp_path / "assembly_manifest.json"
    manifest.write_text(json.dumps({"feature_flags": {k: v for k, v in defaults.items() if k != name}}))

    with pytest.raises(UxOptionError, match=name):
        resolve_features(REPO_ROOT, manifest_path=manifest)
    features, _ = resolve_features(REPO_ROOT, {name: False}, manifest_path=manifest)
    assert features[name] is False


def test_partial_assemble_with_other_flags_marks_manifest_partial(tmp_path):
    """A --type/--name run leaves the flexipages from the previous run, so its
    flags must not become the drift commands' flags unless they match."""
    name = UX_KNOWN_FLAGS[0]
    defaults, _ = resolve_features(REPO_ROOT)
    out = ["--output-path", str(tmp_path)]
    manifest = tmp_path / "assembly_manifest.json"

    assert ux_tool.main(["assemble", *out]) == 0
    assert ux_tool.main(["assemble", "--type", "layouts", *out]) == 0
    assert "partial" not in json.loads(manifest.read_text()), "same flags: still trusted"

    assert ux_tool.main([
        "assemble", "--type", "layouts", *out, "--flag", f"{name}={not defaults[name]}",
    ]) == 0
    assert json.loads(manifest.read_text())["partial"] is True
    assert ux_tool.main(["diff", *out]) == ux_tool.EXIT_ERROR

    assert ux_tool.main(["assemble", *out]) == 0
    assert "partial" not in json.loads(manifest.read_text())


def test_filtered_assemble_deploys_only_what_it_wrote(monkeypatch, tmp_path):
    """After a --type/--name assemble, everything else in the output is left
    over from older runs, so deploy sends only the files the last run wrote."""
    fake = FakeSf({"status": 0, "result": {"status": "Succeeded"}})
    monkeypatch.setattr(_sf.subprocess, "run", fake)
    out = ["--output-path", str(tmp_path)]
    deploy_cmd = ["deploy", *out, "-o", "x"]

    assert ux_tool.main(["assemble", *out]) == 0
    assert ux_tool.main(deploy_cmd) == 0
    assert _arg(fake.calls[-1][0], "--source-dir") == str(tmp_path), "full run: whole directory"

    for selection in (["--type", "flexipages"], ["--name", "RLM_Quote_Record_Page.flexipage-meta.xml"]):
        assert ux_tool.main(["assemble", *selection, *out]) == 0
        assert ux_tool.main(deploy_cmd) == 0
        cmd = fake.calls[-1][0]
        dirs = [cmd[i + 1] for i, a in enumerate(cmd) if a == "--source-dir"]
        assert dirs and all("/flexipages/" in d for d in dirs), selection
        if selection[0] == "--name":
            assert dirs == [str(tmp_path / "flexipages" / selection[1])]


def test_deploy_refuses_an_incomplete_assembly(monkeypatch, tmp_path):
    """An assemble that fails after clearing the output must not leave the
    previous manifest vouching for it."""
    from scripts.ux import _assemble

    fake = FakeSf({"status": 0, "result": {"status": "Succeeded"}})
    monkeypatch.setattr(_sf.subprocess, "run", fake)
    out = ["--output-path", str(tmp_path)]
    assert ux_tool.main(["assemble", *out]) == 0

    def boom(*args, **kwargs):
        raise UxError("malformed template")

    monkeypatch.setattr(_assemble.UxAssembler, "_assemble_layouts", boom)
    assert ux_tool.main(["assemble", *out]) == ux_tool.EXIT_ERROR
    assert ux_tool.main(["deploy", *out, "-o", "x"]) == ux_tool.EXIT_ERROR
    assert ux_tool.main(["diff", *out]) == ux_tool.EXIT_ERROR
    assert not fake.calls


# ── assemble + diff ──────────────────────────────────────────────────────────

def test_assemble_writes_manifest(assembled):
    manifest = json.loads((assembled / "assembly_manifest.json").read_text())
    assert manifest["assembled"]
    assert (assembled / "flexipages" / QUOTE_PAGE).exists()


@pytest.mark.parametrize("command", ["diff", "writeback"])
def test_missing_org_state_is_an_error(command, tmp_path):
    # No flexipages/ directory: nothing was retrieved. (An empty one is valid.)
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


def test_writeback_rejects_a_layout_name(org_state):
    rc = ux_tool.main([
        "writeback", "--name", "RLM_Quote.layout-meta.xml", "--output-path", str(org_state),
    ])
    assert rc == ux_tool.EXIT_ERROR


def test_diff_against_own_assembly_is_clean(org_state):
    rc = ux_tool.main(["diff", "--output-path", str(org_state), "--fail-on-drift"])
    assert rc == 0
    report = json.loads((org_state / "drift_report.json").read_text())
    assert report["summary"]["drifted"] == 0


def test_diff_detects_removed_region(org_state):
    page = org_state / "flexipages" / QUOTE_PAGE
    xml = page.read_text()
    trimmed, n = re.subn(r"<flexiPageRegions>.*?</flexiPageRegions>\s*", "", xml, count=1, flags=re.S)
    assert n == 1
    page.write_text(trimmed)

    rc = ux_tool.main(["diff", "--output-path", str(org_state), "--fail-on-drift"])
    assert rc == ux_tool.EXIT_DRIFT
    assert json.loads((org_state / "drift_report.json").read_text())["summary"]["drifted"] == 1
    # Without --fail-on-drift drift is reported but not an error.
    assert ux_tool.main(["diff", "--output-path", str(org_state)]) == 0


def test_diff_with_no_org_pages_reports_templates_only(tmp_path):
    """An empty retrieve (the org has none of the pages) is drift, not an error."""
    (tmp_path / "flexipages").mkdir()
    rc = ux_tool.main(["diff", "--output-path", str(tmp_path), "--name", QUOTE_PAGE, "--fail-on-drift"])
    assert rc == ux_tool.EXIT_DRIFT
    assert json.loads((tmp_path / "drift_report.json").read_text())["summary"]["templates_only"] == 1
    # Nothing retrieved at all is still an error.
    assert ux_tool.main(["diff", "--output-path", str(tmp_path / "missing")]) == ux_tool.EXIT_ERROR


def test_scoped_diff_reports_org_only_page(org_state):
    name = "RLM_Org_Only_Page.flexipage-meta.xml"
    shutil.copyfile(org_state / "flexipages" / QUOTE_PAGE, org_state / "flexipages" / name)

    rc = ux_tool.main(["diff", "--output-path", str(org_state), "--name", name, "--fail-on-drift"])
    assert rc == ux_tool.EXIT_DRIFT
    summary = json.loads((org_state / "drift_report.json").read_text())["summary"]
    assert summary == {"in_sync": 0, "drifted": 0, "org_only": 1, "templates_only": 0}
    # A name in neither the templates nor the org is still rejected.
    missing = "RLM_Nowhere.flexipage-meta.xml"
    assert ux_tool.main(["diff", "--output-path", str(org_state), "--name", missing]) == ux_tool.EXIT_ERROR


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

    count = retrieve(_ctx(), "my-scratch", tmp_path)

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

    assert retrieve(_ctx(), "my-scratch", tmp_path, QUOTE_PAGE) == 1
    assert other.read_text() == "<keep/>"
    cmd = fake.calls[0][0]
    assert [c for c in cmd if c.startswith("FlexiPage:")] == ["FlexiPage:RLM_Quote_Record_Page"]


def test_single_page_retrieve_the_org_lacks_clears_the_stale_copy(monkeypatch, tmp_path):
    (tmp_path / "flexipages").mkdir()
    stale = tmp_path / "flexipages" / QUOTE_PAGE
    stale.write_text("<old/>")
    monkeypatch.setattr(_sf.subprocess, "run", FakeSf(_retrieve_payload(), on_call=_write_retrieved([])))

    assert retrieve(_ctx(), "my-scratch", tmp_path, QUOTE_PAGE) == 0
    assert not stale.exists()


def test_failed_retrieve_leaves_existing_files(monkeypatch, tmp_path):
    (tmp_path / "flexipages").mkdir()
    existing = tmp_path / "flexipages" / QUOTE_PAGE
    existing.write_text("<keep/>")
    fake = FakeSf({"status": 1, "name": "NamedOrgNotFoundError", "message": "No authorization"})
    monkeypatch.setattr(_sf.subprocess, "run", fake)

    with pytest.raises(UxError, match="NamedOrgNotFoundError"):
        retrieve(_ctx(), "nope", tmp_path)
    assert existing.read_text() == "<keep/>"


def test_retrieve_rejects_wrong_suffix():
    with pytest.raises(UxOptionError):
        retrieve(_ctx(), "my-scratch", Path("/tmp"), "RLM_Quote_Record_Page.layout-meta.xml")


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
    # sf reports the outcome before the subprocess timeout can kill it.
    assert int(_arg(cmd, "--wait")) * 60 < kwargs["timeout"]


def test_deploy_limits_to_source_paths(monkeypatch, tmp_path):
    fake = FakeSf({"status": 0, "result": {"status": "Succeeded", "numberComponentsDeployed": 1}})
    monkeypatch.setattr(_sf.subprocess, "run", fake)

    one, two = tmp_path / "flexipages" / "A.flexipage-meta.xml", tmp_path / "profiles" / "B.profile-meta.xml"
    deploy(tmp_path, "my-scratch", source_paths=[one, two])

    cmd, _ = fake.calls[0]
    assert [cmd[i + 1] for i, arg in enumerate(cmd) if arg == "--source-dir"] == [str(one), str(two)]


def test_cci_filtered_assembly_deploys_only_what_it_assembled(monkeypatch, tmp_path):
    """A --name run leaves the other outputs in place; the CCI task must not deploy them."""
    import tasks.rlm_ux_assembly as task_mod

    deployed = []
    monkeypatch.setattr(task_mod, "deploy", lambda out, user, logger, cwd, source_paths: deployed.append(source_paths))
    repo = tmp_path / "repo"
    shutil.copytree(REPO_ROOT / "templates", repo / "templates")
    task = task_mod.AssembleAndDeployUX.__new__(task_mod.AssembleAndDeployUX)
    task.project_config = types.SimpleNamespace(repo_root=str(repo), project__custom={}, project__package__api_version="68.0")
    task.org_config = types.SimpleNamespace(username="me@example.com")
    task.logger = logging.getLogger("test")

    task.options = {}
    task._run_task()
    assert deployed[-1] is None  # full run: the whole output directory

    name = "RLM_Quote_Record_Page.flexipage-meta.xml"
    task.options = {"metadata_name": name}
    task._run_task()
    assert deployed[-1] == [repo / "unpackaged" / "post_ux" / "flexipages" / name]


def test_deploy_reports_component_failures(monkeypatch, tmp_path):
    failure = {"componentType": "FlexiPage", "fullName": "RLM_X", "problem": "bad region"}
    payload = {"status": 1, "result": {"status": "Failed", "details": {"componentFailures": failure}}}
    monkeypatch.setattr(_sf.subprocess, "run", FakeSf(payload))

    with pytest.raises(UxError, match="FlexiPage/RLM_X: bad region"):
        deploy(tmp_path, "my-scratch")


def test_deploy_partial_success_is_a_failure(monkeypatch, tmp_path):
    payload = {"status": 0, "result": {"status": "SucceededPartial", "numberComponentsDeployed": 2}}
    monkeypatch.setattr(_sf.subprocess, "run", FakeSf(payload))

    with pytest.raises(UxError, match="SucceededPartial"):
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


@pytest.mark.parametrize("name", ["../x.flexipage-meta.xml", "sub/x.flexipage-meta.xml",
                                  "/tmp/x.flexipage-meta.xml", "..\\x.flexipage-meta.xml"])
def test_validate_selection_rejects_paths(name):
    from scripts.ux._assemble import validate_selection

    with pytest.raises(UxOptionError, match="bare filename"):
        validate_selection("flexipages", name, ("flexipages",))


def test_cli_deploy_needs_a_completed_manifest(monkeypatch, tmp_path):
    fake = FakeSf({"status": 0, "result": {"status": "Succeeded"}})
    monkeypatch.setattr(_sf.subprocess, "run", fake)
    manifest = tmp_path / "assembly_manifest.json"
    cmd = ["deploy", "--output-path", str(tmp_path), "-o", "x"]

    assert ux_tool.main(cmd) == ux_tool.EXIT_ERROR, "no manifest"
    for content in ({"incomplete": True}, {"feature_flags": {}}):  # the latter predates scope
        manifest.write_text(json.dumps(content))
        assert ux_tool.main(cmd) == ux_tool.EXIT_ERROR, content
    manifest.write_text(json.dumps({"scope": {"type": "layouts", "name": None}, "assembled": []}))
    assert ux_tool.main(cmd) == ux_tool.EXIT_ERROR, "filtered run wrote nothing"
    assert not fake.calls
    manifest.write_text(json.dumps({"scope": {"type": "all", "name": None}, "assembled": []}))
    assert ux_tool.main(cmd) == 0


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
        "--fail-on-drift",
    ])


def test_writeback_dry_run_changes_nothing(repo_copy):
    root, out = repo_copy
    before = _snapshot(root)
    assert ux_tool.main(["writeback", "--repo-root", str(root), "--output-path", str(out)]) == 0
    assert _snapshot(root) == before


def test_writeback_aborts_without_writing_when_a_reversal_fails(repo_copy, monkeypatch):
    """A failed reversal must not write a page that still holds feature content,
    nor touch any other page or patch file."""
    from scripts.ux import _patch_ops, _writeback

    root, out = repo_copy
    page = out / "flexipages" / QUOTE_PAGE
    page.write_text(PERSONA_RULE.sub("", page.read_text(), count=1))  # real drift to write back
    before = _snapshot(root)

    def reverse(root_, patch, template_root, logger):
        if patch.get("type") == "insert_action":
            return _patch_ops.FAILED
        return _patch_ops.reverse_patch(root_, patch, template_root, logger)

    monkeypatch.setattr(_writeback, "reverse_patch", reverse)
    assert _apply_drift(root, out) == ux_tool.EXIT_ERROR
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


def test_apply_drift_aborts_when_insert_after_xml_anchor_changed(repo_copy):
    """The org renamed the persona rule's anchor component but kept the rule:
    reverse must fail rather than report the rule absent and bake it into base."""
    root, out = repo_copy
    page = out / "flexipages" / QUOTE_PAGE
    xml, n = re.subn(
        r"<identifier>runtime_sales_pathassistant_pathAssistant</identifier>",
        "<identifier>renamed_pathAssistant</identifier>", page.read_text(), count=1,
    )
    assert n == 1
    page.write_text(xml)
    before = _snapshot(root)

    assert _apply_drift(root, out) == ux_tool.EXIT_ERROR
    assert _snapshot(root) == before


@pytest.mark.parametrize("edit", ["rename_and_edit", "edit_in_place"])
def test_apply_drift_aborts_when_insert_after_xml_element_edited(repo_copy, edit):
    """The org edited the persona rule (and maybe renamed its anchor): no exact
    copy survives, but reverse must still fail rather than report it absent."""
    root, out = repo_copy
    page = out / "flexipages" / QUOTE_PAGE
    xml = page.read_text()
    if edit == "rename_and_edit":
        xml = xml.replace(
            "<identifier>runtime_sales_pathassistant_pathAssistant</identifier>",
            "<identifier>renamed_pathAssistant</identifier>", 1,
        )
    xml, n = re.subn(r"RLM Sales Representative", "RLM Sales Manager", xml, count=1)
    assert n == 1
    page.write_text(xml)
    before = _snapshot(root)

    assert _apply_drift(root, out) == ux_tool.EXIT_ERROR
    assert _snapshot(root) == before


def test_writeback_refuses_a_page_owned_by_an_inactive_feature(repo_copy):
    """A page of a disabled standalone feature is not new: saving it as a base
    template would leak it into every build."""
    root, out = repo_copy
    page = root / "templates" / "flexipages" / "standalone" / "payments" / "RLM_Payment_Record_Page.flexipage-meta.xml"
    shutil.copy2(page, out / "flexipages" / page.name)
    before = _snapshot(root)

    rc = ux_tool.main([
        "writeback", "--apply", "--repo-root", str(root), "--output-path", str(out),
        "--flag", "payments=false",
    ])
    assert rc == ux_tool.EXIT_ERROR
    assert _snapshot(root) == before
    assert not (root / "templates" / "flexipages" / "base" / page.name).exists()


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
    from scripts.ux._patch_ops import ABSENT, FAILED, REMOVED, reverse_insert_action

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
    template = ET.fromstring(
        f'<FlexiPage xmlns="{ns}"><a>{action_list("Other", "A")}</a>'
        f'<b>{action_list("Anchor", "B")}</b></FlexiPage>'
    )
    patch = {"after": "Anchor", "actions": ["A", "B"]}

    # The anchor's template list already has B, so the forward patch never
    # inserted it; A is the template's only in the other list, so the copy
    # in the anchor list is the patch's.
    assert reverse_insert_action(org, patch, template) == REMOVED
    values = [v.text for v in org.iter(f"{{{ns}}}value")]
    assert values == ["Other", "A", "Anchor", "B"]
    assert reverse_insert_action(org, patch, template) == ABSENT

    # The org moved a patch action out of the anchor list: it cannot be
    # reversed, and must not be reported absent.
    moved = ET.fromstring(
        f'<FlexiPage xmlns="{ns}"><a>{action_list("Other", "New")}</a>'
        f'<b>{action_list("Anchor", "B")}</b></FlexiPage>'
    )
    assert reverse_insert_action(moved, {"after": "Anchor", "actions": ["New"]}, template) == FAILED


NS = "http://soap.sforce.com/2006/04/metadata"


def _actions_page(*items):
    """A page with one actionNames valueList holding ``items`` (raw valueListItems XML)."""
    return ET.fromstring(
        f'<FlexiPage xmlns="{NS}"><itemInstances><componentInstance>'
        "<componentInstanceProperties><name>actionNames</name><valueList>"
        + "".join(items)
        + "</valueList></componentInstanceProperties></componentInstance></itemInstances></FlexiPage>"
    )


def _action(name, rule=""):
    return f"<valueListItems><value>{name}</value>{rule}</valueListItems>"


def _rule(field, value):
    return (
        "<visibilityRule><criteria><leftValue>{!" + field + "}</leftValue>"
        f"<operator>EQUAL</operator><rightValue>{value}</rightValue></criteria></visibilityRule>"
    )


def _action_names(root):
    from scripts.ux._xml import list_values, value_lists
    return [v for vl in value_lists(root, "actionNames") for v in list_values(vl)]


def test_insert_action_refresh_carries_org_visibility():
    from scripts.ux._patch_ops import PagePair, refresh_insert_action

    keep = {"name": "Keep", "visibility": [{"field": "Record.Status", "operator": "EQUAL", "value": "Draft"}]}
    patch = {"actions": [keep, "Gone"]}

    def refresh(org):
        return refresh_insert_action(patch, PagePair(org, org, "", ""))["actions"]

    # Unchanged rule: the entry keeps its exact shape; the missing action drops.
    assert refresh(_actions_page(_action("Keep", _rule("Record.Status", "Draft")))) == [keep]
    # Edited in the org: the patch takes the org's criteria.
    assert refresh(_actions_page(_action("Keep", _rule("Record.Status", "Approved")))) == [
        {"name": "Keep", "visibility": [{"field": "Record.Status", "operator": "EQUAL", "value": "Approved"}]}
    ]
    # Rule removed in the org: back to a bare name.
    assert refresh(_actions_page(_action("Keep"))) == ["Keep"]


def test_insert_action_without_org_anchor_targets_list_holding_the_actions():
    from scripts.ux._patch_ops import FAILED, REMOVED, PagePair, refresh_insert_action, reverse_insert_action

    patch = {"after": "Anchor", "actions": ["New"]}

    # The org removed the anchor, but the inserted action is still in one list.
    org = _actions_page(_action("Prev"), _action("New"), _action("Next"))
    refreshed = refresh_insert_action(patch, PagePair(org, org, "", ""))
    assert refreshed == {"after": "Prev", "actions": ["New"]}
    assert reverse_insert_action(org, patch) == REMOVED
    assert _action_names(org) == ["Prev", "Next"]

    # Nothing before the action to anchor to: the patch stays as it was.
    org = _actions_page(_action("New"), _action("Next"))
    assert refresh_insert_action(patch, PagePair(org, org, "", "")) is patch

    # Two lists hold the action: neither reverse nor refresh guesses.
    one_list = (
        "<itemInstances><componentInstance><componentInstanceProperties><name>actionNames</name>"
        "<valueList>" + _action("New") + "</valueList></componentInstanceProperties>"
        "</componentInstance></itemInstances>"
    )
    two = ET.fromstring(f'<FlexiPage xmlns="{NS}">{one_list}{one_list}</FlexiPage>')
    assert reverse_insert_action(two, patch) == FAILED
    assert _action_names(two) == ["New", "New"]
    assert refresh_insert_action(patch, PagePair(two, two, "", "")) is patch


def test_remove_action_reverse_restores_template_action():
    from scripts.ux._patch_ops import ABSENT, REMOVED, PagePair, refresh_patch, reverse_patch

    template = _actions_page(_action("A"), _action("B", _rule("Record.X", "1")), _action("C"))
    org = _actions_page(_action("A"), _action("C"))
    patch = {"type": "remove_action", "action": "B"}

    assert reverse_patch(org, patch, template, None) == REMOVED
    assert _action_names(org) == ["A", "B", "C"]
    assert ET.tostring(org).count(b"visibilityRule") == 2  # opening + closing tag, copied from the template
    # Already back in the org: nothing to restore, and refresh drops the patch.
    assert reverse_patch(org, patch, template, None) == ABSENT
    assert refresh_patch(patch, PagePair(template, org, "", "")) is None


def test_remove_action_reverse_targets_the_list_it_removed_from():
    """Action names repeat across lists: a copy in another list does not mean
    the removed one is back."""
    from scripts.ux._patch_ops import REMOVED, PagePair, refresh_patch, reverse_patch

    def page(*lists):
        body = "".join(
            "<itemInstances><componentInstance><componentInstanceProperties><name>actionNames</name>"
            "<valueList>" + "".join(map(_action, names)) + "</valueList></componentInstanceProperties>"
            "</componentInstance></itemInstances>"
            for names in lists
        )
        return ET.fromstring(f'<FlexiPage xmlns="{NS}">{body}</FlexiPage>')

    def lists(root):
        from scripts.ux._xml import list_values, value_lists
        return [list_values(v) for v in value_lists(root, "actionNames")]

    patch = {"type": "remove_action", "action": "New"}
    template = page(["Edit", "Clone"], ["Delete", "New", "Share"])
    org = page(["Edit", "New", "Clone"], ["Delete", "Share"])  # forward removed New from the 2nd list only

    assert refresh_patch(patch, PagePair(template, org, "", "")) == patch
    assert reverse_patch(org, patch, template, None) == REMOVED
    assert lists(org) == [["Edit", "New", "Clone"], ["Delete", "New", "Share"]]
    assert refresh_patch(patch, PagePair(template, org, "", "")) is None


def test_reverse_keeps_fields_the_template_already_has():
    from scripts.ux._patch_ops import ABSENT, reverse_patch

    def display_page(*fields):
        return ET.fromstring(
            f'<FlexiPage xmlns="{NS}"><itemInstances><componentInstance>'
            "<componentInstanceProperties><name>displayFields</name><valueList>"
            + "".join(f"<valueListItems><value>{f}</value></valueListItems>" for f in fields)
            + "</valueList></componentInstanceProperties></componentInstance></itemInstances></FlexiPage>"
        )

    org = display_page("Name", "Total")
    patch = {"type": "add_display_field", "field": "Total"}
    # The forward patch skipped Total because the template had it, so reverse must too.
    assert reverse_patch(org, patch, display_page("Total"), None) == ABSENT
    assert b"Total" in ET.tostring(org)


def test_add_facet_field_reverse_fails_when_a_duplicate_survives():
    """The forward patch adds one instance; a second copy the template lacks
    would be baked into the template if writeback went ahead."""
    from scripts.ux._patch_ops import FAILED, reverse_patch

    def field(name):
        return f"<itemInstances><fieldInstance><fieldItem>Record.{name}</fieldItem></fieldInstance></itemInstances>"

    def facet(name, *fields):
        return f"<flexiPageRegions>{''.join(map(field, fields))}<name>{name}</name><type>Facet</type></flexiPageRegions>"

    org = ET.fromstring(
        f'<FlexiPage xmlns="{NS}">{facet("other", "Dup")}{facet("target", "Anchor", "Dup")}</FlexiPage>'
    )
    patch = {"type": "add_facet_field", "after": "Anchor", "fields": ["Dup"]}
    assert reverse_patch(org, patch, ET.fromstring(f'<FlexiPage xmlns="{NS}"/>'), None) == FAILED


def test_add_component_refresh_carries_org_properties():
    from scripts.ux._patch_ops import PagePair, refresh_patch

    def page(props):
        return ET.fromstring(
            f'<FlexiPage xmlns="{NS}"><flexiPageRegions><itemInstances><componentInstance>'
            + "".join(
                f"<componentInstanceProperties><name>{k}</name><value>{v}</value></componentInstanceProperties>"
                for k, v in props.items()
            )
            + "<componentName>c:x</componentName><identifier>c_x</identifier>"
            "</componentInstance></itemInstances><name>r</name></flexiPageRegions></FlexiPage>"
        )

    patch = {"type": "add_component", "region": "r", "component": "c:x", "identifier": "c_x",
             "properties": {"maxRecords": 5}}
    same = page({"maxRecords": "5"})
    assert refresh_patch(patch, PagePair(same, same, "", "")) is patch
    edited = page({"maxRecords": "10"})
    assert refresh_patch(patch, PagePair(edited, edited, "", ""))["properties"] == {"maxRecords": "10"}


def test_add_component_moved_or_duplicated_fails_reverse():
    from scripts.ux._patch_ops import ABSENT, FAILED, REMOVED, reverse_patch

    item = ("<itemInstances><componentInstance><componentName>c:x</componentName>"
            "<identifier>c_x</identifier></componentInstance></itemInstances>")

    def page(in_r=0, in_s=0):
        return ET.fromstring(
            f'<FlexiPage xmlns="{NS}"><flexiPageRegions>{item * in_r}<name>r</name></flexiPageRegions>'
            f"<flexiPageRegions>{item * in_s}<name>s</name></flexiPageRegions></FlexiPage>"
        )

    patch = {"type": "add_component", "region": "r", "component": "c:x", "identifier": "c_x"}
    template = page()
    assert reverse_patch(page(in_s=1), patch, template, None) == FAILED  # moved
    assert reverse_patch(page(in_r=2), patch, template, None) == FAILED  # duplicated in place
    assert reverse_patch(page(in_r=1), patch, template, None) == REMOVED
    assert reverse_patch(page(), patch, template, None) == ABSENT
    renamed = ET.fromstring(ET.tostring(page(in_r=1)).replace(b"c_x", b"c_renamed"))
    assert reverse_patch(renamed, patch, template, None) == FAILED  # identifier renamed


def test_moved_or_duplicated_fields_fail_reverse():
    from scripts.ux._patch_ops import FAILED, REMOVED, reverse_patch

    def display_page(*lists):
        props = "".join(
            "<componentInstanceProperties><name>displayFields</name><valueList>"
            + "".join(f"<valueListItems><value>{v}</value></valueListItems>" for v in values)
            + "</valueList></componentInstanceProperties>"
            for values in lists
        )
        return ET.fromstring(f'<FlexiPage xmlns="{NS}"><x>{props}</x></FlexiPage>')

    patch = {"type": "add_display_field", "field": "F"}
    template = display_page(["A"], ["B"])
    assert reverse_patch(display_page(["A", "F"], ["B"]), patch, template, None) == REMOVED
    assert reverse_patch(display_page(["A"], ["B", "F"]), patch, template, None) == FAILED
    # The template has F only in a later list, so the forward patch still adds
    # it to the first list: that copy is the patch's.
    template = display_page(["A"], ["B", "F"])
    assert reverse_patch(display_page(["A", "F"], ["B", "F"]), patch, template, None) == REMOVED
    assert reverse_patch(display_page(["A", "F"], ["B", "F", "F"]), patch, template, None) == FAILED

    def facet_page(*regions):
        return ET.fromstring(
            f'<FlexiPage xmlns="{NS}">'
            + "".join(
                "<flexiPageRegions>"
                + "".join(
                    "<itemInstances><fieldInstance><fieldItem>Record." + f
                    + "</fieldItem></fieldInstance></itemInstances>" for f in fields
                )
                + f"<name>Facet-{i}</name><type>Facet</type></flexiPageRegions>"
                for i, fields in enumerate(regions)
            )
            + "</FlexiPage>"
        )

    patch = {"type": "add_facet_field", "fields": ["New"], "after": "A"}
    template = facet_page(["A"], ["B"])
    assert reverse_patch(facet_page(["A", "New"], ["B"]), patch, template, None) == REMOVED
    assert reverse_patch(facet_page(["A", "New"], ["B", "New"]), patch, template, None) == FAILED


def test_insert_after_xml_renamed_region_fails_reverse():
    from scripts.ux._patch_ops import ABSENT, FAILED, REMOVED, reverse_patch

    def region(name, ident="c_x"):
        return (
            "<flexiPageRegions><itemInstances><componentInstance><componentName>c:x</componentName>"
            f"<identifier>{ident}</identifier></componentInstance></itemInstances><name>{name}</name>"
            "<type>Region</type></flexiPageRegions>"
        )

    patch = {"type": "insert_after_xml", "anchor": "<name>main</name>", "xml": region("feature")}
    template = ET.fromstring(f'<FlexiPage xmlns="{NS}"><name>main</name></FlexiPage>')
    org = ET.fromstring(f'<FlexiPage xmlns="{NS}"><name>main</name>{region("feature")}</FlexiPage>')
    assert reverse_patch(org, patch, template, None) == REMOVED
    renamed = ET.fromstring(f'<FlexiPage xmlns="{NS}"><name>main</name>{region("renamed")}</FlexiPage>')
    assert reverse_patch(renamed, patch, template, None) == FAILED
    both = ET.fromstring(f'<FlexiPage xmlns="{NS}"><name>main</name>{region("renamed", "c_y")}</FlexiPage>')
    assert reverse_patch(both, patch, template, None) == FAILED  # region and identifier renamed
    empty = '<flexiPageRegions><name>{}</name><type>Facet</type></flexiPageRegions>'
    patch = {"type": "insert_after_xml", "anchor": "<name>main</name>", "xml": empty.format("f1")}
    org = ET.fromstring(f'<FlexiPage xmlns="{NS}"><name>main</name>{empty.format("f2")}</FlexiPage>')
    assert reverse_patch(org, patch, template, None) == FAILED  # empty region renamed
    assert reverse_patch(copy.deepcopy(template), patch, template, None) == ABSENT

    item = '<itemInstances><fieldInstance><fieldItem>Record.F</fieldItem><identifier>{}</identifier></fieldInstance></itemInstances>'
    patch = {"type": "insert_after_xml", "anchor": "<name>main</name>", "xml": item.format("f_old")}
    host = '<FlexiPage xmlns="{}"><flexiPageRegions>{}<name>main</name></flexiPageRegions></FlexiPage>'
    template = ET.fromstring(host.format(NS, ""))
    assert reverse_patch(ET.fromstring(host.format(NS, item.format("f_old"))), patch, template, None) == REMOVED
    assert reverse_patch(ET.fromstring(host.format(NS, item.format("f_new"))), patch, template, None) == FAILED


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))


def test_writeback_with_no_org_flexipages_is_an_error(tmp_path):
    """An empty or missing flexipages/ means nothing was retrieved, not no drift."""
    (tmp_path / "flexipages").mkdir()
    for apply in ([], ["--apply"]):
        assert ux_tool.main(["writeback", *apply, "--output-path", str(tmp_path)]) == ux_tool.EXIT_ERROR
