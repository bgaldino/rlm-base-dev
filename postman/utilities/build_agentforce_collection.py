#!/usr/bin/env python3
"""
Agentforce Revenue Management APIs (v66.0) Postman Collection Generator

Generates a comprehensive Postman collection JSON file containing all Business APIs
from the Revenue Cloud Developer Guide v260 (Spring '26, API v66.0).

Includes:
- Product Catalog Management (17 endpoints)
- Product Discovery (10 endpoints)
- Salesforce Pricing (19 endpoints)
- Product Configurator (13 endpoints)
- Rate Management (2 endpoints)
- Transaction Management (17 endpoints)
- Usage Management (6 endpoints)
- Billing (30 endpoints)
- Context Service (5 endpoints)
- Setup Runner (SOQL queries + auth)
- Runner workflows (Quote-to-Cash, eCommerce, Billing)

Author: Claude (Anthropic)
Date: 2026-03-26
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime


class PostmanCollectionBuilder:
    """Builds a Postman collection JSON structure."""

    def __init__(self, collection_name: str, description: str):
        self.collection_name = collection_name
        self.description = description
        self.items: List[Dict[str, Any]] = []
        self.variables: List[Dict[str, Any]] = []
        self._setup_variables()

    def _setup_variables(self):
        """Initialize default collection variables."""
        self.variables = [
            {
                "key": "_endpoint",
                "value": "https://your-instance.salesforce.com",
                "type": "string",
                "description": "Salesforce org endpoint"
            },
            {
                "key": "version",
                "value": "66.0",
                "type": "string",
                "description": "API version (v66.0 for Spring '26)"
            },
            {
                "key": "url",
                "value": "https://login.salesforce.com",
                "type": "string",
                "description": "Login URL (login.salesforce.com or test.salesforce.com)"
            },
            {
                "key": "clientId",
                "value": "",
                "type": "string",
                "description": "OAuth2 Client ID"
            },
            {
                "key": "clientSecret",
                "value": "",
                "type": "string",
                "description": "OAuth2 Client Secret"
            },
            {
                "key": "accessToken",
                "value": "",
                "type": "string",
                "description": "OAuth2 Access Token (auto-refreshed)"
            },
            {
                "key": "tokenExpiry",
                "value": "0",
                "type": "string",
                "description": "Token expiry timestamp"
            },
            # Common IDs from setup runner (mirrors old-collection env var names)
            {"key": "defaultAccountId",                    "value": "", "type": "string", "description": "Account ID set by Setup Runner"},
            {"key": "standardPricebookId",                 "value": "", "type": "string", "description": "Standard Pricebook ID"},
            {"key": "defaultCatalogId",                    "value": "", "type": "string", "description": "Default Product Catalog ID"},
            {"key": "defaultCategoryId",                   "value": "", "type": "string", "description": "Default Product Category ID"},
            {"key": "defaultOneTimePSM",                   "value": "", "type": "string", "description": "One-Time Product Selling Model ID"},
            {"key": "defaultEvergreenMonthlyPSM",          "value": "", "type": "string", "description": "Evergreen Monthly PSM ID"},
            {"key": "defaultEvergreenAnnualPSM",           "value": "", "type": "string", "description": "Evergreen Annual PSM ID"},
            {"key": "defaultTermDefinedMonthlyPSM",        "value": "", "type": "string", "description": "Term Monthly PSM ID"},
            {"key": "defaultTermDefinedAnnualPSM",         "value": "", "type": "string", "description": "Term Annual PSM ID"},
            {"key": "defaultOneTimeProductId",             "value": "", "type": "string", "description": "One-Time Product ID"},
            {"key": "defaultOneTimePBE",                   "value": "", "type": "string", "description": "One-Time PricebookEntry ID"},
            {"key": "defaultEvergreenMonthlyProductId",    "value": "", "type": "string", "description": "Evergreen Monthly Product ID"},
            {"key": "defaultEvergreenMonthlyPBE",          "value": "", "type": "string", "description": "Evergreen Monthly PBE ID"},
            {"key": "defaultEvergreenAnnualProductId",     "value": "", "type": "string", "description": "Evergreen Annual Product ID"},
            {"key": "defaultEvergreenAnnualPBE",           "value": "", "type": "string", "description": "Evergreen Annual PBE ID"},
            {"key": "defaultTermDefinedAnnualProductId",   "value": "", "type": "string", "description": "Term Annual Product ID"},
            {"key": "defaultTermDefinedAnnualPBE",         "value": "", "type": "string", "description": "Term Annual PBE ID"},
            {"key": "defaultTermDefinedMonthlyProductId",  "value": "", "type": "string", "description": "Term Monthly Product ID"},
            {"key": "defaultTermDefinedMonthlyPBE",        "value": "", "type": "string", "description": "Term Monthly PBE ID"},
            {"key": "defaultContextDefintionId",           "value": "", "type": "string", "description": "Default Context Definition ID"},
            {"key": "defaultContextMappingId",             "value": "", "type": "string", "description": "Default Context Mapping ID"},
            {"key": "defaultContextMappingName",           "value": "", "type": "string", "description": "Default Context Mapping Name"},
            {"key": "defaultPricingProcedureId",           "value": "", "type": "string", "description": "Default Pricing Procedure ID"},
            {"key": "defaultPricingProcedureName",         "value": "", "type": "string", "description": "Default Pricing Procedure Name"},
            {"key": "customContextDefinitionId",           "value": "", "type": "string", "description": "Custom Context Definition ID"},
            {"key": "customContextMappingId",              "value": "", "type": "string", "description": "Custom Context Mapping ID"},
            {"key": "customContextMappingName",            "value": "", "type": "string", "description": "Custom Context Mapping Name"},
            {"key": "customPricingProcedureId",            "value": "", "type": "string", "description": "Custom Pricing Procedure ID"},
            {"key": "customPricingProcedureName",          "value": "", "type": "string", "description": "Custom Pricing Procedure Name"},
            {"key": "cartContextDefinitionId",             "value": "", "type": "string", "description": "Cart Context Definition ID"},
            {"key": "cartContextMappingId",                "value": "", "type": "string", "description": "Cart Context Mapping ID"},
            {"key": "cartPricingProcedureId",              "value": "", "type": "string", "description": "Cart Pricing Procedure ID"},
            {"key": "cartPricingProcedureName",            "value": "", "type": "string", "description": "Cart Pricing Procedure Name"},
            {"key": "pdContextDefinitionId",               "value": "", "type": "string", "description": "PD Context Definition ID"},
            {"key": "pdContextMappingId",                  "value": "", "type": "string", "description": "PD Context Mapping ID"},
            {"key": "pdContextMappingName",                "value": "", "type": "string", "description": "PD Context Mapping Name"},
            {"key": "pdPricingProcedureId",                "value": "", "type": "string", "description": "PD Pricing Procedure ID"},
            {"key": "pdPricingProcedureName",              "value": "", "type": "string", "description": "PD Pricing Procedure Name"},
            {"key": "qualificationProcedureId",            "value": "", "type": "string", "description": "Qualification Procedure ID"},
            {"key": "qualificationProcedureName",          "value": "", "type": "string", "description": "Qualification Procedure Name"},
            # New-collection generic IDs
            {"key": "pbeId",              "value": "", "type": "string", "description": "PricebookEntry ID"},
            {"key": "quoteId",            "value": "", "type": "string", "description": "Quote record ID"},
            {"key": "orderId",            "value": "", "type": "string", "description": "Order record ID"},
            {"key": "assetId",            "value": "", "type": "string", "description": "Asset record ID"},
            {"key": "invoiceId",          "value": "", "type": "string", "description": "Invoice record ID"},
            {"key": "billingScheduleId",  "value": "", "type": "string", "description": "Billing Schedule record ID"},
            {"key": "contextDefinitionId","value": "", "type": "string", "description": "Context Definition ID (generic)"},
        ]

    def add_folder(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a folder (request group)."""
        folder = {
            "name": name,
            "description": description,
            "item": [],
            "variable": []
        }
        self.items.append(folder)
        return folder

    def add_endpoint_to_folder(
        self,
        folder: Dict[str, Any],
        name: str,
        method: str,
        url: str,
        description: str = "",
        body: Optional[Dict[str, Any]] = None,
        params: Optional[List[Dict[str, str]]] = None,
        tests: Optional[str] = None,
        pre_request: Optional[str] = None,
    ):
        """Add an endpoint to a folder."""
        request_obj: Dict[str, Any] = {
            "method": method,
            "header": [
                {
                    "key": "Content-Type",
                    "value": "application/json",
                    "type": "text"
                },
                {
                    "key": "Authorization",
                    "value": "Bearer {{accessToken}}",
                    "type": "text"
                }
            ],
            "url": self._build_url_object(url)
        }

        if body:
            request_obj["body"] = {
                "mode": "raw",
                "raw": json.dumps(body, indent=2),
                "options": {"raw": {"language": "json"}}
            }

        if params:
            request_obj["url"]["query"] = params

        endpoint = {
            "name": name,
            "request": request_obj,
            "response": []
        }

        if description:
            endpoint["description"] = description

        if tests:
            endpoint["event"] = [
                {
                    "listen": "test",
                    "script": {
                        "exec": [tests],
                        "type": "text/javascript"
                    }
                }
            ]

        if pre_request:
            if "event" not in endpoint:
                endpoint["event"] = []
            endpoint["event"].append({
                "listen": "prerequest",
                "script": {
                    "exec": [pre_request],
                    "type": "text/javascript"
                }
            })

        folder["item"].append(endpoint)

    def _build_url_object(self, raw_url: str) -> dict:
        """Build a correct Postman URL object — no protocol field, host is just {{_endpoint}}."""
        obj: dict = {"raw": raw_url}
        if "/services/data/" in raw_url:
            after = raw_url.split("/services/data/", 1)[1]
            path_parts = ["services", "data"] + [p for p in after.split("/") if p or after.endswith("/")]
            obj["host"] = ["{{_endpoint}}"]
            obj["path"] = path_parts
            # Pull query params out of path if present
            if "?" in raw_url:
                base, qs = raw_url.split("?", 1)
                after_clean = base.split("/services/data/", 1)[1]
                obj["path"] = ["services", "data"] + [p for p in after_clean.split("/") if p]
                obj["query"] = [
                    {"key": k, "value": v}
                    for part in qs.split("&")
                    for k, v in [part.split("=", 1)] if "=" in part
                ]
        elif raw_url.startswith("{{url}}") or raw_url.startswith("{{_endpoint}}"):
            parts = raw_url.split("/")
            obj["host"] = [parts[0]]
            obj["path"] = [p for p in parts[1:] if p]
        return obj

    def build(self) -> Dict[str, Any]:
        """Build the complete collection JSON."""
        return {
            "info": {
                "name": self.collection_name,
                "description": self.description,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                "version": "1.0.0",
                "_exporter_id": str(uuid.uuid4())
            },
            "item": self.items,
            "variable": self.variables,
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{accessToken}}",
                        "type": "string"
                    }
                ]
            },
            "event": [
                {
                    "listen": "prerequest",
                    "script": {
                        "exec": [self._get_collection_pre_request_script()],
                        "type": "text/javascript"
                    }
                }
            ]
        }

    def _get_collection_pre_request_script(self) -> str:
        """Return the collection-level pre-request script for OAuth2 token refresh."""
        return """
// OAuth2 Token Refresh
const tokenUrl = pm.environment.get('url') + '/services/oauth2/token';
const clientId = pm.environment.get('clientId');
const clientSecret = pm.environment.get('clientSecret');

if (!pm.environment.get('accessToken') || pm.environment.get('tokenExpiry') < Date.now()) {
    pm.sendRequest({
        url: tokenUrl,
        method: 'POST',
        header: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: {
            mode: 'urlencoded',
            urlencoded: [
                { key: 'grant_type', value: 'client_credentials' },
                { key: 'client_id', value: clientId },
                { key: 'client_secret', value: clientSecret }
            ]
        }
    }, function (err, res) {
        if (!err && res.code === 200) {
            const json = res.json();
            pm.environment.set('accessToken', json.access_token);
            pm.environment.set('_endpoint', json.instance_url);
            pm.environment.set('tokenExpiry', Date.now() + 7200000);
        }
    });
}
"""

    def _get_soql_test_script(self, env_var: str, field: str = "Id") -> str:
        """Return a test script template for SOQL queries that extracts IDs."""
        return f"""let statusCode = pm.response.code;
pm.test(`Response code - Expected: 200 & Actual: ${{statusCode}}`, () => {{
    pm.expect(statusCode).to.eql(200);
}});
if (statusCode === 200) {{
    const response = pm.response.json();
    const firstRecordId = response.records && response.records[0] && response.records[0].{field};
    if (firstRecordId) {{
        pm.environment.set('{env_var}', firstRecordId);
    }}
}} else {{
    pm.execution.setNextRequest(null); // Stop the workflow if the status code is not 200
}}"""


