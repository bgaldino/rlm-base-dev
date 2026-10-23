"""Generate the Rentokil pest proposal OmniDataTransforms (extract + pass-through transform).

Usage:
    python scripts/docgen/build_rtk_proposal_odts.py unpackaged/post_pest_docgen/omniDataTransforms

Output keys must match the tokens in build_rtk_pest_proposal.py and the template's tokenList.
"""
import json
import os
import sys
import uuid
from xml.sax.saxutils import escape

OUT = sys.argv[1]
EXTRACT = "RLMRTKProposalExtract"
TRANSFORM = "RLMRTKProposalTransform"

# (seq, object, inputField, operator, filterValue, outputPath)
QUERIES = [
    (1, "Quote", "Id", "=", "Id", "Quote"),
    (2, "Account", "Id", "=", "Quote:AccountId", "Account"),
    (3, "User", "Id", "=", "Quote:CreatedById", "SalesRep"),
    (4, "QuoteLineItem", "QuoteId", "=", "Quote:Id", "Quote:Plan"),
    (4, "QuoteLineItem", "BillingFrequency", "<>", "''", "Quote:Plan"),
    (5, "QuoteLineItem", "QuoteId", "=", "Quote:Id", "Quote:OneTime"),
    (5, "QuoteLineItem", "BillingFrequency", "=", "''", "Quote:OneTime"),
    (6, "Product2", "Id", "=", "Quote:Plan:Product2Id", "Quote:Plan:Product"),
    (7, "Product2", "Id", "=", "Quote:OneTime:Product2Id", "Quote:OneTime:Product"),
    (8, "RLM_RTK_Finding__c", "Quote_Id__c", "=", "Quote:Id", "Quote:Finding"),
]

DATE = "Date(MM/dd/yyyy)"
# Fills a single row when the quote has no inspection findings.
DEFAULTS = {
    "Finding:Area": "Whole property",
    "Finding:Observation": "No active activity recorded",
}

# (inputField, outputField, format)
MAPPINGS = [
    ("Quote:Id", "QuoteId", "String"),
    ("Quote:QuoteNumber", "QuoteNumber", "String"),
    ("Quote:CreatedDate", "CreatedDate", DATE),
    ("Quote:ExpirationDate", "ExpirationDate", DATE),
    ("Account:Name", "AccountName", "String"),
    ("Account:Phone", "CustomerPhone", "String"),
    ("Quote:BillingStreet", "BillingStreet", "String"),
    ("Quote:BillingCity", "BillingCity", "String"),
    ("Quote:BillingState", "BillingState", "String"),
    ("Quote:BillingPostalCode", "BillingPostalCode", "String"),
    ("Quote:ShippingStreet", "ServiceStreet", "String"),
    ("Quote:ShippingCity", "ServiceCity", "String"),
    ("Quote:ShippingState", "ServiceState", "String"),
    ("Quote:ShippingPostalCode", "ServicePostalCode", "String"),
    ("SalesRep:Name", "SalesRep", "String"),
    ("SalesRep:Email", "SalesRepEmail", "String"),
    ("Quote:RLM_RTK_Monthly_Total__c", "MonthlyTotal", "Currency"),
    ("Quote:RLM_RTK_One_Time_Total__c", "OneTimeTotal", "Currency"),
    ("Quote:GrandTotal", "GrandTotal", "Currency"),
    ("Quote:Plan:Product:Name", "Plan:Name", "String"),
    ("Quote:Plan:Product:Description", "Plan:Description", "String"),
    ("Quote:Plan:Quantity", "Plan:Quantity", "Integer"),
    ("Quote:Plan:NetTotalPrice", "Plan:MonthlyPrice", "Currency"),
    ("Quote:OneTime:Product:Name", "OneTime:Name", "String"),
    ("Quote:OneTime:Product:Description", "OneTime:Description", "String"),
    ("Quote:OneTime:Quantity", "OneTime:Quantity", "Integer"),
    ("Quote:OneTime:NetTotalPrice", "OneTime:Price", "Currency"),
    ("Quote:Finding:Zone__c", "Finding:Area", "String"),
    ("Quote:Finding:Observation__c", "Finding:Observation", "String"),
    ("Quote:Finding:Severity__c", "Finding:Severity", "String"),
    ("Quote:Finding:Customer_Note__c", "Finding:Note", "String"),
]

SAMPLE_OUTPUT = {
    "QuoteId": "0Q0Ka000000EXAMPLE",
    "QuoteNumber": "00000039",
    "CreatedDate": "10/21/2026",
    "ExpirationDate": "11/20/2026",
    "AccountName": "Michael Reyes",
    "CustomerPhone": "(630) 555-0142",
    "BillingStreet": "316 Ridgewood Dr",
    "BillingCity": "Bloomingdale",
    "BillingState": "IL",
    "BillingPostalCode": "60108",
    "ServiceStreet": "316 Ridgewood Dr",
    "ServiceCity": "Bloomingdale",
    "ServiceState": "IL",
    "ServicePostalCode": "60108",
    "SalesRep": "Sample Specialist",
    "SalesRepEmail": "specialist@example.com",
    "MonthlyTotal": "$187.00",
    "OneTimeTotal": "$199.00",
    "GrandTotal": "$386.00",
    "Plan": [
        {"Name": "Home Protection Plan", "Description": "General pest plus rodent protection, quarterly service.", "Quantity": 1, "MonthlyPrice": "$79.00"},
        {"Name": "Seasonal Mosquito Plan", "Description": "Mosquito protection April through October; pauses in winter.", "Quantity": 1, "MonthlyPrice": "$69.00"},
    ],
    "OneTime": [
        {"Name": "Initial Service", "Description": "One-time cleanout and exclusion at signup.", "Quantity": 1, "Price": "$199.00"},
    ],
    "Finding": [
        {"Area": "Garage", "Observation": "Rodents – Droppings", "Severity": "Moderate", "Note": "Fresh droppings along the back wall."},
        {"Area": "Yard", "Observation": "Mosquitoes – Standing Water", "Severity": "Light", "Note": "Water collecting in the planter by the patio."},
    ],
}


