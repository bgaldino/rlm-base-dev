#!/usr/bin/env python3
"""
One-shot converter: Industries In-App Framework legacy CCI dataset -> SFDMU v5 CSVs.

TEMPORARY tooling for the temporary `inapp` integration. Reads the legacy SQLite
dump (`rlm.dataset.sql`) from the Industries-In-App-Framework repo and emits the six
CSVs for datasets/sfdmu/inapp/, applying the composite-key conversion and the scrub
documented in this plan's README.

Transformations:
  1. lookups (legacy row-ids) -> parent `Name` via `<rel>__r.Name` columns
  2. RecordTypeId -> RecordType.DeveloperName via the legacy `*_rt_mapping` tables
  3. booleans True/False -> true/false
  4. SCRUB: drop 2 dead unreferenced blocks + 2 orphan junction rows
  5. REMAP: demo Account 'Mahesh' -> rlm-base-dev default account 'Infinitech'
     (QuantumBit primary customer); ACC_MAHESH_DYN_LINK token + DynamicLink Name/Identity
     renamed in lockstep
  6. SCRUB: neutralize 15 dead rich-text images hosted on the source learning org

Usage:
  python datasets/sfdmu/inapp/convert_from_legacy.py [path/to/rlm.dataset.sql]
"""
import csv
import re
import sys
from pathlib import Path

DEFAULT_SRC = "/Users/brian/Documents/GitHub/Enterprise/_industries/Industries-In-App-Framework/datasets/rlm/rlm.dataset.sql"
OUT_DIR = Path(__file__).parent.absolute()

# --- scrub / remap constants ---------------------------------------------------
DEAD_BLOCK_IDS = {"Block__c-50", "Block__c-73"}        # legacy source row-ids — unreferenced dup Names
ORPHAN_SB_IDS = {"SectionBlock__c-1", "SectionBlock__c-2"}  # legacy source row-ids — blank Section + Block
ACCT_FROM, ACCT_TO = "Mahesh", "Infinitech"            # demo account -> QB default account
TOKEN_FROM, TOKEN_TO = "ACC_MAHESH_DYN_LINK", "ACC_INFINITECH_DYN_LINK"
DEAD_IMG_HOST = "rlm258learnorg.file.force.com"
STATIC_RESOURCE = "InAppLearningImages"            # self-hosted replacement for the 15 images
SR_DIR = OUT_DIR.parents[2] / "unpackaged" / "post_inapp" / "staticresources" / STATIC_RESOURCE

# --- 258 -> 262 (Summer '26) content updates -----------------------------------
# Verified against docs/salesforce/262/ Help snapshot (838 articles) + dev-guide
# snapshot (1388). Every target below was confirmed to exist in the snapshot.
VERSION_TEXT_REMAPS = {
    "Revenue Cloud Winter'26 Release": "Revenue Cloud Summer '26 Release",
    # 262 capability rename — user-facing label only; app API name standard__PriceManagement unchanged.
    "Price Management": "Salesforce Pricing",
}

