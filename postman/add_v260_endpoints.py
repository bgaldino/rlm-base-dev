#!/usr/bin/env python3
"""
Add v260 API endpoints to Postman collections
Implements P0 critical endpoints first, then P1, P2
"""

import json
import sys
from pathlib import Path

# P0 Critical Endpoints - Invoice Schedulers
INVOICE_SCHEDULERS = {
    "name": "Invoice Schedulers (v260)",
    "item": [
        {
            "name": "Create Invoice Scheduler",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "name": "Monthly Subscription Invoices",
                        "description": "Auto-generate invoices monthly",
                        "frequency": "Monthly",
                        "startDate": "2026-02-01",
                        "isActive": True
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/invoice-schedulers",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "invoice-schedulers"]
                }
            },
            "response": []
        },
        {
            "name": "Get Invoice Scheduler",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/invoice-schedulers/{{invoiceSchedulerId}}",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "invoice-schedulers", "{{invoiceSchedulerId}}"]
                }
            },
            "response": []
        },
        {
            "name": "Update Invoice Scheduler",
            "request": {
                "method": "PATCH",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "isActive": False,
                        "description": "Updated - Paused for review"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/invoice-schedulers/{{invoiceSchedulerId}}",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "invoice-schedulers", "{{invoiceSchedulerId}}"]
                }
            },
            "response": []
        },
        {
            "name": "Delete Invoice Scheduler",
            "request": {
                "method": "DELETE",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/invoice-schedulers/{{invoiceSchedulerId}}",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "invoice-schedulers", "{{invoiceSchedulerId}}"]
                }
            },
            "response": []
        }
    ]
}

# P0 Critical Endpoints - Payment Schedulers
PAYMENT_SCHEDULERS = {
    "name": "Payment Schedulers (v260)",
    "item": [
        {
            "name": "Create Payment Scheduler",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "name": "Auto Payment Collection",
                        "description": "Process payments automatically",
                        "frequency": "Monthly",
                        "startDate": "2026-02-01",
                        "isActive": True
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/payments/payment-schedulers/",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "payments", "payment-schedulers", ""]
                }
            },
            "response": []
        },
        {
            "name": "Get Payment Scheduler",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/payments/payment-schedulers/{{paymentSchedulerId}}",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "payments", "payment-schedulers", "{{paymentSchedulerId}}"]
                }
            },
            "response": []
        },
        {
            "name": "Update Payment Scheduler",
            "request": {
                "method": "PATCH",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "isActive": False
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/payments/payment-schedulers/{{paymentSchedulerId}}",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "payments", "payment-schedulers", "{{paymentSchedulerId}}"]
                }
            },
            "response": []
        },
        {
            "name": "Delete Payment Scheduler",
            "request": {
                "method": "DELETE",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/payments/payment-schedulers/{{paymentSchedulerId}}",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "payments", "payment-schedulers", "{{paymentSchedulerId}}"]
                }
            },
            "response": []
        }
    ]
}