def key(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"rlm-rtk-proposal/{name}"))


def item(name, fields):
    lines = ["    <omniDataTransformItem>"]
    for k in sorted(fields):
        lines.append(f"        <{k}>{escape(str(fields[k]), {chr(39): '&apos;'})}</{k}>")
    lines.append("    </omniDataTransformItem>")
    return "\n".join(lines)


def common(name, gk):
    return {
        "disabled": "false",
        "filterGroup": "0.0",
        "globalKey": gk,
        "linkedObjectSequence": "0.0",
        "name": name,
        "requiredForUpsert": "false",
        "upsertKey": "false",
    }


def doc(name, dtype, items, preview, expected=None, target=None):
    head = f"""<?xml version="1.0" encoding="UTF-8"?>
<OmniDataTransform xmlns="http://soap.sforce.com/2006/04/metadata">
    <active>false</active>
    <assignmentRulesUsed>false</assignmentRulesUsed>
    <deletedOnSuccess>false</deletedOnSuccess>
    <errorIgnored>false</errorIgnored>
"""
    if expected is not None:
        head += f"    <expectedOutputJson>{escape(json.dumps(expected, indent=2))}</expectedOutputJson>\n"
    head += f"""    <fieldLevelSecurityEnabled>false</fieldLevelSecurityEnabled>
    <inputType>JSON</inputType>
    <isManagedUsingStdDesigner>false</isManagedUsingStdDesigner>
    <name>{name}</name>
    <nullInputsIncludedInOutput>false</nullInputsIncludedInOutput>
"""
    tail = f"""    <outputType>JSON</outputType>
    <previewJsonData>{escape(json.dumps(preview, indent=2))}</previewJsonData>
    <processSuperBulk>false</processSuperBulk>
    <responseCacheTtlMinutes>0.0</responseCacheTtlMinutes>
    <rollbackOnError>false</rollbackOnError>
    <sourceObjectDefault>false</sourceObjectDefault>
    <synchronousProcessThreshold>0.0</synchronousProcessThreshold>
"""
    if target:
        tail += f"    <targetOutputFileName>{target}</targetOutputFileName>\n"
    tail += f"""    <type>{dtype}</type>
    <uniqueName>{name}_1</uniqueName>
    <versionNumber>1.0</versionNumber>
    <xmlDeclarationRemoved>false</xmlDeclarationRemoved>
</OmniDataTransform>
"""
    return head + "\n".join(items) + "\n" + tail


def build_extract():
    items = []
    for seq, obj, field, op, value, out in QUERIES:
        f = common(EXTRACT, key(f"q/{seq}/{field}/{op}"))
        f.update({
            "filterOperator": op,
            "filterValue": value,
            "inputFieldName": field,
            "inputObjectName": obj,
            "inputObjectQuerySequence": f"{seq}.0",
            "outputCreationSequence": "0.0",
            "outputFieldName": out,
            "outputObjectName": "json",
        })
        items.append(item(EXTRACT, f))
    for src, out, fmt in MAPPINGS:
        f = common(EXTRACT, key(f"m/{out}"))
        f.update({
            "inputFieldName": src,
            "inputObjectQuerySequence": "0.0",
            "outputCreationSequence": "1.0",
            "outputFieldFormat": fmt,
            "outputFieldName": out,
            "outputObjectName": "json",
            "transformValuesMappings": "{ }",
        })
        if out in DEFAULTS:
            f["defaultValue"] = DEFAULTS[out]
        items.append(item(EXTRACT, f))
    return doc(EXTRACT, "Extract", items, {"Id": "0Q0Ka000000EXAMPLE"})


def build_transform():
    items = []
    for _, out, _ in MAPPINGS:
        f = common(TRANSFORM, key(f"t/{out}"))
        f.update({
            "inputFieldName": out,
            "inputObjectQuerySequence": "0.0",
            "outputCreationSequence": "1.0",
            "outputFieldName": out,
            "outputObjectName": "json",
            "transformValuesMappings": "{ }",
        })
        items.append(item(TRANSFORM, f))
    return doc(TRANSFORM, "Transform", items, SAMPLE_OUTPUT, expected=SAMPLE_OUTPUT,
               target="Rentokil_Pest_Proposal(Version 1)")


os.makedirs(OUT, exist_ok=True)
for name, body in [(EXTRACT, build_extract()), (TRANSFORM, build_transform())]:
    with open(os.path.join(OUT, f"{name}_1.rpt-meta.xml"), "w", encoding="utf-8") as fh:
        fh.write(body)
print("wrote", OUT)
