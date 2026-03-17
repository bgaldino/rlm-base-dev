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
    Creates the org-wide email address used as the PRM community email sender,
    and optionally updates an existing Network's emailSenderAddress to match.

    Run this AFTER create_partner_central so the Network exists and can be
    updated. The metadata deploy (deploy_post_prm) requires emailSenderAddress
    in the Network metadata to match the actual Network value — this task
    ensures both are aligned.
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
        "network_name": {
            "description": (
                "Name of the Network (Experience Cloud site) to update with the "
                "OWA email address. If provided, the Network's emailSenderAddress "
                "is updated via REST API after the OWA is created."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        email_address = self.options.get("email_address", "steelbrick_demo@salesforce.com")
        display_name = self.options.get("display_name", "rlm")
        network_name = self.options.get("network_name", "rlm")

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

        # Update the Network's emailSenderAddress to match the OWA
        if network_name:
            soql = f"SELECT Id, Name, EmailSenderAddress FROM Network WHERE Name = '{network_name}' LIMIT 1"
            response = requests.get(query_url, headers=headers, params={"q": soql})
            response.raise_for_status()
            result = response.json()

            if result.get("totalSize", 0) == 0:
                self.logger.info(
                    f"Network '{network_name}' not found — skipping emailSenderAddress update."
                )
                return

            network = result["records"][0]
            current_email = network.get("EmailSenderAddress", "")

            if current_email == email_address:
                self.logger.info(
                    f"Network '{network_name}' emailSenderAddress already set to '{email_address}', skipping update."
                )
                return

            network_id = network["Id"]
            patch_url = f"{instance_url}/services/data/v{api_version}/sobjects/Network/{network_id}"
            response = requests.patch(
                patch_url,
                headers=headers,
                json={"EmailSenderAddress": email_address},
            )
            if response.status_code == 204:
                self.logger.info(
                    f"Updated Network '{network_name}' emailSenderAddress to '{email_address}'."
                )
            else:
                try:
                    errors = response.json()
                except Exception:
                    errors = response.text
                self.logger.warning(
                    f"Could not update Network '{network_name}' emailSenderAddress: {errors}"
                )


class PatchNetworkEmailForDeploy(BaseTask):
    """
    Reads the current emailSenderAddress from an existing Network via SOQL, then
    patches the Network's .network-meta.xml file on disk with that value before
    the metadata deploy runs.

    Background: Salesforce requires emailSenderAddress in Network metadata for
    both CREATE and UPDATE operations, but the field is immutable after creation
    via all APIs. This task ensures the XML contains the org's actual value so
    the deploy does not attempt to change it.

    Run this AFTER create_partner_central and BEFORE deploy_post_prm.
    """

    task_options = {
        "network_name": {
            "description": "API name of the Network to query (default: rlm).",
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
        network_name = self.options.get("network_name", "rlm")
        default_xml_path = (
            "unpackaged/post_prm/force-app/main/default/networks/rlm.network-meta.xml"
        )
        xml_path = self.options.get("network_meta_xml_path", default_xml_path)

        if not hasattr(self, "org_config") or not self.org_config:
            raise TaskOptionsError("No org_config available")

        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = (
            getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "66.0")
        )

        headers = {"Authorization": f"Bearer {access_token}"}
        query_url = f"{instance_url}/services/data/v{api_version}/query"
        soql = f"SELECT Id, EmailSenderAddress FROM Network WHERE Name = '{network_name}' LIMIT 1"
        response = requests.get(query_url, headers=headers, params={"q": soql})
        response.raise_for_status()
        result = response.json()

        if result.get("totalSize", 0) == 0:
            self.logger.warning(
                f"Network '{network_name}' not found — skipping network-meta.xml patch."
            )
            return

        current_email = result["records"][0].get("EmailSenderAddress", "")
        if not current_email:
            self.logger.warning(
                f"Network '{network_name}' has no EmailSenderAddress — skipping patch."
            )
            return

        repo_root = self.project_config.repo_root
        abs_xml_path = os.path.join(repo_root, xml_path)

        with open(abs_xml_path, "r", encoding="utf-8") as f:
            xml_content = f.read()

        new_tag = f"<emailSenderAddress>{current_email}</emailSenderAddress>"
        if "<emailSenderAddress>" in xml_content:
            xml_content = re.sub(
                r"<emailSenderAddress>[^<]*</emailSenderAddress>",
                new_tag,
                xml_content,
            )
            self.logger.info(
                f"Patched emailSenderAddress to '{current_email}' in {xml_path}."
            )
        else:
            if "<emailSenderName>" in xml_content:
                xml_content = xml_content.replace(
                    "<emailSenderName>",
                    f"{new_tag}\n    <emailSenderName>",
                    1,
                )
            else:
                xml_content = xml_content.replace(
                    "</Network>",
                    f"    {new_tag}\n</Network>",
                    1,
                )
            self.logger.info(
                f"Inserted emailSenderAddress '{current_email}' into {xml_path}."
            )

        with open(abs_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)


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
        "site_meta_xml_path": {
            "description": (
                "Relative path (from repo root) to the .site-meta.xml file to patch "
                "(default: unpackaged/post_payments/sites/Payments_Webhook.site-meta.xml)."
            ),
            "required": False,
        },
    }

    def _run_task(self):
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
            new_tag = f"<{tag}>{username}</{tag}>"
            xml_content = re.sub(
                rf"<{tag}>[^<]*</{tag}>",
                new_tag,
                xml_content,
            )

        with open(abs_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        self.logger.info(
            f"Patched siteAdmin and siteGuestRecordDefaultOwner to '{username}' in {xml_path}."
        )