# 262 product rebrand: standalone "Revenue Cloud" -> "Agentforce Revenue Management", in body
# prose + section headers ONLY (scrub_text is never applied to Name/key fields, so composite
# keys like "Revenue Cloud Fundamentals" are auto-protected). KEEP, via negative lookahead:
#  - hyperlink labels ("...Revenue Cloud</strong>"): Trailhead module/trail/cert titles + headings
#  - editions: " Billing", " Advanced"
#  - cert/Trailhead proper names: " Fundamentals", " Certification", " Consultant"
#  - doc title: " Data Sheet"
# (Per user 2026-06-22, the release header "Revenue Cloud Summer '26 Release", "Revenue Cloud
#  Learning Journey", and the app "Revenue Cloud Learning Home" ARE now rebranded — so " Summer"
#  and " Learning" are no longer kept. The cert "...Revenue Cloud Consultant" stays via " Consultant".)
# This branch (in-app integration) only — base rlm-base-dev "Revenue Cloud" refs untouched.
ARM_NEW = "Agentforce Revenue Management"
_ARM_KEEP = (" Billing", " Advanced", " Fundamentals", " Certification", " Consultant", " Data Sheet")
# also keep hyperlink labels that end "Revenue Cloud:</strong>" (the ":" guard) for consistency
# with the other "...in Revenue Cloud</strong>" labels in the same lists.
_ARM_RE = re.compile(r"Revenue Cloud(?!</strong>)(?!:)" + "".join("(?!%s)" % re.escape(k) for k in _ARM_KEEP))
# Two Trailhead trails Salesforce rebranded Revenue Cloud -> Agentforce Revenue Management in
# their TITLES (verified live on trailhead.salesforce.com 2026-06-22). The ARM regex keeps
# hyperlink labels by default, so relabel these two explicitly to match the new trail titles.
# The ">...<" form on the second targets the link label only — never the Block Name/composite key.
# Each value is the EXACT current Trailhead title (verified live 2026-06-22). For the two pricing
# modules the live title kept "Price Management" (our label had "Salesforce Pricing" from the 262
# VERSION_TEXT_REMAP, which over-applied to these external titles) — matching the exact title fixes
# both. The Salesforce Revenue Cloud Consultant cert trail is NOT rebranded, so it's left as-is.
# "Advanced ..." precedes "Salesforce Pricing ..." so the longer string is replaced first.
TRAILHEAD_RELABEL = {
    "Boost Sales Efficiency with Revenue Cloud": "Boost Sales Efficiency with Agentforce Revenue Management",
    ">Revenue Cloud Fundamentals<": ">Agentforce Revenue Management Fundamentals<",
    "Configure Revenue Cloud": "Configure Agentforce Revenue Management",
    "Advanced Salesforce Pricing with Revenue Cloud": "Advanced Price Management with Agentforce Revenue Management",
    "Salesforce Pricing with Revenue Cloud": "Price Management with Agentforce Revenue Management",
    "Product Configuration with Revenue Cloud": "Product Configuration with Agentforce Revenue Management",
    "Product Catalog Management with Revenue Cloud": "Product Catalog Management with Agentforce Revenue Management",
    "Efficient Sales with Revenue Cloud": "Efficient Sales with Agentforce Revenue Management",
    "Asset Lifecycle Management with Revenue Cloud": "Asset Lifecycle Management with Agentforce Revenue Management",
    "Billing Basics in Revenue Cloud": "Billing Basics in Agentforce Revenue Management",
    # Not an ARM rebrand — the cert prep trail's title changed Exam -> Certification.
    "Consultant Exam": "Consultant Certification",
}
WRONG_VERTICAL_MARKERS = ("Communications_Summer_24", "energy_and_utilities_cloud_winter_25")
# DynamicLink record-Name fixes (these Names are the SFDMU composite key; 0 lockstep refs):
# a stale release label and a typo. Both link to the general rn_revenue (already release=262).
DL_NAME_REMAP = {
    "Winter '25 Release Notes": "Summer '26 Release Notes",
    "Relese Notes Summary": "Release Notes Summary",
}
RC_262_RELNOTES = "https://help.salesforce.com/s/articleView?id=release-notes.rn_revenue.htm&release=262&type=5"