# P0 Critical Endpoints - Product Configurator
PRODUCT_CONFIGURATOR = {
    "name": "Product Configurator (v260)",
    "item": [
        {
            "name": "Configure Product",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "productId": "{{productId}}",
                        "configurationMode": "INTERACTIVE"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/configure",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "cpq", "configurator", "actions", "configure"]
                }
            },
            "response": []
        },
        {
            "name": "Add Configuration Nodes",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "sessionId": "{{configSessionId}}",
                        "nodes": [{
                            "productId": "{{childProductId}}",
                            "quantity": 1
                        }]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/add-nodes",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "cpq", "configurator", "actions", "add-nodes"]
                }
            },
            "response": []
        },
        {
            "name": "Update Configuration Nodes",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "sessionId": "{{configSessionId}}",
                        "nodes": [{
                            "nodeId": "{{nodeId}}",
                            "quantity": 2
                        }]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/update-nodes",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "cpq", "configurator", "actions", "update-nodes"]
                }
            },
            "response": []
        },
        {
            "name": "Delete Configuration Nodes",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "sessionId": "{{configSessionId}}",
                        "nodeIds": ["{{nodeId}}"]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/delete-nodes",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "cpq", "configurator", "actions", "delete-nodes"]
                }
            },
            "response": []
        },
        {
            "name": "Get Configuration Instance",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "sessionId": "{{configSessionId}}"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/get-instance",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "cpq", "configurator", "actions", "get-instance"]
                }
            },
            "response": []
        },
        {
            "name": "Load Configuration Instance",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "productId": "{{productId}}",
                        "savedConfigurationId": "{{savedConfigurationId}}"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/load-instance",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "cpq", "configurator", "actions", "load-instance"]
                }
            },
            "response": []
        },
        {
            "name": "Save Configuration Instance",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "sessionId": "{{configSessionId}}",
                        "name": "My Saved Configuration"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/save-instance",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "cpq", "configurator", "actions", "save-instance"]
                }
            },
            "response": []
        },
        {
            "name": "Set Configuration Instance",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "sessionId": "{{configSessionId}}",
                        "configuration": {}
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/set-instance",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "cpq", "configurator", "actions", "set-instance"]
                }
            },
            "response": []
        },
        {
            "name": "Set Product Quantity",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "sessionId": "{{configSessionId}}",
                        "productId": "{{productId}}",
                        "quantity": 5
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/actions/set-product-quantity",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "cpq", "configurator", "actions", "set-product-quantity"]
                }
            },
            "response": []
        },
        {
            "name": "Create Saved Configuration",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "name": "Standard Configuration",
                        "description": "Default product configuration",
                        "productId": "{{productId}}",
                        "configuration": {}
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/saved-configuration",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "cpq", "configurator", "saved-configuration"]
                }
            },
            "response": []
        },
        {
            "name": "Get Saved Configuration",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/cpq/configurator/saved-configuration/{{savedConfigurationId}}",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "cpq", "configurator", "saved-configuration", "{{savedConfigurationId}}"]
                }
            },
            "response": []
        }
    ]
}

# P0 Critical Endpoints - Invoicing Actions
INVOICING_ACTIONS_P0 = {
    "name": "Invoicing Actions (v260)",
    "item": [
        {
            "name": "Suspend Billing",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "accountId": "{{accountId}}",
                        "effectiveDate": "2026-02-01",
                        "suspendReason": "Customer Request"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/actions/suspend-billing",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "actions", "suspend-billing"]
                }
            },
            "response": []
        },
        {
            "name": "Resume Billing",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "accountId": "{{accountId}}",
                        "effectiveDate": "2026-03-01"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/actions/resume-billing",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "actions", "resume-billing"]
                }
            },
            "response": []
        },
        {
            "name": "Create Billing Schedule",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "orderItemId": "{{orderItemId}}",
                        "billingFrequency": "Monthly",
                        "startDate": "2026-02-01"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/billing-schedules/actions/create",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "billing-schedules", "actions", "create"]
                }
            },
            "response": []
        },
        {
            "name": "Recover Billing Schedule",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "billingScheduleIds": ["{{billingScheduleId}}"]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/billing-schedules/collection/actions/recover",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "billing-schedules", "collection", "actions", "recover"]
                }
            },
            "response": []
        },
        {
            "name": "Generate Invoices",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "invoiceDate": "2026-02-01",
                        "billingScheduleIds": ["{{billingScheduleId}}"]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/invoices/collection/actions/generate",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "invoices", "collection", "actions", "generate"]
                }
            },
            "response": []
        },
        {
            "name": "Post Invoices",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "invoiceIds": ["{{invoiceId}}"]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/invoices/collection/actions/post",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "invoices", "collection", "actions", "post"]
                }
            },
            "response": []
        },
        {
            "name": "Preview Invoice",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "invoiceDate": "2026-02-01",
                        "billingScheduleIds": ["{{billingScheduleId}}"]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/invoices/collection/actions/preview",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "invoices", "collection", "actions", "preview"]
                }
            },
            "response": []
        },
        {
            "name": "Calculate Estimated Tax",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "invoiceIds": ["{{invoiceId}}"]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/invoices/collection/actions/calculate-estimated-tax",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "invoices", "collection", "actions", "calculate-estimated-tax"]
                }
            },
            "response": []
        },
        {
            "name": "Credit Invoice",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "creditDate": "2026-02-01",
                        "reason": "Customer dispute"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/invoices/{{invoiceId}}/actions/credit",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "invoices", "{{invoiceId}}", "actions", "credit"]
                }
            },
            "response": []
        },
        {
            "name": "Void Invoice",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "voidDate": "2026-02-01",
                        "reason": "Duplicate invoice"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/invoices/{{invoiceId}}/actions/void",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "invoices", "{{invoiceId}}", "actions", "void"]
                }
            },
            "response": []
        },
        {
            "name": "Generate Credit Memos",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "creditMemoDate": "2026-02-01",
                        "invoiceIds": ["{{invoiceId}}"]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/credit-memos/actions/generate",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "credit-memos", "actions", "generate"]
                }
            },
            "response": []
        },
        {
            "name": "Apply Credit Memo",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "invoiceId": "{{invoiceId}}",
                        "amount": 100.00
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/invoicing/credit-memos/{{creditMemoId}}/actions/apply",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "invoicing", "credit-memos", "{{creditMemoId}}", "actions", "apply"]
                }
            },
            "response": []
        }
    ]
}