def create_setup_runner(builder: PostmanCollectionBuilder):
    """Create the Setup Runner folder — full set from old Revenue Cloud collection + new unique entries."""
    folder = builder.add_folder(
        "⚙️ Setup Runner",
        "Environment setup via SOQL queries and OAuth2 authentication"
    )

    # ── Auth ──────────────────────────────────────────────────────────────────

    builder.add_endpoint_to_folder(
        folder, "Get Endpoint from User Info", "GET",
        "{{url}}{{site}}/services/oauth2/userinfo",
        "Retrieves the current user info and sets {{_endpoint}}. Run first.",
        tests="""let response = pm.response.json();
if (response.profile) {
    let profileUrl = response.profile;
    let thirdSlashIndex = profileUrl.indexOf('/', profileUrl.indexOf('//') + 2);
    let baseEndpoint = thirdSlashIndex !== -1 ? profileUrl.substring(0, thirdSlashIndex) : profileUrl;
    pm.environment.set("_endpoint", baseEndpoint);
    pm.test("Base URL extracted and set to _endpoint", () => {
        pm.expect(pm.environment.get("_endpoint")).to.eql(baseEndpoint);
    });
} else {
    pm.test("Profile URL is missing in the response", () => {
        pm.expect.fail("Profile URL not found in the response.");
    });
}"""
    )

    builder.add_endpoint_to_folder(
        folder, "Get Latest Release Version", "GET",
        "{{_endpoint}}/services/data/",
        "Lists available API versions and sets {{version}} and {{apiVersion}}.",
        tests="""let statusCode = pm.response.code;
pm.test(`Response code - Expected: 200 & Actual: ${statusCode}`, () => {
    pm.expect(statusCode).to.eql(200);
});
if (statusCode === 200) {
    const response = pm.response.json();
    const lastResponseItem = response[response.length - 1];
    if (lastResponseItem && lastResponseItem.version) {
        pm.environment.set("apiVersion", `v${lastResponseItem.version}`);
        pm.environment.set("version", lastResponseItem.version);
    }
} else {
    pm.execution.setNextRequest(null); // Stop the workflow if the status code is not 200
}"""
    )

    # ── Core record lookups (matches old Revenue Cloud collection) ────────────

    def _add_lookup(name, soql, env_var):
        url = f"{{{{_endpoint}}}}/services/data/v{{{{version}}}}/query?q={soql}"
        builder.add_endpoint_to_folder(
            folder, name, "GET", url,
            f"SOQL lookup: {soql}",
            tests=builder._get_soql_test_script(env_var)
        )

    _add_lookup(
        "Get Default Account",
        "SELECT Id, Name FROM Account WHERE Name = '{{defaultAccountName}}'",
        "defaultAccountId"
    )
    _add_lookup(
        "Get Standard Pricebook",
        "SELECT Id, Name FROM Pricebook2 WHERE Name='{{standardPricebookName}}' and IsActive = true",
        "standardPricebookId"
    )
    _add_lookup(
        "Get Default Catalog",
        "SELECT Id, Name FROM ProductCatalog WHERE name='{{defaultCatalogName}}'",
        "defaultCatalogId"
    )
    _add_lookup(
        "Get Default Category",
        "SELECT Id, Name FROM ProductCategory WHERE Name='{{defaultCategoryName}}' AND CatalogId='{{defaultCatalogId}}'",
        "defaultCategoryId"
    )

    # Product Selling Models (multi-record, custom script)
    psm_url = "{{_endpoint}}/services/data/v{{version}}/query?q=SELECT Id, Name, SellingModelType, PricingTermUnit  FROM ProductSellingModel"
    builder.add_endpoint_to_folder(
        folder, "Get Product Selling Models", "GET", psm_url,
        "Fetches all PSMs and sets env vars for each type/term combination.",
        tests="""let statusCode = pm.response.code;
pm.test(`Response code - Expected: 200 & Actual: ${statusCode}`, () => {
    pm.expect(statusCode).to.eql(200);
});
var response = pm.response.json();
response.records.forEach(function(record) {
    var sellingModelType = record.SellingModelType;
    var pricingTermUnit = record.PricingTermUnit;
    var id = record.Id;
    var prefix = "";
    if (sellingModelType === "OneTime") {
        prefix = "defaultOneTimePSM";
    } else if (sellingModelType === "TermDefined" || sellingModelType === "Evergreen") {
        var termUnit = pricingTermUnit === "Annual" ? "Annual" : pricingTermUnit === "Months" ? "Monthly" : "";
        prefix = "default" + sellingModelType + termUnit + "PSM";
    }
    if (prefix) { pm.environment.set(prefix, id); }
});"""
    )

    _add_lookup(
        "Get One Time Product",
        "SELECT Id, Name FROM Product2 WHERE Name = '{{defaultOneTimeProductName}}'",
        "defaultOneTimeProductId"
    )
    _add_lookup(
        "Get One Time PBE",
        "Select Id from PricebookEntry Where Product2Id='{{defaultOneTimeProductId}}' and ProductSellingModelId='{{defaultOneTimePSM}}' and Pricebook2Id = '{{standardPricebookId}}'",
        "defaultOneTimePBE"
    )
    _add_lookup(
        "Get Evergreen Monthly Product",
        "SELECT Id, Name FROM Product2 WHERE Name = '{{defaultEvergreenMonthlyProductName}}'",
        "defaultEvergreenMonthlyProductId"
    )
    _add_lookup(
        "Get Evergreen Monthly PBE",
        "Select Id from PricebookEntry Where Product2Id='{{defaultEvergreenMonthlyProductId}}' and ProductSellingModelId='{{defaultEvergreenMonthlyPSM}}' and Pricebook2Id='{{standardPricebookId}}'",
        "defaultEvergreenMonthlyPBE"
    )
    _add_lookup(
        "Get Evergreen Annual Product",
        "SELECT Id, Name FROM Product2 WHERE Name = '{{defaultEvergreenAnnualProductName}}'",
        "defaultEvergreenAnnualProductId"
    )
    _add_lookup(
        "Get Evergreen Annual PBE",
        "Select Id from PricebookEntry Where Product2Id='{{defaultEvergreenAnnualProductId}}' and ProductSellingModelId='{{defaultEvergreenAnnualPSM}}' and Pricebook2Id='{{standardPricebookId}}'",
        "defaultEvergreenAnnualPBE"
    )
    _add_lookup(
        "Get Term Annual Product",
        "SELECT Id, Name FROM Product2 WHERE Name = '{{defaultTermDefinedAnnualProductName}}'",
        "defaultTermDefinedAnnualProductId"
    )
    _add_lookup(
        "Get Term Annual PBE",
        "Select Id from PricebookEntry Where Product2Id='{{defaultTermDefinedAnnualProductId}}' and ProductSellingModelId='{{defaultTermDefinedAnnualPSM}}' and Pricebook2Id='{{standardPricebookId}}'",
        "defaultTermDefinedAnnualPBE"
    )
    _add_lookup(
        "Get Term Monthly Product",
        "SELECT Id, Name FROM Product2 WHERE Name = '{{defaultTermDefinedMonthlyProductName}}'",
        "defaultTermDefinedMonthlyProductId"
    )
    _add_lookup(
        "Get Term Monthly PBE",
        "Select Id from PricebookEntry Where Product2Id='{{defaultTermDefinedMonthlyProductId}}' and ProductSellingModelId='{{defaultTermDefinedMonthlyPSM}}' and Pricebook2Id='{{standardPricebookId}}'",
        "defaultTermDefinedMonthlyPBE"
    )

    # ── Context / Pricing Procedure lookups ───────────────────────────────────

    # Default context set
    _add_lookup(
        "Get Default Context Definition",
        "Select Id, DeveloperName from ContextDefinition Where DeveloperName='{{defaultContextDefinitionName}}'",
        "defaultContextDefintionId"
    )

    ctx_mapping_url = "{{_endpoint}}/services/data/v{{version}}/query?q=SELECT Id, Title FROM ContextMapping WHERE ContextDefinitionVersion.ContextDefinition.Id='{{defaultContextDefintionId}}' AND IsDefault=true"
    builder.add_endpoint_to_folder(
        folder, "Get Default Context Mapping", "GET", ctx_mapping_url,
        "Fetches the default ContextMapping and sets defaultContextMappingId and defaultContextMappingName.",
        tests="""let statusCode = pm.response.code;
pm.test(`Response code - Expected: 200 & Actual: ${statusCode}`, () => {
    pm.expect(statusCode).to.eql(200);
});
if (statusCode === 200) {
    const response = pm.response.json();
    const firstRecord = response.records && response.records[0];
    if (firstRecord) {
        pm.environment.set("defaultContextMappingId", firstRecord.Id);
        pm.environment.set("defaultContextMappingName", firstRecord.Title);
    }
} else {
    pm.execution.setNextRequest(null); // Halt the workflow if the status code isn't 200
}"""
    )
    _add_lookup(
        "Get Default Pricing Procedure",
        "Select Id, MasterLabel, DeveloperName from ExpressionSetDefinition Where DeveloperName='{{defaultPricingProcedureDeveloperName}}'",
        "defaultPricingProcedureId"
    )

    # Custom context set
    _add_lookup(
        "Get Custom Context Definition",
        "SELECT Id, DeveloperName FROM ContextDefinition WHERE DeveloperName='{{customContextDefinitionName}}'",
        "customContextDefinitionId"
    )
    ctx_custom_mapping_url = "{{_endpoint}}/services/data/v{{version}}/query?q=SELECT Id, Title FROM ContextMapping WHERE ContextDefinitionVersion.ContextDefinition.Id='{{customContextDefinitionId}}' AND IsDefault=true"
    builder.add_endpoint_to_folder(
        folder, "Get Custom Context Mapping", "GET", ctx_custom_mapping_url,
        "Fetches the custom ContextMapping.",
        tests="""let statusCode = pm.response.code;
pm.test(`Response code - Expected: 200 & Actual: ${statusCode}`, () => {
    pm.expect(statusCode).to.eql(200);
});
if (statusCode === 200) {
    const response = pm.response.json();
    const firstRecord = response.records && response.records[0];
    if (firstRecord) {
        pm.environment.set("customContextMappingId", firstRecord.Id);
        pm.environment.set("customContextMappingName", firstRecord.Title);
    }
} else {
    pm.execution.setNextRequest(null);
}"""
    )
    _add_lookup(
        "Get Custom Pricing Procedure",
        "Select Id, MasterLabel, DeveloperName from ExpressionSetDefinition Where DeveloperName='{{customPricingProcedureDeveloperName}}'",
        "customPricingProcedureId"
    )

    # Cart context set
    _add_lookup(
        "Get Cart Context Definition",
        "Select Id, DeveloperName from ContextDefinition Where DeveloperName='{{cartContextDefinitionName}}'",
        "cartContextDefinitionId"
    )
    ctx_cart_mapping_url = "{{_endpoint}}/services/data/v{{version}}/query?q=Select Id, Title from ContextMapping Where Title='{{cartContextMappingName}}'"
    builder.add_endpoint_to_folder(
        folder, "Get Cart Context Mapping", "GET", ctx_cart_mapping_url,
        "Fetches the cart ContextMapping.",
        tests="""let statusCode = pm.response.code;
pm.test(`Response code - Expected: 200 & Actual: ${statusCode}`, () => {
    pm.expect(statusCode).to.eql(200);
});
if (statusCode === 200) {
    const response = pm.response.json();
    const firstRecord = response.records && response.records[0];
    if (firstRecord) { pm.environment.set("cartContextMappingId", firstRecord.Id); }
} else { pm.execution.setNextRequest(null); }"""
    )
    _add_lookup(
        "Get Cart Pricing Procedure",
        "SELECT Id, MasterLabel, DeveloperName FROM ExpressionSetDefinition WHERE DeveloperName='{{cartPricingProcedureDeveloperName}}'",
        "cartPricingProcedureId"
    )

    # PD context set
    _add_lookup(
        "Get PD Context Definition",
        "SELECT Id, DeveloperName FROM ContextDefinition WHERE DeveloperName='{{pdContextDefinitionName}}'",
        "pdContextDefinitionId"
    )
    ctx_pd_mapping_url = "{{_endpoint}}/services/data/v{{version}}/query?q=SELECT Id, Title FROM ContextMapping WHERE ContextDefinitionVersion.ContextDefinition.Id='{{pdContextDefinitionId}}' AND IsDefault=true"
    builder.add_endpoint_to_folder(
        folder, "Get PD Context Mapping", "GET", ctx_pd_mapping_url,
        "Fetches the PD ContextMapping.",
        tests="""let statusCode = pm.response.code;
pm.test(`Response code - Expected: 200 & Actual: ${statusCode}`, () => {
    pm.expect(statusCode).to.eql(200);
});
if (statusCode === 200) {
    const response = pm.response.json();
    const firstRecord = response.records && response.records[0];
    if (firstRecord) {
        pm.environment.set("pdContextMappingId", firstRecord.Id);
        pm.environment.set("pdContextMappingName", firstRecord.Title);
    }
} else { pm.execution.setNextRequest(null); }"""
    )
    _add_lookup(
        "Get PD Pricing Procedure",
        "SELECT Id, MasterLabel, DeveloperName FROM ExpressionSetDefinition WHERE DeveloperName='{{pdPricingProcedureDeveloperName}}'",
        "pdPricingProcedureId"
    )
    _add_lookup(
        "Get Qualification Procedure",
        "SELECT Id, MasterLabel, DeveloperName FROM ExpressionSetDefinition WHERE DeveloperName='{{qualificationProcedureDeveloperName}}'",
        "qualificationProcedureId"
    )

    # ── New-collection generic lookups ────────────────────────────────────────
    _add_lookup("Lookup: PricingBookEntry",
        "SELECT Id, Pricebook2Id, Product2Id FROM PricebookEntry WHERE IsActive = true LIMIT 5",
        "pbeId")
    _add_lookup("Lookup: Quote",
        "SELECT Id, Name FROM Quote WHERE IsActive = false LIMIT 5",
        "quoteId")
    _add_lookup("Lookup: Order",
        "SELECT Id, OrderNumber FROM Order LIMIT 5",
        "orderId")
    _add_lookup("Lookup: Asset",
        "SELECT Id, Name FROM Asset LIMIT 5",
        "assetId")
    _add_lookup("Lookup: Context Definition",
        "SELECT Id, Name FROM ContextDefinition LIMIT 5",
        "contextDefinitionId")