# 48 Help article IDs renamed/reorganized in 262 -> verified 262 equivalents.
# Where 262 reorganized deep articles into a consolidated area, the link lands on the
# capability's 262 page (e.g. Contracts -> ind.qocal_*; precise article kept when the
# 262 match is unambiguous). All values confirmed present in docs/salesforce/262/help/.
HELP_ID_REMAP = {
    # DRO
    "ind.dro_design_time_administration.htm": "ind.dro_dynamic_revenue_orchestrator.htm",
    "ind.dro_get_started_with_dynamic_revenue_orchestrator.htm": "ind.dro_turn_on_dynamic_revenue_orchestrator.htm",
    "ind.dynamic_revenue_orchestration_essentials.htm": "ind.dro_dynamic_revenue_orchestrator.htm",
    "ind.dynamic_revenue_orchestrator_setup.htm": "ind.dro_basic_set_up.htm",
    "ind.enable_dynamic_revenue_orchestrator.htm": "ind.dro_turn_on_dynamic_revenue_orchestrator.htm",
    "ind.enable_future_dated_steps.htm": "ind.dro_turn_on_future_dated_steps.htm",
    "ind.enable_in_flight_amendments.htm": "ind.dro_enable_in_flight_amendments.htm",
    "ind.create_queues.htm": "ind.dro_create_queues.htm",
    "ind.order_submission_to_dynamic_order_orchestrator.htm": "ind.qocal_order_submission_for_fulfillment.htm",
    "ind.set_up_fallout_and_service_level_agreements_settings.htm": "ind.dro_turn_on_features_to_manage_fallout_and_service_level_agreements.htm",
    # Usage Management
    "ind.usage_management_essentials.htm": "ind.um_usage_management.htm",
    "ind.set_up_usage_management.htm": "ind.um_usage_management_setup.htm",
    "ind.um_usage_selling.htm": "ind.um_usage_management.htm",
    "ind.um_rate_management_setup.htm": "ind.um_usage_management_setup.htm",
    "ind.create_unit_of_measure.htm": "ind.um_create_unit_of_measure_class.htm",
    "ind.rev_cloud_setup_create_units_of_measure_class.htm": "ind.um_create_unit_of_measure_class.htm",
    "ind.rev_cloud_setup_create_products_for_usage.htm": "ind.um_usage_management.htm",
    "ind.rev_cloud_setup_create_usage_aggregation_policies.htm": "ind.um_usage_management.htm",
    "ind.rm_create_usage_resource.htm": "ind.um_create_usage_resource_policy.htm",
    "ind.usage_pricing_turn_on_rating_waterfall.htm": "ind.um_usage_management.htm",
    # Salesforce Pricing
    "ind.salesforce_pricing_setup.htm": "ind.pricing_salesforce_pricing.htm",
    "ind.pricing_salesforce_pricing_access_members.htm": "ind.pricing_salesforce_pricing.htm",
    "ind.set_up_product_discovery_pricing_procedures.htm": "ind.pricing_salesforce_pricing.htm",
    # Product Catalog
    "ind.set_up_product_catalog.htm": "ind.product_catalog_introduction.htm",
    "ind.update_your_product_discovery_settings.htm": "ind.qocal_set_up_product_discovery.htm",
    # Product Configurator
    "ind.product_configurator_learn_and_explore_product_configurator.htm": "ind.product_configurator_explore_the_product_configurator_flow.htm",
    "ind.product_configurator_work_with_product_configurator.htm": "ind.product_configurator_introduction.htm",
    "ind.set_up_configuration_rules.htm": "ind.product_configurator_introduction.htm",
    # Transaction Management + Salesforce Contracts (consolidated into ind.qocal_* in 262)
    "ind.transaction_management_essentials.htm": "ind.qocal_set_up_quote_and_order_capture.htm",
    "ind.configure_transaction_management_settings.htm": "ind.qocal_sales_transactions_rev_cloud.htm",
    "ind.object_setup.htm": "ind.qocal_sales_transactions_rev_cloud.htm",
    "ind.record_sharing.htm": "ind.qocal_sales_transactions_rev_cloud.htm",
    "ind.sf_contracts_salesforce_contracts_overview.htm": "ind.qocal_contract_management_essentials.htm",
    "ind.sf_contracts_turn_on_salesforce_contracts.htm": "ind.qocal_contract_management_essentials.htm",
    "ind.sf_contracts_add_salesforce_contracts_licenses_and_install_omnistudio_package.htm": "ind.qocal_contract_management_essentials.htm",
    "ind.sf_contracts_map_fields_for_opportunity_order_and_quote.htm": "ind.qocal_contract_management_essentials.htm",
    "ind.sf_contracts_invocable_actions_for_salesforce_contracts.htm": "ind.qocal_contract_management_essentials.htm",
    "ind.sf_contracts_contracts_ai_overview.htm": "ind.qocal_contract_management_essentials.htm",
    "ind.sf_contracts_post-install_steps_for_salesforce_contracts_winter_23.htm": "ind.qocal_contract_management_essentials.htm",
    # Billing
    "ind.guided_setup_for_billing.htm": "ind.billing_guided_setup.htm",
    "ind.setup_guided.htm": "ind.billing_guided_setup.htm",
    "ind.invoice_management_essentials.htm": "ind.billing.htm",
    "ind.newpay_terms_for_invoices.htm": "ind.billing.htm",
    "ind.set_up_billing_defaults.htm": "ind.billing.htm",
    "ind.billing_setup_impl.htm": "ind.billing_guided_setup.htm",
    "ind.billing_setup_clone_order_to_schedule_flow.htm": "ind.billing.htm",
    "ind.billing_setup_salesforce_payments.htm": "ind.billing_setup_salesforce_payments_features.htm",
    "ind.collections_enable_timeline.htm": "ind.billing.htm",
    # NOTE: ind.setup_revenue_cloud.htm ("Get Ready for Your Revenue Management Implementation")
    # is the correct Home "Read Implementation Guide" link — renders live (it's just absent from
    # the partial 262 snapshot), so it is intentionally NOT remapped.
}

# 2 stale atlas Dev Guide pages -> 262 equivalents (assets are QOCAL standard objects in 262).
DEVGUIDE_ID_REMAP = {
    "asset_lifecycle_overview": "quote_and_order_capture_standard_objects",
    "transaction_management_overview": "quote_and_order_capture_standard_objects",
}
_DG = "revenue_lifecycle_management_dev_guide/"

