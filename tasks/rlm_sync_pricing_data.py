import requests
from cumulusci.tasks.sfdx import SFDXBaseTask
from cumulusci.core.keychain import BaseProjectKeychain
from abc import abstractmethod

# ExtendStandardContext is a custom task that extends the SFDXBaseTask provided by CumulusCI.
class SyncPricingData(SFDXBaseTask):
    
    # Task options are used to set up configuration settings for this particular task.
    task_options = {
        'access_token': {
            'description': 'The access token for the org. Defaults to the project default',
        }
    }

    # Initialize the task options and environment variables    
    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        self.env = self._get_env()

    # Load keychain with either the current keychain or generate a new one based on environment configuration
    def _load_keychain(self):
        if not hasattr(self, 'keychain') or not self.keychain:
            keychain_class = self.get_keychain_class() or BaseProjectKeychain
            keychain_key = self.get_keychain_key() if keychain_class.encrypted else None
            self.keychain = keychain_class(self.project_config or self.universal_config, keychain_key)
            if self.project_config:
                self.project_config.keychain = self.keychain

    # Prepare runtime by loading keychain and setting up access token and instance URL from options or defaults
    def _prep_runtime(self):
        self._load_keychain()
        self.access_token = self.options.get("access_token", self.org_config.access_token)
        self.instance_url = self.options.get("instance_url", self.org_config.instance_url)

    # Execute the task after preparation, where the core functionality will be implemented
    def _run_task(self):
        self._prep_runtime()
        self._extend_context_definition()

    # Core logic to extend an existing context definition
    def _extend_context_definition(self):
        url, headers = self._build_url_and_headers("connect/core-pricing/sync/syncData")

        response = self._make_request("get", url, headers=headers)
        if response:
            self.success = response.get('success')
            if self.success:
                self.logger.info(f"Sync Process Success: {self.success}")

    # Helper to construct the request URL and headers for making API calls
    def _build_url_and_headers(self, endpoint):
        url = f"{self.instance_url}/services/data/v{self.project_config.project__package__api_version}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        return url, headers

    # Make an HTTP request using the requests library and handle the response
    def _make_request(self, method, url, **kwargs):
        response = requests.request(method, url, **kwargs)
        if response.ok:
            return response.json()
        else:
            self.logger.error(f"Failed {method.upper()} request to {url}: {response.text}")
            return None

    # Abstract method to get the keychain class, needs to be implemented by subclasses
    @abstractmethod
    def get_keychain_class(self):
        pass

    # Abstract method to retrieve the keychain key, needs to be implemented by subclasses
    @abstractmethod
    def get_keychain_key(self):
        pass
