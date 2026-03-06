"""
Custom CumulusCI tasks for Partner Relationship Management (PRM) community setup.
"""
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

    In scratch orgs no email verification is required, so the address is immediately
    usable. Must run before deploy_post_prm so the Network is created with the
    correct emailSenderAddress (the field is immutable once the Network exists).
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

        # Check if OWA already exists
        query_url = f"{instance_url}/services/data/v{api_version}/query"
        soql = f"SELECT Id, Address, DisplayName FROM OrgWideEmailAddress WHERE Address = '{email_address}' LIMIT 1"
        response = requests.get(query_url, headers=headers, params={"q": soql})
        response.raise_for_status()
        result = response.json()

        if result.get("totalSize", 0) > 0:
            record = result["records"][0]
            self.logger.info(
                f"OrgWideEmailAddress '{email_address}' already exists (Id: {record['Id']}), skipping creation."
            )
            return

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
