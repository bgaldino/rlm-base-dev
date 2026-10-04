"""
AssembleAndDeployUX — CumulusCI wrapper for late-stage UX metadata assembly.

The assembly logic lives in ``scripts/ux/`` (CCI-free); this task only maps
CCI options, feature flags and the target org onto it, so ``prepare_ux`` keeps
assembling and deploying in one step. Drift capture/writeback has no CCI task:
use ``python scripts/ux/ux_tool.py`` (see ``scripts/ux/README.md``).

Usage examples (this task has no --org option; deploy uses your DEFAULT cci org):
    cci task run assemble_and_deploy_ux
    cci task run assemble_and_deploy_ux -o deploy false        # dry-run: local only, no org
    cci task run assemble_and_deploy_ux \\
        -o metadata_name RLM_Quote_Record_Page.flexipage-meta.xml
    cci task run assemble_and_deploy_ux \\
        -o metadata_type profiles -o deploy false
"""
import logging
import sys
from pathlib import Path
from typing import Any, Dict

try:
    from cumulusci.tasks.sfdx import SFDXBaseTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
    from cumulusci.core.keychain import BaseProjectKeychain
    from cumulusci.core.utils import process_bool_arg
except ImportError:
    SFDXBaseTask = object
    TaskOptionsError = Exception
    CommandException = Exception
    BaseProjectKeychain = object
    process_bool_arg = None

# Bootstrap the repo root onto sys.path so the scripts.ux package resolves when
# CCI imports this task module.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.ux._assemble import UxAssembler, validate_selection  # noqa: E402
from scripts.ux._context import DEFAULT_API_VERSION, UxContext, UxError, UxOptionError  # noqa: E402
from scripts.ux._deploy import deploy  # noqa: E402
from scripts.ux._flags import features_from_custom, to_bool  # noqa: E402

process_bool_arg = process_bool_arg or to_bool


class AssembleAndDeployUX(SFDXBaseTask):
    """
    Assembles feature-conditional UX metadata from templates and deploys it.

    Reads base templates + YAML patch files from the templates/ directory tree,
    assembles the correct variant based on active CCI feature flags, writes
    assembled SFDX-format metadata to unpackaged/post_ux/, and optionally
    deploys that directory via sf project deploy start.
    """

    keychain_class = BaseProjectKeychain
    task_options: Dict[str, Dict[str, Any]] = {
        "metadata_type": {
            "description": (
                "Which metadata type(s) to assemble. One of: all, flexipages, "
                "layouts, applications, profiles, objects. "
                "Defaults to 'all'. 'objects' covers compactLayouts and listViews."
            ),
            "required": False,
        },
        "metadata_name": {
            "description": (
                "A specific metadata item to generate, identified by its full source "
                "filename including the type suffix, e.g. "
                "'RLM_Quote_Record_Page.flexipage-meta.xml', "
                "'Admin.profile-meta.xml', "
                "'OrderItem-RLM Order Product Layout.layout-meta.xml'. "
                "The suffix disambiguates the metadata type automatically. "
                "When provided, only this item is assembled and deployed."
            ),
            "required": False,
        },
        "deploy": {
            "description": (
                "Whether to deploy the assembled output. Defaults to true. "
                "Set to false to generate output only."
            ),
            "required": False,
        },
        "output_path": {
            "description": (
                "Output directory for assembled metadata. Defaults to 'unpackaged/post_ux'."
            ),
            "required": False,
        },
    }

    def _validate_options(self):
        super()._validate_options()
        try:
            validate_selection(
                self.options.get("metadata_type", "all"),
                self.options.get("metadata_name"),
            )
        except UxOptionError as exc:
            raise TaskOptionsError(str(exc)) from exc

    def _run_task(self):
        repo_root = Path(self.project_config.repo_root)
        output_path = repo_root / self.options.get("output_path", "unpackaged/post_ux")
        should_deploy = process_bool_arg(self.options.get("deploy", True))

        ctx = UxContext(
            repo_root=repo_root,
            features=features_from_custom(getattr(self.project_config, "project__custom", {})),
            api_version=str(
                getattr(self.project_config, "project__package__api_version", None) or DEFAULT_API_VERSION
            ),
            logger=self.logger or logging.getLogger("rlm_ux"),
        )
        metadata_type = self.options.get("metadata_type", "all")
        metadata_name = self.options.get("metadata_name")
        try:
            manifest = UxAssembler(ctx).run(output_path, metadata_type, metadata_name)
            if should_deploy:
                if not manifest["assembled"]:
                    self.logger.warning("No items assembled — skipping deploy")
                    return
                username = getattr(self.org_config, "username", None)
                if not username:
                    raise TaskOptionsError(
                        "Org config has no username. Cannot deploy without a target org."
                    )
                # A filtered run leaves the other outputs in place; deploy only
                # what it assembled.
                sources = None
                if metadata_name or metadata_type != "all":
                    sources = [output_path.parent.parent / item["dest"] for item in manifest["assembled"]]
                deploy(output_path, username, self.logger, cwd=repo_root, source_paths=sources)
        except UxOptionError as exc:
            raise TaskOptionsError(str(exc)) from exc
        except UxError as exc:
            raise CommandException(str(exc)) from exc