# P1 High Priority - PCM Index Management
PCM_INDEX_MANAGEMENT = {
    "name": "PCM Index Management (v260)",
    "item": [
        {
            "name": "Get Index Configurations",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/configurations?includeMetadata=true&fieldTypes=Standard,Custom",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "pcm", "index", "configurations"],
                    "query": [
                        {"key": "includeMetadata", "value": "true"},
                        {"key": "fieldTypes", "value": "Standard,Custom"}
                    ]
                }
            },
            "response": []
        },
        {
            "name": "Deploy Index Configuration",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "fields": ["Name", "Description", "ProductCode"],
                        "includeMetadata": True
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/deploy",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "pcm", "index", "deploy"]
                }
            },
            "response": []
        },
        {
            "name": "Get Index Settings",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/setting",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "pcm", "index", "setting"]
                }
            },
            "response": []
        },
        {
            "name": "Update Index Settings",
            "request": {
                "method": "PATCH",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "autoIndexing": True,
                        "indexRefreshInterval": 60
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/setting",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "pcm", "index", "setting"]
                }
            },
            "response": []
        },
        {
            "name": "Get Index Snapshots",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/snapshots",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "pcm", "index", "snapshots"]
                }
            },
            "response": []
        },
        {
            "name": "Get Index Errors",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/pcm/index/error",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "pcm", "index", "error"]
                }
            },
            "response": []
        }
    ]
}

# P1 High Priority - PCM Deep Clone & Unit of Measure
PCM_ENHANCEMENTS = {
    "name": "PCM Enhancements (v260)",
    "item": [
        {
            "name": "Deep Clone Product",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "sourceRecordId": "{{productId}}",
                        "objectType": "Product2",
                        "includeRelatedRecords": True
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/pcm/deep-clone",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "pcm", "deep-clone"]
                }
            },
            "response": []
        },
        {
            "name": "Get Unit of Measure Info",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/pcm/unit-of-measure/info",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "pcm", "unit-of-measure", "info"]
                }
            },
            "response": []
        },
        {
            "name": "Calculate Rounded UoM Data",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "unitOfMeasure": "Each",
                        "quantity": 10.567,
                        "roundingMode": "HALF_UP"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/pcm/unit-of-measure/rounded-data",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "pcm", "unit-of-measure", "rounded-data"]
                }
            },
            "response": []
        }
    ]
}

# P1 High Priority - Billing Actions
BILLING_ACTIONS_P1 = {
    "name": "Billing Actions (v260)",
    "item": [
        {
            "name": "Apply Payment",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "invoiceId": "{{invoiceId}}",
                        "amount": 100.00,
                        "effectiveDate": "2026-02-01"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/billing/payments/{{paymentId}}/actions/apply",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "billing", "payments", "{{paymentId}}", "actions", "apply"]
                }
            },
            "response": []
        },
        {
            "name": "Unapply Payment Line",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "effectiveDate": "2026-02-01"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/billing/payments/{{paymentId}}/paymentlines/{{paymentLineId}}/actions/unapply",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "billing", "payments", "{{paymentId}}", "paymentlines", "{{paymentLineId}}", "actions", "unapply"]
                }
            },
            "response": []
        },
        {
            "name": "Apply Refund",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "paymentId": "{{paymentId}}",
                        "amount": 50.00,
                        "effectiveDate": "2026-02-01"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/billing/refunds/{{refundId}}/actions/apply",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "billing", "refunds", "{{refundId}}", "actions", "apply"]
                }
            },
            "response": []
        },
        {
            "name": "Void Credit Memo",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "voidDate": "2026-02-01",
                        "reason": "Error correction"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/billing/credit-memos/{{creditMemoId}}/actions/void",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "billing", "credit-memos", "{{creditMemoId}}", "actions", "void"]
                }
            },
            "response": []
        }
    ]
}

