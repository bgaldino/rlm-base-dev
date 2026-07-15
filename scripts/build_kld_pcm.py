#!/usr/bin/env python3
"""Generate datasets/sfdmu/kld/en-US/kld-pcm CSV content from the approved product map."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "datasets/sfdmu/kld/en-US/kld-pcm"


def write_csv(name: str, header: list[str], rows: list[list]) -> None:
    path = PLAN / name
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)


# --- Product definitions ---
# (sku, name, family, type, classification, uom, description)
PRODUCTS = [
    # Pathway bundles (configuration shells)
    ("KLD-PATH-NEB-NEB", "Nebula ECA to Nebula Review", "Bundle", "Bundle", "PC-KLD-PATHWAY", "",
     "Matter pathway: Nebula Early Case Assessment through Nebula Review hosting."),
    ("KLD-PATH-NEB-R1", "Nebula ECA to RelOne", "Bundle", "Bundle", "PC-KLD-PATHWAY", "",
     "Matter pathway: Nebula ECA with promotion to RelativityOne Review."),
    ("KLD-PATH-R1-R1", "RelOne ECA to RelOne", "Bundle", "Bundle", "PC-KLD-PATHWAY", "",
     "Matter pathway: RelativityOne ECA through RelOne Review hosting."),
    # Setup / staging / hosting
    ("KLD-SETUP-MATTER-GB", "Transactional Matter Set Up Fee", "Services", "", "PC-KLD-SETUP", "GB",
     "Per-GB transactional matter setup fee."),
    ("KLD-STAGING", "Staging", "Services", "", "PC-KLD-HOST", "GB",
     "One-time per GB fee for project staging."),
    ("KLD-NEB-ECA-HOST", "Nebula ECA Hosting", "Software", "", "PC-KLD-HOST", "GB-MO",
     "Nebula Processing/ECA repository hosting. Supports up to 10 concurrent users."),
    ("KLD-NEB-REVIEW", "Nebula Review", "Software", "", "PC-KLD-HOST", "GB-MO",
     "Promotion, hosting, and analytics for data promoted to active Nebula Review."),
    ("KLD-R1-ECA-HOST", "RelOne ECA Hosting", "Software", "", "PC-KLD-HOST", "GB-MO",
     "RelativityOne Early Case Assessment repository hosting."),
    ("KLD-R1-REVIEW", "RelOne Review", "Software", "", "PC-KLD-HOST", "GB-MO",
     "RelativityOne review hosting for promoted active review data."),
    # Forensics & collection
    ("KLD-FOR-COLL", "Forensic Data Collection", "Services", "", "PC-KLD-FORENS", "h",
     "On-site forensic collection of computers, servers, mobile, and external devices."),
    ("KLD-FOR-RCOLL", "Remote Forensic Data Collection", "Services", "", "PC-KLD-FORENS", "h",
     "Remote/in-lab forensic collection including O365, social media, and webmail sources."),
    ("KLD-FOR-DOWNTIME", "Forensic Data Collection - Downtime", "Services", "", "PC-KLD-FORENS", "h",
     "Onsite downtime caused by the client during forensic collection."),
    ("KLD-RMDC-HR", "RMDC - Remote Mobile Device Collection (Hourly)", "Services", "", "PC-KLD-FORENS", "h",
     "Remote mobile device collection billed hourly (2-hour minimum)."),
    ("KLD-RMDC-FLAT", "RMDC - Remote Mobile Device Collection (Flat)", "Services", "", "PC-KLD-FORENS", "EACH",
     "Flat-fee remote mobile device collection including image, media, and shipping."),
    ("KLD-RCMGR-PC", "RCMgr Self Collection Computer", "Services", "", "PC-KLD-FORENS", "EACH",
     "Self-collection kit for computers including drive image and shipping."),
    ("KLD-RCMGR-SRV", "RCMgr Self Collection Server", "Services", "", "PC-KLD-FORENS", "EACH",
     "Self-collection kit for servers including drive image and shipping."),
    ("KLD-RCMGR-DECRYPT", "RCMgr Drive Decryption", "Services", "", "PC-KLD-FORENS", "EACH",
     "Decryption fee for native delivery of collected data."),
    ("KLD-FOR-ANALYSIS", "Forensic Analysis", "Services", "", "PC-KLD-FORENS", "h",
     "Computer forensic analysis including preservation, listings, and deliverables."),
    ("KLD-TRAVEL-TIME", "Travel Time", "Services", "", "PC-KLD-FORENS", "h",
     "Travel time billed at 50% of the applicable service hourly rate."),
    ("KLD-TRAVEL-EXP", "Travel Expense", "Services", "", "PC-KLD-FORENS", "USD",
     "Travel-related expenses billed at actual cost."),
    # eDiscovery AI
    ("KLD-AI-ECI-CORE", "eDiscovery AI - Early Case Insight (Core)", "Software", "", "PC-KLD-AI", "DOC-RUN",
     "ECI Core modeling for early case insight and intelligent data reduction."),
    ("KLD-AI-ECI-ELEMENTS", "eDiscovery AI - Early Case Insight (Case Elements)", "Software", "", "PC-KLD-AI", "DOC-RUN",
     "Identifies Key People, Key Events, and Key Documents. Requires ECI Core."),
    ("KLD-AI-CASEBOT", "eDiscovery AI - Early Case Bot (CaseBot)", "Software", "", "PC-KLD-AI", "DOC-QTR",
     "Natural-language chatbot against ECI Core data, billed per document every 3 months."),
    ("KLD-AI-RELEVANCE", "eDiscovery AI - Relevance", "Software", "", "PC-KLD-AI", "DOC-RUN",
     "AI/GenAI relevancy scoring (up to 15 prompts per run)."),
    ("KLD-AI-PRIVILEGE", "eDiscovery AI - Privilege", "Software", "", "PC-KLD-AI", "DOC-RUN",
     "Privilege detection with pre-built and custom privilege identifiers."),
    ("KLD-AI-PII-DETECT", "eDiscovery AI - PII Detect", "Software", "", "PC-KLD-AI", "DOC",
     "Detects common PII and PHI within the target data set."),
    ("KLD-AI-PII-EXTRACT", "eDiscovery AI - PII Extract", "Software", "", "PC-KLD-AI", "DOC",
     "Extracts identified PII/PHI from target data sets."),
    ("KLD-AI-PII-REDACT", "eDiscovery AI - PII Redact", "Software", "", "PC-KLD-AI", "PAGE",
     "AI-driven redaction using PII Detect results."),
    # Analytics a-la-carte
    ("KLD-AN-ANALYTICS", "KLDiscovery Analytics", "Software", "", "PC-KLD-ANALYTICS", "GB",
     "Predictive coding, threading, near-duplicate detection, and workflow analytics."),
    ("KLD-AN-SUM", "Nebula AI Summarization", "Software", "", "PC-KLD-ANALYTICS", "MCHARS",
     "LLM summarization of authored content (per million characters)."),
    ("KLD-AN-SUM-MED", "Nebula AI Summarization (Medical)", "Software", "", "PC-KLD-ANALYTICS", "PAGE",
     "Purpose-built summarization for medical records."),
    ("KLD-AN-XLAT", "AI Translation", "Software", "", "PC-KLD-ANALYTICS", "MCHARS",
     "Document translation (per million characters)."),
    ("KLD-AN-TRANSCRIBE", "KLD Transcription Service", "Software", "", "PC-KLD-ANALYTICS", "ATRANS-HR",
     "Automated transcription of audio content."),
    # Professional services & delivery
    ("KLD-PS-PM", "Project Management", "Services", "", "PC-KLD-PS", "h",
     "Consultative support for ESI analysis, workflows, and quality control."),
    ("KLD-PS-TECH", "Technical Support", "Services", "", "PC-KLD-PS", "h",
     "Processing, load file customization, and review platform technical support."),
    ("KLD-MED-HDD", "Hard Drive", "Services", "", "PC-KLD-MEDIA", "EACH",
     "Hard drive media for deliverables."),
    ("KLD-MED-FREIGHT", "Freight", "Services", "", "PC-KLD-MEDIA", "USD",
     "Shipping charges billed as incurred."),
]

PATHWAYS = {
    "KLD-PATH-NEB-NEB": {
        "eca": "KLD-NEB-ECA-HOST",
        "review": "KLD-NEB-REVIEW",
    },
    "KLD-PATH-NEB-R1": {
        "eca": "KLD-NEB-ECA-HOST",
        "review": "KLD-R1-REVIEW",
    },
    "KLD-PATH-R1-R1": {
        "eca": "KLD-R1-ECA-HOST",
        "review": "KLD-R1-REVIEW",
    },
}

AI_SKUS = [
    "KLD-AI-ECI-CORE",
    "KLD-AI-ECI-ELEMENTS",
    "KLD-AI-CASEBOT",
    "KLD-AI-RELEVANCE",
    "KLD-AI-PRIVILEGE",
    "KLD-AI-PII-DETECT",
    "KLD-AI-PII-EXTRACT",
    "KLD-AI-PII-REDACT",
]

# Category mapping: sku -> (catalog, category)
CATEGORY_MAP = {
    "KLD-PATH-NEB-NEB": ("CAT-KLD-EDISC", "KLD-CAT-PATHWAY"),
    "KLD-PATH-NEB-R1": ("CAT-KLD-EDISC", "KLD-CAT-PATHWAY"),
    "KLD-PATH-R1-R1": ("CAT-KLD-EDISC", "KLD-CAT-PATHWAY"),
    "KLD-SETUP-MATTER-GB": ("CAT-KLD-EDISC", "KLD-CAT-SETUP"),
    "KLD-STAGING": ("CAT-KLD-EDISC", "KLD-CAT-STAGING"),
    "KLD-NEB-ECA-HOST": ("CAT-KLD-EDISC", "KLD-CAT-ECA"),
    "KLD-NEB-REVIEW": ("CAT-KLD-EDISC", "KLD-CAT-REVIEW"),
    "KLD-R1-ECA-HOST": ("CAT-KLD-EDISC", "KLD-CAT-ECA"),
    "KLD-R1-REVIEW": ("CAT-KLD-EDISC", "KLD-CAT-REVIEW"),
}
for sku in [
    "KLD-FOR-COLL", "KLD-FOR-RCOLL", "KLD-FOR-DOWNTIME", "KLD-RMDC-HR", "KLD-RMDC-FLAT",
    "KLD-RCMGR-PC", "KLD-RCMGR-SRV", "KLD-RCMGR-DECRYPT", "KLD-FOR-ANALYSIS",
    "KLD-TRAVEL-TIME", "KLD-TRAVEL-EXP",
]:
    CATEGORY_MAP[sku] = ("CAT-KLD-FORENS", "KLD-CAT-COLL" if sku != "KLD-FOR-ANALYSIS" and "TRAVEL" not in sku else (
        "KLD-CAT-ANALYSIS" if sku == "KLD-FOR-ANALYSIS" else "KLD-CAT-TRAVEL"
    ))
CATEGORY_MAP["KLD-FOR-ANALYSIS"] = ("CAT-KLD-FORENS", "KLD-CAT-ANALYSIS")
CATEGORY_MAP["KLD-TRAVEL-TIME"] = ("CAT-KLD-FORENS", "KLD-CAT-TRAVEL")
CATEGORY_MAP["KLD-TRAVEL-EXP"] = ("CAT-KLD-FORENS", "KLD-CAT-TRAVEL")
for sku in AI_SKUS:
    if "ECI" in sku or sku == "KLD-AI-CASEBOT":
        CATEGORY_MAP[sku] = ("CAT-KLD-AI", "KLD-CAT-ECI")
    elif "PII" in sku:
        CATEGORY_MAP[sku] = ("CAT-KLD-AI", "KLD-CAT-PII")
    else:
        CATEGORY_MAP[sku] = ("CAT-KLD-AI", "KLD-CAT-RELEVANCE")
for sku in ["KLD-AN-ANALYTICS", "KLD-AN-SUM", "KLD-AN-SUM-MED", "KLD-AN-XLAT", "KLD-AN-TRANSCRIBE"]:
    CATEGORY_MAP[sku] = ("CAT-KLD-AI", "KLD-CAT-ANALYTICS")
CATEGORY_MAP["KLD-PS-PM"] = ("CAT-KLD-PS", "KLD-CAT-PS-CORE")
CATEGORY_MAP["KLD-PS-TECH"] = ("CAT-KLD-PS", "KLD-CAT-PS-CORE")
CATEGORY_MAP["KLD-MED-HDD"] = ("CAT-KLD-MEDIA", "KLD-CAT-DELIVERY")
CATEGORY_MAP["KLD-MED-FREIGHT"] = ("CAT-KLD-MEDIA", "KLD-CAT-DELIVERY")

HOSTING_SKUS = {"KLD-NEB-ECA-HOST", "KLD-NEB-REVIEW", "KLD-R1-ECA-HOST", "KLD-R1-REVIEW"}
ONE_TIME_GB = {"KLD-STAGING", "KLD-SETUP-MATTER-GB"}
CASEBOT = "KLD-AI-CASEBOT"


def product2_rows() -> list[list]:
    rows = []
    for sku, name, family, ptype, based_on, uom, desc in PRODUCTS:
        is_bundle = ptype == "Bundle"
        rows.append([
            based_on,
            "false",
            "Allowed" if is_bundle else "",
            desc,
            "",
            family,
            "true",
            "true",
            "false",
            name,
            sku,
            uom if uom in ("GB", "h") else "",
            "",
            sku,
            ptype,
            uom,
        ])
    return rows


def psmo_rows() -> list[list]:
    rows = []
    for sku, name, family, ptype, _cls, uom, _desc in PRODUCTS:
        if ptype == "Bundle":
            rows.append([f"{sku};One-Time;OneTime", "true", sku, "One-Time;OneTime", ""])
            continue
        if sku in HOSTING_SKUS:
            rows.append([f"{sku};Evergreen Monthly;Evergreen", "true", sku, "Evergreen Monthly;Evergreen", "Default Proration Policy"])
            rows.append([f"{sku};Term Monthly;TermDefined", "false", sku, "Term Monthly;TermDefined", "Default Proration Policy"])
        elif sku == CASEBOT:
            rows.append([f"{sku};Evergreen - Quarterly;Evergreen", "true", sku, "Evergreen - Quarterly;Evergreen", "Default Proration Policy"])
        else:
            rows.append([f"{sku};One-Time;OneTime", "true", sku, "One-Time;OneTime", ""])
    return rows


def component_groups() -> list[list]:
    rows = []
    suffix_map = {
        "KLD-PATH-NEB-NEB": "NEBNEB",
        "KLD-PATH-NEB-R1": "NEBR1",
        "KLD-PATH-R1-R1": "R1R1",
    }
    for path_sku, cfg in PATHWAYS.items():
        sfx = suffix_map[path_sku]
        groups = [
            (f"KLD-CG-{sfx}-STAGING", "Staging", 1, 1, 1),
            (f"KLD-CG-{sfx}-ECA", "ECA Hosting", 1, 1, 2),
            (f"KLD-CG-{sfx}-REVIEW", "Review Hosting", 1, 1, 3),
            (f"KLD-CG-{sfx}-PS", "Professional Services", 0, 2, 4),
            (f"KLD-CG-{sfx}-AI", "Optional AI", 0, 8, 5),
        ]
        for code, gname, mn, mx, order in groups:
            rows.append([
                f"{code};{path_sku}",
                code,
                "",
                mx if mx else "",
                mn,
                gname,
                "",
                path_sku,
                order,
            ])
    return rows


def related_components() -> list[list]:
    rel = "Bundle to Bundle Component Relationship"
    rows = []
    suffix_map = {
        "KLD-PATH-NEB-NEB": "NEBNEB",
        "KLD-PATH-NEB-R1": "NEBR1",
        "KLD-PATH-R1-R1": "R1R1",
    }
    for path_sku, cfg in PATHWAYS.items():
        sfx = suffix_map[path_sku]
        core = [
            ("KLD-STAGING", f"KLD-CG-{sfx}-STAGING", True, 1, 10),
            (cfg["eca"], f"KLD-CG-{sfx}-ECA", True, 1, 20),
            (cfg["review"], f"KLD-CG-{sfx}-REVIEW", True, 1, 30),
        ]
        for child, group, required, qty, seq in core:
            rows.append(prc_row(path_sku, child, group, rel, required, qty, seq, True))
        for child, seq in [("KLD-PS-PM", 40), ("KLD-PS-TECH", 50)]:
            rows.append(prc_row(path_sku, child, f"KLD-CG-{sfx}-PS", rel, False, 1, seq, True))
        ai_seq = 60
        for child in AI_SKUS:
            rows.append(prc_row(path_sku, child, f"KLD-CG-{sfx}-AI", rel, False, 1, ai_seq, True))
            ai_seq += 10
    return rows


def prc_row(parent, child, group, rel, required, qty, seq, qty_editable):
    return [
        f";{child};{parent};{group};{rel}",
        child,
        "",
        "BundleComponent",
        "",
        "false",
        "true" if required else "false",
        "false",
        "true" if qty_editable else "false",
        "",
        "1" if required else "",
        parent,
        "Bundle",
        "",
        group,
        rel,
        str(qty),
        "",
        "Always",
        str(seq),
        "",
    ]


def main() -> None:
    write_csv(
        "UnitOfMeasureClass.csv",
        ["BaseUnitOfMeasure.UnitCode", "Code", "DefaultUnitOfMeasure.UnitCode", "Description", "Name", "Status", "Type"],
        [
            ["EACH", "KLD-COUNT", "EACH", "Count-based units", "KLD Count", "Active", "Usage"],
            ["USD", "CURRENCY", "USD", "", "Currency", "Active", "Currency"],
            ["GB", "DATAVOL", "GB", "Data volume", "Data Volume", "Active", "Usage"],
            ["h", "TIME", "h", "Time-based units", "Time", "Active", "Usage"],
        ],
    )

    write_csv(
        "UnitOfMeasure.csv",
        ["ConversionFactor", "Description", "Name", "RoundingMethod", "Scale", "Sequence", "Status", "Type", "UnitCode", "UnitOfMeasureClass.Code"],
        [
            ["1", "Gigabyte", "Gigabyte", "", "", "1", "Active", "Data", "GB", "DATAVOL"],
            ["1", "Gigabyte per month", "Gigabyte Month", "", "", "2", "Active", "Data", "GB-MO", "DATAVOL"],
            ["1", "Hour", "Hour", "", "", "1", "Active", "Time", "h", "TIME"],
            ["1", "Each", "Each", "", "", "1", "Active", "Count", "EACH", "KLD-COUNT"],
            ["1", "Document", "Document", "", "", "2", "Active", "Count", "DOC", "KLD-COUNT"],
            ["1", "Document per run", "Document Run", "", "", "3", "Active", "Count", "DOC-RUN", "KLD-COUNT"],
            ["1", "Document per quarter", "Document Quarter", "", "", "4", "Active", "Count", "DOC-QTR", "KLD-COUNT"],
            ["1", "Page", "Page", "", "", "5", "Active", "Count", "PAGE", "KLD-COUNT"],
            ["1", "Million characters", "Million Characters", "", "", "6", "Active", "Count", "MCHARS", "KLD-COUNT"],
            ["1", "Transcription hour", "Automated Transcription Hour", "", "", "7", "Active", "Time", "ATRANS-HR", "TIME"],
            ["1", "US Dollar pass-through", "USD", "", "", "1", "Active", "Cost", "USD", "CURRENCY"],
        ],
    )

    classifications = [
        ("PC-KLD-PATHWAY", "KLD Pathway", "Active"),
        ("PC-KLD-HOST", "KLD Hosting", "Active"),
        ("PC-KLD-SETUP", "KLD Setup", "Active"),
        ("PC-KLD-FORENS", "KLD Forensics", "Active"),
        ("PC-KLD-AI", "KLD eDiscovery AI", "Active"),
        ("PC-KLD-ANALYTICS", "KLD Analytics", "Active"),
        ("PC-KLD-PS", "KLD Professional Services", "Active"),
        ("PC-KLD-MEDIA", "KLD Media & Delivery", "Active"),
    ]
    write_csv(
        "ProductClassification.csv",
        ["Code", "Name", "ParentProductClassification.Code", "Status"],
        [[c, n, "", s] for c, n, s in classifications],
    )

    write_csv(
        "Product2.csv",
        ["BasedOn.Code", "CanRamp", "ConfigureDuringSale", "Description", "DisplayUrl", "Family", "IsActive", "IsAssetizable", "IsSoldOnlyWithOtherProds", "Name", "ProductCode", "QuantityUnitOfMeasure", "SpecificationType", "StockKeepingUnit", "Type", "UnitOfMeasure.UnitCode"],
        product2_rows(),
    )

    write_csv(
        "ProductSellingModel.csv",
        ["$$Name$SellingModelType", "DoesAutoRenewAssetByDefault", "Name", "PricingTerm", "PricingTermUnit", "SellingModelType", "Status"],
        [
            ["Evergreen - Quarterly;Evergreen", "false", "Evergreen - Quarterly", "1", "Quarterly", "Evergreen", "Active"],
            ["Evergreen Monthly;Evergreen", "false", "Evergreen Monthly", "1", "Months", "Evergreen", "Active"],
            ["One-Time;OneTime", "false", "One-Time", "", "", "OneTime", "Active"],
            ["Term Monthly;TermDefined", "false", "Term Monthly", "1", "Months", "TermDefined", "Active"],
        ],
    )

    write_csv(
        "ProrationPolicy.csv",
        ["ArePartialPeriodsAllowed", "Name", "ProrationPolicyType", "RemainderStrategy"],
        [["true", "Default Proration Policy", "StandardTimePeriods", "AddToLast"]],
    )

    write_csv(
        "ProductSellingModelOption.csv",
        ["$$Product2.StockKeepingUnit$ProductSellingModel.Name$ProductSellingModel.SellingModelType", "IsDefault", "Product2.StockKeepingUnit", "ProductSellingModel.$$Name$SellingModelType", "ProrationPolicy.Name"],
        psmo_rows(),
    )

    write_csv(
        "ProductRelationshipType.csv",
        ["AssociatedProductRoleCat", "MainProductRoleCat", "Name"],
        [["BundleComponent", "Bundle", "Bundle to Bundle Component Relationship"]],
    )

    write_csv(
        "ProductComponentGroup.csv",
        ["$$Code$ParentProduct.StockKeepingUnit", "Code", "Description", "MaxBundleComponents", "MinBundleComponents", "Name", "ParentGroup.Code", "ParentProduct.StockKeepingUnit", "Sequence"],
        component_groups(),
    )

    prc_header = [
        "$$ChildProductClassification.Code$ChildProduct.StockKeepingUnit$ParentProduct.StockKeepingUnit$ProductComponentGroup.Code$ProductRelationshipType.Name",
        "ChildProduct.StockKeepingUnit", "ChildProductClassification.Code", "ChildProductRole",
        "ChildSellingModel.$$Name$SellingModelType", "DoesBundlePriceIncludeChild", "IsComponentRequired",
        "IsDefaultComponent", "IsQuantityEditable", "MaxQuantity", "MinQuantity", "ParentProduct.StockKeepingUnit",
        "ParentProductRole", "ParentSellingModel.$$Name$SellingModelType", "ProductComponentGroup.Code",
        "ProductRelationshipType.Name", "Quantity", "QuantityScaleMethod", "QuoteVisibility", "Sequence",
        "UnitOfMeasure.UnitCode",
    ]
    write_csv("ProductRelatedComponent.csv", prc_header, related_components())

    write_csv(
        "ProductCatalog.csv",
        ["CatalogType", "Code", "Description", "EffectiveEndDate", "EffectiveStartDate", "Name"],
        [
            ["Sales", "CAT-KLD-EDISC", "KLDiscovery eDiscovery hosting and pathways", "", "", "KLDiscovery eDiscovery"],
            ["Sales", "CAT-KLD-AI", "KLDiscovery eDiscovery AI and analytics", "", "", "KLDiscovery AI & Analytics"],
            ["Sales", "CAT-KLD-FORENS", "KLDiscovery forensics and collection", "", "", "KLDiscovery Forensics"],
            ["Sales", "CAT-KLD-PS", "KLDiscovery professional services", "", "", "KLDiscovery Professional Services"],
            ["Sales", "CAT-KLD-MEDIA", "KLDiscovery media and delivery", "", "", "KLDiscovery Media & Delivery"],
        ],
    )

    categories = [
        ("CAT-KLD-EDISC", "KLD-CAT-STAGING", "Staging", "true", 10),
        ("CAT-KLD-EDISC", "KLD-CAT-ECA", "ECA Hosting", "true", 20),
        ("CAT-KLD-EDISC", "KLD-CAT-REVIEW", "Review Hosting", "true", 30),
        ("CAT-KLD-EDISC", "KLD-CAT-SETUP", "Matter Setup", "true", 40),
        ("CAT-KLD-EDISC", "KLD-CAT-PATHWAY", "Matter Pathways", "true", 50),
        ("CAT-KLD-AI", "KLD-CAT-ECI", "Early Case Insight", "true", 10),
        ("CAT-KLD-AI", "KLD-CAT-RELEVANCE", "Relevance & Privilege", "true", 20),
        ("CAT-KLD-AI", "KLD-CAT-PII", "PII Services", "true", 30),
        ("CAT-KLD-AI", "KLD-CAT-ANALYTICS", "Analytics A-La-Carte", "true", 40),
        ("CAT-KLD-FORENS", "KLD-CAT-COLL", "Collection", "true", 10),
        ("CAT-KLD-FORENS", "KLD-CAT-ANALYSIS", "Forensic Analysis", "true", 20),
        ("CAT-KLD-FORENS", "KLD-CAT-TRAVEL", "Travel", "true", 30),
        ("CAT-KLD-PS", "KLD-CAT-PS-CORE", "Professional Services", "true", 10),
        ("CAT-KLD-MEDIA", "KLD-CAT-DELIVERY", "Media & Delivery", "true", 10),
    ]
    write_csv(
        "ProductCategory.csv",
        ["Catalog.Code", "Code", "Description", "IsNavigational", "Name", "ParentCategory.Code", "SortOrder"],
        [[c, code, "", nav, name, "", sort] for c, code, name, nav, sort in categories],
    )

    cat_prod_rows = []
    for sku in [p[0] for p in PRODUCTS]:
        cat, cat_code = CATEGORY_MAP[sku]
        cat_prod_rows.append([f"{cat_code};{sku}", cat, "true", sku, cat_code])
    write_csv(
        "ProductCategoryProduct.csv",
        ["$$ProductCategory.Code$Product.StockKeepingUnit", "Catalog.Code", "IsPrimaryCategory", "Product.StockKeepingUnit", "ProductCategory.Code"],
        cat_prod_rows,
    )

    write_csv(
        "ProductQualification.csv",
        ["EffectiveFromDate", "EffectiveToDate", "IsQualified", "Name", "ParentProduct.StockKeepingUnit", "Product.StockKeepingUnit"],
        [],
    )

    # Thin attribute infrastructure for pathway estimate drivers
    write_csv("AttributePicklist.csv", ["Code", "DataType", "Description", "Name", "Status", "UnitOfMeasureId"], [])
    write_csv("AttributePicklistValue.csv", ["Code", "DisplayValue", "IsDefault", "Name", "Picklist.Name", "Sequence", "Status", "Value"], [])
    write_csv(
        "AttributeDefinition.csv",
        ["Code", "DataType", "DefaultHelpText", "DefaultValue", "Description", "DeveloperName", "IsActive", "IsRequired", "Label", "Name", "Picklist.Name", "SourceSystemIdentifier", "UnitOfMeasure.UnitCode", "ValueDescription"],
        [
            ["ATTR-KLD-SOURCE-GB", "Number", "", "1000", "Estimated source data volume in GB", "Source_Data_GB", "true", "false", "Source Data (GB)", "Source Data GB", "", "", "GB", ""],
            ["ATTR-KLD-ECA-PCT", "Number", "", "70", "Percent of expanded data in ECA hosting", "ECA_Data_Pct", "true", "false", "ECA Data %", "ECA Data Percent", "", "", "", ""],
            ["ATTR-KLD-REVIEW-PCT", "Number", "", "30", "Percent of ECA data promoted to review", "Active_Review_Pct", "true", "false", "Active Review %", "Active Review Percent", "", "", "", ""],
        ],
    )
    write_csv("AttributeCategory.csv", ["Code", "Description", "Name"], [["AC-KLD-MATTER", "", "Matter Estimate"]])
    write_csv(
        "AttributeCategoryAttribute.csv",
        ["$$AttributeCategory.Code$AttributeDefinition.Code", "AttributeCategory.Code", "AttributeDefinition.Code"],
        [
            ["AC-KLD-MATTER;ATTR-KLD-SOURCE-GB", "AC-KLD-MATTER", "ATTR-KLD-SOURCE-GB"],
            ["AC-KLD-MATTER;ATTR-KLD-ECA-PCT", "AC-KLD-MATTER", "ATTR-KLD-ECA-PCT"],
            ["AC-KLD-MATTER;ATTR-KLD-REVIEW-PCT", "AC-KLD-MATTER", "ATTR-KLD-REVIEW-PCT"],
        ],
    )
    write_csv("ProductClassificationAttr.csv", ["AttributeCategory.Code", "AttributeDefinition.Code", "AttributeNameOverride", "DefaultValue", "Description", "DisplayType", "HelpText", "IsHidden", "IsPriceImpacting", "IsReadOnly", "IsRequired", "MaximumCharacterCount", "MaximumValue", "MinimumCharacterCount", "MinimumValue", "Name", "ProductClassification.Code", "Sequence", "Status", "StepValue", "UnitOfMeasure.UnitCode", "ValueDescription"], [
        ["AC-KLD-MATTER", "ATTR-KLD-SOURCE-GB", "", "1000", "", "", "", "false", "false", "false", "false", "", "", "", "", "KLD Pathway Source GB", "PC-KLD-PATHWAY", "1", "Active", "", "GB", ""],
        ["AC-KLD-MATTER", "ATTR-KLD-ECA-PCT", "", "70", "", "", "", "false", "false", "false", "false", "", "100", "", "0", "KLD Pathway ECA Percent", "PC-KLD-PATHWAY", "2", "Active", "", "", ""],
        ["AC-KLD-MATTER", "ATTR-KLD-REVIEW-PCT", "", "30", "", "", "", "false", "false", "false", "false", "", "100", "", "0", "KLD Pathway Review Percent", "PC-KLD-PATHWAY", "3", "Active", "", "", ""],
    ])
    write_csv("ProductAttributeDefinition.csv", ["AttributeCategory.Code", "AttributeDefinition.Code", "AttributeNameOverride", "DefaultValue", "Description", "DisplayType", "HelpText", "IsHidden", "IsPriceImpacting", "IsReadOnly", "IsRequired", "MaximumCharacterCount", "MaximumValue", "MinimumCharacterCount", "MinimumValue", "Name", "OverriddenProductAttributeDefinitionId", "Product2.StockKeepingUnit", "ProductClassificationAttribute.Name", "Sequence", "Status", "StepValue", "UnitOfMeasure.UnitCode", "ValueDescription"], [])

    write_csv("ProductRampSegment.csv", ["DurationType", "Name", "Product.StockKeepingUnit", "ProductSellingModel.SellingModelType", "SegmentType", "TrialDuration"], [])
    write_csv("ProductDisqualification.csv", ["EffectiveFromDate", "EffectiveToDate", "IsDisqualified", "Name", "ParentProductId", "ProductId", "Reason", "RootProductId"], [])
    write_csv("ProductCategoryDisqual.csv", ["CategoryId", "EffectiveFromDate", "EffectiveToDate", "IsDisqualified", "Name", "Reason"], [])
    write_csv("ProductCategoryQualification.csv", ["CategoryId", "EffectiveFromDate", "EffectiveToDate", "IsQualified", "Name"], [])
    write_csv("ProdtAttrScope.csv", ["Name", "Scope", "UsageType"], [])

    print(f"Generated kld-pcm with {len(PRODUCTS)} products")


if __name__ == "__main__":
    main()
