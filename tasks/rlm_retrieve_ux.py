"""
RetrieveUXFromOrg — Retrieves live UX metadata (flexipages) from a target org
and writes them to unpackaged/post_ux/, replacing the assembled output with
the org's current state. Intended as the first step in the capture_ux_drift
flow before running diff_ux_templates.

Usage examples:
    cci task run retrieve_ux_from_org --org dev-sb0
    cci task run retrieve_ux_from_org \\
        -o metadata_name RLM_Order_Record_Page.flexipage-meta.xml --org dev-sb0
"""
import base64
import io
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

try:
    from cumulusci.core.tasks import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
    from cumulusci.core.utils import process_bool_arg
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception
    CommandException = Exception

    def process_bool_arg(val):
        if isinstance(val, bool):
            return val
        return str(val).lower() in ("true", "1", "yes")


_SUPPORTED_TYPES = {
    "flexipages": "FlexiPage",
}

_SF_MDAPI_NS = "http://soap.sforce.com/2006/04/metadata"


class RetrieveUXFromOrg(BaseSalesforceTask):
    """
    Retrieves live UX metadata from a target org into unpackaged/post_ux/,
    replacing the assembled output with the org's current state for drift
    comparison via diff_ux_templates.

    Uses the Metadata API directly (SOAP retrieve) to avoid sf CLI PATH
    and environment issues when running inside CCI's Python process.

    Retrieval scope defaults to all flexipages defined in
    templates/flexipages/base/. Pass metadata_name to limit to one page.
    """

    task_options = {
        "metadata_name": {
            "description": (
                "Specific file to retrieve, identified by its full source filename "
                "including the type suffix, e.g. "
                "'RLM_Order_Record_Page.flexipage-meta.xml'. "
                "Retrieves all base-template pages when omitted."
            ),
            "required": False,
        },
        "metadata_type": {
            "description": (
                "Metadata type to retrieve. Currently supports 'flexipages'. "
                "Defaults to 'flexipages'."
            ),
            "required": False,
        },
        "output_path": {
            "description": (
                "Output directory for retrieved metadata. "
                "Defaults to 'unpackaged/post_ux'."
            ),
            "required": False,
        },
    }

    def _validate_options(self):
        super()._validate_options()
        mtype = self.options.get("metadata_type", "flexipages")
        if mtype not in _SUPPORTED_TYPES:
            raise TaskOptionsError(
                f"metadata_type must be one of {sorted(_SUPPORTED_TYPES)}, "
                f"got: '{mtype}'"
            )
        mname = self.options.get("metadata_name")
        if mname and not mname.endswith(".flexipage-meta.xml"):
            raise TaskOptionsError(
                f"metadata_name must end in '.flexipage-meta.xml', got: '{mname}'"
            )

    def _run_task(self):
        repo_root = Path(self.project_config.repo_root)
        output_path = repo_root / self.options.get("output_path", "unpackaged/post_ux")
        metadata_name = self.options.get("metadata_name")
        metadata_type = self.options.get("metadata_type", "flexipages")
        templates_path = repo_root / "templates"

        if metadata_type == "flexipages":
            self._retrieve_flexipages(
                repo_root, templates_path, output_path, metadata_name
            )

    def _get_feature_flags(self) -> Dict[str, bool]:
        """Read feature flags from project_config.project__custom__*."""
        custom = getattr(self.project_config, "project__custom", {}) or {}
        known_flags = [
            "qb", "billing", "billing_ui", "tax", "rating", "rates", "clm", "dro",
            "guidedselling", "ramps", "tso", "prm", "agents", "docgen",
            "payments", "constraints", "analytics", "procedureplans",
            "collections",
        ]
        flags = {}
        for flag in known_flags:
            val = custom.get(flag, False)
            flags[flag] = process_bool_arg(val) if isinstance(val, (str, bool)) else bool(val)
        return flags

    def _retrieve_flexipages(
        self,
        repo_root: Path,
        templates_path: Path,
        output_path: Path,
        filter_name: Optional[str],
    ) -> None:
        base_dir = templates_path / "flexipages" / "base"
        standalone_dir = templates_path / "flexipages" / "standalone"

        if filter_name:
            pages = [filter_name]
        else:
            if not base_dir.exists():
                self.logger.warning(f"Flexipage base directory not found: {base_dir}")
                return

            # Build page list matching the assembler's page_sources logic so that
            # standalone-only pages (e.g. billing, billing_ui, constraints) are
            # included in the retrieve and don't show as templates_only in drift.
            features = self._get_feature_flags()
            page_sources: Dict[str, Path] = {}

            for base_file in sorted(base_dir.glob("*.flexipage-meta.xml")):
                page_sources[base_file.name] = base_file

            standalone_copy_order = [
                ("payments",    features.get("payments", False)),
                ("billing",     features.get("billing", False)),
                ("billing_ui",  features.get("billing_ui", False)),
                ("quantumbit",  features.get("qb", False)),
                ("tso",         features.get("tso", False)),
                ("constraints", features.get("constraints", False)),
                ("utils",       features.get("qb", False)),
                ("docgen",      features.get("docgen", False)),
                ("approvals",   features.get("qb", False)),
                ("collections", features.get("collections", False)),
            ]
            for feature_dir, active in standalone_copy_order:
                if not active:
                    continue
                src_dir = standalone_dir / feature_dir
                if not src_dir.exists():
                    continue
                for src_file in sorted(src_dir.glob("*.flexipage-meta.xml")):
                    page_sources[src_file.name] = src_file

            pages = sorted(page_sources.keys())

        if not pages:
            self.logger.warning("No flexipages found to retrieve.")
            return

        # Extract API names from filenames
        api_names = [
            name.replace(".flexipage-meta.xml", "") for name in pages
        ]

        self.logger.info(
            f"Retrieving {len(api_names)} flexipage(s) from "
            f"'{self.org_config.username}': {', '.join(api_names)}"
        )

        dest_dir = output_path / "flexipages"
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Full retrieve: clear existing files to prevent stale leftovers
        if not filter_name:
            for old_file in dest_dir.glob("*.flexipage-meta.xml"):
                old_file.unlink()

        # Retrieve via Metadata API SOAP
        instance_url = self.org_config.instance_url
        access_token = self.org_config.access_token
        api_version = self.project_config.project__package__api_version or "66.0"

        retrieved = self._mdapi_retrieve(
            instance_url, access_token, api_version,
            "FlexiPage", api_names, dest_dir, repo_root,
        )

        if retrieved == 0:
            self.logger.warning(
                "No FlexiPage files found in retrieve result. "
                "The org may not have deployed flexipages for the requested names."
            )
        else:
            self.logger.info(
                f"Retrieved {retrieved} flexipage(s) written to {dest_dir}"
            )

    def _mdapi_retrieve(
        self,
        instance_url: str,
        access_token: str,
        api_version: str,
        metadata_type: str,
        members: List[str],
        dest_dir: Path,
        repo_root: Path,
    ) -> int:
        """Retrieve metadata via the Metadata API SOAP endpoint."""
        mdapi_url = f"{instance_url}/services/Soap/m/{api_version}"

        # Step 1: Start the retrieve
        members_xml = "\n".join(
            f"            <md:members>{m}</md:members>" for m in members
        )
        retrieve_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:md="http://soap.sforce.com/2006/04/metadata">
  <soap:Header>
    <md:SessionHeader>
      <md:sessionId>{access_token}</md:sessionId>
    </md:SessionHeader>
  </soap:Header>
  <soap:Body>
    <md:retrieve>
      <md:retrieveRequest>
        <md:apiVersion>{api_version}</md:apiVersion>
        <md:unpackaged>
          <md:types>
{members_xml}
            <md:name>{metadata_type}</md:name>
          </md:types>
        </md:unpackaged>
      </md:retrieveRequest>
    </md:retrieve>
  </soap:Body>