# release-notes area pages that 404 at release=262 -> browser-verified valid 262 equivalents.
# (rn_salesforce_qoc and rn_rate_management have no 262 page; QOC -> Transaction Management,
# Rate Management folded into Usage Management.)
RN_ID_REMAP = {
    "release-notes.rn_salesforce_qoc.htm": "release-notes.rn_transaction_management.htm",
    "release-notes.rn_rate_management.htm": "release-notes.rn_um_usage_management.htm",
}
# personal demo org whose absolute Lightning URLs don't resolve anywhere else -> relativize
# (strip the host so `/lightning/...` resolves in whatever org the framework is deployed to).
DEMO_ORG_HOST = "dwd000004pe09mag.lightning.force.com"

# Billing "Dashboard Setup" link: was a placeholder Drive doc + "To Be Updated" -> the 262
# Billing Operations Console Help article, with a grounded description (per user, 2026-06-21).
DASHBOARD_SETUP_FIND = ('<a href="https://drive.google.com/file/d/10sW4qQu7eRak_GQN7lqhLO79GSwX437G/view" '
                        'target="_blank"><strong>Dashboard Setup:</strong></a> To Be Updated.')
DASHBOARD_SETUP_REPL = ('<a href="https://help.salesforce.com/s/articleView?id=ind.billing_operations_console.htm&amp;type=5" '
                        'target="_blank"><strong>Dashboard Setup:</strong></a> <span style="color: rgb(0, 0, 0);">'
                        'Monitor invoices, credit memos, and invoice schedules from the Billing Operations Console. '
                        'View key financial metrics in summary cards and manage invoice batch runs with timely '
                        'insights into revenue transaction log errors and failed invoices.</span>')

# longest-first so no key is corrupted by a shorter substring match
_HELP_KEYS = sorted(HELP_ID_REMAP, key=len, reverse=True)


def parse_table(sql, obj):
    """Return list of value-lists for INSERT INTO "<obj>" rows."""
    out = []
    for m in re.finditer(r'INSERT INTO "%s" VALUES\((.*)\);' % re.escape(obj), sql):
        vals = re.findall(r"'(?:[^']|'')*'", m.group(1))
        out.append([v[1:-1].replace("''", "'") for v in vals])
    return out


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _img_alt(block_name):
    """A clean, human-readable alt from the Block topic — strips the administrative
    'Learning [Hub] Block N' suffix (e.g. 'Billing Learning Hub Block 1' -> 'Billing')."""
    return re.sub(r"\s+Learning(\s+Hub)?\s+Block\s+\d+$", "", block_name).strip() or block_name


def rewrite_block_images(desc, block_name):
    """Rebuild a Block's cross-org <img> (dead learning-org host): point src at the
    self-hosted `InAppLearningImages` static resource (matched by Block-Name slug; the
    on-disk file supplies the extension, all normalized to .png) AND replace the stale
    alt (originally the upload filename, e.g. 'Screenshot 2025-10-06….png') with a
    topic-derived alt. Returns desc unchanged when no staged image matches (scrub_text
    then strips the dead tag), so the converter still runs if images aren't staged."""
    if not desc or DEAD_IMG_HOST not in desc:
        return desc
    fname = next((p.name for p in sorted(SR_DIR.glob(_slug(block_name) + ".*"))), None)
    if not fname:
        return desc
    new_tag = '<img src="/resource/%s/%s" alt="%s">' % (STATIC_RESOURCE, fname, _img_alt(block_name))
    return re.sub(r'<img\b[^>]*%s[^>]*>(\s*</img>)?' % re.escape(DEAD_IMG_HOST),
                  lambda _m: new_tag, desc)


# --- Home announcement: 258 -> 262 (Summer '26) marquee features ----------------
# The Home "Launching Fast Revenue Cloud Setup" block listed four 258 features. Replace
# them with four Summer '26 (262) headline features, each verified in
# docs/salesforce/262/feature-index.md (release-wide RCA highlights + the per-area row
# cited): Product Discovery w/ Constraint Rules (GA, PCM §), Accelerated Deal Approvals
# in Slack (New, Transaction Mgmt §), Guided Ramp Creation w/ Trial Segments (GA,
# Transaction Mgmt §), AI-Supported Bulk Contract Extraction (New, Contracts §).
HOME_RELNOTES_BLOCK = "Home Left Top Block"
_LI = '<li><strong style="background-color: transparent; font-size: 14px;">%s</strong>%s</li>'
_QUAL = '<span style="background-color: transparent; font-size: 14px;">%s</span>'
HOME_262_BULLETS = "<ul>" + "".join([
    _LI % ("Product Discovery with Constraint Rules", _QUAL % " (Generally Available)"),
    _LI % ("Accelerated Deal Approvals in Slack", _QUAL % "."),
    _LI % ("Guided Ramp Creation with Trial Segments", _QUAL % "."),
    _LI % ("AI-Supported Bulk Contract Extraction", _QUAL % "."),
]) + "</ul>"