def create_pcm_folder(builder: PostmanCollectionBuilder):
    """Create Product Catalog Management folder (17 endpoints)."""
    folder = builder.add_folder(
        "Product Catalog Management",
        "Create and manage product catalogs, categories, and product metadata"
    )

    # List Catalogs
    builder.add_endpoint_to_folder(
        folder,
        "PCM: List Catalogs",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/catalogs",
        "List all product catalogs with filtering and pagination.",
        body={
            "pageSize": 100,
            "offset": 0,
            "q": ""
        }
    )

    # Get Catalog
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Get Catalog",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/catalogs/{{defaultCatalogId}}",
        "Retrieve details for a specific product catalog."
    )

    # List Categories
    builder.add_endpoint_to_folder(
        folder,
        "PCM: List Categories",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/catalogs/{{defaultCatalogId}}/categories",
        "List all categories within a catalog."
    )

    # Get Category
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Get Category",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/categories/{{defaultCategoryId}}",
        "Retrieve details for a specific product category."
    )

    # List Products
    builder.add_endpoint_to_folder(
        folder,
        "PCM: List Products",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/products",
        "List products with filtering, sorting, and pagination.",
        body={
            "pageSize": 100,
            "offset": 0,
            "filters": [],
            "sortBy": "Name",
            "sortOrder": "ASC"
        }
    )

    # Get Product
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Get Product",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/products/{{defaultTermDefinedAnnualProductId}}",
        "Retrieve complete product details including attributes and relationships."
    )

    # Bulk Product Details
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Bulk Product Details",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/products/bulk",
        "Fetch details for multiple products in a single request.",
        body={
            "productIds": ["{{defaultTermDefinedAnnualProductId}}"]
        }
    )

    # Product Related Records
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Product Related Records",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/products/{{defaultTermDefinedAnnualProductId}}/related-records",
        "Retrieve related records for a product (variants, bundles, dependencies).",
        body={
            "relationshipTypes": ["VARIANTS", "BUNDLES"]
        }
    )

    # Product Classification Details (NEW v66.0)
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Product Classification Details (v66.0)",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/products/classification",
        "Retrieve product classification hierarchy and attributes (new in Spring '26).",
        body={
            "productIds": ["{{defaultTermDefinedAnnualProductId}}"],
            "includeHierarchy": True
        }
    )

    # Deep Clone
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Deep Clone Product",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/products/{{defaultTermDefinedAnnualProductId}}/actions/deep-clone",
        "Deep clone a product including all related records and configurations.",
        body={
            "cloneName": "Product Clone",
            "cloneAttributes": True,
            "cloneRelationships": True
        }
    )

    # Index Configuration Collection
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Index Configuration Collection",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/configurations",
        "Retrieve product index configurations."
    )

    # Update Index Configuration
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Update Index Configuration",
        "PUT",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/configurations",
        "Update product index configurations.",
        body={
            "indexConfigurations": [
                {
                    "id": "config-id",
                    "name": "Default Index",
                    "fields": ["Name", "Description", "SKU"]
                }
            ]
        }
    )

    # Index Setting
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Index Setting",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/setting",
        "Get current product index settings."
    )

    # Update Index Setting
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Update Index Setting",
        "PATCH",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/setting",
        "Update product index settings.",
        body={
            "indexingEnabled": True,
            "autoIndexFrequency": "DAILY",
            "batchSize": 1000
        }
    )

    # Snapshot Collection
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Snapshot Collection",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/snapshots",
        "List all product index snapshots."
    )

    # Deploy Snapshot
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Deploy Snapshot",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/snapshots/{snapshotId}/actions/deploy",
        "Deploy a product index snapshot to production.",
        body={
            "options": {
                "deploymentStrategy": "INCREMENTAL"
            }
        }
    )

    # Snapshot Index Error
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Snapshot Index Error",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/snapshots/{snapshotId}/errors",
        "Retrieve indexing errors for a snapshot."
    )

    # Unit of Measure Info
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Unit of Measure Info",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/unit-of-measure",
        "Get available units of measure."
    )

    # Unit of Measure Rounded Data
    builder.add_endpoint_to_folder(
        folder,
        "PCM: Unit of Measure Rounded Data",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/pcm/unit-of-measure/actions/round",
        "Round quantity values to the nearest unit of measure increment.",
        body={
            "quantity": 10.456,
            "unitOfMeasure": "LITRE",
            "decimalPlaces": 2
        }
    )


