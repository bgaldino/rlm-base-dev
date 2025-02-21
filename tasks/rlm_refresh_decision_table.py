import requests
from cumulusci.tasks.sfdx import SFDXBaseTask
from cumulusci.core.keychain import BaseProjectKeychain
from abc import abstractmethod

# ExtendStandardContext is a custom task that extends the SFDXBaseTask provided by CumulusCI.
class RefreshDecisionTable(SFDXBaseTask):
    
    # Task options are used to set up configuration settings for this particular task.
    task_options = {
        "access_token": {
            "description": "The access token for the org. Defaults to the project default",
        },
        "developerNames": {
            "description": "Required. API name of an active decision table that you want to refresh.",
            "required": True,
        },
        "isIncremental": {
            "description": "Specifies whether to trigger an incremental refresh (true) or not (false). If set to true, this field triggers an update only on changes made to the recent sObject data instead of performing a full refresh.",
            "required": False,
        },
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
        
        # Debug: Print the type and content of self.options
        self.logger.info(f"Type of self.options: {type(self.options)}")
        self.logger.info(f"Content of self.options: {self.options}")

        # Check if self.options is a list (which it shouldn't be)
        if isinstance(self.options, list):
            raise TypeError("self.options is a list, but it should be a dictionary. This is likely a configuration issue.")

        # Safely get developerNames and isIncremental
        developer_names = self.options.get("developerNames")
        is_incremental = self.options.get("isIncremental", False)

        # Debug: Print the values of developer_names and is_incremental
        self.logger.info(f"developer_names: {developer_names}")
        self.logger.info(f"is_incremental: {is_incremental}")

        # Check if developer_names is None or empty
        if not developer_names:
            raise ValueError("developerNames is required but was not provided or is empty")

        # Convert to list if it's a string
        if isinstance(developer_names, str):
            developer_names = [developer_names]
        elif not isinstance(developer_names, list):
            raise ValueError(f"developerNames must be a string or a list of strings, but got {type(developer_names)}")

        for developer_name in developer_names:
            self._refresh_decision_table(developer_name, is_incremental)

    # Core logic to refresh decision tables
    def _refresh_decision_table(self, developer_name, is_incremental):
        url, headers = self._build_url_and_headers("actions/standard/refreshDecisionTable")
        payload = {
            "inputs": [
                {
                    "decisionTableApiName": developer_name,
                    "isIncremental": is_incremental
                }
            ]
        }
        response = self._make_request("post", url, headers=headers, json=payload)
        if response:
            # Debug: Print the type and content of the response
            self.logger.info(f"Type of response: {type(response)}")
            self.logger.info(f"Content of response: {response}")

            # Handle the case where response is a list
            if isinstance(response, list):
                if len(response) > 0:
                    result = response[0]
                else:
                    self.logger.warning(f"Empty response list for Decision Table '{developer_name}'")
                    return
            elif isinstance(response, dict):
                result = response
            else:
                raise TypeError(f"Unexpected response type: {type(response)}")

            # Process the result
            success = result.get('isSuccess')
            if success:
                self.logger.info(f"Decision Table '{developer_name}' Refresh Process Success: {success}")
                status = result.get('outputValues', {}).get('Status')
                if status:
                    self.logger.info(f"Refresh Status: {status}")
            else:
                self.logger.error(f"Decision Table '{developer_name}' Refresh Process Failed")
                errors = result.get('errors', [])
                for error in errors:
                    if isinstance(error, dict):
                        self.logger.error(f"Error: {error.get('message', 'Unknown error')}")
                    else:
                        self.logger.error(f"Error: {error}")
        else:
            self.logger.error(f"No response received for Decision Table '{developer_name}'")

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
