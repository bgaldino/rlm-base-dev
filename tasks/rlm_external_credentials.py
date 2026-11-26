"""
Deploy a bundle whose AWS external credential carries the target AWS account id only at
deploy time.

``SalesforceContractsExtCredentials`` (``unpackaged/post_quantumbit``) is an ``AwsSv4``
external credential. Help's Contracts AI setup fills its AWS Account Id with the
customer's own account (``ind.sf_contracts_create_an_external_credential_and_named_credential``),
so the value is an environment detail, not something the public repo can carry. The
committed file holds ``PLACEHOLDER`` instead, and this task decides in the deploy zip
what the org receives:

- **A value is configured** (the ``aws_account_id`` option, else the ``RLM_AWS_ACCOUNT_ID``
  environment variable): the placeholder is replaced with it. It must be the 12 digits
  AWS uses.
- **Nothing is configured**: the ``AwsAccountId`` AuthParameter is dropped from the
  package, so the credential deploys without one.

Measured on a 264 scratch org (2026-11-26, todo 481): a new ``AwsSv4`` credential deploys
with the placeholder text as its account id (the platform does not check its format) and
with no ``AwsAccountId`` at all; a redeploy that omits the parameter deletes it from the
org, and one that carries a value replaces the old one. The NamedPrincipal parameter keeps
its record id across those redeploys, so permission set grants to the principal survive.
Dropping it is the default because it leaves Setup showing an empty field rather than a
value that looks configured and is not. Either way a redeploy replaces whatever an admin
set in Setup, as the committed value did before.

The substitution happens in the deploy zip, as in ``tasks/rlm_deploy_with_fragments.py``:
repo files are never written, so the working tree stays clean even when the deploy fails
or is interrupted. (The PRM network email patch/revert edits the file in place and
restores it in a later flow step, which a failed deploy never reaches.)

The file must hold exactly one ``AwsAccountId`` parameter whose value is the placeholder;
anything else fails the deploy, so a real id retrieved or pasted back into the file is
caught before it ships. ``tests/test_external_credentials.py`` checks the same offline.
"""
import io
import os
import re
import xml.etree.ElementTree as ET
import zipfile

try:
    from cumulusci.core.exceptions import CumulusCIException, TaskOptionsError
    from cumulusci.core.source_transforms.transforms import SourceTransform
    from cumulusci.tasks.salesforce import Deploy
except ImportError:
    Deploy = object
    SourceTransform = object
    CumulusCIException = RuntimeError
    TaskOptionsError = ValueError

PLACEHOLDER = "aws-account-id-placeholder"
ENV_VAR = "RLM_AWS_ACCOUNT_ID"
PARAMETER = "AwsAccountId"
DEFAULT_CREDENTIAL = "SalesforceContractsExtCredentials"

_BLOCK = re.compile(r"[ \t]*<externalCredentialParameters>.*?</externalCredentialParameters>[ \t]*\n?", re.S)
_ACCOUNT_ID = re.compile(r"^[0-9]{12}$")


def package_path(credential):
    """The credential's file in the deploy zip (Metadata API layout)."""
    return f"externalCredentials/{credential}.externalCredential"


def resolve_account_id(option_value, environ=None):
    """(value, source) from the option, else the environment variable; (None, None) when neither is set.

    Fails on a value that isn't 12 digits. An unquoted number in YAML arrives as an int
    and loses any leading zero, which then fails the length check rather than deploying
    the wrong account.
    """
    environ = os.environ if environ is None else environ
    for value, source in ((option_value, "the aws_account_id option"), (environ.get(ENV_VAR), ENV_VAR)):
        if value is None:
            continue
        value = str(value).strip()
        if not value:
            continue
        if not _ACCOUNT_ID.match(value):
            raise TaskOptionsError(
                f"{source} must be a 12-digit AWS account id (quote it in YAML so a leading zero survives)"
            )
        return value, source
    return None, None


def account_block(text, name):
    """The one AwsAccountId parameter block in ``text``; fails unless it holds the placeholder."""
    blocks = [m for m in _BLOCK.finditer(text) if f"<parameterName>{PARAMETER}</parameterName>" in m.group(0)]
    if len(blocks) != 1:
        raise CumulusCIException(f"{name}: expected one {PARAMETER} parameter, found {len(blocks)}")
    block = blocks[0]
    if f"<parameterValue>{PLACEHOLDER}</parameterValue>" not in block.group(0):
        raise CumulusCIException(
            f"{name}: the {PARAMETER} parameter must hold the placeholder {PLACEHOLDER!r} in the repo; "
            "the real value is supplied at deploy time (aws_account_id option or "
            f"{ENV_VAR}), never committed"
        )
    return block


def apply_account_id(text, account_id, name):
    """``text`` with the placeholder replaced by ``account_id``, or the parameter removed when it is None."""
    block = account_block(text, name)
    if account_id is None:
        new = text[:block.start()] + text[block.end():]
    else:
        new = text[:block.start()] + block.group(0).replace(
            f"<parameterValue>{PLACEHOLDER}</parameterValue>", f"<parameterValue>{account_id}</parameterValue>"
        ) + text[block.end():]
    try:
        ET.fromstring(new.encode("utf-8"))
    except ET.ParseError as e:
        raise CumulusCIException(f"{name}: not well-formed XML after setting {PARAMETER}: {e}")
    return new


class AwsAccountIdTransform(SourceTransform):
    """Set or drop the AwsAccountId parameter of one external credential in the deploy zip."""

    options_model = None
    identifier = "aws_account_id"

    def __init__(self, credential, account_id):
        self.path = package_path(credential)
        self.account_id = account_id

    def process(self, zf, context):
        if self.path not in zf.namelist():
            raise CumulusCIException(f"not in the deploy package: {self.path}")
        out = zipfile.ZipFile(io.BytesIO(), "w", zipfile.ZIP_DEFLATED)
        for info in zf.infolist():
            data = zf.read(info.filename)
            if info.filename == self.path:
                data = apply_account_id(data.decode("utf-8"), self.account_id, self.path).encode("utf-8")
            out.writestr(info, data)
        return out


class DeployWithAwsAccountId(Deploy):
    """Deploy ``path``, giving the external credential the configured AWS account id or none."""

    task_options = {
        **getattr(Deploy, "task_options", {}),
        "aws_account_id": {
            "description": (
                f"12-digit AWS account id for the credential's {PARAMETER}. Falls back to the "
                f"{ENV_VAR} environment variable; with neither set the parameter is left out"
            ),
            "required": False,
        },
        "external_credential": {
            "description": f"External credential to set it on (default: {DEFAULT_CREDENTIAL})",
            "required": False,
        },
    }

    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        self.credential = self.options.get("external_credential") or DEFAULT_CREDENTIAL
        self.account_id, self.account_source = resolve_account_id(self.options.get("aws_account_id"))
        # A new list: Deploy.transforms is a class-level list shared by every Deploy task in the
        # run when no transforms option is set, so appending to it would leak this transform.
        self.transforms = list(self.transforms) + [AwsAccountIdTransform(self.credential, self.account_id)]

    def _run_task(self):
        if self.account_id is None:
            self.logger.info(
                f"No AWS account id configured (aws_account_id option or {ENV_VAR}): deploying "
                f"{self.credential} without its {PARAMETER} parameter"
            )
        else:
            # The value is not a secret, but logs travel further than the org does.
            self.logger.info(f"Setting {self.credential} {PARAMETER} from {self.account_source}")
        return super()._run_task()
