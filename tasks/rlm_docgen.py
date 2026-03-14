"""
CumulusCI tasks for Document Generation post-deploy fixes.

FixDocumentTemplateBinaries
    Salesforce metadata API bug: when multiple DocumentTemplates are deployed in
    a single batch, ALL of them receive the same ContentDocument binary (the first
    one processed, alphabetically). This task corrects each template's ContentDocument
    by uploading the proper .dt binary from the repo.

    Run after deploy_post_docgen + activate_docgen_templates.
"""
import base64
import glob
import os
import xml.etree.ElementTree as ET

try:
    from cumulusci.tasks.salesforce import BaseSalesforceApiTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceApiTask = object
    TaskOptionsError = Exception

METADATA_NS = "http://soap.sforce.com/2006/04/metadata"


class FixDocumentTemplateBinaries(BaseSalesforceApiTask):
    """
    Correct DocumentTemplate ContentDocument binaries after a batch metadata deploy.

    Salesforce's metadata API assigns the same ContentDocument binary to every
    DocumentTemplate deployed in a single request (alphabetically first wins).
    This task reads each .dt file from the repo and creates a new ContentVersion
    for the corresponding ContentDocument in the DocGen library, replacing the
    wrong binary with the correct one.

    Must run after deploy_post_docgen and activate_docgen_templates.
    """

    task_options = {
        "templates_dir": {
            "description": (
                "Directory containing .dt and .dt-meta.xml files. "
                "Defaults to unpackaged/post_docgen/documentTemplates."
            ),
            "required": False,
            "default": "unpackaged/post_docgen/documentTemplates",
        },
        "library_developer_name": {
            "description": (
                "DeveloperName of the DocGen ContentWorkspace library. "
                "Defaults to DocgenDocumentTemplateLibrary."
            ),
            "required": False,
            "default": "DocgenDocumentTemplateLibrary",
        },
    }

    def _run_task(self):
        templates_dir = self.options.get(
            "templates_dir", "unpackaged/post_docgen/documentTemplates"
        )
        library_dev_name = self.options.get(
            "library_developer_name", "DocgenDocumentTemplateLibrary"
        )

        # Find the DocGen library
        safe_lib = library_dev_name.replace("'", "\\'")
        result = self.sf.query(
            f"SELECT Id FROM ContentWorkspace "
            f"WHERE DeveloperName = '{safe_lib}' LIMIT 1"
        )
        if not result["records"]:
            raise TaskOptionsError(
                f"ContentWorkspace with DeveloperName '{library_dev_name}' not found. "
                f"Run create_docgen_library first."
            )
        library_id = result["records"][0]["Id"]
        self.logger.info(f"DocGen library: {library_id}")

        # Enumerate .dt files — exclude macOS/editor temp files (e.g. ~$...)
        dt_files = sorted(
            f for f in glob.glob(os.path.join(templates_dir, "*.dt"))
            if not os.path.basename(f).startswith("~")
        )
        if not dt_files:
            self.logger.warning(f"No .dt files found in {templates_dir}")
            return

        fixed = 0
        eligible = 0
        for dt_path in dt_files:
            meta_path = dt_path + "-meta.xml"
            if not os.path.exists(meta_path):
                self.logger.warning(f"No meta.xml for {dt_path}, skipping")
                continue

            template_name = self._parse_template_name(meta_path)
            if not template_name:
                self.logger.warning(f"Could not read <name> from {meta_path}, skipping")
                continue

            self.logger.info(f"Fixing binary for template: {template_name}")

            content_doc_id = self._find_latest_content_doc(library_id, template_name)
            if not content_doc_id:
                self.logger.warning(
                    f"No ContentDocument for '{template_name}' in library — "
                    f"deploy may not have run yet, or library name mismatch"
                )
                continue

            eligible += 1
            self._upload_correct_binary(content_doc_id, template_name, dt_path)
            fixed += 1

        self.logger.info(
            f"Fixed {fixed}/{eligible} DocumentTemplate binaries "
            f"({len(dt_files)} .dt files found, {len(dt_files) - eligible} skipped)."
        )

    def _parse_template_name(self, meta_path):
        """Return the <name> value from a .dt-meta.xml file."""
        try:
            tree = ET.parse(meta_path)
            root = tree.getroot()
            # ElementTree includes namespace in tag — try both with and without
            for tag in (f"{{{METADATA_NS}}}name", "name"):
                el = root.find(tag)
                if el is not None and el.text:
                    return el.text.strip()
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse {meta_path}: {e}")
        return None

    def _find_latest_content_doc(self, library_id, template_name):
        """
        Return the ContentDocumentId of the most recently created ContentDocument
        in the DocGen library whose Title matches template_name.
        """
        safe_name = template_name.replace("'", "\\'")
        result = self.sf.query(
            f"SELECT Id, CreatedDate FROM ContentDocument "
            f"WHERE Title = '{safe_name}' "
            f"AND Id IN ("
            f"  SELECT ContentDocumentId FROM ContentWorkspaceDoc "
            f"  WHERE ContentWorkspaceId = '{library_id}'"
            f") "
            f"ORDER BY CreatedDate DESC LIMIT 1"
        )
        records = result.get("records", [])
        if not records:
            return None
        doc_id = records[0]["Id"]
        self.logger.debug(
            f"  ContentDocument {doc_id} (created {records[0]['CreatedDate']})"
        )
        return doc_id

    def _upload_correct_binary(self, content_doc_id, template_name, dt_path):
        """
        Create a new ContentVersion for content_doc_id using the binary from dt_path.
        The .dt file is a valid DOCX (ZIP) and can be uploaded as-is.
        """
        with open(dt_path, "rb") as f:
            raw = f.read()

        version_data = base64.b64encode(raw).decode("utf-8")
        file_size_kb = len(raw) // 1024

        self.logger.info(
            f"  Uploading {file_size_kb}KB binary for ContentDocument {content_doc_id}"
        )

        response = self.sf.ContentVersion.create(
            {
                "ContentDocumentId": content_doc_id,
                "Title": template_name,
                "PathOnClient": f"{template_name}.docx",
                "VersionData": version_data,
            }
        )

        if response.get("id"):
            self.logger.info(
                f"  Created ContentVersion {response['id']} for {template_name}"
            )
        else:
            raise Exception(
                f"Failed to create ContentVersion for {template_name}: {response}"
            )


# TODO: PatchDocumentTemplateLogos task — fetch the active BrandingSet logo asset
# (e.g. via ConnectApi or ContentAsset query) and patch the DocumentTemplate
# ContentDocument binary to replace the embedded QuantumBit logo image with the
# org's current brand logo. This cannot be done purely through metadata deploy
# because logo references inside DOCX binaries are embedded image bytes, not
# metadata-resolvable references. Implement as a CCI task that: (1) queries the
# org for the active BrandingSet primary logo ContentAsset, (2) downloads the
# image bytes, (3) unpacks the .dt ZIP, (4) replaces the logo image in
# word/media/, updates the image dimensions in word/document.xml if needed, and
# (5) re-uploads via FixDocumentTemplateBinaries-style ContentVersion creation.