def rewrite_home_relnotes(desc, block_name):
    """On the Home announcement block, swap the 258 feature bullets for the 262
    marquee list and fix the release-notes link label (the href is already
    release=262). No-op on every other block."""
    if block_name != HOME_RELNOTES_BLOCK or not desc:
        return desc
    desc = re.sub(r"<ul>.*?</ul>", lambda _m: HOME_262_BULLETS, desc, count=1, flags=re.S)
    # The old green banner was a Salesforce Go setup CTA — meaningless on an already-configured
    # learning org. Replace it with a neutral "what's new" header (no setup/Go framing).
    desc = desc.replace("Launching Fast Revenue Cloud Setup with Salesforce Go!",
                        "What's New in Summer '26")
    return desc.replace("Explore Winter&#39;26 Release Notes",
                        "Explore Summer &#39;26 Release Notes")


# --- 8 area "what's new" blocks: 258 (Winter '26) bullets -> 262 (Summer '26) ----------
# Each block heads its area's release-notes list. Swap the heading Winter'26 -> Summer '26
# and replace the 258 bullets with that area's 262 features, each verified in
# docs/salesforce/262/feature-index.md (tier shown for honesty — Summer '26 is still
# preview). The area-level "Read More" link (outside the <ul>, already release=262) is
# preserved; the 258 per-feature deep links are dropped (their IDs aren't verified at 262).
SIBLING_262 = {
    "Product Catalog Management Learning Block 1": [
        ("Product Discovery with Constraint Rules", "Generally Available",
         "Constraint Rules now enforce product compatibility and surface recommendations in real time during product discovery, with auto-save so products are added to a transaction without leaving discovery and a preview of existing quote lines."),
        ("Product Variants", "Generally Available",
         "Define and manage base products with their specific variants such as color, size, and material, for a consistent variant experience across B2B Commerce and Revenue Cloud quote-to-cash."),
    ],
    "Price Management Learning Block 1": [
        ("CSV Based Decision Tables", "Generally Available",
         "Source decision tables from CSV uploads that support more than 30 inputs and 5 outputs — create a decision table with Type CSV, upload the file, activate it, and map it to a pricing element in your pricing procedure."),
        ("Pricing General Enhancements", "Generally Available",
         "The Revenue Operations Console adds a date and time hover and a currency column, and the Map Line Items element now supports up to 100 default tags and runs within Parallel Execution."),
    ],
    "Product Configurator Learning Block 2": [
        ("Group and Ramp Segment Scope Rules", "Generally Available",
         "The Advanced Configurator now applies transaction scope rules to Quote Groups and Ramp Segments, resolving cases where scope rules previously failed when groups were present on a quote, especially group ramps."),
        ("Product Loader and Default Component", "Generally Available",
         "Automatically include default components from the product catalog when importing bundles, and use the new productField annotation to load standard or custom Product fields directly into CML attributes."),
    ],
    "Transaction Management Learning Block 2": [
        ("Guided Ramp Schedule Generation with Trial and Prorated Segments", "Generally Available",
         "Replace slow manual cloning for multi-year ramp deals with guided generation that supports free or trial segments and prorated stub periods; reps start from the Create Ramp Schedule action."),
        ("Early Renewal for Ramped Asset", "Generally Available",
         "Renew a ramped asset ahead of schedule by setting a future renewal start date — the renewal quote replaces the remainder of the existing ramp schedule with new ramp segments."),
    ],
    "DRO Learning Block 2": [
        ("DRO Templates", "Beta",
         "Stand up orchestration faster with pre-built Dynamic Revenue Orchestrator templates."),
        ("DRO and OMS Interop", "Beta",
         "Keep Dynamic Revenue Orchestrator and your Order Management System in real-time sync, closing the gap where teams previously managed two non-synced platforms."),
    ],
    "Salesforce Contracts Learning Hub Block 2": [
        ("AI-Supported Bulk Contract Extraction", "New",
         "Extract metadata at scale from existing contract PDFs to unlock historical data trapped in legacy documents, protecting margins and increasing renewal revenue."),
        ("Advanced Approvals for Contracts", "New",
         "Run multi-stakeholder, serial-approval workflows on Contracts using the Approvals framework."),
    ],
    "Usage Management Learning Block 2": [
        ("Usage Product Guided Setup", "Enhanced",
         "A streamlined guided setup flow for configuring usage products."),
        ("Consumption Agent", "Enhanced",
         "Agentforce-powered assistance for usage selling and consumption insights (requires Revenue Cloud Billing and Agentforce)."),
    ],
    "Billing Learning Hub Block 3": [
        ("Statement of Account", "New",
         "Generate a consolidated view that summarizes all billing transactions — invoices, payments, credits, debits, and refunds — for an account over a period, on demand from the Account page (requires Document Generation enabled in Billing Settings)."),
        ("Advanced Amendments", "Enhanced",
         "Generate accurate billing schedules for amendments tied to milestone billing, asset transfers, and coterminous contracts."),
    ],
}
_SIB_LI = '<li><strong style="color: rgb(2, 80, 217);">%s (%s):</strong> %s</li>'
# matches the 18px heading + "Winter'26" in any apostrophe encoding (&#39; / curly / straight)
_WINTER_HEAD = '(<strong style="font-size: 18px;">)\\s*Winter\\s*(?:&#39;|’|\')?\\s*26'