# P2 Medium Priority - Revenue Management
REVENUE_MANAGEMENT_P2 = {
    "name": "Revenue Management (v260)",
    "item": [
        {
            "name": "Create Ramp Deal",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "rampDealName": "Q1 Ramp Promotion",
                        "startDate": "2026-01-01",
                        "endDate": "2026-03-31",
                        "rampPercentages": [
                            {"period": 1, "percentage": 50},
                            {"period": 2, "percentage": 75},
                            {"period": 3, "percentage": 100}
                        ]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/sales-transaction-contexts/{{salesTransactionContextId}}/actions/ramp-deal-create",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "revenue-management", "sales-transaction-contexts", "{{salesTransactionContextId}}", "actions", "ramp-deal-create"]
                }
            },
            "response": []
        },
        {
            "name": "Update Ramp Deal",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "rampDealId": "{{rampDealId}}",
                        "rampPercentages": [
                            {"period": 1, "percentage": 60},
                            {"period": 2, "percentage": 80},
                            {"period": 3, "percentage": 100}
                        ]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/sales-transaction-contexts/{{salesTransactionContextId}}/actions/ramp-deal-update",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "revenue-management", "sales-transaction-contexts", "{{salesTransactionContextId}}", "actions", "ramp-deal-update"]
                }
            },
            "response": []
        },
        {
            "name": "Delete Ramp Deal",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "rampDealId": "{{rampDealId}}"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/sales-transaction-contexts/{{salesTransactionContextId}}/actions/ramp-deal-delete",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "revenue-management", "sales-transaction-contexts", "{{salesTransactionContextId}}", "actions", "ramp-deal-delete"]
                }
            },
            "response": []
        },
        {
            "name": "View Ramp Deal",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/sales-transaction-contexts/{{salesTransactionContextId}}/actions/ramp-deal-view",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "revenue-management", "sales-transaction-contexts", "{{salesTransactionContextId}}", "actions", "ramp-deal-view"]
                }
            },
            "response": []
        },
        {
            "name": "Amend Asset",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "assetId": "{{assetId}}",
                        "amendmentDate": "2026-02-01",
                        "changes": {
                            "quantity": 10
                        }
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/assets/actions/amend",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "revenue-management", "assets", "actions", "amend"]
                }
            },
            "response": []
        },
        {
            "name": "Cancel Asset",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "assetId": "{{assetId}}",
                        "cancellationDate": "2026-02-01",
                        "reason": "Customer request"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/assets/actions/cancel",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "revenue-management", "assets", "actions", "cancel"]
                }
            },
            "response": []
        },
        {
            "name": "Renew Asset",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "assetId": "{{assetId}}",
                        "renewalDate": "2026-12-01",
                        "renewalTerm": 12
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/revenue-management/assets/actions/renew",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "revenue-management", "assets", "actions", "renew"]
                }
            },
            "response": []
        },
        {
            "name": "Place Sales Transaction",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "accountId": "{{accountId}}",
                        "transactionDate": "2026-02-01",
                        "lineItems": []
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/rev/sales-transaction/actions/place",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "rev", "sales-transaction", "actions", "place"]
                }
            },
            "response": []
        }
    ]
}

