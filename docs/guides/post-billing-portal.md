# post_billing_portal

Metadata for the Self-Service Billing Portal Experience Cloud site: the `Billing Portal` Network, the
`Billing_Portal1` Aura (Picasso) ExperienceBundle, its NavigationMenu, and ExperienceBundle settings.
This is the unmodified, out-of-the-box "Self-Service Billing Portal" template shipped in Salesforce
Release 262 (Summer '26, API v67.0), plus the portability fixes documented in the README below.

Deploy through the `prepare_billing_portal` flow. When `billing_portal` and
`billing_portal_deploy` are true, it runs `create_billing_portal`, patches the Network email
placeholder, deploys this bundle with `deploy_post_billing_portal`, reverts the placeholder, then
publishes the community. Running the deploy task directly bypasses the required email patch.

See [`unpackaged/post_billing_portal/README.md`](../../unpackaged/post_billing_portal/README.md) for
contents, the naming-derivation rule, PII handling and failure recovery, portability notes, and
deployment/testing commands.