def rewrite_sibling_relnotes(desc, block_name):
    """For the 8 area "what's new" blocks, swap the heading Winter'26 -> Summer '26 and
    replace the 258 feature bullets with the area's verified 262 features. Preserves the
    area-level "Read More" link; no-op on other blocks."""
    spec = SIBLING_262.get(block_name)
    if not spec or not desc:
        return desc
    desc = re.sub(_WINTER_HEAD, lambda m: m.group(1) + "Summer &#39;26", desc, count=1)
    bullets = "<ul>" + "".join(_SIB_LI % (n, t, d) for (n, t, d) in spec) + "</ul>"
    return re.sub(r"<ul>.*?</ul>", lambda _m: bullets, desc, count=1, flags=re.S)


def scrub_text(s):
    """Apply all text/URL transforms for a non-key field: dead-image strip, token
    rename, 262 label renames, Help/Dev-Guide article-ID remap, and release pin bump."""
    if not s:
        return s
    # Fallback strip for any cross-org <img ... rlm258learnorg ...> tag NOT already
    # rewritten to the static resource by rewrite_block_images() (DONE: the 15 binaries
    # are self-hosted under /resource/InAppLearningImages/ — see README). After a rewrite
    # the src is `/resource/...` so it no longer matches this strip; this only fires if an
    # image is unstaged.
    s = re.sub(r'<img\b[^>]*%s[^>]*>(\s*</img>)?' % re.escape(DEAD_IMG_HOST), "", s)
    s = s.replace(DASHBOARD_SETUP_FIND, DASHBOARD_SETUP_REPL)   # Billing dashboard placeholder
    s = s.replace(TOKEN_FROM, TOKEN_TO)
    for old in _HELP_KEYS:                              # renamed Help article IDs
        s = s.replace(old, HELP_ID_REMAP[old])
    for old, new in DEVGUIDE_ID_REMAP.items():         # 2 renamed Dev Guide pages
        s = s.replace(_DG + old + ".htm", _DG + new + ".htm")
    for old, new in RN_ID_REMAP.items():               # release-notes pages dead at 262
        s = s.replace(old, new)
    s = s.replace("https://" + DEMO_ORG_HOST, "")      # relativize personal demo-org URLs
    s = s.replace("/lightning/lightning/", "/lightning/")  # fix malformed doubled nav path
    s = s.replace("release=258", "release=262")        # pin bump
    for old, new in VERSION_TEXT_REMAPS.items():       # label renames (after ID remap)
        s = s.replace(old, new)
    # 262 rebrand (after VERSION_TEXT_REMAPS so " Summer" guard protects the release header)
    for old, new in TRAILHEAD_RELABEL.items():         # rebranded Trailhead trail labels
        s = s.replace(old, new)
    s = s.replace("with Salesforce Revenue Cloud.", "with " + ARM_NEW + ".")  # avoid "Salesforce Agentforce"
    s = _ARM_RE.sub(ARM_NEW, s)
    return s