# P2 Medium Priority - Decision Explainer
DECISION_EXPLAINER_P2 = {
    "name": "Decision Explainer (v260)",
    "item": [
        {
            "name": "Get Action Logs by Context",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/decision-explainer/action-logs?actionContextCode={{contextCode}}&applicationType=7",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "decision-explainer", "action-logs"],
                    "query": [
                        {"key": "actionContextCode", "value": "{{contextCode}}"},
                        {"key": "applicationType", "value": "7"}
                    ]
                }
            },
            "response": []
        },
        {
            "name": "Get DRO Decomposition Logs",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/decision-explainer/action-logs?applicationSubType=DroDcmp&applicationType=7&processType=DcmpEnrich&primaryFilter={{droId}}&secondaryFilter={{hash}}",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "decision-explainer", "action-logs"],
                    "query": [
                        {"key": "applicationSubType", "value": "DroDcmp"},
                        {"key": "applicationType", "value": "7"},
                        {"key": "processType", "value": "DcmpEnrich"},
                        {"key": "primaryFilter", "value": "{{droId}}"},
                        {"key": "secondaryFilter", "value": "{{hash}}"}
                    ]
                }
            },
            "response": []
        },
        {
            "name": "Get DRO Scoring Logs",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/decision-explainer/action-logs?applicationSubType=DroDcmp&applicationType=7&processType=DcmpScp&primaryFilter={{droId}}",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "decision-explainer", "action-logs"],
                    "query": [
                        {"key": "applicationSubType", "value": "DroDcmp"},
                        {"key": "applicationType", "value": "7"},
                        {"key": "processType", "value": "DcmpScp"},
                        {"key": "primaryFilter", "value": "{{droId}}"}
                    ]
                }
            },
            "response": []
        },
        {
            "name": "Get Pricing Decision Logs",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/decision-explainer/action-logs?applicationSubType=DroPcmp&applicationType=7&processType=PcmpSteps&primaryFilter={{pricingId}}",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "decision-explainer", "action-logs"],
                    "query": [
                        {"key": "applicationSubType", "value": "DroPcmp"},
                        {"key": "applicationType", "value": "7"},
                        {"key": "processType", "value": "PcmpSteps"},
                        {"key": "primaryFilter", "value": "{{pricingId}}"}
                    ]
                }
            },
            "response": []
        },
        {
            "name": "Get DRO Submit Logs",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/connect/decision-explainer/action-logs?applicationSubType=DroSubmit&applicationType=7&processType=DroSubmit&primaryFilter={{droId}}",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "connect", "decision-explainer", "action-logs"],
                    "query": [
                        {"key": "applicationSubType", "value": "DroSubmit"},
                        {"key": "applicationType", "value": "7"},
                        {"key": "processType", "value": "DroSubmit"},
                        {"key": "primaryFilter", "value": "{{droId}}"}
                    ]
                }
            },
            "response": []
        }
    ]
}

# P2 Medium Priority - Usage Details
USAGE_DETAILS_P2 = {
    "name": "Usage Details (v260)",
    "item": [
        {
            "name": "Get Asset Usage Details",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/asset-management/assets/{{assetId}}/usage-details",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "asset-management", "assets", "{{assetId}}", "usage-details"]
                }
            },
            "response": []
        },
        {
            "name": "Get Quote Line Item Usage Details",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/quotes/line-items/{{quoteLineItemId}}/usage-details",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "quotes", "line-items", "{{quoteLineItemId}}", "usage-details"]
                }
            },
            "response": []
        },
        {
            "name": "Get Sales Order Line Item Usage Details",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/commerce/sales-orders/line-items/{{orderItemId}}/usage-details",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "commerce", "sales-orders", "line-items", "{{orderItemId}}", "usage-details"]
                }
            },
            "response": []
        },
        {
            "name": "Get Binding Object Usage Details",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/revenue/usage-management/binding-objects/{{bindingObjectId}}/actions/usage-details?effectiveDate=2026-02-01",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "revenue", "usage-management", "binding-objects", "{{bindingObjectId}}", "actions", "usage-details"],
                    "query": [
                        {"key": "effectiveDate", "value": "2026-02-01"}
                    ]
                }
            },
            "response": []
        },
        {
            "name": "Trace Usage Consumption",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "usageProductId": "{{usageProductId}}",
                        "consumptionPeriod": "2026-02"
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/revenue/usage-management/consumption/actions/trace",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "revenue", "usage-management", "consumption", "actions", "trace"]
                }
            },
            "response": []
        },
        {
            "name": "Validate Usage Products",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps({
                        "usageProductIds": ["{{usageProductId}}"]
                    }, indent=2)
                },
                "url": {
                    "raw": "{{_endpoint}}/services/data/v{{version}}/revenue/usage-management/usage-products/actions/validate",
                    "host": ["{{_endpoint}}"],
                    "path": ["services", "data", "v{{version}}", "revenue", "usage-management", "usage-products", "actions", "validate"]
                }
            },
            "response": []
        }
    ]
}


