"""Provision the opt-in mock payment gateway and seed test saved methods."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Tuple

import requests

try:
    from cumulusci.core.exceptions import TaskOptionsError
    from cumulusci.tasks.salesforce import BaseSalesforceApiTask
except ImportError:
    BaseSalesforceApiTask = object
    TaskOptionsError = Exception


ADAPTER_CLASS = "RLM_MockPaymentGatewayAdapter"
PROVIDER_NAME = "RLM_MockPaymentGateway"
GATEWAY_NAME = "RLM Mock Payments"
MERCHANT_NAME = "RLM Mock Merchant"
CREDENTIAL_NAME = "RLM_MockPayments"
PAYMENT_METHOD_SET_KEY = "RLM_Mock_Card_ACH"
PAYMENT_METHOD_TYPES = {
    "card": 1,
    "us_bank_account": 2,
}
GATEWAY_PROVIDER_PAYMENT_METHOD_TYPES = {
    "card": "CardPaymentMethod",
    "us_bank_account": "AlternativePaymentMethod",
}
SCENARIOS = {
    "Success": "MOCK:SUCCESS",
    "Decline": "MOCK:DECLINE",
    "Invalid": "MOCK:INVALID",
    "Gateway Error": "MOCK:ERROR",
}


class MockPaymentGateway(BaseSalesforceApiTask):
    """Ensure mock gateway configuration or seed saved methods for one account."""

    task_options = {
        "operation": {
            "description": "Operation: 'ensure' gateway setup or 'seed' saved methods.",
            "required": True,
        },
        "account_id": {
            "description": "Account ID required for the 'seed' operation.",
            "required": False,
        },
        "api_version": {
            "description": "Salesforce API version override.",
            "required": False,
        },
    }

    def _run_task(self) -> None:
        operation = (self.options.get("operation") or "").strip().lower()
        if operation == "ensure":
            self._ensure_gateway()
        elif operation == "seed":
            self._seed_methods()
        else:
            raise TaskOptionsError("operation must be 'ensure' or 'seed'")

    def _api_context(self) -> Tuple[str, str, str]:
        token = self.org_config.access_token
        instance = self.org_config.instance_url.rstrip("/")
        version = (
            self.options.get("api_version")
            or getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "68.0")
        )
        return token, instance, version

    def _headers(self, token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _url(self, instance: str, version: str, path: str, tooling: bool = False) -> str:
        prefix = "/services/data/v" + version + ("/tooling" if tooling else "")
        return f"{instance}{prefix}/{path.lstrip('/')}"

    def _query(
        self, token: str, instance: str, version: str, soql: str, tooling: bool = False
    ) -> List[Dict[str, Any]]:
        response = requests.get(
            self._url(instance, version, "query", tooling),
            headers=self._headers(token),
            params={"q": soql},
            timeout=30,
        )
        if not response.ok:
            raise TaskOptionsError(f"Salesforce query failed ({response.status_code}): {response.text}")
        body = response.json()
        records = body.get("records", [])
        while not body.get("done", True) and body.get("nextRecordsUrl"):
            response = requests.get(
                f"{instance}{body['nextRecordsUrl']}",
                headers=self._headers(token),
                timeout=30,
            )
            if not response.ok:
                raise TaskOptionsError(
                    f"Salesforce query pagination failed ({response.status_code}): {response.text}"
                )
            body = response.json()
            records.extend(body.get("records", []))
        return records

    def _create(
        self,
        token: str,
        instance: str,
        version: str,
        object_name: str,
        record: Dict[str, Any],
        tooling: bool = False,
    ) -> str:
        response = requests.post(
            self._url(instance, version, f"sobjects/{object_name}", tooling),
            headers=self._headers(token),
            json=record,
            timeout=30,
        )
        if not response.ok:
            raise TaskOptionsError(
                f"Creating {object_name} failed ({response.status_code}): {response.text}"
            )
        return response.json()["id"]

    def _update(
        self,
        token: str,
        instance: str,
        version: str,
        object_name: str,
        record_id: str,
        record: Dict[str, Any],
    ) -> None:
        response = requests.patch(
            self._url(instance, version, f"sobjects/{object_name}/{record_id}"),
            headers=self._headers(token),
            json=record,
            timeout=30,
        )
        if not response.ok:
            raise TaskOptionsError(
                f"Updating {object_name} failed ({response.status_code}): {response.text}"
            )

    @staticmethod
    def _escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace("'", "\\'")

    def _ensure_gateway(self) -> None:
        token, instance, version = self._api_context()
        credential = self._one(
            self._query(
                token,
                instance,
                version,
                "SELECT Id, DeveloperName FROM NamedCredential "
                f"WHERE DeveloperName = '{CREDENTIAL_NAME}'",
            ),
            "Named Credential",
        )
        if not credential:
            raise TaskOptionsError(
                "RLM_MockPayments Named Credential is missing. Deploy the payments extension metadata first."
            )

        adapter = self._one(
            self._query(
                token,
                instance,
                version,
                "SELECT Id, Name FROM ApexClass "
                f"WHERE Name = '{ADAPTER_CLASS}'",
                tooling=True,
            ),
            "Apex adapter class",
        )
        if not adapter:
            raise TaskOptionsError(f"Apex adapter {ADAPTER_CLASS} is not deployed.")

        provider = self._one(
            self._query(
                token,
                instance,
                version,
                "SELECT Id, ApexAdapterId, IdempotencySupported FROM PaymentGatewayProvider "
                f"WHERE DeveloperName = '{PROVIDER_NAME}'",
                tooling=True,
            ),
            "mock payment gateway provider",
        )
        if not provider:
            raise TaskOptionsError(
                "RLM_MockPaymentGateway provider metadata is missing. Deploy the payments extension before running ensure_mock_payment_gateway."
            )
        if (
            provider["ApexAdapterId"] != adapter["Id"]
            or provider["IdempotencySupported"] != "No"
        ):
            raise TaskOptionsError(
                "An existing RLM_MockPaymentGateway provider has conflicting adapter or idempotency settings."
            )
        provider_id = provider["Id"]

        merchant = self._ensure_merchant(token, instance, version)
        gateway = self._one(
            self._query(
                token,
                instance,
                version,
                "SELECT Id, PaymentGatewayProviderId, MerchantCredentialId, MerchantAccountId, Status "
                f"FROM PaymentGateway WHERE PaymentGatewayName = '{GATEWAY_NAME}'",
            ),
            "mock payment gateway",
        )
        expected = {
            "PaymentGatewayProviderId": provider_id,
            "MerchantCredentialId": credential["Id"],
            "MerchantAccountId": merchant,
            "Status": "Active",
        }
        if gateway:
            if any(gateway.get(key) != value for key, value in expected.items()):
                raise TaskOptionsError(
                    "An existing RLM Mock Payments gateway has conflicting provider, credential, merchant, or status."
                )
            gateway_id = gateway["Id"]
        else:
            gateway_id = self._create(
                token,
                instance,
                version,
                "PaymentGateway",
                {
                    "PaymentGatewayName": GATEWAY_NAME,
                    **expected,
                    "GatewayMode": "Test",
                    "PaymentStatus": "Enabled",
                },
            )
        method_set = self._ensure_payment_method_set(
            token, instance, version, merchant
        )
        self._ensure_provider_payment_method_types(
            token, instance, version, provider_id
        )
        self.logger.info(
            f"Mock payment gateway ready: provider={provider_id}, gateway={gateway_id}, "
            f"merchant={merchant}, payment_method_set_key={method_set}."
        )

    def _ensure_payment_method_set(
        self, token: str, instance: str, version: str, merchant_id: str
    ) -> str:
        method_set = self._one(
            self._query(
                token,
                instance,
                version,
                "SELECT Id, MerchantAccountId FROM MerchAccPaymentMethodSet "
                f"WHERE DeveloperName = '{PAYMENT_METHOD_SET_KEY}'",
            ),
            "mock payment method set",
        )
        if method_set:
            if method_set["MerchantAccountId"] != merchant_id:
                raise TaskOptionsError(
                    "The RLM mock payment method set key already belongs to a different merchant account."
                )
            method_set_id = method_set["Id"]
        else:
            method_set_id = self._create(
                token,
                instance,
                version,
                "MerchAccPaymentMethodSet",
                {
                    "DeveloperName": PAYMENT_METHOD_SET_KEY,
                    "MerchantAccountId": merchant_id,
                },
            )

        existing_types = self._query(
            token,
            instance,
            version,
            "SELECT Id, PaymentInstrumentType FROM MerchAccPaymentMethodType "
            f"WHERE PaymentMethodSetId = '{self._escape(method_set_id)}'",
        )
        by_type: Dict[str, List[Dict[str, Any]]] = {}
        for record in existing_types:
            by_type.setdefault(record["PaymentInstrumentType"], []).append(record)

        for payment_type, sort_order in PAYMENT_METHOD_TYPES.items():
            matches = by_type.get(payment_type, [])
            if len(matches) > 1:
                raise TaskOptionsError(
                    f"The RLM mock payment method set has duplicate {payment_type} entries."
                )
            if not matches:
                self._create(
                    token,
                    instance,
                    version,
                    "MerchAccPaymentMethodType",
                    {
                        "PaymentMethodSetId": method_set_id,
                        "PaymentInstrumentType": payment_type,
                        "SortOrder": sort_order,
                    },
                )
        return PAYMENT_METHOD_SET_KEY

    def _ensure_provider_payment_method_types(
        self, token: str, instance: str, version: str, provider_id: str
    ) -> None:
        existing_types = self._query(
            token,
            instance,
            version,
            "SELECT Id, DeveloperName, PaymentMethodType, GtwyProviderPaymentMethodType "
            "FROM GtwyProvPaymentMethodType "
            f"WHERE PaymentGatewayProviderId = '{self._escape(provider_id)}'",
        )
        by_gateway_type: Dict[str, List[Dict[str, Any]]] = {}
        for record in existing_types:
            by_gateway_type.setdefault(
                record["GtwyProviderPaymentMethodType"], []
            ).append(record)

        for gateway_type, salesforce_type in GATEWAY_PROVIDER_PAYMENT_METHOD_TYPES.items():
            matches = by_gateway_type.get(gateway_type, [])
            if len(matches) > 1:
                raise TaskOptionsError(
                    f"The RLM mock gateway provider has duplicate {gateway_type} payment-type mappings."
                )
            if matches:
                if matches[0]["PaymentMethodType"] != salesforce_type:
                    raise TaskOptionsError(
                        f"The RLM mock gateway provider has a conflicting mapping for {gateway_type}."
                    )
                continue

            developer_name = "RLM_Mock_" + "".join(
                character if character.isalnum() else "_"
                for character in gateway_type
            ).strip("_")
            self._create(
                token,
                instance,
                version,
                "GtwyProvPaymentMethodType",
                {
                    "DeveloperName": developer_name[:80],
                    "MasterLabel": f"RLM Mock {gateway_type} payment type",
                    "PaymentGatewayProviderId": provider_id,
                    "PaymentMethodType": salesforce_type,
                    "GtwyProviderPaymentMethodType": gateway_type,
                },
            )

    def _ensure_merchant(self, token: str, instance: str, version: str) -> str:
        merchant = self._one(
            self._query(
                token,
                instance,
                version,
                "SELECT Id, Mode, Status FROM MerchantAccount "
                f"WHERE Name = '{MERCHANT_NAME}'",
            ),
            "mock merchant account",
        )
        if merchant:
            if merchant["Mode"] != "Test" or merchant["Status"] != "Active":
                raise TaskOptionsError(
                    "An existing RLM Mock Merchant has conflicting mode or status."
                )
            return merchant["Id"]
        return self._create(
            token,
            instance,
            version,
            "MerchantAccount",
            {
                "Name": MERCHANT_NAME,
                "Mode": "Test",
                "Status": "Active",
                "CountryIsoCode": "US",
                "CurrencyIsoCode": "USD",
                "PaymentStatus": "Enabled",
                "PayoutStatus": "Disabled",
            },
        )

    def _seed_methods(self) -> None:
        account_id = (self.options.get("account_id") or "").strip()
        if not account_id or not account_id.startswith("001"):
            raise TaskOptionsError("account_id must be an Account ID for the 'seed' operation.")

        token, instance, version = self._api_context()
        accounts = self._query(
            token,
            instance,
            version,
            "SELECT Id, BillingStreet, BillingCity, BillingState, BillingPostalCode, "
            "BillingCountry FROM Account "
            f"WHERE Id = '{self._escape(account_id)}'",
        )
        if not accounts:
            raise TaskOptionsError("The supplied Account ID is not visible in this org.")
        account = accounts[0]
        default_billing_address = {
            "BillingStreet": "1 Market St",
            "BillingCity": "San Francisco",
            "BillingState": "CA",
            "BillingPostalCode": "94105",
            "BillingCountry": "US",
        }
        missing_billing_fields = {
            field: value
            for field, value in default_billing_address.items()
            if not account.get(field)
        }
        if missing_billing_fields:
            self._update(
                token,
                instance,
                version,
                "Account",
                account_id,
                missing_billing_fields,
            )
            self.logger.info(
                "Filled missing billing address fields on the selected test Account."
            )

        gateway = self._one(
            self._query(
                token,
                instance,
                version,
                "SELECT Id, MerchantAccountId FROM PaymentGateway "
                f"WHERE PaymentGatewayName = '{GATEWAY_NAME}' AND Status = 'Active'",
            ),
            "active mock payment gateway",
        )
        if not gateway or not gateway.get("MerchantAccountId"):
            raise TaskOptionsError("Run ensure_mock_payment_gateway before seeding methods.")

        existing = self._query(
            token,
            instance,
            version,
            "SELECT Id, Name, AccountHolderName, AccountHolderEmail, ExpiryMonth, "
            "ExpiryYear, BillingStreet, BillingCity, BillingState, BillingPostalCode, "
            "BillingCountry FROM SavedPaymentMethod "
            f"WHERE ReferenceOwnerId = '{self._escape(account_id)}' "
            f"AND PaymentGatewayId = '{gateway['Id']}'",
        )
        existing_by_name = {record.get("Name"): record for record in existing}
        created = 0
        for name, gateway_token in SCENARIOS.items():
            record_name = f"RLM Mock {name}"
            previous = existing_by_name.get(record_name)
            complete_name = record_name + " Complete"
            complete = existing_by_name.get(complete_name)
            if complete and all(
                complete.get(field)
                for field in (
                    "AccountHolderName",
                    "AccountHolderEmail",
                    "ExpiryMonth",
                    "ExpiryYear",
                    "BillingStreet",
                    "BillingCity",
                    "BillingState",
                    "BillingPostalCode",
                    "BillingCountry",
                )
            ):
                continue
            if previous and all(
                previous.get(field)
                for field in (
                    "AccountHolderName",
                    "AccountHolderEmail",
                    "ExpiryMonth",
                    "ExpiryYear",
                    "BillingStreet",
                    "BillingCity",
                    "BillingState",
                    "BillingPostalCode",
                    "BillingCountry",
                )
            ):
                continue
            # SavedPaymentMethod records aren't updateable. If an earlier version
            # of this task already created a sparse scenario, add a complete
            # companion record with a distinct mock token instead of attempting
            # an update or leaving the account without realistic billing data.
            if previous:
                record_name += " Complete"
                gateway_token += ":COMPLETE"
            self._create(
                token,
                instance,
                version,
                "SavedPaymentMethod",
                {
                    "Name": record_name,
                    "ReferenceOwnerId": account_id,
                    "PaymentGatewayId": gateway["Id"],
                    "MerchantAccountId": gateway["MerchantAccountId"],
                    "Status": "Active",
                    "UsageType": "OffSession",
                    "IsDefault": False,
                    "IsMerchantCreated": True,
                    "IsSharedWithinSameAccount": False,
                    "Type": "card",
                    "GatewayReference": f"mock-saved-{name.lower().replace(' ', '-')}",
                    "GatewayToken": gateway_token,
                    "Checksum": hashlib.sha256(gateway_token.encode()).hexdigest()[:63],
                    "Last4": "4242",
                    "Network": "Visa",
                    "AccountHolderName": "RLM Billing Test",
                    "AccountHolderEmail": "mock-billing-test@example.invalid",
                    "ExpiryMonth": 12,
                    "ExpiryYear": 2030,
                    "NickName": "Visa" if name == "Success" else f"Visa · {name}",
                    "BillingStreet": "1 Market St",
                    "BillingCity": "San Francisco",
                    "BillingState": "CA",
                    "BillingPostalCode": "94105",
                    "BillingCountry": "US",
                },
            )
            created += 1
        ach_record_name = "RLM Mock ACH Success"
        if ach_record_name not in existing_by_name:
            self._create(
                token,
                instance,
                version,
                "SavedPaymentMethod",
                {
                    "Name": ach_record_name,
                    "ReferenceOwnerId": account_id,
                    "PaymentGatewayId": gateway["Id"],
                    "MerchantAccountId": gateway["MerchantAccountId"],
                    "Status": "Active",
                    "UsageType": "OffSession",
                    "IsDefault": False,
                    "IsMerchantCreated": True,
                    "IsSharedWithinSameAccount": False,
                    "Type": "us_bank_account",
                    "BankName": "RLM Mock Bank",
                    "BankCode": "000000000",
                    "BankAccountType": "Checking",
                    "BankAccountHolderType": "Individual",
                    "GatewayReference": f"mock-ach-{account_id}",
                    "GatewayToken": "MOCK:SUCCESS:ACH",
                    "Checksum": hashlib.sha256(b"MOCK:SUCCESS:ACH").hexdigest()[:63],
                    "Last4": "6789",
                    "AccountHolderName": "RLM Billing Test",
                    "AccountHolderEmail": "mock-billing-test@example.invalid",
                    "NickName": "Checking account",
                    "BillingStreet": "1 Market St",
                    "BillingCity": "San Francisco",
                    "BillingState": "CA",
                    "BillingPostalCode": "94105",
                    "BillingCountry": "US",
                },
            )
            created += 1
            self.logger.info(
                f"Created a synthetic ACH test method for Account {account_id}."
            )
        self.logger.info(
            f"Created {created} mock saved payment method(s) for Account {account_id}; existing scenarios were kept."
        )

    @staticmethod
    def _one(records: List[Dict[str, Any]], label: str) -> Dict[str, Any] | None:
        if len(records) > 1:
            raise TaskOptionsError(f"Found multiple {label} records; refusing ambiguous setup.")
        return records[0] if records else None