</soap:Envelope>"""

        req = Request(
            mdapi_url,
            data=retrieve_body.encode("utf-8"),
            headers={
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": "retrieve",
            },
        )

        try:
            resp = urlopen(req, timeout=120)
            resp_body = resp.read().decode("utf-8")
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8") if exc.fp else ""
            raise CommandException(
                f"Metadata API retrieve request failed ({exc.code}): {error_body[:500]}"
            ) from exc

        # Parse retrieve ID from response
        root = ET.fromstring(resp_body)
        id_el = root.find(
            f".//{{{_SF_MDAPI_NS}}}id"
        )
        if id_el is None or not id_el.text:
            raise CommandException(
                f"No retrieve ID in response: {resp_body[:500]}"
            )
        retrieve_id = id_el.text
        self.logger.info(f"  Retrieve started: {retrieve_id}")

        # Step 2: Poll for completion
        zip_data = self._poll_retrieve(mdapi_url, access_token, retrieve_id)

        # Step 3: Extract flexipages from zip
        return self._extract_from_zip(zip_data, dest_dir, repo_root)

    def _poll_retrieve(
        self,
        mdapi_url: str,
        access_token: str,
        retrieve_id: str,
    ) -> bytes:
        """Poll checkRetrieveStatus until done, return the zip bytes."""
        max_polls = 60
        poll_interval = 2

        for i in range(max_polls):
            check_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:md="http://soap.sforce.com/2006/04/metadata">
  <soap:Header>
    <md:SessionHeader>
      <md:sessionId>{access_token}</md:sessionId>
    </md:SessionHeader>
  </soap:Header>
  <soap:Body>
    <md:checkRetrieveStatus>
      <md:asyncProcessId>{retrieve_id}</md:asyncProcessId>
      <md:includeZip>true</md:includeZip>
    </md:checkRetrieveStatus>
  </soap:Body>
</soap:Envelope>"""

            req = Request(
                mdapi_url,
                data=check_body.encode("utf-8"),
                headers={
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": "checkRetrieveStatus",
                },
            )

            try:
                resp = urlopen(req, timeout=120)
                resp_body = resp.read().decode("utf-8")
            except HTTPError as exc:
                error_body = exc.read().decode("utf-8") if exc.fp else ""
                raise CommandException(
                    f"checkRetrieveStatus failed ({exc.code}): {error_body[:500]}"
                ) from exc

            root = ET.fromstring(resp_body)
            done_el = root.find(f".//{{{_SF_MDAPI_NS}}}done")
            done = done_el is not None and done_el.text == "true"

            if done:
                status_el = root.find(f".//{{{_SF_MDAPI_NS}}}status")
                status = status_el.text if status_el is not None else "Unknown"
                self.logger.info(f"  Retrieve complete: {status}")

                if status != "Succeeded":
                    msg_el = root.find(f".//{{{_SF_MDAPI_NS}}}errorMessage")
                    msg = msg_el.text if msg_el is not None else "unknown error"
                    raise CommandException(
                        f"Retrieve failed with status {status}: {msg}"
                    )

                zip_el = root.find(f".//{{{_SF_MDAPI_NS}}}zipFile")
                if zip_el is None or not zip_el.text:
                    raise CommandException(
                        "Retrieve succeeded but no zip data in response"
                    )
                return base64.b64decode(zip_el.text)

            if i > 0 and i % 10 == 0:
                self.logger.info(f"  Still waiting... (poll {i}/{max_polls})")
            time.sleep(poll_interval)

        raise CommandException(
            f"Retrieve timed out after {max_polls * poll_interval}s"
        )

    def _extract_from_zip(
        self,
        zip_data: bytes,
        dest_dir: Path,
        repo_root: Path,
    ) -> int:
        """Extract flexipage XML files from the retrieve zip."""
        count = 0
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            for name in zf.namelist():
                # Metadata API zips use paths like:
                # unpackaged/flexipages/MyPage.flexipage
                if name.endswith(".flexipage"):
                    basename = name.rsplit("/", 1)[-1]
                    # Convert MDAPI name to source format name
                    dest_name = basename + "-meta.xml"
                    dest = dest_dir / dest_name
                    dest.write_bytes(zf.read(name))
                    self.logger.info(
                        f"  [retrieved] {dest_name}"
                        f" -> {dest.relative_to(repo_root)}"
                    )
                    count += 1
        return count