def create_product_discovery_folder(builder: PostmanCollectionBuilder):
    """Create Product Discovery folder (10 endpoints)."""
    folder = builder.add_folder(
        "Product Discovery",
        "Discover products for quotes and sales transactions via CPQ APIs"
    )

    # List Catalogs
    builder.add_endpoint_to_folder(
        folder,
        "Discovery: List Catalogs",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/catalogs",
        "List product catalogs available for quote configuration.",
        body={"pageSize": 100}
    )

    # Get Catalog
    builder.add_endpoint_to_folder(
        folder,
        "Discovery: Get Catalog",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/catalogs/{{defaultCatalogId}}",
        "Retrieve a specific catalog with all categories and products.",
        body={}
    )

    # List Categories
    builder.add_endpoint_to_folder(
        folder,
        "Discovery: List Categories",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/categories",
        "List product categories available for selection.",
        body={"pageSize": 100}
    )

    # Get Category
    builder.add_endpoint_to_folder(
        folder,
        "Discovery: Get Category",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/categories/{{defaultCategoryId}}",
        "Retrieve a specific category with child products.",
        body={}
    )

    # List Products
    builder.add_endpoint_to_folder(
        folder,
        "Discovery: List Products",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/products",
        "List products available for quote configuration.",
        body={
            "pageSize": 100,
            "offset": 0,
            "filters": []
        }
    )

    # Get Product
    builder.add_endpoint_to_folder(
        folder,
        "Discovery: Get Product",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/products/{{defaultTermDefinedAnnualProductId}}",
        "Retrieve product details including options and features for configuration.",
        body={}
    )

    # Global Search
    builder.add_endpoint_to_folder(
        folder,
        "Discovery: Global Search",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/products/search",
        "Search across all products by keyword.",
        body={
            "query": "software",
            "pageSize": 100,
            "filters": []
        }
    )

    # Bulk Product Details
    builder.add_endpoint_to_folder(
        folder,
        "Discovery: Bulk Product Details",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/products/bulk",
        "Fetch details for multiple products in one request.",
        body={
            "productIds": ["{{defaultTermDefinedAnnualProductId}}"]
        }
    )

    # Guided Selection
    builder.add_endpoint_to_folder(
        folder,
        "Discovery: Guided Selection",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/products/guided-selection",
        "Get product recommendations based on guided selling rules.",
        body={
            "accountId": "{{defaultAccountId}}",
            "criteria": {"industry": "Technology"}
        }
    )

    # Qualification
    builder.add_endpoint_to_folder(
        folder,
        "Discovery: Qualification",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/qualification",
        "Qualify products based on account, opportunity, or context criteria.",
        body={
            "accountId": "{{defaultAccountId}}",
            "qualificationCriteria": {"type": "ACCOUNT_BASED"}
        }
    )


def create_pricing_folder(builder: PostmanCollectionBuilder):
    """Create Salesforce Pricing folder (19 endpoints)."""
    folder = builder.add_folder(
        "Salesforce Pricing",
        "Core pricing engine, waterfall, and procedure plan definition endpoints"
    )

    # Core Pricing subfolder
    core_pricing = builder.add_folder(
        "Core Pricing",
        "PBE-derived pricing, price context, and execution"
    )
    folder["item"].append(core_pricing)

    # PBE Derived Pricing
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: PBE Derived Pricing",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/derived-pricing",
        "Get pricing derived from PricingBookEntry for a product.",
        body={
            "pricebookEntryId": "{{pbeId}}",
            "quantity": 100,
            "currencyCode": "USD"
        }
    )

    # Price Context
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: Price Context",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/price-context",
        "Build a price context for a transaction with account, products, and modifiers.",
        body={
            "accountId": "{{defaultAccountId}}",
            "effectiveDate": "2026-03-26",
            "pricingInputs": [
                {
                    "productId": "{{defaultTermDefinedAnnualProductId}}",
                    "quantity": 100,
                    "currencyCode": "USD"
                }
            ]
        }
    )

    # Pricing
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: Execute Pricing",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/pricing",
        "Execute core pricing logic and return price with modifiers.",
        body={
            "priceInputContext": {
                "accountId": "{{defaultAccountId}}",
                "pricingInputs": [
                    {
                        "productId": "{{defaultTermDefinedAnnualProductId}}",
                        "quantity": 100,
                        "currencyCode": "USD"
                    }
                ]
            }
        }
    )

    # API Execution Logs
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: API Execution Logs",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/pricing/api-execution-logs",
        "Retrieve execution logs for pricing API calls."
    )

    # Process Execution
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: Process Execution",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/pricing/execution",
        "Get execution details for a pricing process."
    )

    # Process Execution for Line Items
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: Process Execution for Line Items",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/pricing/execution/line-items",
        "Get execution details broken down by line item."
    )

    # Pricing Data Sync
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: Data Sync",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/sync/syncData",
        "Sync pricing data from cache to persistent store."
    )

    # Pricing Recipe
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: Recipe",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/recipe",
        "Retrieve the pricing recipe (calculation rules) for a catalog or account."
    )

    # Pricing Recipe Mapping
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: Recipe Mapping",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/recipe/mapping",
        "Map pricing recipe inputs to transaction fields.",
        body={
            "recipeId": "recipe-id",
            "mappings": [
                {"field": "quantity", "value": "100"}
            ]
        }
    )

    # Pricing Versioned Revision Details
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: Versioned Revision Details",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/versioned-revision-details",
        "Get details of a specific pricing revision version.",
        body={
            "revisionId": "revision-id",
            "version": 1
        }
    )

    # Pricing Waterfall (GET)
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: Waterfall (GET)",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/waterfall/{lineItemId}/{executionId}",
        "Get the pricing waterfall breakdown showing all adjustments and modifiers."
    )

    # Pricing Waterfall (POST)
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: Waterfall (POST)",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/waterfall",
        "Calculate and retrieve pricing waterfall for line items.",
        body={
            "lineItemIds": ["lineitem-id"],
            "executionId": "execution-id"
        }
    )

    # Pricing Simulation Input Variables
    builder.add_endpoint_to_folder(
        core_pricing,
        "Pricing: Simulation Input Variables",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/simulation/input-variables",
        "Get available input variables for pricing simulations."
    )

    # Procedure Plan Definitions subfolder
    proc_defs = builder.add_folder(
        "Procedure Plan Definitions",
        "CRUD operations on Procedure Plan Definitions"
    )
    folder["item"].append(proc_defs)

    # List Procedure Plan Definitions
    builder.add_endpoint_to_folder(
        proc_defs,
        "Pricing: List Procedure Plan Definitions",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/procedure-plan-definitions",
        "List all procedure plan definitions."
    )

    # Create Procedure Plan Definition
    builder.add_endpoint_to_folder(
        proc_defs,
        "Pricing: Create Procedure Plan Definition",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/procedure-plan-definitions",
        "Create a new procedure plan definition.",
        body={
            "name": "Standard Pricing Procedure",
            "description": "Standard pricing procedure with discounts",
            "steps": [
                {"stepNumber": 1, "procedureId": "list-price"},
                {"stepNumber": 2, "procedureId": "volume-discount"}
            ]
        }
    )

    # Get Procedure Plan Definition
    builder.add_endpoint_to_folder(
        proc_defs,
        "Pricing: Get Procedure Plan Definition",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/procedure-plan-definitions/{definitionId}",
        "Retrieve a specific procedure plan definition."
    )

    # Update Procedure Plan Definition
    builder.add_endpoint_to_folder(
        proc_defs,
        "Pricing: Update Procedure Plan Definition",
        "PATCH",
        "{{_endpoint}}/services/data/v{{version}}/connect/procedure-plan-definitions/{definitionId}",
        "Update an existing procedure plan definition.",
        body={
            "name": "Standard Pricing Procedure (Updated)",
            "steps": [
                {"stepNumber": 1, "procedureId": "list-price"},
                {"stepNumber": 2, "procedureId": "volume-discount"},
                {"stepNumber": 3, "procedureId": "margin-check"}
            ]
        }
    )

    # Delete Procedure Plan Definition
    builder.add_endpoint_to_folder(
        proc_defs,
        "Pricing: Delete Procedure Plan Definition",
        "DELETE",
        "{{_endpoint}}/services/data/v{{version}}/connect/procedure-plan-definitions/{definitionId}",
        "Delete a procedure plan definition."
    )

    # Evaluate by Object
    builder.add_endpoint_to_folder(
        proc_defs,
        "Pricing: Evaluate by Object",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/procedure-plan-definitions/actions/evaluate",
        "Evaluate a procedure plan against an object instance.",
        body={
            "definitionId": "definition-id",
            "objectName": "QuoteLineItem",
            "objectId": "line-item-id"
        }
    )


