"""
Custom CumulusCI tasks for Partner Relationship Management (PRM) community setup.
"""
import os
import re
import requests

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class SetupPrmOrgEmail(BaseTask):
    """
    Creates the org-wide email address used as the PRM community email sender.

    Note: Network.EmailSenderAddress is immutable after creation and cannot be
    updated via the REST API. The patch_network_email_for_deploy task handles
    aligning the repo metadata file with the Network's existing email for deploy.
    """

    task_options = {
        "email_address": {
            "description": "Email address to create as an org-wide email address.",
            "required": False,
        },
        "display_name": {
            "description": "Display name for the org-wide email address.",
            "required": False,
        },
    }

    def _run_task(self):
        email_address = self.options.get("email_address", "steelbrick_demo@salesforce.com")
        display_name = self.options.get("display_name", "rlm")

        if not hasattr(self, "org_config") or not self.org_config:
            raise TaskOptionsError("No org_config available")

        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = (
            getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "66.0")
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        query_url = f"{instance_url}/services/data/v{api_version}/query"

        # Check if OWA already exists
        soql = f"SELECT Id, Address, DisplayName FROM OrgWideEmailAddress WHERE Address = '{email_address}' LIMIT 1"
        response = requests.get(query_url, headers=headers, params={"q": soql})
        response.raise_for_status()
        result = response.json()

        if result.get("totalSize", 0) > 0:
            record = result["records"][0]
            self.logger.info(
                f"OrgWideEmailAddress '{email_address}' already exists (Id: {record['Id']}), skipping creation."
            )
        else:
            # Create OWA via REST API
            create_url = f"{instance_url}/services/data/v{api_version}/sobjects/OrgWideEmailAddress"
            payload = {"Address": email_address, "DisplayName": display_name}
            response = requests.post(create_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()

            if result.get("success"):
                self.logger.info(
                    f"Created OrgWideEmailAddress '{email_address}' (Id: {result['id']})."
                )
            else:
                errors = result.get("errors", [])
                raise Exception(f"Failed to create OrgWideEmailAddress: {errors}")


class PatchNetworkEmailForDeploy(BaseTask):
    """
    Replaces the placeholder emailSenderAddress in the Network .network-meta.xml
    with the Network's actual current EmailSenderAddress so the metadata deploy succeeds.
    The repo file must contain the placeholder (non-PII); run revert_network_email_after_deploy
    after deploy to restore the placeholder so the repo never stores the real email.

    Background: Salesforce requires emailSenderAddress in Network metadata for UPDATE
    operations, and the field is immutable after Network creation. The committed file uses
    a placeholder; this task reads the Network's actual current value and substitutes it
    only during deployment so the deployed value exactly matches the org's existing value.

    Run AFTER create_partner_central and BEFORE deploy_post_prm.
    """

    task_options = {
        "placeholder_email": {
            "description": (
                "Placeholder value in the repo file to replace with the Network's actual "
                "EmailSenderAddress (default: rlm-network-sender@example.com)."
            ),
            "required": False,
        },
        "network_name": {
            "description": (
                "Name of the Network record to read EmailSenderAddress from "
                "(default: rlm)."
            ),
            "required": False,
        },
        "network_meta_xml_path": {
            "description": (
                "Relative path (from repo root) to the .network-meta.xml file "
                "to patch (default: unpackaged/post_prm/force-app/main/default/"
                "networks/rlm.network-meta.xml)."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        placeholder = self.options.get(
            "placeholder_email", "rlm-network-sender@example.com"
        )
        network_name = self.options.get("network_name", "rlm")
        default_xml_path = (
            "unpackaged/post_prm/force-app/main/default/networks/rlm.network-meta.xml"
        )
        xml_path = self.options.get("network_meta_xml_path", default_xml_path)

        if not hasattr(self, "org_config") or not self.org_config:
            raise TaskOptionsError("No org_config available")

        instance_url = self.org_config.instance_url
        api_version = (
            getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "66.0")
        )
        headers = {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }
        query_url = f"{instance_url}/services/data/v{api_version}/query"
        network_name_escaped = network_name.replace("'", "''")
        soql = f"SELECT EmailSenderAddress FROM Network WHERE Name = '{network_name_escaped}' LIMIT 1"
        response = requests.get(query_url, headers=headers, params={"q": soql})
        response.raise_for_status()
        result = response.json()
        if result.get("totalSize", 0) == 0:
            raise TaskOptionsError(
                f"Network '{network_name}' not found in org. "
                "Ensure create_partner_central has run before this task."
            )
        deploy_email = result["records"][0].get("EmailSenderAddress", "").strip()
        if not deploy_email:
            raise TaskOptionsError(
                f"Network '{network_name}' has no EmailSenderAddress set."
            )

        repo_root = self.project_config.repo_root
        abs_xml_path = os.path.join(repo_root, xml_path)

        with open(abs_xml_path, "r", encoding="utf-8") as f:
            xml_content = f.read()

        placeholder_tag = f"<emailSenderAddress>{placeholder}</emailSenderAddress>"
        if placeholder_tag not in xml_content:
            raise TaskOptionsError(
                f"Placeholder '{placeholder}' not found in {xml_path}. "
                "Ensure the repo file contains the placeholder before deploying."
            )

        xml_content = xml_content.replace(
            placeholder_tag,
            f"<emailSenderAddress>{deploy_email}</emailSenderAddress>",
        )

        with open(abs_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        self.logger.info(
            f"Patched emailSenderAddress to Network '{network_name}' value in {xml_path} (for deploy only)."
        )


class RevertNetworkEmailAfterDeploy(BaseTask):
    """
    Restores the placeholder emailSenderAddress in the Network .network-meta.xml
    after deploy_post_prm so the repo never stores the target org's real email.

    Run AFTER deploy_post_prm in the same flow so the file on disk is reverted
    before the next commit.
    """

    task_options = {
        "placeholder_email": {
            "description": (
                "Placeholder value to write back into the file "
                "(default: rlm-network-sender@example.com). Must match the value used in the repo."
            ),
            "required": False,
        },
        "network_meta_xml_path": {
            "description": (
                "Relative path (from repo root) to the .network-meta.xml file "
                "(default: unpackaged/post_prm/force-app/main/default/networks/rlm.network-meta.xml)."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        placeholder = self.options.get(
            "placeholder_email", "rlm-network-sender@example.com"
        )
        default_xml_path = (
            "unpackaged/post_prm/force-app/main/default/networks/rlm.network-meta.xml"
        )
        xml_path = self.options.get("network_meta_xml_path", default_xml_path)
        repo_root = self.project_config.repo_root
        abs_xml_path = os.path.join(repo_root, xml_path)

        with open(abs_xml_path, "r", encoding="utf-8") as f:
            xml_content = f.read()

        if "<emailSenderAddress>" not in xml_content:
            self.logger.warning(
                f"No emailSenderAddress element in {xml_path}; skipping revert."
            )
            return

        xml_content = re.sub(
            r"<emailSenderAddress>[^<]*</emailSenderAddress>",
            f"<emailSenderAddress>{placeholder}</emailSenderAddress>",
            xml_content,
        )

        with open(abs_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        self.logger.info(
            f"Reverted emailSenderAddress to placeholder in {xml_path}."
        )


class PatchPaymentsSiteForDeploy(BaseTask):
    """
    Reads the current authenticated user's username from the org and patches
    the Payments_Webhook.site-meta.xml on disk before the metadata deploy runs.

    Background: CustomSite metadata requires siteAdmin and siteGuestRecordDefaultOwner
    to reference a User that exists in the target org. The committed XML contains the
    scratch org test user, which doesn't exist in non-scratch orgs. This task replaces
    those fields with the CCI-authenticated user's username before deploy.

    Run this BEFORE deploy_post_payments_site.
    """

    task_options = {
        "placeholder_username": {
            "description": (
                "Placeholder value in the repo file to replace with the running user username "
                "(default: payments-site-admin@example.com)."
            ),
            "required": False,
        },
        "site_meta_xml_path": {
            "description": (
                "Relative path (from repo root) to the .site-meta.xml file to patch "
                "(default: unpackaged/post_payments/sites/Payments_Webhook.site-meta.xml)."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        placeholder = self.options.get(
            "placeholder_username", "payments-site-admin@example.com"
        )
        default_xml_path = (
            "unpackaged/post_payments/sites/Payments_Webhook.site-meta.xml"
        )
        xml_path = self.options.get("site_meta_xml_path", default_xml_path)

        if not hasattr(self, "org_config") or not self.org_config:
            raise TaskOptionsError("No org_config available")

        username = self.org_config.username
        if not username:
            raise TaskOptionsError("Could not determine org username from org_config")

        repo_root = self.project_config.repo_root
        abs_xml_path = os.path.join(repo_root, xml_path)

        with open(abs_xml_path, "r", encoding="utf-8") as f:
            xml_content = f.read()

        for tag in ("siteAdmin", "siteGuestRecordDefaultOwner"):
            placeholder_tag = f"<{tag}>{placeholder}</{tag}>"
            if placeholder_tag not in xml_content:
                raise TaskOptionsError(
                    f"Placeholder '{placeholder}' not found in <{tag}> in {xml_path}. "
                    "Ensure the repo file contains the placeholder before deploying."
                )
            xml_content = xml_content.replace(
                placeholder_tag,
                f"<{tag}>{username}</{tag}>",
            )

        with open(abs_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        self.logger.info(
            f"Patched siteAdmin and siteGuestRecordDefaultOwner to '{username}' in {xml_path}."
        )


class RevertPaymentsSiteAfterDeploy(BaseTask):
    """
    Restores the placeholder siteAdmin and siteGuestRecordDefaultOwner in
    Payments_Webhook.site-meta.xml after deploy_post_payments_site so the repo
    never stores the target org's real username.

    Run AFTER deploy_post_payments_site in the same flow.
    """

    task_options = {
        "placeholder_username": {
            "description": (
                "Placeholder value to write back into the file "
                "(default: payments-site-admin@example.com). Must match the value used in the repo."
            ),
            "required": False,
        },
        "site_meta_xml_path": {
            "description": (
                "Relative path (from repo root) to the .site-meta.xml file "
                "(default: unpackaged/post_payments/sites/Payments_Webhook.site-meta.xml)."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        placeholder = self.options.get(
            "placeholder_username", "payments-site-admin@example.com"
        )
        default_xml_path = (
            "unpackaged/post_payments/sites/Payments_Webhook.site-meta.xml"
        )
        xml_path = self.options.get("site_meta_xml_path", default_xml_path)
        repo_root = self.project_config.repo_root
        abs_xml_path = os.path.join(repo_root, xml_path)

        with open(abs_xml_path, "r", encoding="utf-8") as f:
            xml_content = f.read()

        for tag in ("siteAdmin", "siteGuestRecordDefaultOwner"):
            xml_content = re.sub(
                rf"<{tag}>[^<]*</{tag}>",
                f"<{tag}>{placeholder}</{tag}>",
                xml_content,
            )

        with open(abs_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        self.logger.info(
            f"Reverted siteAdmin and siteGuestRecordDefaultOwner to placeholder in {xml_path}."
        )
