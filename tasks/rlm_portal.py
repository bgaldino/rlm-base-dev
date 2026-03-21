"""
CumulusCI tasks for the Revenue Cloud Portal (rlm-webapp) feature flag.

Tasks:
  ConfigurePortalWebapp  — queries the RLMPortal Connected App's Consumer Key
                           from the org (via Tooling API) and writes
                           rlm-webapp/.env.local so Vite picks up the correct
                           instanceUrl and clientId automatically.

Usage:
  cci task run configure_portal_webapp --org <alias>

The task is a no-op when portal=false (enforced by the when: condition in the
prepare_portal flow).  Run it standalone after creating a new org or after the
Connected App is re-deployed.
"""

import os

import requests

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class ConfigurePortalWebapp(BaseTask):
    """
    Reads the RLM Portal Connected App's Consumer Key from the org and writes
    rlm-webapp/.env.local with VITE_SF_INSTANCE_URL and VITE_SF_CLIENT_ID.

    Vite automatically loads .env.local at dev-server startup, so the webapp
    will connect to the correct org without any manual config editing.

    The .env.local file is gitignored — it is never committed.
    """

    task_docs = """
    After `deploy_portal_connected_app` has created the RLM Portal Connected App,
    this task:

    1. Queries the ConnectedApplication Tooling API object for the Consumer Key.
    2. Resolves the org's instance URL from org_config.
    3. Writes ``rlm-webapp/.env.local`` with::

         VITE_SF_INSTANCE_URL=https://<org>.my.salesforce.com
         VITE_SF_CLIENT_ID=<consumerKey>

    The webapp's ``src/config.js`` reads these env vars at build/dev time via
    ``import.meta.env``, falling back to the hardcoded values for manual setups.
    """

    task_options = {
        "connected_app_name": {
            "description": (
                "Label of the Connected App to look up in the org "
                "(default: 'RLM Portal')."
            ),
            "required": False,
        },
        "env_file_path": {
            "description": (
                "Relative path from the repo root to the .env.local file to write "
                "(default: 'rlm-webapp/.env.local')."
            ),
            "required": False,
        },
        "extra_callback_urls": {
            "description": (
                "Comma-separated list of additional callback URLs to add to the "
                "Connected App (e.g. your Heroku URL). These are appended to the "
                "existing callbackUrl list via a PATCH on the ConnectedApplication "
                "record. Optional."
            ),
            "required": False,
        },
    }

    def _run_task(self):
        app_name = self.options.get("connected_app_name", "RLM Portal")
        env_path = self.options.get("env_file_path", "rlm-webapp/.env.local")
        extra_urls = self.options.get("extra_callback_urls", "")

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

        # ── 1. Query ConsumerKey via Tooling API ─────────────────────────────
        # ConnectedApplication is the Tooling API object; Name matches the label.
        tooling_url = (
            f"{instance_url}/services/data/v{api_version}/tooling/query"
        )
        app_name_escaped = app_name.replace("'", "\\'")
        soql = (
            f"SELECT Id, Name, ConsumerKey FROM ConnectedApplication "
            f"WHERE Name = '{app_name_escaped}' LIMIT 1"
        )
        self.logger.info(f"Querying Tooling API for Connected App '{app_name}'...")
        resp = requests.get(tooling_url, headers=headers, params={"q": soql})
        resp.raise_for_status()
        result = resp.json()

        if result.get("totalSize", 0) == 0:
            raise TaskOptionsError(
                f"Connected App '{app_name}' not found in org. "
                "Run deploy_portal_connected_app first."
            )

        record = result["records"][0]
        consumer_key = record["ConsumerKey"]
        app_id = record["Id"]
        self.logger.info(f"Found Connected App '{app_name}' — ConsumerKey: {consumer_key[:12]}...")

        # ── 2. Optionally patch extra callback URLs ───────────────────────────
        if extra_urls.strip():
            new_urls = [u.strip() for u in extra_urls.split(",") if u.strip()]
            self._add_callback_urls(instance_url, api_version, headers, app_id, new_urls)

        # ── 3. Write rlm-webapp/.env.local ───────────────────────────────────
        repo_root = self.project_config.repo_root
        abs_env_path = os.path.join(repo_root, env_path)
        os.makedirs(os.path.dirname(abs_env_path), exist_ok=True)

        env_content = (
            "# Revenue Cloud Portal — auto-generated by CCI configure_portal_webapp\n"
            "# Do NOT commit this file — it contains org-specific values.\n"
            "# Re-run `cci task run configure_portal_webapp --org <alias>` after org changes.\n"
            f"VITE_SF_INSTANCE_URL={instance_url}\n"
            f"VITE_SF_CLIENT_ID={consumer_key}\n"
        )

        with open(abs_env_path, "w", encoding="utf-8") as f:
            f.write(env_content)

        self.logger.info(f"Wrote {env_path} with instance URL and Client ID.")
        self.logger.info(
            "Start (or restart) the Vite dev server to pick up the new values:\n"
            "  cd rlm-webapp && npm run dev"
        )

    def _add_callback_urls(self, instance_url, api_version, headers, app_id, new_urls):
        """
        Append new_urls to the Connected App's callbackUrl list via Tooling API PATCH.
        Only adds URLs that are not already present.
        """
        tooling_base = f"{instance_url}/services/data/v{api_version}/tooling"

        # Fetch current callback URLs
        detail_resp = requests.get(
            f"{tooling_base}/sobjects/ConnectedApplication/{app_id}",
            headers=headers,
        )
        detail_resp.raise_for_status()
        detail = detail_resp.json()

        # callbackUrl is a newline-separated string in Tooling API
        existing_raw = detail.get("oauthConfig", {}).get("callbackUrl", "")
        existing = [u.strip() for u in existing_raw.splitlines() if u.strip()]

        to_add = [u for u in new_urls if u not in existing]
        if not to_add:
            self.logger.info("All extra callback URLs already present — skipping patch.")
            return

        updated = existing + to_add
        updated_str = "\n".join(updated)

        patch_resp = requests.patch(
            f"{tooling_base}/sobjects/ConnectedApplication/{app_id}",
            headers=headers,
            json={"oauthConfig": {"callbackUrl": updated_str}},
        )
        if patch_resp.status_code == 204:
            self.logger.info(f"Added callback URLs: {', '.join(to_add)}")
        else:
            try:
                err = patch_resp.json()
            except Exception:
                err = patch_resp.text
            self.logger.warning(f"Could not patch callback URLs: {err}")