def create_configurator_folder(builder: PostmanCollectionBuilder):
    """Create Product Configurator folder (13 endpoints)."""
    folder = builder.add_folder(
        "Product Configurator",
        "Configure products with options, bundles, and constraints"
    )

    # Configure
    builder.add_endpoint_to_folder(
        folder,
        "Config: Configure",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/configure",
        "Configure a product with selected options and features.",
        body={
            "productId": "{{defaultTermDefinedAnnualProductId}}",
            "selectedOptions": [
                {"optionId": "option-1", "value": "VALUE_A"}
            ]
        }
    )

    # List Saved Configurations
    builder.add_endpoint_to_folder(
        folder,
        "Config: List Saved Configurations",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/saved-configuration",
        "List all saved product configurations for a user or account."
    )

    # Create Saved Configuration
    builder.add_endpoint_to_folder(
        folder,
        "Config: Create Saved Configuration",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/saved-configuration",
        "Save a product configuration for reuse.",
        body={
            "name": "My Configuration",
            "productId": "{{defaultTermDefinedAnnualProductId}}",
            "configurationData": {
                "selectedOptions": [
                    {"optionId": "option-1", "value": "VALUE_A"}
                ]
            }
        }
    )

    # Update Saved Configuration
    builder.add_endpoint_to_folder(
        folder,
        "Config: Update Saved Configuration",
        "PUT",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/saved-configuration/{configurationId}",
        "Update a saved configuration.",
        body={
            "name": "My Configuration (Updated)",
            "configurationData": {
                "selectedOptions": [
                    {"optionId": "option-1", "value": "VALUE_B"}
                ]
            }
        }
    )

    # Delete Saved Configuration
    builder.add_endpoint_to_folder(
        folder,
        "Config: Delete Saved Configuration",
        "DELETE",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/saved-configuration/{configurationId}",
        "Delete a saved configuration."
    )

    # Get Instance
    builder.add_endpoint_to_folder(
        folder,
        "Config: Get Instance",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/get-instance",
        "Retrieve the current configuration instance.",
        body={
            "instanceId": "instance-id"
        }
    )

    # Load Instance
    builder.add_endpoint_to_folder(
        folder,
        "Config: Load Instance",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/load-instance",
        "Load a saved configuration instance.",
        body={
            "configurationId": "config-id"
        }
    )

    # Save Instance
    builder.add_endpoint_to_folder(
        folder,
        "Config: Save Instance",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/save-instance",
        "Save the current configuration instance.",
        body={
            "instanceId": "instance-id",
            "configurationData": {}
        }
    )

    # Set Instance
    builder.add_endpoint_to_folder(
        folder,
        "Config: Set Instance",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/set-instance",
        "Set or update configuration instance data.",
        body={
            "instanceId": "instance-id",
            "configurationData": {
                "selectedOptions": []
            }
        }
    )

    # Add Nodes
    builder.add_endpoint_to_folder(
        folder,
        "Config: Add Nodes",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/add-nodes",
        "Add configuration nodes (products/options) to configuration tree.",
        body={
            "instanceId": "instance-id",
            "nodesToAdd": [
                {"parentNodeId": "root", "productId": "product-id"}
            ]
        }
    )

    # Delete Nodes
    builder.add_endpoint_to_folder(
        folder,
        "Config: Delete Nodes",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/delete-nodes",
        "Remove configuration nodes from configuration tree.",
        body={
            "instanceId": "instance-id",
            "nodeIdsToDelete": ["node-id-1", "node-id-2"]
        }
    )

    # Update Nodes
    builder.add_endpoint_to_folder(
        folder,
        "Config: Update Nodes",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/update-nodes",
        "Update configuration node properties.",
        body={
            "instanceId": "instance-id",
            "nodesToUpdate": [
                {"nodeId": "node-id", "properties": {"quantity": 2}}
            ]
        }
    )

    # Set Product Quantity
    builder.add_endpoint_to_folder(
        folder,
        "Config: Set Product Quantity",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/set-product-quantity",
        "Set the quantity for a product in configuration.",
        body={
            "instanceId": "instance-id",
            "productId": "{{defaultTermDefinedAnnualProductId}}",
            "quantity": 10
        }
    )


def create_rate_management_folder(builder: PostmanCollectionBuilder):
    """Create Rate Management folder (2 endpoints)."""
    folder = builder.add_folder(
        "Rate Management",
        "Get rate plans and rating waterfalls"
    )

    # Get Rate Plan
    builder.add_endpoint_to_folder(
        folder,
        "Rate: Get Rate Plan",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-rating/rate-plan",
        "Retrieve a rate plan with rates, dimensions, and tiers."
    )

    # Get Rating Waterfall
    builder.add_endpoint_to_folder(
        folder,
        "Rate: Get Rating Waterfall",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/waterfall/{lineItemId}/{executionId}?ratingParameters=true",
        "Get rating waterfall showing usage-based pricing breakdown."
    )


def create_transaction_management_folder(builder: PostmanCollectionBuilder):
    """Create Transaction Management folder (17 endpoints)."""
    folder = builder.add_folder(
        "Transaction Management",
        "Place and manage sales transactions, assets, and ramp deals"
    )

    # Sales Transaction Actions subfolder
    sales_actions = builder.add_folder(
        "Sales Transaction Actions",
        "Place, read, clone, and preview sales transactions"
    )
    folder["item"].append(sales_actions)

    # Place Sales Transaction
    builder.add_endpoint_to_folder(
        sales_actions,
        "Transaction: Place Sales Transaction",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/actions/place",
        "Place a sales transaction (quote, order, subscription).",
        body={
            "accountId": "{{defaultAccountId}}",
            "effectiveDate": "2026-03-26",
            "currencyCode": "USD",
            "lineItems": [
                {
                    "productId": "{{defaultTermDefinedAnnualProductId}}",
                    "quantity": 10,
                    "term": 12,
                    "sellingModelId": "selling-model-id"
                }
            ]
        }
    )

    # Read Sales Transaction
    builder.add_endpoint_to_folder(
        sales_actions,
        "Transaction: Read Sales Transaction",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/actions/read",
        "Read/retrieve a sales transaction.",
        body={
            "transactionId": "transaction-id"
        }
    )

    # Clone Sales Transaction
    builder.add_endpoint_to_folder(
        sales_actions,
        "Transaction: Clone Sales Transaction",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/actions/clone",
        "Clone a sales transaction to create a new one based on existing.",
        body={
            "sourceTransactionId": "transaction-id",
            "newAccountId": "{{defaultAccountId}}"
        }
    )

    # Instant Pricing
    builder.add_endpoint_to_folder(
        sales_actions,
        "Transaction: Instant Pricing",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/industries/cpq/quotes/actions/get-instant-price",
        "Get instant price for products without creating a quote.",
        body={
            "lineItems": [
                {
                    "productId": "{{defaultTermDefinedAnnualProductId}}",
                    "quantity": 10
                }
            ],
            "accountId": "{{defaultAccountId}}"
        }
    )

    # Preview Approval
    builder.add_endpoint_to_folder(
        sales_actions,
        "Transaction: Preview Approval",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/actions/preview-approval",
        "Preview approval requirements for a sales transaction.",
        body={
            "transactionId": "transaction-id"
        }
    )

    # Get Eligible Promotions (v66.0)
    builder.add_endpoint_to_folder(
        sales_actions,
        "Transaction: Get Eligible Promotions (v66.0)",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/actions/get-eligible-promotions",
        "Get list of eligible promotions for a transaction (new in Spring '26).",
        body={
            "transactionId": "transaction-id",
            "effectiveDate": "2026-03-26"
        }
    )

    # Retrieve API Errors
    builder.add_endpoint_to_folder(
        sales_actions,
        "Transaction: Retrieve API Errors",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/api-errors",
        "Retrieve API execution errors for sales transactions."
    )

    # Place Supplemental Transaction
    builder.add_endpoint_to_folder(
        sales_actions,
        "Transaction: Place Supplemental Transaction",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/actions/place-supplemental",
        "Place a supplemental transaction (amendment, renewal, cross-sell).",
        body={
            "parentTransactionId": "transaction-id",
            "transactionType": "AMENDMENT",
            "lineItems": [
                {
                    "productId": "{{defaultTermDefinedAnnualProductId}}",
                    "quantity": 5,
                    "changeType": "ADD"
                }
            ]
        }
    )

    # Asset Lifecycle subfolder
    asset_lifecycle = builder.add_folder(
        "Asset Lifecycle",
        "Asset amendment, cancellation, and renewal"
    )
    folder["item"].append(asset_lifecycle)

    # Asset Amendment
    builder.add_endpoint_to_folder(
        asset_lifecycle,
        "Transaction: Asset Amendment",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/assets/actions/amend",
        "Create an amendment for an existing asset.",
        body={
            "assetId": "{{assetId}}",
            "effectiveDate": "2026-03-26",
            "changes": [
                {"fieldName": "Quantity", "newValue": 20}
            ]
        }
    )

    # Asset Cancellation
    builder.add_endpoint_to_folder(
        asset_lifecycle,
        "Transaction: Asset Cancellation",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/assets/actions/cancel",
        "Cancel an asset.",
        body={
            "assetId": "{{assetId}}",
            "cancellationDate": "2026-03-26",
            "reason": "CUSTOMER_REQUEST"
        }
    )

    # Asset Renewal
    builder.add_endpoint_to_folder(
        asset_lifecycle,
        "Transaction: Asset Renewal",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/assets/actions/renew",
        "Renew an expiring asset.",
        body={
            "assetId": "{{assetId}}",
            "renewalDate": "2027-03-26",
            "renewalTerm": 12
        }
    )

    # Ramp Deals subfolder
    ramp_deals = builder.add_folder(
        "Ramp Deals",
        "Create, update, delete, and view ramp deals"
    )
    folder["item"].append(ramp_deals)

    # Create Ramp Deal
    builder.add_endpoint_to_folder(
        ramp_deals,
        "Transaction: Create Ramp Deal",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/ramp-deals",
        "Create a ramp deal with escalating commitments.",
        body={
            "name": "Ramp Deal 2026",
            "accountId": "{{defaultAccountId}}",
            "startDate": "2026-03-26",
            "endDate": "2027-03-26",
            "rampSegments": [
                {"segment": 1, "startDate": "2026-03-26", "endDate": "2026-09-26", "commitment": 1000},
                {"segment": 2, "startDate": "2026-09-27", "endDate": "2027-03-26", "commitment": 1500}
            ]
        }
    )

    # Update Ramp Deal
    builder.add_endpoint_to_folder(
        ramp_deals,
        "Transaction: Update Ramp Deal",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/ramp-deals/actions/update",
        "Update an existing ramp deal.",
        body={
            "rampDealId": "ramp-deal-id",
            "rampSegments": [
                {"segment": 1, "commitment": 1200}
            ]
        }
    )

    # Delete Ramp Deal
    builder.add_endpoint_to_folder(
        ramp_deals,
        "Transaction: Delete Ramp Deal",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/ramp-deals/actions/delete",
        "Delete a ramp deal.",
        body={
            "rampDealId": "ramp-deal-id"
        }
    )

    # View Ramp Deal
    builder.add_endpoint_to_folder(
        ramp_deals,
        "Transaction: View Ramp Deal",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/ramp-deals",
        "View all ramp deals for an account."
    )

    # Deprecated folder
    deprecated = builder.add_folder(
        "Deprecated (v63+)",
        "Deprecated endpoints - use Sales Transaction APIs instead"
    )
    folder["item"].append(deprecated)

    # Place Order (deprecated)
    builder.add_endpoint_to_folder(
        deprecated,
        "Transaction: Place Order [DEPRECATED v63]",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-orders/actions/place",
        "DEPRECATED (Spring 23 v63.0) - Use Place Sales Transaction instead.",
        body={
            "accountId": "{{defaultAccountId}}",
            "lineItems": []
        }
    )

    # Place Quote (deprecated)
    builder.add_endpoint_to_folder(
        deprecated,
        "Transaction: Place Quote [DEPRECATED v63]",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/quotes/actions/place",
        "DEPRECATED (Spring 23 v63.0) - Use Place Sales Transaction instead.",
        body={
            "accountId": "{{defaultAccountId}}",
            "lineItems": []
        }
    )