def write_csv(name, header, rows):
    path = OUT_DIR / f"{name}.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {name}.csv  ({len(rows)} rows)")
    return len(rows)


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(DEFAULT_SRC)
    sql = src.read_text()

    # NOTE: parse_table reads the LEGACY SQL dump, which uses the ORIGINAL (unprefixed) table
    # names. Only the OUTPUT (write_csv object names + column headers + __r traversals) carries
    # the RLM_Learning_ prefix. Do not prefix these source-side table names.
    icon = parse_table(sql, "Icon__c")            # id,Name,Size,Type
    page = parse_table(sql, "Page__c")            # id,Active,Name,Type
    section = parse_table(sql, "Section__c")      # id,Active,Header,Name,SubHeader,RT,Video,Icon,Page
    dlink = parse_table(sql, "DynamicLink__c")    # id,App,Filter,Identity,Link,Name,Object,PageName,RT,Rel,RelUrl,Setup,Site,Text,Where,Page,Section
    block = parse_table(sql, "Block__c")          # id,ActionText,Active,Desc,Header,Name,Note,SubHeader,Action,Icon
    sblock = parse_table(sql, "SectionBlock__c")  # id,Order,Block,Section

    sec_rt = {r[0]: r[1] for r in parse_table(sql, "Section__c_rt_mapping")}
    dl_rt = {r[0]: r[1] for r in parse_table(sql, "DynamicLink__c_rt_mapping")}

    # --- 262 capability rename: Page "Price Management" -> "Salesforce Pricing" --
    # Mutating the source page row renames the Page record AND every RLM_Learning_Page__r.Name
    # reference (all resolved through page_n below), keeping the data consistent.
    pricing_renamed = 0
    for r in page:
        if r[2] == "Price Management":
            r[2] = "Salesforce Pricing"
            pricing_renamed += 1

    # --- REMAP demo account + fix wrong-vertical release-notes links ----------
    remapped = relnotes_fixed = dl_renamed = 0
    for r in dlink:
        if r[14] == "Name = '%s'" % ACCT_FROM:
            r[14] = "Name = '%s'" % ACCT_TO
            r[5] = r[5].replace(ACCT_FROM, ACCT_TO)      # Name: "Account Name Mahesh" -> Infinitech
            r[3] = r[3].replace(TOKEN_FROM, TOKEN_TO)    # RLM_Learning_Identity__c token
            remapped += 1
        if any(mk in r[4] for mk in WRONG_VERTICAL_MARKERS):   # RLM_Learning_Link__c (Comms/Energy -> RC 262)
            r[4] = RC_262_RELNOTES
            relnotes_fixed += 1
        if r[5] in DL_NAME_REMAP:                        # stale/typo DynamicLink Names
            r[5] = DL_NAME_REMAP[r[5]]
            dl_renamed += 1

    # --- id -> Name maps (post-remap) for lookup resolution -------------------
    icon_n = {r[0]: r[1] for r in icon}
    page_n = {r[0]: r[2] for r in page}
    sec_n = {r[0]: r[3] for r in section}
    dl_n = {r[0]: r[5] for r in dlink}

    b = lambda v: {"True": "true", "False": "false"}.get(v, v)
    # RecordType is matched on a 2-part DeveloperName;SobjectType externalId (set on the
    # RecordType object in export.json) — dropping NamespacePrefix avoids SFDMU's
    # null-vs-empty composite mismatch on unmanaged custom-object record types.
    rtc = lambda dev, sobj: f"{dev};{sobj}" if dev else ""

    # --- RLM_Learning_Icon__c ---------------------------------------------------------------
    write_csv("RLM_Learning_Icon__c", ["Name", "RLM_Learning_Size__c", "RLM_Learning_Type__c"],
              [[r[1], r[2], r[3]] for r in icon])

    # --- RLM_Learning_Page__c ---------------------------------------------------------------
    write_csv("RLM_Learning_Page__c", ["RLM_Learning_Active__c", "Name", "RLM_Learning_Type__c"],
              [[b(r[1]), r[2], r[3]] for r in page])

    # --- RLM_Learning_Section__c ------------------------------------------------------------
    write_csv("RLM_Learning_Section__c",
              ["RLM_Learning_Active__c", "RLM_Learning_Header__c", "Name", "RLM_Learning_Sub_Header__c", "RLM_Learning_Video_Link__c",
               "RecordType.$$DeveloperName$SobjectType", "RLM_Learning_Icon__r.Name", "RLM_Learning_Page__r.Name"],
              [[b(r[1]), scrub_text(r[2]), r[3], scrub_text(r[4]), r[6],
                rtc(sec_rt.get(r[5], ""), "RLM_Learning_Section__c"), icon_n.get(r[7], ""), page_n.get(r[8], "")]
               for r in section])

    # --- RLM_Learning_DynamicLink__c --------------------------------------------------------
    write_csv("RLM_Learning_DynamicLink__c",
              ["RLM_Learning_App_API_Name__c", "RLM_Learning_Filter_Name__c", "RLM_Learning_Identity__c", "RLM_Learning_Link__c", "Name",
               "RLM_Learning_Object__c", "RLM_Learning_Page_Name__c", "RLM_Learning_Relationship_API_Name__c", "RLM_Learning_Relative_Url__c",
               "RLM_Learning_Setup_Page__c", "RLM_Learning_Site_Name__c", "RLM_Learning_Text_Value__c", "RLM_Learning_Where_Condition__c",
               "RecordType.$$DeveloperName$SobjectType", "RLM_Learning_Page__r.Name", "RLM_Learning_Section__r.Name"],
              [[r[1], r[2], r[3], scrub_text(r[4]), r[5], r[6], r[7], r[9], r[10], r[11], r[12],
                scrub_text(r[13]), r[14], rtc(dl_rt.get(r[8], ""), "RLM_Learning_DynamicLink__c"), page_n.get(r[15], ""), sec_n.get(r[16], "")]
               for r in dlink])

    # --- RLM_Learning_Block__c (drop dead rows; rewrite cross-org images + Home 262 announcement) -
    img_rewrites = home_rewrites = sib_rewrites = 0
    block_rows = []
    for r in block:
        if r[0] in DEAD_BLOCK_IDS:
            continue
        desc = rewrite_block_images(r[3], r[5])
        if desc != r[3]:
            img_rewrites += 1
        home_desc = rewrite_home_relnotes(desc, r[5])
        if home_desc != desc:
            home_rewrites += 1
        sib_desc = rewrite_sibling_relnotes(home_desc, r[5])
        if sib_desc != home_desc:
            sib_rewrites += 1
        desc = sib_desc
        block_rows.append([scrub_text(r[1]), b(r[2]), scrub_text(desc), scrub_text(r[4]), r[5],
                           scrub_text(r[6]), scrub_text(r[7]), dl_n.get(r[8], ""), icon_n.get(r[9], "")])
    write_csv("RLM_Learning_Block__c",
              ["RLM_Learning_ActionText__c", "RLM_Learning_Active__c", "RLM_Learning_Description__c", "RLM_Learning_Header__c", "Name",
               "RLM_Learning_Note__c", "RLM_Learning_Sub_Header__c", "RLM_Learning_Action__r.Name", "RLM_Learning_Icon__r.Name"],
              block_rows)

    # --- RLM_Learning_SectionBlock__c (drop orphans) ---------------------------------------
    # Composite externalId requires an SFDMU v5 `$$` key column: header is
    # `$$` + components joined by `$`; value is the component values joined by `;`.
    block_n = {r[0]: r[5] for r in block}
    sb_rows = []
    for r in sblock:
        if r[0] in ORPHAN_SB_IDS or not r[2] or not r[3]:
            continue
        s_name, b_name, order = sec_n.get(r[3], ""), block_n.get(r[2], ""), r[1]
        sb_rows.append([";".join([s_name, b_name, order]), s_name, b_name, order])
    write_csv("RLM_Learning_SectionBlock__c",
              ["$$RLM_Learning_Section__r.Name$RLM_Learning_Block__r.Name$RLM_Learning_Order_Sequence__c",
               "RLM_Learning_Section__r.Name", "RLM_Learning_Block__r.Name", "RLM_Learning_Order_Sequence__c"],
              sb_rows)

    print(f"\nScrub: dropped {len(DEAD_BLOCK_IDS)} dead blocks, {len(ORPHAN_SB_IDS)} orphan junctions")
    print(f"Remap: {remapped} Account link Mahesh -> {ACCT_TO}; {dl_renamed} DynamicLink Name(s) fixed")
    print(f"262:   {relnotes_fixed} wrong-vertical link(s) -> RC 262; version Winter'26 -> Summer '26;")
    print(f"       {len(HELP_ID_REMAP)} renamed Help IDs + {len(DEVGUIDE_ID_REMAP)} Dev-Guide IDs remapped, "
          f"release pin 258 -> 262;")
    print(f"       {pricing_renamed} Page 'Price Management' -> 'Salesforce Pricing' (label)")
    print(f"Images: {img_rewrites} block <img> rewritten -> /resource/{STATIC_RESOURCE}/ (self-hosted)")
    print(f"Home:   {home_rewrites} announcement block -> 262 marquee features + 'Summer 26' link label")
    print(f"Areas:  {sib_rewrites} area block(s) -> 262 features + 'Summer 26' heading (expect 8)")


if __name__ == "__main__":
    main()
