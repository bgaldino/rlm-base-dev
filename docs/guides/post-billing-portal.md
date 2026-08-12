# post_billing_portal

Metadata for the Self-Service Billing Portal Experience Cloud site: the `Billing Portal` Network, the
`Billing_Portal1` Aura (Picasso) ExperienceBundle, its NavigationMenu, and ExperienceBundle settings.
This is the unmodified, out-of-the-box "Self-Service Billing Portal" template shipped in Salesforce
Release 262 (Summer '26, API v67.0), plus the portability fixes documented in the README below.

Deployed by the `deploy_post_billing_portal` task when `billing_portal` and `billing_portal_deploy` are
true. The `prepare_billing_portal` flow runs `create_billing_portal`, patches the Network email
placeholder, deploys this bundle, reverts the placeholder, then publishes the community.

See [`unpackaged/post_billing_portal/README.md`](../../unpackaged/post_billing_portal/README.md) for
contents, the naming-derivation rule, PII handling, portability notes (embedded messaging removal), and
deployment/testing commands.