def create_usage_management_folder(builder: PostmanCollectionBuilder):
    """Create Usage Management folder (6 endpoints)."""
    folder = builder.add_folder(
        "Usage Management",
        "Track and retrieve usage details across assets and orders"
    )

    # Asset Usage Details
    builder.add_endpoint_to_folder(
        folder,
        "Usage: Asset Usage Details",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/asset-management/assets/{{assetId}}/usage-details",
        "Get usage details and consumption data for an asset."
    )

    # Order Item Usage Details
    builder.add_endpoint_to_folder(
        folder,
        "Usage: Order Item Usage Details",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/commerce/sales-orders/line-items/{orderItemId}/usage-details",
        "Get usage details for an order line item."
    )

    # Quote Line Item Usage Details
    builder.add_endpoint_to_folder(
        folder,
        "Usage: Quote Line Item Usage Details",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/commerce/quotes/line-items/{quoteLineItemId}/usage-details",
        "Get usage details for a quote line item."
    )

    # Binding Object Usage Details
    builder.add_endpoint_to_folder(
        folder,
        "Usage: Binding Object Usage Details",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/revenue/usage-management/binding-objects/{{bindingObjectId}}/actions/usage-details",
        "Get usage details for a usage binding object."
    )

    # Consumption Traceabilities (v66.0)
    builder.add_endpoint_to_folder(
        folder,
        "Usage: Consumption Traceabilities (v66.0)",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/revenue/usage-management/consumption/actions/trace",
        "Trace consumption data and correlate with usage (new in Spring '26).",
        body={
            "bindingObjectId": "{{bindingObjectId}}",
            "dateRange": {
                "startDate": "2026-01-01",
                "endDate": "2026-03-26"
            }
        }
    )

    # Usage Product Validation (v66.0)
    builder.add_endpoint_to_folder(
        folder,
        "Usage: Usage Product Validation (v66.0)",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/revenue/usage-management/usage-products/actions/validate",
        "Validate usage products and configurations (new in Spring '26).",
        body={
            "productIds": ["{{defaultTermDefinedAnnualProductId}}"],
            "usageAttributes": {
                "dimension": "GB",
                "metric": "DATA_CONSUMED"
            }
        }
    )


