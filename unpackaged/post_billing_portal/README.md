# Self-Service Billing Portal Metadata

This directory contains the Experience Cloud site metadata for the RLM Self-Service Billing Portal: an Aura (Picasso) `ExperienceBundle`, its `Network`, `NavigationMenu`, and `ExperienceBundle` settings.

## Overview

The Self-Service Billing Portal lets customers view invoices, make payments, and manage cases without an internal login. It uses the same Aura `ChatterNetworkPicasso` Experience Cloud architecture as the Partner Central site (`unpackaged/post_prm/`) — not the newer LWR `DigitalExperienceBundle` used by Payments (`unpackaged/post_payments/`).

This bundle is the unmodified, out-of-the-box "Self-Service Billing Portal" Experience Cloud template as shipped in Salesforce Release 262 (Summer '26, API v67.0), with only the portability fixes below applied. No page, theme, or content customization has been layered on top yet — this is the baseline to build on.

## Contents

### Experience Cloud Site

**Network:**

- `Billing Portal.network-meta.xml` - Self-Service Billing Portal community (status: UnderConstruction, URL prefix: `billing`)

**Experience (Billing_Portal1):**

- Built from the standard "Self-Service Billing Portal" template: home, invoice list/detail, payment/checkout, cases, help center, wallet, register/login routes and views.
- Theme: `selfServiceBillingPortal`
- Branding set: `selfServiceBillingPortal`

**Navigation:**

- `SFDC_Default_Navigation_Billing_Portal.navigationMenu-meta.xml` - Default navigation (Cases, Help Center)

### Other Assets

- ExperienceBundle settings (`enableExperienceBundleMetadata`, mirrors the org-wide setting already deployed in `unpackaged/pre/2_settings/`)

## Naming

`create_billing_portal` creates the community with `name: "Billing Portal"` (a space, not `BillingPortal`). Salesforce derives the rest from that name:

| Metadata | Name |
|----------|------|
| Network | `Billing Portal` (spaces preserved — the file name **is** the metadata full name) |
| Site (CustomSite, not committed) | `Billing_Portal` |
| ExperienceBundle | `Billing_Portal1` |
| NavigationMenu | `SFDC_Default_Navigation_Billing_Portal` |

All three committed files must agree with the Network Name: the `networks/*.network-meta.xml` file name, the `<site>`/`<picassoSite>` values inside it, and every `navigationMenu-meta.xml`'s `<container>` element. If `create_billing_portal`'s `name` option ever changes, re-derive all of the above the same way (create a throwaway community with the new name, then query the resulting `Network.Name`, `Site.Name`, and `ExperienceBundle` fullName) — don't guess the naming transform.

## Deployment

Use the `prepare_billing_portal` flow so community creation, the required Network email patch,
metadata deployment, placeholder restoration, and publication run in the correct order. The flow
is also invoked as the last step of `prepare_billing`. Every step requires both `billing` and
`billing_portal`:

```bash
cci flow run prepare_billing_portal --org <org-alias>
```

The `prepare_billing_portal` flow runs the following numbered steps:

1. Create Self-Service Billing Portal community (`create_billing_portal`)
1. Patch network metadata (email placeholder) — only when `billing_portal_deploy` is also true
1. Deploy `post_billing_portal` metadata — only when `billing_portal_deploy` is also true
1. Revert network metadata — only when `billing_portal_deploy` is also true
1. Publish Self-Service Billing Portal community

Steps 2-4 are skipped when `billing_portal_deploy` is false: the community is created from the standard template but no custom site content is deployed over it.

## PII Handling

`Network.EmailSenderAddress` is immutable after community creation and required by the metadata deploy. The committed `Billing Portal.network-meta.xml` stores the non-PII placeholder `billing-portal-sender@example.com`. `patch_network_email_for_deploy` reads the target org's actual current value and substitutes it into the file for deployment; after a successful deploy, `revert_network_email_after_deploy` restores the placeholder. This is the same pattern `post_prm` uses for `rlm.network-meta.xml`, reusing the same parameterized task classes (`tasks/rlm_community.py`) via `options:` overrides — no new Python code.

If the deployment step fails, CumulusCI stops the flow before the revert step. Restore the placeholder
before committing or rerunning the flow:

```bash
cci task run revert_network_email_after_deploy \
  -o network_meta_xml_path "unpackaged/post_billing_portal/force-app/main/default/networks/Billing Portal.network-meta.xml" \
  -o placeholder_email billing-portal-sender@example.com
```

This local recovery task does not take `--org`. The shared failure-path limitation and proposed
in-memory deployment-transform replacement are tracked in
[`#354`](https://github.com/bgaldino/rlm-base-dev/issues/354).

The retrieved metadata also carried a `newSenderAddress` element (a pending-sender-change artifact set by the org, not required by the deploy) and was dropped entirely rather than placeholdered, matching `post_prm`'s `rlm.network-meta.xml`, which never carries this field either.

## Portability Notes

This metadata is retrieved via `sf project retrieve start --metadata "ExperienceBundle:..." --metadata "Network:..." --metadata "NavigationMenu:..."`, which pulls in whatever the source org's template instance contains. Two fixes are applied to keep that extraction portable and understandable:

- **Embedded Messaging removed.** The "Self-Service Billing Portal" template drops an unconfigured `experience_messaging:embeddedMessaging` component into the Home and Inner theme regions by default. Each instance carries a `scrtUrl` hardcoded to the org's auto-generated SCRT (Salesforce Content Relay Target) domain, which is meaningless on any other org. The component isn't wired to a real Messaging Deployment (no channel reference in its attributes), so removing it costs no functionality. Both occurrences are stripped from `themes/selfServiceBillingPortal.json`, leaving the sibling `forceCommunity:htmlBlock` component in each region untouched. Adding real chat support later requires provisioning an actual Embedded Service Messaging Deployment and re-patching `scrtUrl` at deploy time — it can't be a static placeholder, since it's genuinely per-org.
- **Payment redirect view label repaired.** The retrieved payment-redirect view used a generated
  `__MISSING LABEL__ ... not found` value as both its label and filename. Its route already supplies
  the canonical `Payment Redirect Return` label and references the view by UUID, so the view now uses
  that label and the conventional `paymentRedirectReturn.json` filename without changing its ID,
  component, or route type.

No other portability fixes were needed: `appPageId` references are internally consistent, `enableImageOptimizationCDN` was already `false`, and no `trustedSites` entries or other org-specific domains were found elsewhere in the bundle.

## Feature Flags

Enable the Billing Portal in `cumulusci.yml`:

```yaml
project_config:
  project__custom__:
    billing: true                # Required parent feature
    billing_portal: true         # Create the community
    billing_portal_deploy: true  # Also deploy this bundle's site content and publish with it applied
```

`prepare_billing_portal` is invoked automatically as step 14 of `prepare_billing` (see `README.md`'s Sub-Flows table), so it runs as part of `prepare_rlm_org` whenever `billing` and `billing_portal` are true — no separate wiring is needed. Set `billing_portal_deploy` to false to keep the generated standard-template content instead of deploying this bundle.

## Testing

```bash
# Run the full flow (create, patch, deploy, revert, publish)
cci flow run prepare_billing_portal --org dev

# Verify the Network exists with the expected name
sf data query --query "SELECT Name, Status, UrlPathPrefix FROM Network WHERE UrlPathPrefix='billing'" --target-org rlm-base__dev

# Confirm the repo file was reverted to the placeholder (should show no diff)
git diff --stat unpackaged/post_billing_portal/force-app/main/default/networks/
```

## References

- Structural precedent: `unpackaged/post_prm/README.md` (same Aura ExperienceBundle architecture, same email-placeholder pattern)

## Related Documentation

- [Repository Integration Skill](../../.cursor/skills/repo-integration/SKILL.md) - Feature integration patterns
- [`docs/guides/post-billing-portal.md`](../../docs/guides/post-billing-portal.md) - Short pointer to this README