def add_folder_to_collection(collection_path, folder_data):
    """Add a new folder to a Postman collection"""
    with open(collection_path, 'r') as f:
        collection = json.load(f)

    # Check if folder already exists
    folder_name = folder_data["name"]
    existing = [item for item in collection.get("item", []) if item.get("name") == folder_name]

    if existing:
        print(f"⚠️  Folder '{folder_name}' already exists in {collection_path.name}")
        return False

    # Add folder to collection
    collection["item"].append(folder_data)

    # Write back
    with open(collection_path, 'w') as f:
        json.dump(collection, f, indent=2)

    print(f"✅ Added folder '{folder_name}' to {collection_path.name}")
    return True


def main():
    script_dir = Path(__file__).parent
    rca_collection = script_dir / "RCA APIs - Winter'25 (258) Latest.postman_collection.json"

    if not rca_collection.exists():
        print(f"❌ Collection not found: {rca_collection}")
        return 1

    print("=" * 80)
    print("Adding v260 API Endpoints to RCA Collection")
    print("=" * 80)
    print()

    # Track additions
    added_folders = []
    total_endpoints = 0

    # Add P0 Critical endpoints
    print("📋 Phase 1: P0 Critical Endpoints")
    print("-" * 80)

    if add_folder_to_collection(rca_collection, INVOICE_SCHEDULERS):
        added_folders.append(("Invoice Schedulers (v260)", 4, "P0"))
        total_endpoints += 4

    if add_folder_to_collection(rca_collection, PAYMENT_SCHEDULERS):
        added_folders.append(("Payment Schedulers (v260)", 4, "P0"))
        total_endpoints += 4

    if add_folder_to_collection(rca_collection, PRODUCT_CONFIGURATOR):
        added_folders.append(("Product Configurator (v260)", 11, "P0"))
        total_endpoints += 11

    if add_folder_to_collection(rca_collection, INVOICING_ACTIONS_P0):
        added_folders.append(("Invoicing Actions (v260)", 12, "P0"))
        total_endpoints += 12

    print()

    # Add P1 High Priority endpoints
    print("📋 Phase 2: P1 High Priority Endpoints")
    print("-" * 80)

    if add_folder_to_collection(rca_collection, PCM_INDEX_MANAGEMENT):
        added_folders.append(("PCM Index Management (v260)", 6, "P1"))
        total_endpoints += 6

    if add_folder_to_collection(rca_collection, PCM_ENHANCEMENTS):
        added_folders.append(("PCM Enhancements (v260)", 3, "P1"))
        total_endpoints += 3

    if add_folder_to_collection(rca_collection, BILLING_ACTIONS_P1):
        added_folders.append(("Billing Actions (v260)", 4, "P1"))
        total_endpoints += 4

    print()

    # Add P2 Medium Priority endpoints
    print("📋 Phase 3: P2 Medium Priority Endpoints")
    print("-" * 80)

    if add_folder_to_collection(rca_collection, REVENUE_MANAGEMENT_P2):
        added_folders.append(("Revenue Management (v260)", 8, "P2"))
        total_endpoints += 8

    if add_folder_to_collection(rca_collection, DECISION_EXPLAINER_P2):
        added_folders.append(("Decision Explainer (v260)", 5, "P2"))
        total_endpoints += 5

    if add_folder_to_collection(rca_collection, USAGE_DETAILS_P2):
        added_folders.append(("Usage Details (v260)", 6, "P2"))
        total_endpoints += 6

    print()
    print("=" * 80)
    print("✅ v260 Endpoint Addition Complete!")
    print("=" * 80)
    print()

    if added_folders:
        print("📊 Summary of Added Folders:")
        print()
        for name, count, priority in added_folders:
            print(f"  [{priority}] {name} - {count} endpoints")
        print()
        print(f"📈 Total New Endpoints Added: {total_endpoints}")
        print()
        print("✨ Collection Coverage Enhanced:")
        print(f"   • Billing & Invoicing automation (schedulers, actions)")
        print(f"   • Product Configurator for CPQ")
        print(f"   • PCM enhancements (indexing, cloning, UoM)")
        print(f"   • Advanced billing operations (payments, credit memos)")
    else:
        print("⚠️  All folders already exist in the collection")

    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
