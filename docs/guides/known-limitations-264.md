# Known Limitations for Release 264

[Home](../../README.md) · [Documentation](../index.md)

What a default Foundations build does **not** set up for Release 264 (Winter '27). Each item below
is a Revenue Cloud feature the demo script or Help describes that this repository does not provision.
Do not assume these work on a freshly built org. Each limitation cites the repository file or
the 264 Help snapshot it is grounded in.

| Area | Not provisioned by the build | Grounding |
|---|---|---|
| [Approvals](#approvals-delegation-slack-and-the-approval-agent) | Delegation, Slack notifications, Approval Agent | 264 Help snapshot |
| [Tax](#revenue-standard-tax-engine) | Revenue Standard tax engine extension | `unpackaged/pre/4_tax/`, 264 Help snapshot |
| [Payments](#payment-gateways) | Payment gateway, merchant account, payment method | `datasets/sfdmu/qb/en-US/qb-billing/README.md`, demo script |
| [Billing Forecast and Lockbox](#billing-forecast-console-and-lockbox) | Forecast Console, Lockbox reconciliation (Data 360) | 264 Help and release-note snapshots |

## Approvals: delegation, Slack, and the Approval Agent

The build ships the quote approval flows (see the `advanced-approvals` skill) but does not turn on
the 264 add-ons:

- **Delegation.** Help describes *Use Advanced Approval Delegation* in Approval Settings. Turning it
  on stops delegations configured on user records from applying; reviewers must create Approval
  Delegation records instead. The build leaves it off so shipped approval demos keep their behavior.
  ([Help](../salesforce/264/help/articles/ind.approvals_turn_on_delegation.htm.md))
- **Slack notifications.** Requires a Salesforce org already connected to a Slack workspace before
  *Notify Reviewers on Slack* and *Notify Submitters on Slack* can be turned on. The build does
  not create that connection.
  ([Help](../salesforce/264/help/articles/ind.approvals_turn_on_slack_notifs.htm.md))
- **Approval Agent.** Help says to set up Agentforce for Revenue Cloud and connect the agent to Slack
  first. The build does not ship an Approval Agent.
  ([Help](../salesforce/264/help/articles/ind.rev_agent_approval_agent.htm.md))

The repository contains no setting, metadata or data plan for any of the three.

## Revenue Standard tax engine

The build's tax engine is the Apex mock adapter (`unpackaged/pre/4_tax/RLM_MockTaxAdapter.cls`;
Avalara and invalid-adapter test classes sit beside it). Help describes extending the Revenue
Standard tax engine with a custom metadata type that maps billing fields to a cloned Revenue
Standard Tax Entries decision table
([Help](../salesforce/264/help/articles/ind.billing_extend_revenue_standard_tax_engine.htm.md)).
The build ships no such custom metadata type, decision-table clone or second tax engine, so that
feature cannot be shown on a default build. Estimated tax on quotes and orders is also off by default
(`quote_est_tax: false` in `cumulusci.yml`).

## Payment gateways

The demo script says Revenue Cloud Billing supports payment methods such as credit card and ACH with
gateways like Stripe and Adyen ([demo script](../enablement/264/qb-demo-script.md)). The build
configures no payment gateway, merchant account or payment method; the only gateway-related data it
loads is the payment retry rules (`datasets/sfdmu/qb/en-US/qb-billing/README.md`). Help states the
payment methods available in the Self-Service Billing Portal depend on the gateway you configure
([Help](../salesforce/264/help/articles/ind.billing_supported_payment_methods_for_the_self_service_billing_portal.htm.md)).
Flows that need a gateway (collecting a payment through a gateway, refunds issued to a gateway,
saved wallets) are not exercised by a default build. Configure a gateway sandbox in the org yourself;
never commit gateway keys to this repository.

## Billing Forecast Console and Lockbox

The build turns on Billing Forecast in Billing Settings (`enableBillingForecast`, see
`unpackaged/post_billing/settings/Billing.settings-meta.xml`), which lets the org generate forecast
runs. It does not provision what the rest needs:

- **Billing Forecast Console.** Help says it uses Tableau Next and requires Data 360 to be enabled
  and connected, with the Billing Forecast added to the Advanced Billing Bundle
  ([Help](../salesforce/264/help/articles/ind.billing_forecast_data_360.htm.md)).
- **Lockbox reconciliation.** The 264 release notes say it uses Document AI and requires the Billing
  Admin and Data Cloud Architect permission sets
  ([release note](../salesforce/264/release-notes/articles/release-notes.rn_billing_lockbox_reconciliation.htm.md)).
  The repository contains no Lockbox configuration.

The build does not provision Data 360.