def create_billing_folder(builder: PostmanCollectionBuilder):
    """Create Billing folder (30 endpoints)."""
    folder = builder.add_folder(
        "Billing",
        "Generate, post, and manage invoices; handle payments, credits, and tax"
    )

    # Credits subfolder
    credits = builder.add_folder(
        "Credits",
        "Apply, generate, void, and unapply credit memos"
    )
    folder["item"].append(credits)

    builder.add_endpoint_to_folder(
        credits,
        "Billing: Apply Credit",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/credit-memos/actions/apply",
        "Apply a credit memo to one or more invoices.",
        body={
            "creditMemoId": "credit-id",
            "invoiceIds": ["invoice-id-1"],
            "amount": 500
        }
    )

    builder.add_endpoint_to_folder(
        credits,
        "Billing: Generate Credit Memo",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/credit-memos/actions/generate",
        "Generate a credit memo from an invoice.",
        body={
            "sourceInvoiceId": "invoice-id",
            "reason": "PRODUCT_RETURN",
            "lineItems": [
                {"invoiceLineId": "line-id", "creditAmount": 500}
            ]
        }
    )

    builder.add_endpoint_to_folder(
        credits,
        "Billing: Void Posted Credit Memo",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/credit-memos/actions/void",
        "Void a posted credit memo.",
        body={
            "creditMemoId": "credit-id",
            "reason": "INCORRECT_CREDIT"
        }
    )

    builder.add_endpoint_to_folder(
        credits,
        "Billing: Unapply Credit",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/credit-memos/actions/unapply",
        "Remove a credit memo from an invoice.",
        body={
            "creditMemoId": "credit-id",
            "invoiceIds": ["invoice-id"]
        }
    )

    # Billing Schedules subfolder
    schedules = builder.add_folder(
        "Billing Schedules",
        "Create, suspend, resume, and recover billing schedules"
    )
    folder["item"].append(schedules)

    builder.add_endpoint_to_folder(
        schedules,
        "Billing: Create Billing Schedules from Transaction",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/billing-schedules/actions/create-from-billing-transaction",
        "Create billing schedules from a billing transaction.",
        body={
            "transactionId": "transaction-id",
            "schedules": [
                {"type": "INVOICE_SCHEDULE", "frequency": "MONTHLY"}
            ]
        }
    )

    builder.add_endpoint_to_folder(
        schedules,
        "Billing: Create Standalone Billing Schedules",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/billing-schedules/actions/create-standalone",
        "Create standalone billing schedules not tied to a transaction.",
        body={
            "accountId": "{{defaultAccountId}}",
            "schedules": [
                {
                    "type": "INVOICE_SCHEDULE",
                    "frequency": "MONTHLY",
                    "startDate": "2026-04-01",
                    "endDate": "2027-03-31"
                }
            ]
        }
    )

    builder.add_endpoint_to_folder(
        schedules,
        "Billing: Suspend Billing Schedule",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/billing-schedules/actions/suspend",
        "Suspend a billing schedule.",
        body={
            "billingScheduleId": "{{billingScheduleId}}",
            "suspensionDate": "2026-04-01"
        }
    )

    builder.add_endpoint_to_folder(
        schedules,
        "Billing: Resume Billing Schedule",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/billing-schedules/actions/resume",
        "Resume a suspended billing schedule.",
        body={
            "billingScheduleId": "{{billingScheduleId}}",
            "resumeDate": "2026-05-01"
        }
    )

    builder.add_endpoint_to_folder(
        schedules,
        "Billing: Recover Billing Schedules",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/billing-schedules/actions/recover",
        "Recover billing schedules after failure or error.",
        body={
            "billingScheduleIds": ["schedule-id-1"],
            "recoveryMode": "INCREMENTAL"
        }
    )

    # Invoicing subfolder
    invoicing = builder.add_folder(
        "Invoicing",
        "Generate, post, preview, write-off, void, and ingest invoices"
    )
    folder["item"].append(invoicing)

    builder.add_endpoint_to_folder(
        invoicing,
        "Billing: Generate Invoice",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/invoices/actions/generate",
        "Generate draft invoices from billing schedules.",
        body={
            "billingScheduleIds": ["{{billingScheduleId}}"],
            "invoiceDate": "2026-03-26"
        }
    )

    builder.add_endpoint_to_folder(
        invoicing,
        "Billing: Post Draft Invoice",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/invoices/actions/post",
        "Post a draft invoice (make final and prevent further edits).",
        body={
            "invoiceIds": ["{{invoiceId}}"]
        }
    )

    builder.add_endpoint_to_folder(
        invoicing,
        "Billing: Post Draft Invoice Batch Run",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/invoices/actions/post-batch",
        "Post multiple draft invoices in a batch operation.",
        body={
            "invoiceIds": ["invoice-id-1", "invoice-id-2"],
            "batchSize": 100
        }
    )

    builder.add_endpoint_to_folder(
        invoicing,
        "Billing: Preview Next Invoice",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/invoices/actions/preview",
        "Preview the next invoice before generation.",
        body={
            "billingScheduleId": "{{billingScheduleId}}"
        }
    )

    builder.add_endpoint_to_folder(
        invoicing,
        "Billing: Write Off Invoices",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/invoices/actions/write-off",
        "Write off (forgive) invoice balances.",
        body={
            "invoiceIds": ["{{invoiceId}}"],
            "writeOffReason": "UNCOLLECTIBLE"
        }
    )

    builder.add_endpoint_to_folder(
        invoicing,
        "Billing: Void Invoice",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/invoices/actions/void",
        "Void a posted invoice.",
        body={
            "invoiceIds": ["{{invoiceId}}"],
            "voidReason": "INCORRECT_INVOICE"
        }
    )

    builder.add_endpoint_to_folder(
        invoicing,
        "Billing: Ingest Invoice",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/invoices/actions/ingest",
        "Ingest an external invoice into the system.",
        body={
            "accountId": "{{defaultAccountId}}",
            "invoiceNumber": "INV-2026-001",
            "invoiceDate": "2026-03-26",
            "amount": 5000,
            "lineItems": [
                {"description": "Service", "amount": 5000}
            ]
        }
    )

    builder.add_endpoint_to_folder(
        invoicing,
        "Billing: Generate Invoice Documents",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/invoices/actions/generate-documents",
        "Generate PDF or other documents for invoices.",
        body={
            "invoiceIds": ["{{invoiceId}}"],
            "format": "PDF",
            "includeAttachments": True
        }
    )

    # Invoice Scheduling subfolder
    scheduling = builder.add_folder(
        "Invoice Scheduling",
        "Create and manage invoice schedulers"
    )
    folder["item"].append(scheduling)

    builder.add_endpoint_to_folder(
        scheduling,
        "Billing: Create Invoice Scheduler",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/invoice-schedulers",
        "Create an invoice scheduler for recurring invoice generation.",
        body={
            "name": "Monthly Invoice Scheduler",
            "accountId": "{{defaultAccountId}}",
            "frequency": "MONTHLY",
            "dayOfMonth": 1
        }
    )

    # Payments subfolder
    payments = builder.add_folder(
        "Payments",
        "Apply, unapply, and manage payments"
    )
    folder["item"].append(payments)

    builder.add_endpoint_to_folder(
        payments,
        "Billing: Apply Payment",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/payments/actions/apply",
        "Apply a payment to invoices.",
        body={
            "paymentId": "payment-id",
            "invoiceIds": ["{{invoiceId}}"],
            "amount": 1000
        }
    )

    builder.add_endpoint_to_folder(
        payments,
        "Billing: Unapply Payment",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/payments/actions/unapply",
        "Remove a payment from an invoice.",
        body={
            "paymentId": "payment-id",
            "invoiceIds": ["{{invoiceId}}"]
        }
    )

    builder.add_endpoint_to_folder(
        payments,
        "Billing: Apply Payments and Credits by Rules",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/payment-credits/actions/apply-by-rules",
        "Apply payments and credits according to rules.",
        body={
            "invoiceId": "{{invoiceId}}",
            "ruleSet": "STANDARD"
        }
    )

    builder.add_endpoint_to_folder(
        payments,
        "Billing: Refund",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/refunds/actions/generate",
        "Generate a refund for overpaid invoices.",
        body={
            "invoiceIds": ["{{invoiceId}}"],
            "refundAmount": 500,
            "refundMethod": "CREDIT_MEMO"
        }
    )

    # Tax subfolder
    tax = builder.add_folder(
        "Tax",
        "Calculate and estimate tax"
    )
    folder["item"].append(tax)

    builder.add_endpoint_to_folder(
        tax,
        "Billing: Calculate Tax",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/tax/actions/calculate",
        "Calculate tax for invoice line items.",
        body={
            "invoiceId": "{{invoiceId}}",
            "taxPolicy": "DEFAULT"
        }
    )

    builder.add_endpoint_to_folder(
        tax,
        "Billing: Estimate Tax",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/tax/actions/estimate",
        "Estimate tax before posting an invoice.",
        body={
            "accountId": "{{defaultAccountId}}",
            "lineItems": [
                {
                    "description": "Product",
                    "amount": 1000,
                    "taxCategory": "TAXABLE"
                }
            ],
            "shipToAddress": {
                "state": "CA",
                "country": "US"
            }
        }
    )

    # Account Statement subfolder
    statements = builder.add_folder(
        "Account Statement",
        "Generate account statements"
    )
    folder["item"].append(statements)

    builder.add_endpoint_to_folder(
        statements,
        "Billing: Generate Account Statement",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/commerce/billing/account-statements/actions/generate",
        "Generate an account statement showing all transactions.",
        body={
            "accountId": "{{defaultAccountId}}",
            "startDate": "2026-01-01",
            "endDate": "2026-03-26",
            "format": "PDF"
        }
    )


def create_context_service_folder(builder: PostmanCollectionBuilder):
    """Create Context Service folder (5 endpoints)."""
    folder = builder.add_folder(
        "Context Service",
        "Create and manage context definitions and mappings"
    )

    # Create Context Definition
    builder.add_endpoint_to_folder(
        folder,
        "Context: Create Context Definition",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/context-definitions",
        "Create a new context definition for pricing or configuration.",
        body={
            "name": "Industry Context",
            "description": "Context for industry-specific pricing",
            "contextType": "PRICING"
        }
    )

    # List Context Definitions
    builder.add_endpoint_to_folder(
        folder,
        "Context: List Context Definitions",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/context-definitions",
        "List all context definitions."
    )

    # Get Context Definition
    builder.add_endpoint_to_folder(
        folder,
        "Context: Get Context Definition",
        "GET",
        "{{_endpoint}}/services/data/v{{version}}/connect/context-definitions/{{contextDefinitionId}}",
        "Retrieve a specific context definition."
    )

    # Create Context Nodes
    builder.add_endpoint_to_folder(
        folder,
        "Context: Create Context Nodes",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/context-definitions/{{contextDefinitionId}}/context",
        "Create context nodes (attributes/values) within a definition.",
        body={
            "nodes": [
                {
                    "name": "Enterprise",
                    "value": "ENTERPRISE",
                    "attributes": {"tier": "HIGH"}
                },
                {
                    "name": "SMB",
                    "value": "SMB",
                    "attributes": {"tier": "STANDARD"}
                }
            ]
        }
    )

    # Create Context Mappings
    builder.add_endpoint_to_folder(
        folder,
        "Context: Create Context Mappings",
        "POST",
        "{{_endpoint}}/services/data/v{{version}}/connect/context-definitions/{{contextDefinitionId}}/context",
        "Map context definitions to Salesforce objects.",
        body={
            "mappings": [
                {
                    "objectName": "Account",
                    "fieldName": "Industry",
                    "contextAttribute": "industry"
                }
            ]
        }
    )


def create_quote_to_cash_runner(builder: PostmanCollectionBuilder):
    """Create the Quote-to-Cash Runner workflow folder."""
    folder = builder.add_folder(
        "▶️ Quote-to-Cash Runner",
        "End-to-end workflow: Pricing → Sales Transaction → Order → Activate → Asset → Amendment"
    )

    steps = [
        {
            "name": "Step 1: Get Pricing for Products",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/connect/core-pricing/pricing",
            "body": {
                "priceInputContext": {
                    "accountId": "{{defaultAccountId}}",
                    "pricingInputs": [
                        {
                            "productId": "{{defaultTermDefinedAnnualProductId}}",
                            "quantity": 100,
                            "currencyCode": "USD"
                        }
                    ]
                }
            },
            "test": """
const response = pm.response.json();
pm.environment.set('basePrice', response.pricing[0].totalPrice);
pm.test("Pricing executed", function () {
    pm.expect(response.pricing).to.be.an('array').that.is.not.empty;
});
"""
        },
        {
            "name": "Step 2: Place Sales Transaction (Quote)",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/actions/place",
            "body": {
                "accountId": "{{defaultAccountId}}",
                "effectiveDate": "2026-03-26",
                "currencyCode": "USD",
                "lineItems": [
                    {
                        "productId": "{{defaultTermDefinedAnnualProductId}}",
                        "quantity": 100,
                        "term": 12
                    }
                ]
            },
            "test": """
const response = pm.response.json();
pm.environment.set('transactionId', response.id);
pm.environment.set('quoteId', response.quoteId);
pm.test("Sales transaction created", function () {
    pm.expect(response.id).to.exist;
});
"""
        },
        {
            "name": "Step 3: Create Order from Quote",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/commerce/quotes/actions/create-order",
            "body": {
                "quoteId": "{{quoteId}}",
                "effectiveDate": "2026-03-26"
            },
            "test": """
const response = pm.response.json();
pm.environment.set('orderId', response.orderId);
pm.test("Order created from quote", function () {
    pm.expect(response.orderId).to.exist;
});
"""
        },
        {
            "name": "Step 4: Activate Order",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/orders/actions/activate",
            "body": {
                "orderId": "{{orderId}}",
                "activationDate": "2026-03-26"
            },
            "test": """
const response = pm.response.json();
pm.test("Order activated", function () {
    pm.expect(response.status).to.equal('ACTIVATED');
});
"""
        },
        {
            "name": "Step 5: Verify Assets Created",
            "method": "GET",
            "url": "{{_endpoint}}/services/data/v{{version}}/asset-management/assets?orderId={{orderId}}",
            "test": """
const response = pm.response.json();
if (response.records && response.records.length > 0) {
    pm.environment.set('assetId', response.records[0].Id);
    console.log('Asset ID: ' + response.records[0].Id);
}
pm.test("Assets exist for order", function () {
    pm.expect(response.records).to.be.an('array').that.is.not.empty;
});
"""
        },
        {
            "name": "Step 6: Create Asset Amendment",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/assets/actions/amend",
            "body": {
                "assetId": "{{assetId}}",
                "effectiveDate": "2026-06-26",
                "changes": [
                    {"fieldName": "Quantity", "newValue": 150}
                ]
            },
            "test": """
const response = pm.response.json();
pm.test("Asset amended successfully", function () {
    pm.expect(response.success).to.equal(true);
});
"""
        }
    ]

    for step in steps:
        test_script = step.get("test", "")
        builder.add_endpoint_to_folder(
            folder,
            step["name"],
            step["method"],
            step["url"],
            f"Q2C Workflow: {step['name']}",
            body=step.get("body"),
            tests=test_script
        )


