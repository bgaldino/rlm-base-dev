"""
Deploy a bundle with text spliced in at markers when a feature flag is on, for content
that only some builds can deploy.

Written for estimated tax on quotes (quote_est_tax). With it off, the Quote and
QuoteLineItem tax fields don't exist, so the partner permission set can't grant them
unconditionally; with it on, the grants belong there. Two simpler routes don't work
(measured on a 264 scratch org, 2026-10-15):

- CumulusCI's find_replace transform rewrites only element text in an XML file, never
  a comment, and inserts its replacement as escaped text, so it can't add elements.
- Deploying a second copy of the permission set holding only the extra grants replaces
  the permission set's field grants instead of adding to them. A separate permission set
  would need assigning, and the build never assigns RLM_Partner_Community_User_Perm_Set:
  an admin does when creating partner users.

Each fragment names a file in the deploy package, in Metadata API layout (for example
``permissionsets/RLM_Partner_Community_User_Perm_Set.permissionset``), a marker that
must appear in it exactly once, and the text that replaces it.

``flag`` names one or more project custom flags ("quote_est_tax,tax"): the first is the
feature, the rest what it needs, and a feature that's on without them is logged as a
warning. With every one on, the text is spliced in, indented to the marker's column, and
the result must parse as XML. Otherwise the bundle deploys unchanged, but the markers are
still checked, so a lost marker fails the deploy either way. A step that deploy_when
skips deploys and checks nothing; the offline suite (tests/test_deploy_with_fragments.py)
checks every marker on each gate run. The splice happens in the deploy zip; repo files
are never modified.

``deploy_when`` lets two flow steps share one task and one flag list: ``off`` deploys
only while the flags aren't all on, ``on`` only once they are, ``always`` (the default)
every time. quote_est_tax uses it to deploy the setting off early in prepare_core and on
only after prepare_tax has created the tax engine.

``require_on`` is a SOQL COUNT() query that must find at least one record before a
splicing deploy runs. If it finds none, the bundle deploys unspliced with a warning,
as if a flag were off, and the build goes on. Estimated tax uses it twice: the setting
requires an active tax policy, which Help says must exist first, and the partner grants
require the fields the setting creates, so the two can't disagree.
"""
import io
import xml.etree.ElementTree as ET
import zipfile

try:
    from cumulusci.core.exceptions import CumulusCIException, TaskOptionsError
    from cumulusci.core.source_transforms.transforms import SourceTransform
    from cumulusci.core.utils import process_bool_arg, process_list_arg
    from cumulusci.tasks.salesforce import Deploy
except ImportError:
    Deploy = object
    SourceTransform = object
    CumulusCIException = RuntimeError
    TaskOptionsError = ValueError

    def process_bool_arg(value):
        return value if isinstance(value, bool) else str(value).lower() in ("true", "1", "yes")

    def process_list_arg(value):
        # Like CumulusCI's: keeps empty items ("a," -> ["a", ""]), which flag_states rejects.
        if value is None or isinstance(value, list):
            return value
        return [v.strip() for v in str(value).split(",")]


def check_marker(text, marker, name):
    """Fail unless ``marker`` appears exactly once in ``text``."""
    found = text.count(marker)
    if found != 1:
        raise CumulusCIException(f"{name}: expected the marker {marker!r} once, found it {found} times")


def splice(text, marker, fragment, name):
    """``text`` with its single ``marker`` replaced by ``fragment``.

    Fragment lines after the first get the marker's indentation, so the result lines up.
    """
    check_marker(text, marker, name)
    start = text.index(marker)
    line = text[text.rfind("\n", 0, start) + 1:start]
    indent = line if not line.strip() else ""
    return text.replace(marker, fragment.replace("\n", "\n" + indent))


class SpliceFragmentsTransform(SourceTransform):
    """Replace a marker in named package files with fragment text (or only check it, when ``apply`` is off)."""

    options_model = None
    identifier = "splice_fragments"

    def __init__(self, fragments, apply=True):
        # [(package path, marker, fragment text)]
        self.fragments = fragments
        self.apply = apply

    def process(self, zf, context):
        names = set(zf.namelist())
        missing = [p for p, _, _ in self.fragments if p not in names]
        if missing:
            raise CumulusCIException(f"not in the deploy package: {', '.join(missing)}")
        out = zipfile.ZipFile(io.BytesIO(), "w", zipfile.ZIP_DEFLATED)
        for info in zf.infolist():
            data = zf.read(info.filename)
            for path, marker, fragment in self.fragments:
                if info.filename != path:
                    continue
                if not self.apply:
                    check_marker(data.decode("utf-8"), marker, path)
                    continue
                text = splice(data.decode("utf-8"), marker, fragment, path)
                try:
                    ET.fromstring(text.encode("utf-8"))
                except ET.ParseError as e:
                    raise CumulusCIException(f"{path}: not well-formed XML after the splice: {e}")
                context.logger.info(f"Spliced a fragment into {path}")
                data = text.encode("utf-8")
            out.writestr(info, data)
        return out


