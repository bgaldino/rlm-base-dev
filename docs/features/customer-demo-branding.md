# Customer Demo Branding

## Overview

Customer demo branding automates the creation and deployment of a **customer-branded Lightning Experience Theme** as part of the customer demo onboarding flow. Given a company name, logo URL, and brand color, the tooling generates three Salesforce metadata artifacts (ContentAsset, BrandingSet, LightningExperienceTheme), deploys them to the target org, and instructs the user to activate the theme.

This feature was added because demo orgs ship with the QuantumBit theme, which is not appropriate when presenting to a specific customer. The branding step personalizes the entire Lightning Experience UI — header logo, brand color on buttons/links/borders, and the App Launcher tile — to match the customer's identity.

## Salesforce Platform Constraints

### Three Metadata Types

Salesforce Themes and Branding is built on three metadata types that all deploy via the Metadata API:

| Metadata Type | Purpose | File Pattern |
|---|---|---|
| `ContentAsset` | Binary image file (logo) stored as a versioned asset in the `sfdc_asset_company_assets` library. Accessible at `/file-asset/<AssetName>` after deploy. | `<Name>.asset` + `<Name>.asset-meta.xml` |
| `BrandingSet` | Branding properties XML: brand color, header background color, `BRAND_IMAGE` (points to ContentAsset `/file-asset/` URL), and placeholder slots for banner/group/profile images. API name **must** use the `LEXTHEMING` prefix (e.g., `LEXTHEMINGacme_corpSLDSv2`). | `LEXTHEMING<Name>.brandingSet-meta.xml` |
| `LightningExperienceTheme` | Theme definition referencing a BrandingSet by API name. Sets SLDS design system version (`SLDS_v2` for current orgs). | `<Name>.lightningExperienceTheme-meta.xml` |

All three deploy cleanly via `sf project deploy start`.

### Theme Activation Has No API

**Salesforce has confirmed there is no Metadata API, Tooling API, REST API, or UI API endpoint to programmatically activate a LightningExperienceTheme.** Activation is Web UI only.

