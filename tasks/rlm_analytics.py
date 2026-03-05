import json
import requests

from cumulusci.core.tasks import BaseTask
from cumulusci.core.exceptions import TaskOptionsError


class EnableAnalyticsReplication(BaseTask):
    """
    Enables CRM Analytics data replication via the Wave REST API.

    PATCH /services/data/v{api_version}/wave/settings
          { "enableWaveReplication": true }

    MDAPI deployment of AnalyticsSettings raises AutoInstallException
    (setCommitAllowed=false) in scratch orgs, so this task calls the
    Wave API directly instead.
    """

    task_docs = (
        "Enable CRM Analytics data replication by patching the Wave REST API "
        "settings endpoint. Equivalent to toggling 'Enable Replication' in "
        "Setup → CRM Analytics → Settings."
    )

    def _run_task(self):
        access_token = self.org_config.access_token
        instance_url = self.org_config.instance_url
        api_version = (
            getattr(self.org_config, "api_version", None)
            or self.project_config.project__package__api_version
            or "66.0"
        )

        url = f"{instance_url}/services/data/v{api_version}/wave/settings"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = {"enableWaveReplication": True}

        self.logger.info("Enabling CRM Analytics replication via Wave REST API...")
        self.logger.info(f"PATCH {url}")

        response = requests.patch(url, headers=headers, json=payload)

        if response.status_code in (200, 204):
            self.logger.info("CRM Analytics replication enabled successfully.")
        else:
            raise TaskOptionsError(
                f"Failed to enable CRM Analytics replication: "
                f"{response.status_code} {response.text}"
            )
