"""docker-publish.yml moves `:latest` only on purpose (offline, needs PyYAML and bash).

Every run used to push `:latest` alongside its own tag, so a manual test build (any tag, one
platform) replaced what an unpinned `docker pull …:latest` returns. That happened on 2026-10-12:
an amd64-only `phase3-test` dispatch became `:latest`, and arm64 pulls broke until it was rebuilt.

This runs the workflow's own "Set image coordinates" script, taken from the parsed YAML, under each
event, and checks the tags it hands the build step:

- the weekly schedule publishes its date tag plus `:latest`;
- an `image-v*` tag push publishes only its version (a patch line must not move `:latest` back);
- a manual run publishes only its tag, unless that tag is `latest`;
- a manual `latest` must build both platforms from the default branch, or the run fails;
- the build step takes its tags only from that output, with no `:latest` of its own.
"""
import os
import re
import subprocess
import sys
import tempfile

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(REPO, ".github", "workflows", "docker-publish.yml")
ALL = "linux/amd64,linux/arm64"
IMAGE = "ghcr.io/owner-x/rlm-base"

_passed = _total = 0


def check(label, ok, detail=""):
    global _passed, _total
    _total += 1
    if ok:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}" + (f"\n         {detail}" if detail else ""))


def parse_outputs(text):
    """$GITHUB_OUTPUT as a dict, including `name<<DELIM` multi-line values."""
    out, lines, i = {}, text.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        if "<<" in line and "=" not in line.split("<<", 1)[0]:
            name, delim = line.split("<<", 1)
            i += 1
            body = []
            while i < len(lines) and lines[i] != delim:
                body.append(lines[i])
                i += 1
            if i == len(lines):
                raise ValueError(f"unterminated {name}<<{delim}")  # GitHub would fail the step too
            out[name] = body
        elif "=" in line:
            name, value = line.split("=", 1)
            out[name] = value
        i += 1
    return out


with open(WORKFLOW, encoding="utf-8") as fh:
    doc = yaml.safe_load(fh)
steps = doc["jobs"]["build-and-push"]["steps"]
meta = next(s for s in steps if s.get("id") == "meta")
build = next(s for s in steps if str(s.get("uses", "")).startswith("docker/build-push-action@"))


def coordinates(event, tag="", platforms="", ref_name="main"):
    """Run the meta step's script; return (exit code, outputs, stderr+stdout)."""
    with tempfile.NamedTemporaryFile("r", suffix=".out", delete=False) as fh:
        out_path = fh.name
    env = dict(os.environ, EVENT_NAME=event, INPUT_TAG=tag, INPUT_PLATFORMS=platforms,
               GITHUB_REPOSITORY_OWNER="Owner-X", GITHUB_REF_NAME=ref_name, DEFAULT_BRANCH="main",
               GITHUB_OUTPUT=out_path)
    # GitHub runs a `run:` step on Linux as `bash -e {0}`.
    proc = subprocess.run(["bash", "-e", "-c", meta["run"]], env=env, capture_output=True, text=True)
    with open(out_path, encoding="utf-8") as fh:
        outputs = parse_outputs(fh.read())
    os.unlink(out_path)
    return proc.returncode, outputs, proc.stdout + proc.stderr


print("When :latest moves")
code, out, log = coordinates("schedule")
check("the weekly schedule publishes its date tag and :latest",
      code == 0 and len(out.get("tags", [])) == 2
      and re.fullmatch(rf"{re.escape(IMAGE)}:\d{{8}}", out["tags"][0]) is not None
      and out["tags"][1] == f"{IMAGE}:latest" and out.get("latest") == "yes", (code, out, log))
code, out, log = coordinates("workflow_dispatch", tag="latest", platforms=ALL)
check("a manual run tagged latest on both platforms publishes :latest once",
      code == 0 and out.get("tags") == [f"{IMAGE}:latest"] and out.get("latest") == "yes",
      (code, out, log))

print("\nWhen it doesn't")
code, out, log = coordinates("push", ref_name="image-v262.1")
check("an image-v* tag push publishes only its version, so a patch line can't move :latest back",
      code == 0 and out.get("tags") == [f"{IMAGE}:262.1"] and out.get("latest") == "no",
      (code, out, log))
code, out, log = coordinates("push", ref_name="image-vlatest")
check("an image-vlatest tag push fails rather than publishing :latest around the rule",
      code != 0 and "tags" not in out and "can't publish :latest" in log, (code, out, log))
code, out, log = coordinates("workflow_dispatch", tag="phase3-test", platforms="linux/amd64")
check("a manual test build publishes only its own tag (the 2026-10-12 case)",
      code == 0 and out.get("tags") == [f"{IMAGE}:phase3-test"] and out.get("latest") == "no",
      (code, out, log))
code, out, log = coordinates("workflow_dispatch", tag="262", platforms=ALL)
check("a manual run with another tag leaves :latest alone even on both platforms",
      code == 0 and out.get("tags") == [f"{IMAGE}:262"] and out.get("latest") == "no",
      (code, out, log))
code, out, log = coordinates("workflow_dispatch", tag="latest", platforms="linux/amd64")
check("a manual latest built for one platform fails instead of publishing a partial :latest",
      code != 0 and "tags" not in out and "latest must be built" in log, (code, out, log))
code, out, log = coordinates("workflow_dispatch", tag="latest", platforms=ALL, ref_name="feature")
check("a manual latest from a branch other than the default fails",
      code != 0 and "tags" not in out and "only from the default branch" in log, (code, out, log))
code, out, log = coordinates("workflow_dispatch", tag="bad tag", platforms=ALL)
check("an invalid tag fails, for that reason, before anything reaches the outputs",
      code != 0 and "tags" not in out and "invalid image tag" in log, (code, out, log))

print("\nThe build step")
tags = str(build.get("with", {}).get("tags", ""))
check("the build step takes its tags only from the coordinates step",
      tags.strip() == "${{ steps.meta.outputs.tags }}", tags)

print("\nConcurrency")
# A group holds one running and one pending run, and a newer pending run replaces the older. The
# runs that move :latest share a group so nothing else can replace a pending weekly publish; the
# key is pinned because its effect only shows up in GitHub's scheduler, which nothing here runs.
group = str((doc.get("concurrency") or {}).get("group", ""))
check("only the runs that move :latest share a concurrency group (the schedule and a manual latest)",
      group == "docker-publish-${{ github.ref }}-${{ github.event_name == 'schedule' && 'latest' "
               "|| github.event.inputs.tag || 'tag-push' }}", group)
check("and runs queue rather than cancel each other",
      (doc.get("concurrency") or {}).get("cancel-in-progress") is False, doc.get("concurrency"))

print(f"\n{_passed}/{_total} checks passed")
sys.exit(0 if _passed == _total else 1)