def create_ecommerce_runner(builder: PostmanCollectionBuilder):
    """Create the eCommerce Runner workflow folder."""
    folder = builder.add_folder(
        "▶️ eCommerce Runner",
        "Simplified headless flow: List Products → Get Product → Price → Place Order → Activate"
    )

    steps = [
        {
            "name": "Step 1: List Products",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/connect/pcm/products",
            "body": {"pageSize": 100},
            "test": """
const response = pm.response.json();
if (response.products && response.products.length > 0) {
    pm.environment.set('ecomProductId', response.products[0].id);
}
pm.test("Products retrieved", function () {
    pm.expect(response.products).to.be.an('array').that.is.not.empty;
});
"""
        },
        {
            "name": "Step 2: Get Product Details",
            "method": "GET",
            "url": "{{_endpoint}}/services/data/v{{version}}/connect/pcm/products/{{ecomProductId}}",
            "test": """
const response = pm.response.json();
pm.test("Product details retrieved", function () {
    pm.expect(response.name).to.exist;
});
"""
        },
        {
            "name": "Step 3: Get Instant Price",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/industries/cpq/quotes/actions/get-instant-price",
            "body": {
                "lineItems": [
                    {
                        "productId": "{{ecomProductId}}",
                        "quantity": 10
                    }
                ],
                "accountId": "{{defaultAccountId}}"
            },
            "test": """
const response = pm.response.json();
pm.environment.set('instantPrice', response.price);
pm.test("Instant price calculated", function () {
    pm.expect(response.price).to.be.a('number');
});
"""
        },
        {
            "name": "Step 4: Place Sales Order",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/commerce/sales-transactions/actions/place",
            "body": {
                "accountId": "{{defaultAccountId}}",
                "effectiveDate": "2026-03-26",
                "currencyCode": "USD",
                "lineItems": [
                    {
                        "productId": "{{ecomProductId}}",
                        "quantity": 10
                    }
                ]
            },
            "test": """
const response = pm.response.json();
pm.environment.set('ecomOrderId', response.orderId);
pm.test("Order placed", function () {
    pm.expect(response.orderId).to.exist;
});
"""
        },
        {
            "name": "Step 5: Activate Order",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/orders/actions/activate",
            "body": {
                "orderId": "{{ecomOrderId}}",
                "activationDate": "2026-03-26"
            },
            "test": """
const response = pm.response.json();
pm.test("Order activated for fulfillment", function () {
    pm.expect(response.status).to.equal('ACTIVATED');
});
"""
        }
    ]

    for step in steps:
        test_script = step.get("test", "")
        builder.add_endpoint_to_folder(
            folder,
            step["name"],
            step["method"],
            step["url"],
            f"eCommerce Workflow: {step['name']}",
            body=step.get("body"),
            tests=test_script
        )


def create_billing_runner(builder: PostmanCollectionBuilder):
    """Create the Billing Runner workflow folder."""
    folder = builder.add_folder(
        "▶️ Billing Runner",
        "Billing workflow: Create Schedule → Generate Invoice → Post → Apply Payment"
    )

    steps = [
        {
            "name": "Step 1: Create Billing Schedule",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/commerce/billing/billing-schedules/actions/create-standalone",
            "body": {
                "accountId": "{{defaultAccountId}}",
                "schedules": [
                    {
                        "type": "INVOICE_SCHEDULE",
                        "frequency": "MONTHLY",
                        "startDate": "2026-04-01",
                        "endDate": "2027-03-31"
                    }
                ]
            },
            "test": """
const response = pm.response.json();
pm.environment.set('billingScheduleId', response.schedules[0].id);
pm.test("Billing schedule created", function () {
    pm.expect(response.schedules).to.be.an('array').that.is.not.empty;
});
"""
        },
        {
            "name": "Step 2: Generate Invoice",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/commerce/billing/invoices/actions/generate",
            "body": {
                "billingScheduleIds": ["{{billingScheduleId}}"],
                "invoiceDate": "2026-03-26"
            },
            "test": """
const response = pm.response.json();
if (response.invoices && response.invoices.length > 0) {
    pm.environment.set('generatedInvoiceId', response.invoices[0].id);
}
pm.test("Invoice generated", function () {
    pm.expect(response.invoices).to.be.an('array').that.is.not.empty;
});
"""
        },
        {
            "name": "Step 3: Post Draft Invoice",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/commerce/billing/invoices/actions/post",
            "body": {
                "invoiceIds": ["{{generatedInvoiceId}}"]
            },
            "test": """
const response = pm.response.json();
pm.environment.set('postedInvoiceId', response.invoices[0].id);
pm.test("Invoice posted successfully", function () {
    pm.expect(response.invoices[0].status).to.equal('POSTED');
});
"""
        },
        {
            "name": "Step 4: Apply Payment to Invoice",
            "method": "POST",
            "url": "{{_endpoint}}/services/data/v{{version}}/commerce/billing/payments/actions/apply",
            "body": {
                "paymentId": "payment-id",
                "invoiceIds": ["{{postedInvoiceId}}"],
                "amount": 5000
            },
            "test": """
const response = pm.response.json();
pm.test("Payment applied", function () {
    pm.expect(response.success).to.equal(true);
});
"""
        }
    ]

    for step in steps:
        test_script = step.get("test", "")
        builder.add_endpoint_to_folder(
            folder,
            step["name"],
            step["method"],
            step["url"],
            f"Billing Workflow: {step['name']}",
            body=step.get("body"),
            tests=test_script
        )


def main():
    """Generate the complete Postman collection."""
    print("[*] Building Agentforce Revenue Management APIs (v66.0) Postman Collection...")

    builder = PostmanCollectionBuilder(
        collection_name="Agentforce Revenue Management APIs (v66.0)",
        description="""
Comprehensive Postman collection for Revenue Cloud Business APIs (Spring '26, API v66.0).

Covers:
- Product Catalog Management (PCM) - 17 endpoints
- Product Discovery (CPQ) - 10 endpoints
- Salesforce Pricing - 19 endpoints
- Product Configurator - 13 endpoints
- Rate Management - 2 endpoints
- Transaction Management - 17 endpoints
- Usage Management - 6 endpoints
- Billing - 30 endpoints
- Context Service - 5 endpoints
- Setup & Workflows (SOQL queries, auth, Q2C, eCommerce, Billing runners)

Environment Variables:
- {{_endpoint}} - Salesforce org endpoint
- {{version}} - API version (66.0)
- {{url}} - Login URL
- {{clientId}}, {{clientSecret}} - OAuth2 credentials
- {{accessToken}} - Auto-refreshed bearer token

Collection Auth: OAuth2 Bearer Token (inherits from collection level)
Collection Pre-request Script: Automatic OAuth2 token refresh

Generated: 2026-03-26
"""
    )

    print("[*] Adding Setup Runner...")
    create_setup_runner(builder)

    print("[*] Adding Product Catalog Management (17 endpoints)...")
    create_pcm_folder(builder)

    print("[*] Adding Product Discovery (10 endpoints)...")
    create_product_discovery_folder(builder)

    print("[*] Adding Salesforce Pricing (19 endpoints)...")
    create_pricing_folder(builder)

    print("[*] Adding Product Configurator (13 endpoints)...")
    create_configurator_folder(builder)

    print("[*] Adding Rate Management (2 endpoints)...")
    create_rate_management_folder(builder)

    print("[*] Adding Transaction Management (17 endpoints)...")
    create_transaction_management_folder(builder)

    print("[*] Adding Usage Management (6 endpoints)...")
    create_usage_management_folder(builder)

    print("[*] Adding Billing (30 endpoints)...")
    create_billing_folder(builder)

    print("[*] Adding Context Service (5 endpoints)...")
    create_context_service_folder(builder)

    print("[*] Adding Quote-to-Cash Runner...")
    create_quote_to_cash_runner(builder)

    print("[*] Adding eCommerce Runner...")
    create_ecommerce_runner(builder)

    print("[*] Adding Billing Runner...")
    create_billing_runner(builder)

    # Build and save
    collection = builder.build()
    output_path = "/sessions/clever-intelligent-ramanujan/mnt/rlm-base-dev/postman/Agentforce Revenue Management APIs.postman_collection.json"

    with open(output_path, "w") as f:
        json.dump(collection, f, indent=2)

    print(f"\n[+] Collection generated successfully!")
    print(f"[+] Output: {output_path}")
    print(f"[+] Total items: {len(builder.items)} top-level folders")
    print(f"[+] Collection variables: {len(builder.variables)}")
    print(f"\n[+] To use this collection:")
    print(f"    1. Import into Postman")
    print(f"    2. Create/select an environment with clientId, clientSecret, url")
    print(f"    3. Run 'Get Endpoint from User Info' to initialize {{_endpoint}}")
    print(f"    4. Subsequent requests will auto-refresh OAuth2 tokens")
    print(f"    5. Use the Runner workflows (Q2C, eCommerce, Billing) for end-to-end flows")


if __name__ == "__main__":
    main()
