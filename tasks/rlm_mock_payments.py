"""Provision the opt-in mock payment gateway and its test configuration."""

from __future__ import annotations

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


class MockPaymentGateway(BaseSalesforceApiTask):
    """Provision the opt-in mock payment gateway and merchant account."""

    task_options = {
        "api_version": {
            "description": "Salesforce API version override.",
            "required": False,
        },
    }

    def _run_task(self) -> None:
        self._ensure_gateway()

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
                "SELECT Id, PaymentGatewayProviderId, MerchantCredentialId, MerchantAccountId, "
                "GatewayMode, PaymentStatus, Status "
                f"FROM PaymentGateway WHERE PaymentGatewayName = '{GATEWAY_NAME}'",
            ),
            "mock payment gateway",
        )
        expected = {
            "PaymentGatewayProviderId": provider_id,
            "MerchantCredentialId": credential["Id"],
            "MerchantAccountId": merchant,
            "GatewayMode": "Test",
            "PaymentStatus": "Enabled",
            "Status": "Active",
        }
        if gateway:
            if any(gateway.get(key) != value for key, value in expected.items()):
                raise TaskOptionsError(
                    "An existing RLM Mock Payments gateway has conflicting provider, credential, merchant, mode, payment, or status settings."
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
            "SELECT Id, PaymentInstrumentType, SortOrder FROM MerchAccPaymentMethodType "
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
            elif matches[0]["SortOrder"] != sort_order:
                raise TaskOptionsError(
                    f"The RLM mock payment method set has a conflicting sort order for {payment_type}."
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
                "SELECT Id, Mode, Status, PaymentStatus, PayoutStatus FROM MerchantAccount "
                f"WHERE Name = '{MERCHANT_NAME}'",
            ),
            "mock merchant account",
        )
        if merchant:
            if any(
                merchant.get(field) != value
                for field, value in {
                    "Mode": "Test",
                    "Status": "Active",
                    "PaymentStatus": "Enabled",
                    "PayoutStatus": "Disabled",
                }.items()
            ):
                raise TaskOptionsError(
                    "An existing RLM Mock Merchant has conflicting mode, payment, payout, or status settings."
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

    @staticmethod
    def _one(records: List[Dict[str, Any]], label: str) -> Dict[str, Any] | None:
        if len(records) > 1:
            raise TaskOptionsError(f"Found multiple {label} records; refusing ambiguous setup.")
        return records[0] if records else None
