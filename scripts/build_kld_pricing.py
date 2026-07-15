#!/usr/bin/env python3
"""Generate datasets/sfdmu/kld/en-US/kld-pricing CSV content."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "datasets/sfdmu/kld/en-US/kld-pricing"
EFFECTIVE = "2024-01-01T00:00:00.000+0000"
PAS = "Standard Price Adjustment Tier"
PAS_KEY = f"{PAS};USD"
PB = "Standard Price Book;true"

PATHWAY_SKUS = {
    "KLD-PATH-NEB-NEB",
    "KLD-PATH-NEB-R1",
    "KLD-PATH-R1-R1",
}

HOSTING_SKUS = {
    "KLD-NEB-ECA-HOST",
    "KLD-NEB-REVIEW",
    "KLD-R1-ECA-HOST",
    "KLD-R1-REVIEW",
}

HOSTING_PSMS = [
    ("Evergreen Monthly", "Evergreen"),
    ("Term Monthly", "TermDefined"),
]

ECA_TIERS = [
    (0, 500, 2.50),
    (501, 1000, 2.40),
    (1001, 1500, 2.30),
    (1501, 2000, 2.20),
    (2001, 2500, 2.10),
    (2501, 3000, 2.00),
    (3001, 3500, 1.90),
    (3501, 4000, 1.80),
    (4001, 4500, 1.70),
    (4501, 5000, 1.60),
    (5001, None, 1.50),
]

REVIEW_TIERS = [
    (0, 250, 14.00),
    (251, 500, 13.75),
    (501, 1000, 13.50),
    (1001, 2000, 13.25),
    (2001, 3000, 13.00),
    (3001, 4000, 12.75),
    (4001, 5000, 12.50),
    (5001, 6000, 12.25),
    (6001, 7000, 12.00),
    (7001, 8000, 11.75),
    (8001, 9000, 11.50),
    (9001, 10000, 11.25),
    (10001, None, 11.25),
]

# (sku, psm_name, psm_type) -> unit price USD — One-Time unless noted
FLAT_PBE: dict[tuple[str, str, str], float] = {
    ("KLD-STAGING", "One-Time", "OneTime"): 10.00,
    ("KLD-SETUP-MATTER-GB", "One-Time", "OneTime"): 10.00,
    ("KLD-FOR-COLL", "One-Time", "OneTime"): 350.00,
    ("KLD-FOR-RCOLL", "One-Time", "OneTime"): 295.00,
    ("KLD-FOR-DOWNTIME", "One-Time", "OneTime"): 175.00,
    ("KLD-RMDC-HR", "One-Time", "OneTime"): 295.00,
    ("KLD-RMDC-FLAT", "One-Time", "OneTime"): 1250.00,
    ("KLD-RCMGR-PC", "One-Time", "OneTime"): 550.00,
    ("KLD-RCMGR-SRV", "One-Time", "OneTime"): 850.00,
    ("KLD-RCMGR-DECRYPT", "One-Time", "OneTime"): 200.00,
    ("KLD-FOR-ANALYSIS", "One-Time", "OneTime"): 450.00,
    ("KLD-TRAVEL-TIME", "One-Time", "OneTime"): 175.00,
    ("KLD-TRAVEL-EXP", "One-Time", "OneTime"): 0.00,
    ("KLD-AI-ECI-CORE", "One-Time", "OneTime"): 0.04,
    ("KLD-AI-ECI-ELEMENTS", "One-Time", "OneTime"): 0.04,
    ("KLD-AI-CASEBOT", "Evergreen - Quarterly", "Evergreen"): 0.08,
    ("KLD-AI-RELEVANCE", "One-Time", "OneTime"): 0.30,
    ("KLD-AI-PRIVILEGE", "One-Time", "OneTime"): 0.30,
    ("KLD-AI-PII-DETECT", "One-Time", "OneTime"): 0.20,
    ("KLD-AI-PII-EXTRACT", "One-Time", "OneTime"): 1.05,
    ("KLD-AI-PII-REDACT", "One-Time", "OneTime"): 0.35,
    ("KLD-AN-ANALYTICS", "One-Time", "OneTime"): 5.00,
    ("KLD-AN-SUM", "One-Time", "OneTime"): 25.00,
    ("KLD-AN-SUM-MED", "One-Time", "OneTime"): 0.50,
    ("KLD-AN-XLAT", "One-Time", "OneTime"): 40.00,
    ("KLD-AN-TRANSCRIBE", "One-Time", "OneTime"): 15.00,
    ("KLD-PS-PM", "One-Time", "OneTime"): 195.00,
    ("KLD-PS-TECH", "One-Time", "OneTime"): 175.00,
    ("KLD-MED-HDD", "One-Time", "OneTime"): 150.00,
    ("KLD-MED-FREIGHT", "One-Time", "OneTime"): 0.00,
}

PRODUCT_NAMES = {
    "KLD-PATH-NEB-NEB": "Nebula ECA to Nebula Review",
    "KLD-PATH-NEB-R1": "Nebula ECA to RelOne",
    "KLD-PATH-R1-R1": "RelOne ECA to RelOne",
    "KLD-STAGING": "Staging",
    "KLD-SETUP-MATTER-GB": "Transactional Matter Set Up Fee",
    "KLD-NEB-ECA-HOST": "Nebula ECA Hosting",
    "KLD-NEB-REVIEW": "Nebula Review",
    "KLD-R1-ECA-HOST": "RelOne ECA Hosting",
    "KLD-R1-REVIEW": "RelOne Review",
    "KLD-FOR-COLL": "Forensic Data Collection",
    "KLD-FOR-RCOLL": "Remote Forensic Data Collection",
    "KLD-FOR-DOWNTIME": "Forensic Data Collection - Downtime",
    "KLD-RMDC-HR": "RMDC - Remote Mobile Device Collection (Hourly)",
    "KLD-RMDC-FLAT": "RMDC - Remote Mobile Device Collection (Flat)",
    "KLD-RCMGR-PC": "RCMgr Self Collection Computer",
    "KLD-RCMGR-SRV": "RCMgr Self Collection Server",
    "KLD-RCMGR-DECRYPT": "RCMgr Drive Decryption",
    "KLD-FOR-ANALYSIS": "Forensic Analysis",
    "KLD-TRAVEL-TIME": "Travel Time",
    "KLD-TRAVEL-EXP": "Travel Expense",
    "KLD-AI-ECI-CORE": "eDiscovery AI - Early Case Insight (Core)",
    "KLD-AI-ECI-ELEMENTS": "eDiscovery AI - Early Case Insight (Case Elements)",
    "KLD-AI-CASEBOT": "eDiscovery AI - Early Case Bot (CaseBot)",
    "KLD-AI-RELEVANCE": "eDiscovery AI - Relevance",
    "KLD-AI-PRIVILEGE": "eDiscovery AI - Privilege",
    "KLD-AI-PII-DETECT": "eDiscovery AI - PII Detect",
    "KLD-AI-PII-EXTRACT": "eDiscovery AI - PII Extract",
    "KLD-AI-PII-REDACT": "eDiscovery AI - PII Redact",
    "KLD-AN-ANALYTICS": "KLDiscovery Analytics",
    "KLD-AN-SUM": "Nebula AI Summarization",
    "KLD-AN-SUM-MED": "Nebula AI Summarization (Medical)",
    "KLD-AN-XLAT": "AI Translation",
    "KLD-AN-TRANSCRIBE": "KLD Transcription Service",
    "KLD-PS-PM": "Project Management",
    "KLD-PS-TECH": "Technical Support",
    "KLD-MED-HDD": "Hard Drive",
    "KLD-MED-FREIGHT": "Freight",
}


def write_csv(name: str, header: list[str], rows: list[list]) -> None:
    with (PLAN / name).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)


def tier_list_for_sku(sku: str) -> list[tuple[int, int | None, float]]:
    if sku in ("KLD-NEB-ECA-HOST", "KLD-R1-ECA-HOST"):
        return ECA_TIERS
    if sku in ("KLD-NEB-REVIEW", "KLD-R1-REVIEW"):
        return REVIEW_TIERS
    return []


def pat_rows() -> list[list]:
    header = [
        "$$PriceAdjustmentSchedule.Name$Product2.StockKeepingUnit$ProductSellingModel.Name$ProductSellingModel.SellingModelType$TierType$TierValue$LowerBound$CurrencyIsoCode$EffectiveFrom",
        "AdjustmentType", "CurrencyIsoCode", "EffectiveFrom", "EffectiveTo", "LowerBound",
        "PriceAdjustmentSchedule.$$Name$CurrencyIsoCode", "PricingTerm", "PricingTermUnit",
        "Product2.StockKeepingUnit", "ProductSellingModel.$$Name$SellingModelType",
        "ScheduleType", "SellingModelType", "TierType", "TierValue", "UpperBound",
    ]
    rows: list[list] = []
    for sku in sorted(HOSTING_SKUS):
        tiers = tier_list_for_sku(sku)
        base_price = tiers[0][2]
        for psm_name, psm_type in HOSTING_PSMS:
            for lower, upper, price in tiers:
                tier_type = "AdjustmentAmount"
                composite = f"{PAS};{sku};{psm_name};{psm_type};{tier_type};{price};{lower};USD;{EFFECTIVE}"
                psm_combo = f"{psm_name};{psm_type}"
                rows.append([
                    composite,
                    "Override",
                    "USD",
                    EFFECTIVE,
                    "",
                    str(lower),
                    PAS_KEY,
                    "1",
                    "Months",
                    sku,
                    psm_combo,
                    "Volume",
                    psm_type,
                    tier_type,
                    str(price),
                    "" if upper is None else str(upper),
                ])
    return rows


def pbe_rows() -> list[list]:
    rows: list[list] = []
    for sku in sorted(PATHWAY_SKUS):
        rows.append([
            f"{sku};One-Time;USD",
            "USD", "true", "false", PRODUCT_NAMES[sku], PB, sku, "One-Time;OneTime", "0",
        ])
    for (sku, psm_name, psm_type), price in sorted(FLAT_PBE.items()):
        rows.append([
            f"{sku};{psm_name};USD",
            "USD", "true", "false", PRODUCT_NAMES[sku], PB, sku, f"{psm_name};{psm_type}", str(price),
        ])
    for sku in sorted(HOSTING_SKUS):
        tiers = tier_list_for_sku(sku)
        base = tiers[0][2]
        for psm_name, psm_type in HOSTING_PSMS:
            rows.append([
                f"{sku};{psm_name};USD",
                "USD", "true", "false", PRODUCT_NAMES[sku], PB, sku, f"{psm_name};{psm_type}", str(base),
            ])
    return rows


def cost_multiplier(sku: str) -> float:
    digest = hashlib.sha256(sku.encode()).hexdigest()
    return 0.40 + (int(digest[:8], 16) % 11) / 100.0


def cbe_rows() -> list[list]:
    rows: list[list] = []
    prices: dict[str, float] = {}
    for (sku, _psm, _type), price in FLAT_PBE.items():
        prices[sku] = max(prices.get(sku, 0), price)
    for sku in HOSTING_SKUS:
        prices[sku] = tier_list_for_sku(sku)[0][2]
    for sku, price in sorted(prices.items()):
        if sku in PATHWAY_SKUS or price <= 0:
            continue
        cost = round(price * cost_multiplier(sku), 2)
        rows.append([
            f"Standard Cost Book;{sku};USD",
            str(cost),
            "Standard Cost Book",
            "USD",
            "",
            "2024-01-01T17:00:00.000+0000",
            "",
            sku,
        ])
    return rows


def product2_skus() -> list[str]:
    skus = set(PATHWAY_SKUS) | set(HOSTING_SKUS) | {s for s, _, _ in FLAT_PBE}
    return sorted(skus)


def main() -> None:
    write_csv("CurrencyType.csv", ["ConversionRate", "DecimalPlaces", "IsActive", "IsCorporate", "IsoCode"], [[1, 2, "true", "true", "USD"]])
    write_csv("ProrationPolicy.csv", ["ArePartialPeriodsAllowed", "Name", "ProrationPolicyType", "RemainderStrategy"], [["true", "Default Proration Policy", "StandardTimePeriods", "AddToLast"]])
    write_csv("CostBook.csv", ["Name", "IsDefault", "EffectiveFrom", "EffectiveTo"], [["Standard Cost Book", "true", "2024-01-01T17:00:00.000+0000", ""]])
    write_csv("Pricebook2.csv", ["$$Name$IsStandard", "CostBook.Name", "Description", "IsActive", "IsStandard", "Name", "ValidFrom", "ValidTo"], [[f"Standard Price Book;true", "Standard Cost Book", "", "true", "true", "Standard Price Book", "", ""]])
    write_csv(
        "PriceAdjustmentSchedule.csv",
        ["$$Name$CurrencyIsoCode", "AdjustmentMethod", "CurrencyIsoCode", "Description", "EffectiveFrom", "EffectiveTo", "IsActive", "Name", "Pricebook2.$$Name$IsStandard", "ScheduleType"],
        [
            [f"Standard Attribute Based Adjustment;USD", "Range", "USD", "", "2023-01-01T00:00:00.000+0000", "", "true", "Standard Attribute Based Adjustment", PB, "Attribute"],
            [f"Standard Bundle Based Adjustment;USD", "Range", "USD", "", "2023-01-01T00:00:00.000+0000", "", "true", "Standard Bundle Based Adjustment", PB, "Bundle"],
            [PAS_KEY, "Range", "USD", "", "2023-01-01T00:00:00.000+0000", "", "false", PAS, PB, "Volume"],
        ],
    )
    write_csv(
        "PricebookEntry.csv",
        ["$$Product2.StockKeepingUnit$ProductSellingModel.Name$CurrencyIsoCode", "CurrencyIsoCode", "IsActive", "IsDerived", "Name", "Pricebook2.$$Name$IsStandard", "Product2.StockKeepingUnit", "ProductSellingModel.$$Name$SellingModelType", "UnitPrice"],
        pbe_rows(),
    )
    write_csv(
        "PriceAdjustmentTier.csv",
        [
            "$$PriceAdjustmentSchedule.Name$Product2.StockKeepingUnit$ProductSellingModel.Name$ProductSellingModel.SellingModelType$TierType$TierValue$LowerBound$CurrencyIsoCode$EffectiveFrom",
            "AdjustmentType", "CurrencyIsoCode", "EffectiveFrom", "EffectiveTo", "LowerBound",
            "PriceAdjustmentSchedule.$$Name$CurrencyIsoCode", "PricingTerm", "PricingTermUnit",
            "Product2.StockKeepingUnit", "ProductSellingModel.$$Name$SellingModelType",
            "ScheduleType", "SellingModelType", "TierType", "TierValue", "UpperBound",
        ],
        pat_rows()[1:],
    )
    write_csv(
        "CostBookEntry.csv",
        ["$$CostBook.Name$Product.StockKeepingUnit$CurrencyIsoCode", "Cost", "CostBook.Name", "CurrencyIsoCode", "Description", "EffectiveFrom", "EffectiveTo", "Product.StockKeepingUnit"],
        cbe_rows(),
    )
    write_csv("Product2.csv", ["StockKeepingUnit"], [[s] for s in product2_skus()])
    psm_names = {("One-Time", "OneTime")}
    psm_names.add(("Evergreen - Quarterly", "Evergreen"))
    for _n, t in HOSTING_PSMS:
        psm_names.add((_n, t))
    write_csv(
        "ProductSellingModel.csv",
        ["$$Name$SellingModelType", "Name", "SellingModelType"],
        [[f"{n};{t}", n, t] for n, t in sorted(psm_names)],
    )
    write_csv("AttributeDefinition.csv", ["Code"], [])
    for empty in (
        "AttributeBasedAdjRule.csv",
        "AttributeAdjustmentCondition.csv",
        "AttributeBasedAdjustment.csv",
        "BundleBasedAdjustment.csv",
        "PricebookEntryDerivedPrice.csv",
    ):
        write_csv(empty, ["Name"], [])

    print(f"Generated kld-pricing: {len(pbe_rows())} PBE, {len(pat_rows()) - 1} PAT, {len(cbe_rows())} CBE")


if __name__ == "__main__":
    main()