def with_splice(transforms, fragments, apply):
    """A new transform list: ``transforms`` plus the splice. Never mutates ``transforms``.

    ⚠ Deploy.transforms is a class-level list shared by every Deploy task in the run
    when no transforms option is set, so appending to it would leak this transform.
    """
    return list(transforms) + [SpliceFragmentsTransform(fragments, apply)]


def flag_states(project_config, flag):
    """{name: bool} for the project custom flags ``flag`` names ("a,b" or a list).

    Fails on an empty name or one cumulusci.yml doesn't define, so a typo can't read as
    "off". Values may be the strings a command-line override passes ("false", "True").
    """
    names = [str(n).strip() for n in (process_list_arg(flag) or [])]
    if not names or not all(names):
        raise TaskOptionsError(f"flag must name one or more project custom flags, comma-separated: {flag!r}")
    states = {}
    for name in names:
        value = project_config.lookup(f"project__custom__{name}")
        if value is None:
            raise TaskOptionsError(f"flag {name!r} isn't a project custom flag in cumulusci.yml")
        states[name] = process_bool_arg(value)
    return states


def missing_prerequisites(states):
    """The prerequisite flags that are off while the first (feature) flag is on.

    The first flag named is the feature (quote_est_tax), the rest what it needs (tax);
    a feature left off is the normal case and not worth a warning.
    """
    names = list(states)
    return [n for n in names[1:] if not states[n]] if states[names[0]] else []


DEPLOY_WHEN = ("always", "on", "off")


def should_deploy(deploy_when, splice_on):
    """Whether a ``deploy_when`` step deploys, given whether every flag is on."""
    # ⚠ Strings only: unquoted YAML off/on load as booleans, and False must not read as "always".
    if not isinstance(deploy_when, str) or deploy_when not in DEPLOY_WHEN:
        raise TaskOptionsError(f"deploy_when must be one of {', '.join(DEPLOY_WHEN)}: {deploy_when!r}")
    return deploy_when == "always" or (deploy_when == "on") == splice_on


def parse_fragments(fragments):
    """[(path, marker, text)] from the ``fragments`` option."""
    if not isinstance(fragments, list) or not fragments:
        raise TaskOptionsError("fragments must be a non-empty list of {path, marker, text}")
    parsed = []
    for spec in fragments:
        if not isinstance(spec, dict) or not all(spec.get(k) for k in ("path", "marker", "text")):
            raise TaskOptionsError(f"each fragment needs path, marker and text: {spec!r}")
        parsed.append((spec["path"], spec["marker"], spec["text"].rstrip("\n")))
    return parsed


class DeployWithFragments(Deploy):
    """Deploy ``path``, splicing fragments in at markers when the project flag ``flag`` is on."""

    task_options = {
        **getattr(Deploy, "task_options", {}),
        "flag": {
            "description": "Project custom flags that must all be on for the splice, comma-separated, feature first and then what it needs: quote_est_tax,tax",
            "required": True,
        },
        "require_on": {
            "description": "SOQL COUNT() query that must find a record before a splicing deploy (e.g. an active TaxPolicy)",
            "required": False,
        },
        "deploy_when": {
            "description": "always (default), on (deploy only when every flag is on) or off (only when they aren't)",
            "required": False,
        },
        "fragments": {
            "description": (
                "List of {path, marker, text}: path is the file in the deploy package "
                "(Metadata API layout), marker the text to replace (exactly once), and "
                "text what replaces it"
            ),
            "required": True,
        },
    }

    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        self.flag_states = flag_states(self.project_config, self.options.get("flag"))
        self.splice_on = all(self.flag_states.values())
        value = self.options.get("deploy_when")
        self.deploy_when = "always" if value is None else value
        should_deploy(self.deploy_when, self.splice_on)  # validates the option early
        self.fragments = parse_fragments(self.options.get("fragments"))
        # The splice transform is added in _run_task, once require_on has been checked.
        self.base_transforms = list(self.transforms)

    def _run_task(self):
        names = ", ".join(self.flag_states)
        if not should_deploy(self.deploy_when, self.splice_on):
            # Nothing is deployed, so nothing (markers included) is checked by this step.
            other = "on" if self.deploy_when == "off" else "off"
            self.logger.info(f"Skipped: {names} {'all on' if self.splice_on else 'not all on'}, so the "
                             f"deploy_when={other} step of this task deploys instead")
            return
        apply = self.splice_on
        soql = self.options.get("require_on")
        if soql and apply:
            try:
                count = self.org_config.salesforce_client.query(soql)["totalSize"]
            except Exception as e:  # noqa: BLE001 - simple_salesforce raises several types
                raise CumulusCIException(f"require_on query failed ({soql!r}): {e}") from e
            if count < 1:
                self.logger.warning(f"Not splicing: nothing matches {soql!r}, which the splice requires; "
                                    "deploying the bundle unchanged")
                apply = False
        self.transforms = with_splice(self.base_transforms, self.fragments, apply)
        missing = missing_prerequisites(self.flag_states)
        if missing:
            self.logger.warning(f"{next(iter(self.flag_states))} is on but {', '.join(missing)} is off, "
                                f"so it has no effect ({names} must all be on)")
        return super()._run_task()
