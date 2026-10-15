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
must appear in it exactly once, and the text that replaces it. With ``flag`` on, the
text is spliced in, indented to the marker's column, and the result must parse as XML.
With it off the bundle deploys unchanged, but the markers are still checked, so a lost
marker fails both kinds of build. The splice happens in the deploy zip; repo files are
never modified.
"""
import io
import xml.etree.ElementTree as ET
import zipfile

try:
    from cumulusci.core.exceptions import CumulusCIException, TaskOptionsError
    from cumulusci.core.source_transforms.transforms import SourceTransform
    from cumulusci.core.utils import process_bool_arg
    from cumulusci.tasks.salesforce import Deploy
except ImportError:
    Deploy = object
    SourceTransform = object
    CumulusCIException = RuntimeError
    TaskOptionsError = ValueError

    def process_bool_arg(value):
        return value if isinstance(value, bool) else str(value).lower() in ("true", "1", "yes")


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


def flag_value(project_config, flag):
    """The project custom flag ``flag`` as a bool; fails if cumulusci.yml doesn't define it.

    Accepts the strings a runtime override can pass ("false", "True").
    """
    value = project_config.lookup(f"project__custom__{flag}") if flag else None
    if value is None:
        raise TaskOptionsError(f"flag {flag!r} isn't a project custom flag in cumulusci.yml")
    return process_bool_arg(value)


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
            "description": "Project custom flag (project -> custom in cumulusci.yml) that turns the splice on",
            "required": True,
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
        self.splice_on = flag_value(self.project_config, self.options.get("flag"))
        self.transforms = with_splice(self.transforms, parse_fragments(self.options.get("fragments")), self.splice_on)