This was verified through:
- Salesforce Product team confirmation ([StackExchange](https://salesforce.stackexchange.com/questions/407953))
- Salesforce IdeaExchange request ([idea](https://ideas.salesforce.com/s/idea/a0B8W00000QOAcAUAX))
- Research into internal Aura controllers — unlike the App Launcher (where `AppLauncherController/saveOrder` provides a backdoor), no equivalent Aura controller for theme activation has been found

**Workaround options considered:**

| Approach | Feasibility | Status |
|---|---|---|
| Metadata API deploy | Deploys theme but does not activate | Implemented |
| Tooling API update | No `IsActive` field exposed | Not possible |
| REST API / UI API | Read-only (`/ui-api/themes/active` returns current theme styling) | Not possible |
| Aura controller XHR | No known controller (unlike AppLauncher) | Not found |
| Robot Framework / Selenium | Navigate Setup UI, click Activate button via DOM | Feasible but brittle; deferred |

**Current approach:** Deploy + manual activation via a direct link to the Setup page.

### Verifying the Active Theme

After activation, the active theme can be verified via the UI API:

```bash
sf api request rest /services/data/v66.0/ui-api/themes/active --target-org <alias>
```

Returns `brandColor`, `brandImage` URLs, `headerColor`, `linkColor`, `pageColor`. Compare `brandColor` against the customer's hex value to confirm activation.

### Brand Image Requirements

Salesforce requires the brand image to be **600×120 pixels, PNG format**. This is confirmed by:
- The existing QuantumBit brand image (`RLM_quantumBit_rectangle.asset`): 600×120 PNG, 8-bit RGBA
- Salesforce documentation recommending 600×120 for Themes and Branding

The script accepts **any image size and format** (PNG, JPEG, GIF, WebP) and automatically:
1. Downloads the source image
2. Converts to RGBA
3. Scales to fit within 600×120 while preserving aspect ratio (Lanczos resampling)
4. Centers the scaled image on a solid-color canvas (letterboxing)
5. Exports as optimized PNG

| Input Shape | Behavior |
|---|---|
| Already 600×120 | Passes through (re-encoded as PNG) |
| Square (e.g., 512×512) | Scaled to 120px height, centered horizontally with background fill |
| Wide banner (e.g., 1200×200) | Scaled down to fit width, centered vertically |
| Small image (e.g., 50×10) | Scaled up to fill, centered |
| JPEG / GIF / WebP | Converted to PNG with alpha channel |

The `--bg-color` argument controls the letterbox background color (default: `#FFFFFF` white).

## Implementation

### Script

**`scripts/customer-demo/prepare_customer_branding.py`**

Generates all three metadata artifacts from CLI arguments.

**Arguments:**

| Argument | Required | Description |
|---|---|---|
| `--company-name` | Yes | Customer name (used for theme label and API name slugs) |
| `--logo-url` | Yes | Public URL to a logo image (any size/format) |
| `--brand-color` | Yes | Hex brand color, e.g., `#0176D3` |
| `--bg-color` | No | Hex letterbox background color (default: `#FFFFFF`) |
| `--output-dir` | No | Output directory (default: `unpackaged/post_customer_demo/branding/`) |

**Dependencies:** `Pillow`, `requests` (install via `pip install Pillow requests`)

**Generated naming convention:**

| Artifact | API Name Pattern | Example (company: "Acme Corp") |
|---|---|---|
| ContentAsset | `RLM_customer_<slug>_brand` | `RLM_customer_acme_corp_brand` |
| BrandingSet | `LEXTHEMING<slug>SLDSv2` | `LEXTHEMINGacme_corpSLDSv2` |
| LightningExperienceTheme | `<slug>SLDSv2` | `acme_corpSLDSv2` |
| Theme label (UI) | `<Company Name> SLDSv2` | `Acme Corp SLDSv2` |

**Output directory structure:**

```
unpackaged/post_customer_demo/branding/
├── contentassets/
│   ├── RLM_customer_acme_corp_brand.asset          # 600×120 PNG binary
│   └── RLM_customer_acme_corp_brand.asset-meta.xml
├── brandingSets/
│   └── LEXTHEMINGacme_corpSLDSv2.brandingSet-meta.xml
└── lightningExperienceThemes/
    └── acme_corpSLDSv2.lightningExperienceTheme-meta.xml
```

This directory is git-ignored (`unpackaged/post_customer_demo/branding/` in `.gitignore`) since it contains customer-specific generated output.

### CCI Tasks

**`prepare_customer_demo_branding`** — Runs the script. Pass options via `-o`:

```bash
cci task run prepare_customer_demo_branding \
  -o company_name "Acme Corp" \
  -o logo_url "https://example.com/acme-logo.png" \
  -o brand_color "#FF5733" \
  --org beta
```

**`deploy_customer_demo_branding`** — Deploys the output directory:

```bash
cci task run deploy_customer_demo_branding --org beta
```

### Feature Flag

```yaml
# cumulusci.yml → project → custom
customer_demo_branding: false
```

When `true`, `deploy_customer_demo_branding` runs as step 4 of `prepare_customer_demo_catalog` (after `deploy_customer_demo_staticresources`, before `insert_customer_demo_product_images_data`).

### Flow Integration

`prepare_customer_demo_catalog` step order (with branding enabled):

| Step | Task | Condition |
|---|---|---|
| 1 | `customer_demo_purge_records` | Always |
| 2 | `insert_customer_demo_pcm_data` | Always |
| 3 | `deploy_customer_demo_staticresources` | Always |
| **4** | **`deploy_customer_demo_branding`** | **`customer_demo_branding: true`** |
| 5 | `insert_customer_demo_product_images_data` | Always |
| 6 | `insert_customer_demo_billing_data` | Always |
| 7 | `customer_demo_recreate_pricebook_via_api` | Always |
| 8 | `customer_demo_verify_catalog` | Always |
| 9–14 | Usage + rates steps | `customer_demo_usage: true` |

The branding step is positioned after static resources (step 3) because the ContentAsset needs to deploy alongside its metadata. It runs before product images (step 5) because there is no dependency between them — the branding image is a theme-level asset, not a product `DisplayUrl`.

## Usage

### Full Workflow

```bash
# 1. Generate branding metadata (run once per customer)
cci task run prepare_customer_demo_branding \
  -o company_name "Acme Corp" \
  -o logo_url "https://example.com/acme-logo.png" \
  -o brand_color "#0176D3" \
  --org beta

# 2a. Deploy standalone
cci task run deploy_customer_demo_branding --org beta

# 2b. Or set flag and include in full flow
#     (set customer_demo_branding: true in cumulusci.yml first)
cci flow run prepare_customer_demo_catalog --org beta

# 3. MANUAL — activate the theme in the org:
#    Open: <org-url>/lightning/setup/ThemingAndBranding/home
#    Find "Acme Corp SLDSv2" → dropdown → Activate
```

### Custom Letterbox Background

For logos that don't look right on white, use `--bg-color`:

```bash
cci task run prepare_customer_demo_branding \
  -o company_name "DarkCo" \
  -o logo_url "https://example.com/darkco-white-on-transparent.png" \
  -o brand_color "#1A1A2E" \
  -o bg_color "#1A1A2E" \
  --org beta
```

### Re-running for a Different Customer

The output directory is overwritten on each run. To switch customers:

1. Run `prepare_customer_demo_branding` with new parameters
2. Deploy
3. Activate the new theme (the old customer theme remains in the org but inactive)

## Relationship to Existing QuantumBit Themes

The repo ships with two QuantumBit themes in `unpackaged/post_quantumbit/`:

| Theme | BrandingSet | Design System | Active by Default |
|---|---|---|---|
| QuantumBit | `LEXTHEMINGQuantumBit` | SLDS v1 | No |
| QuantumBit SLDSv2 | `LEXTHEMINGQuantumBitSLDSv2` | SLDS v2 | Yes (on QB orgs) |

The customer demo branding clones the **SLDSv2** pattern (same BrandingSet properties, same `designSystemVersion: SLDS_v2`). The QuantumBit themes are deployed by `deploy_quantumbit` (step 3 of `prepare_quantumbit`) and remain in the org. Activating the customer theme simply deactivates the QuantumBit theme.

## Future Considerations

### Automated Activation via Robot Framework

If the volume of customer onboardings makes manual activation painful, a Robot Framework suite could automate it by:
1. Navigating to `/lightning/setup/ThemingAndBranding/home`
2. Locating the row matching the customer theme label
3. Clicking the dropdown action → Activate

This follows the same pattern as `reorder_app_launcher` (Robot + CCI task wrapper). The trade-off is that DOM-based automation is brittle across Salesforce releases and requires maintenance. For now, the one-click Setup deep link is sufficient.

### Loading Page Override

The `shouldOverrideLoadingImage` property is set to `false` and `OVERRIDE_LOADING_PAGE` is `false`. A future enhancement could generate a custom loading spinner using the customer's brand image, but this requires additional ContentAsset work and is not currently needed for demos.
