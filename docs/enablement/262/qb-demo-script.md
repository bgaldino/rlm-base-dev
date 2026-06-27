# :quantumbit: FY27 Revenue Cloud QuantumBit Script — Summer '26 (Release 262)

> **Generated:** 2026-05-24 by `.cursor/skills/qb-demo-script/SKILL.md`
> **Source canvas (260):** [F09Q04HEC8Y](https://salesforce.enterprise.slack.com/docs/T45GK97GB/F09Q04HEC8Y)
> **Salesforce Release:** 262 (Summer '26) · API v67.0
> **Status:** DRAFT — preview release, not yet GA. Requires SME pass for Setup-UI verification, Known-Bugs population, image capture, and Slack canvas publish.
> **Grounded on:**
> - `docs/enablement/master/qb-scenario-reference.md` (canonical demo data — Infinitech / Global Media accounts, QB-COMPLETE / QB-QRack-750 SKUs, QB Q-Rack 750 / QB Complete Solution / QB Services Project bundles)
> - `.agents/artifacts/qb-canvas-260-source.md` (prior-release Slack canvas — source of the 6 persona names + bios; personas are stable release-to-release and **not yet** in `qb-scenario-reference.md` — migration tracked separately so future regenerations don't depend on the local-only canvas source)
> - `docs/salesforce/262/feature-index.md` (262 feature inventory)
> - `docs/salesforce/262/help/articles/` (932-article Help portal mirror)
> - `cumulusci.yml` `project.custom` (39 active feature flags)

### How do I get my own copy of QuantumBit?

Jump over to <@U03S5J7DVRD> or [Solutions Workspace](https://www.solutionswork.space/), find the Demos tab and search for **Revenue Cloud - QuantumBit (CDO).** Click the '**Spin Up**' button and fill out the information. Don't forget to run through the [Demo Setup](#demo-setup-required) steps and [Known Bugs & Areas to Avoid](#known-bugs--issues-to-avoid) before diving in!

Latest TFID (Prod) 262.x.x : **TBD** *(populate when 262 TFID is published)*

**For T&P - 260 & 262 DOT files:** populate Drive folder URL once 262 deploy is staged.

Please provide feedback on demo errors, issues, and missing functionality in the workflow below.

---

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-quantumbit-hero]
:::
:::

::: {.layout}
::: {.column}
### :sf-setup: [Demo Setup [required]](#demo-setup-required)
:::
::: {.column}
### :bug_60: [Known Bugs & Issues to Avoid](#known-bugs--issues-to-avoid)
:::
:::

### :persona: [Demo Personas](#demo-personas)

::: {.layout}
::: {.column}
### :arrow: [Opportunity To Order](#opportunity-to-order)
[Configuration - QB Complete Solution](#opportunity-to-order)
[Configuration - QB Q-Rack 750](#opportunity-to-order)
[Configuration - QB Professional Services Project](#opportunity-to-order)
[Pricing](#opportunity-to-order)
[Ramping & Grouping (NEW: Guided Ramp Schedule with Trials)](#opportunity-to-order)
[Document Generation](#opportunity-to-order)
[Advanced Approvals (NEW: Slack Approvals + Preview UX)](#opportunity-to-order)
[Quoting Agent (Enhanced)](#opportunity-to-order)
[Product Discovery with Constraint Rules (NEW)](#opportunity-to-order)
:::
::: {.column}
### :arrow: [Usage Management & Rating](#usage-management--rating)
:::
:::

::: {.layout}
::: {.column}
### :arrow: [Order Entry, Fulfillment, & DRO](#order-entry-fulfillment--dro)
:::
::: {.column}
### :arrow: [Asset Lifecycle](#asset-lifecycle)
:::
:::

::: {.layout}
::: {.column}
### :arrow: [Invoicing & Billing](#invoicing--billing)
:::
::: {.column}
### :tableaunext2: [Revenue Management Intelligence](#revenue-management-intelligence)
:::
:::

::: {.layout}
::: {.column}
### :arrow: [Payments & Collections](#payments--collections)
:::
::: {.column}
### :contract: [Salesforce Contracts (NEW: Advanced Approvals + Bulk Extraction)](#salesforce-contracts)
:::
:::

---

## What's New in 262 (Summer '26)

> Distilled from `docs/salesforce/262/feature-index.md`. SME pass required to confirm GA vs Beta vs Preview status before publishing to consumer-facing canvas.

**Headline highlights (RCA):**
- Accelerated Deal Approvals in Slack
- Guided Ramp Creation with Trials and Prorated Segments
- Constraint Rules in Product Discovery (real-time compatibility enforcement)
- AI-Supported Bulk Contract Extraction
- Enhanced B2B Commerce Interop (Product Variants)
- Streaming Invoice Processing
- Advanced Approvals with Preview UX
- Advanced Approvals for Contracts (multi-stakeholder serial workflows)
- Large Transaction Scale (Beta — successor to 260's 15K Beta)
- DRO Templates (Beta) + DRO & OMS Interop (Beta)

**Headline highlights (RCB):**
- Upgraded Invoice Batch Run
- Billing Settlements Central
- Advanced Amendments
- Amendments with Milestone Billing
- Refund Orchestration
- Collections Agent
- OOB Dunning Template

**Branding note:** Solution Overview decks for 262 still use "Revenue Cloud Advanced" / "Revenue Cloud Billing". The Spring '26 rebrand to "Agentforce Revenue Management" continues to propagate.

---

## Demo Setup [required]

> Verified against `cumulusci.yml` `project.custom` and `docs/salesforce/262/feature-index.md` "Cross-Area: Salesforce Go (Setup Automation)" section. SME pass required to capture 262-specific Setup UI changes (Salesforce Go is heavily updated in 262).

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-demo-setup-hero]
:::
:::

::: {.layout}
::: {.column}
### Build Catalog Index
From the Revenue Cloud App Homepage in your freshly created org, find the *Click here to Build Catalog Index* section and click the link.
This will kickoff the process which will take roughly 2-10 minutes.
![placeholder][img-PLACEHOLDER-build-catalog-index]
:::
::: {.column}
### Refresh Decision Tables
In the meantime, navigate back to the Revenue Cloud App Homepage and find the RC Refresh Decision Tables section.
Click Next twice and then Finish to refresh all of the decision tables in the org.
**262 NOTE:** with CSV-Based Decision Tables now GA, you can also upload custom CSV-sourced DTs (max 100K rows per CSV DT, 500 CSV DTs per org). See `feature-index.md` Pricing section.
![placeholder][img-PLACEHOLDER-refresh-decision-tables]
:::
::: {.column}
### Approval Emails (optional)
Navigate to Setup → 'Einstein' → 'Einstein Generative AI' → 'Einstein Setup' and click 'Turn On Einstein'.
Do a browser refresh.
Navigate to Setup → 'Einstein' → 'Einstein Sales' → 'Einstein for Sales' and click 'Turn On Sales Emails'.
![placeholder][img-PLACEHOLDER-approval-emails]
:::
:::

::: {.layout}
::: {.column}
### Billing Portal Payment Site (1 of 2) optional
Navigate to Setup → All Sites → Workspaces (for the Self-Service Billing Hub).
Find Administration → Activate.
*(Requires `billing_portal: true` and `billing_portal_deploy: true` in `cumulusci.yml`.)*
![placeholder][img-PLACEHOLDER-billing-portal-1]
:::
::: {.column}
### Billing Portal Payment Site (2 of 2) optional
Navigate to Setup → *All Sites* → *Builder* (for the Self-Service Billing Hub).
Find the Invoice and Payment Details page.
Click the Invoice Payment Options component and fill in the **Merchant ID** field on the right with a Merchant Account that is set up.
Publish your community.
![placeholder][img-PLACEHOLDER-billing-portal-2]
:::
::: {.column}
### Revenue Cloud Agents
Navigate to Setup → Salesforce Go.
In search, enter "agentforce for revenue" → select Set Up → select Turn On.
**262 NOTE:** Salesforce Go received setup-automation enhancements in 262 — verify the exact navigation path against the live org before publishing.
![placeholder][img-PLACEHOLDER-rc-agents]
:::
:::

::: {.layout}
::: {.column}
### Slack Approvals Setup (NEW in 262)
For the Slack Accelerated Deal Approvals feature: Navigate to Setup → Approvals → Slack Integration → Configure.
Pair an Approval Process with a Slack workspace channel.
**Required for the Approvals demo flow.** Verify against 262 Help: search `docs/salesforce/262/help/articles/` for "Slack Approvals" — published article should be present.
![placeholder][img-PLACEHOLDER-slack-approvals-setup]
:::
::: {.column}
### Constraint Rules in Product Discovery (NEW in 262)
Navigate to Setup → Revenue Cloud → Product Discovery → Configure Constraint Rules.
Enable "Real-time compatibility enforcement" toggle.
**SME pass needed:** verify exact toggle label against published 262 Setup UI.
![placeholder][img-PLACEHOLDER-product-discovery-constraints]
:::
:::

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-tools-hero]
:::
:::

::: {.layout}
::: {.column}
### :utility-knife: Account Utilities
Navigate to the Account screen and use the action dropdown to find 'Reset Account'.
Account utilities allows you to choose which data you would like to clear from your account.
![placeholder][img-PLACEHOLDER-account-utilities]
:::
::: {.column}
### Usage Management Tool
Navigate to Usage Tab on Account → Add Usage.
Select Asset → add Single Entry or Upload CSV → Upload Usage.
Process Usage (*may take 15-20 min*).
View Usage once workflow services confirm completion.
![placeholder][img-PLACEHOLDER-usage-management-tool]
:::
::: {.column}
### Create Ramp Schedule (GA in 262, Summer '26)
Navigate to an empty quote → Create Ramp Schedule.
Edit *Ramp Schedule Name*, *Type*, and *Start Date* (*as needed*) → add Discount/Uplifts (*as needed*) → Create.
Add Products to first ramp segment (*will be displayed option upon save to add to current & subsequent segments or only first segment*) → Reprice All.
**262 NEW:** Trial segments and prorated stub periods are now supported (was preview in 260, GA in 262). See `feature-index.md` Transaction Management → "Guided Ramp Schedule Generation with Trial and Prorated Segments".
![placeholder][img-PLACEHOLDER-create-ramp-schedule]
:::
:::

::: {.layout}
::: {.column}
**Quick Quote**
Navigate to top right dropdown of Account Record.
Select 'Quick Quote'.
*Opportunity and quote records get auto-created, as well as standard pricebook defaulted, immediately bringing you to the quote record.*
![placeholder][img-PLACEHOLDER-quick-quote]
:::
:::

---

## Known Bugs & Issues to Avoid

> SME pass required to populate from 262 release notes + active issue tracker. Carry-over candidates from 260 listed below; verify each against 262 before publishing.

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-bugs-hero]
:::
:::

:x: **CARRY-OVER FROM 260 — VERIFY:** Manage Header Adjustments not functional with the default QuantumBit Pricing Procedure

:x: **CARRY-OVER FROM 260 — VERIFY:** Delta Pricing for Quote and Orders — confirm if the 258-era bugs were resolved by 262

:x: **CARRY-OVER FROM 260 — VERIFY:** Advanced Transaction Detail Line Pricing — confirm if the 258-era bugs were resolved by 262

:warning: **NEW IN 262 — POPULATE FROM RELEASE NOTES:** SME pass against `salesforce-release-notes-summer-26-2026-05-07.pdf` (Revenue Management section, p. 720+) for net-new bugs and Beta-feature limitations.

---

## Demo Personas

> Sourced verbatim from the prior-release canvas at `.agents/artifacts/qb-canvas-260-source.md` (lines 199–225). Personas are stable across releases. Migration of the persona inventory into `docs/enablement/master/qb-scenario-reference.md` is tracked as a follow-up so future regenerations don't depend on a local-only artifact.

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-personas-hero]
:::
:::

::: {.layout}
::: {.column}
### Edgar Fallon
![placeholder][img-PLACEHOLDER-persona-edgar]
As the Chief Financial Officer (CFO) of QuantumBit, Edgar Fallon is responsible for overseeing all financial aspects of the company. His role involves managing financial planning, budgeting, and forecasting to ensure the company's long-term financial stability and growth. Edgar also oversees financial reporting, ensuring compliance with regulatory requirements and providing accurate and timely financial information to stakeholders. Additionally, he plays a key role in strategic decision-making by providing financial analysis and guidance to the executive team, helping to drive the company's overall success and profitability.
:::
::: {.column}
### Kristen O'Reilly
![placeholder][img-PLACEHOLDER-persona-kristen]
Kristen is an Account Executive at QuantumBit who loves collaborating with her team members and ensuring customers are successful on QuantumBit's platform. She's been at the company about a year and has seen rapid growth take place. In this economic environment she knows it's important to be able to do more with less to grow revenue and keep existing customers happy.
:::
::: {.column}
### Anne Wei
![placeholder][img-PLACEHOLDER-persona-anne]
Anne Wei's role in Sales Ops at QuantumBit involves supporting the sales team and ensuring smooth operations within the sales department. Anne plays a crucial role in supporting the sales team and driving business growth at QuantumBit through data analysis, process improvement, and cross-functional collaboration.
:::
:::

::: {.layout}
::: {.column}
### Shaun Holter
![placeholder][img-PLACEHOLDER-persona-shaun]
As a Renewals Manager at QuantumBit, Shaun is responsible for managing the overall renewal process for customers. His role involves proactively engaging with existing customers to ensure timely renewals, negotiating terms and pricing, and collaborating with sales and customer success teams to maximize customer retention and revenue growth.
**NEW USE CASE FOR 262:** Shaun's Renewal flow now leverages **Early Renewal for Ramped Asset** — start a new (often larger/longer) subscription ahead of schedule, replacing the remainder of an existing ramp schedule.
:::
::: {.column}
### Beth Henderson
![placeholder][img-PLACEHOLDER-persona-beth]
Beth's role on the Order Management team at QuantumBit involves processing and managing customer orders for the company's various products. She ensures accuracy in order processing, coordinates with various departments such as sales, inventory management, and shipping to fulfill orders efficiently, and handles any inquiries or issues related to orders from customers. In addition, she monitors order trends to identify potential bottlenecks or process improvements and collaborates with operations to streamline workflows.
**NEW USE CASE FOR 262:** Beth's DRO flow now leverages **DRO & OMS Interop (Beta)** for real-time sync between DRO and OMS, eliminating dual-platform reconciliation.
:::
::: {.column}
### Jeane Claude Perrier
![placeholder][img-PLACEHOLDER-persona-jeane-claude]
Jean Claude manages billing processes to ensure accurate invoicing, revenue recognition, and customer satisfaction, while collaborating with teams like Sales, Finance, and Customer Success.
**NEW USE CASE FOR 262:** Jeane Claude's Billing flow now leverages **Streaming Invoice Processing**, **Upgraded Invoice Batch Run**, and **Refund Orchestration**.
:::
:::

---

## Opportunity To Order

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-opp-to-order-hero]
:::
:::

> **What's new in 262:** Product Discovery with Constraint Rules (real-time compatibility enforcement, auto-save, transaction preview), Product Variants in Quotes & Orders, Group and Ramp Segment Scope Rules (Configurator), Approval Preview UX, Slack Approvals.

|**Click Path/Action**|**Talk Track**|**Screenshot**|
|  ---  |  ---  |  ---  |
|- Click on the accounts navigation<br><br>- Click on the **Infinitech** account (or **Acme** legacy account if not yet migrated)<br><br>- Click Related|Hi, I'm Kristen an Account Executive at QuantumBit. Conversations with **Infinitech** are progressing extremely well, and they would like to receive a budgetary quote.<br><br>As you can see by the looks of this account, **Infinitech** is a new prospect, so we don't have a lot of information about them yet, but our quote information will drive a wealth of valuable data when it's complete. But first, I must create an opportunity.|![placeholder][img-PLACEHOLDER-account-infinitech]|
|- Click **Create Opportunity**|I'll begin by completing any essential information about this opportunity.<br><br>This step is crucial as it lays the groundwork for the tailored quote the customer has requested.|![placeholder][img-PLACEHOLDER-create-opportunity]|
|- Click "**New Quote**" (top right)|Revenue Lifecycle Management eliminates the need for Deal Desk or cumbersome spreadsheets by integrating everything directly with the opportunity.<br><br>To start the quoting process, I click on "New Quote".|![placeholder][img-PLACEHOLDER-new-quote]|
|- Add a Quote Name and any other required fields<br><br>- Click "Save"<br><br>- Navigate to your newly created quote record|Salesforce has populated most of the important information for me, leaving room for additional input where it matters.<br><br>Upon saving, the quote is generated and attached to the opportunity. Now I'm ready to start adding products.|![placeholder][img-PLACEHOLDER-save-quote]|
|- Click 'Browse Catalog' button<br><br>- Select the 'Standard Pricebook'|As I browse the catalog, I will first be prompted to select a Price Book, so that the relevant prices will be displayed for the products. **NEW in 262:** Product Discovery now enforces Constraint Rules in real time as you browse — incompatible products surface inline, recommendations appear as you select.|![placeholder][img-PLACEHOLDER-browse-catalog]|
||Once I've selected the appropriate Price Book, the system will allow me to choose the catalog I would like to explore.|![placeholder][img-PLACEHOLDER-select-catalog]|
|## :solution-found: Product Configuration - QuantumBit Complete Solution|||
|- Select the 'Software' catalog and click "Next"|As a QuantumBit Account Executive, I have a large product catalog to choose from, but RLM makes it easy to find the exact product suite I'm looking for.|![placeholder][img-PLACEHOLDER-software-catalog]|
|- Select the 'Bundle' category<br><br>- Find the "**QuantumBit Complete Solution**" (SKU: **QB-COMPLETE**)<br><br>- Choose the Buying Option for your product by clicking the Price Tag icon, choosing an option, and hitting '**Add**'<br>(We recommend using the 'TermDefined Annual' option to keep amendments simple)<br><br>- Once the product has been added, click **'Save Quote'**|At QuantumBit, we have a lot of products in our catalog where in the past accurately selecting what I needed for a quote required tribal knowledge. By selecting the appropriate category, I can quickly filter through the product catalog to easily find what my customer needs and how they want to buy.|![placeholder][img-PLACEHOLDER-qb-complete-add]|
|- Once the quote has been updated and the products appear on the **Quote Lines** tab, click the dropdown next to the 'QuantumBit Complete Solution' parent line item, and choose '**Configure**'|I've selected the product my customer needs but I need to go and configure this to their specific asks.|![placeholder][img-PLACEHOLDER-qb-complete-configure]|
|- First thing to highlight is the general layout of the configurator (Config, Summary, Subtotals)<br><br>- Navigate to the top of the configurator and choose '**Redhat Enterprise Linux**' for your **Operating System** attribute<br><br>- Configuration Rules have now been included that will drive compatibility between the attributes and product selections|**NEW in 262:** the configurator now supports Group and Ramp Segment Scope Rules — transaction scope rules apply correctly to Quote Groups and Ramp Segments. Previously, scope rules failed when groups were present.|![placeholder][img-PLACEHOLDER-configurator-os]|
|- Notice when **Operating System** was changed a rule message showed up at the top of the screen identifying that a rule has been enforced on the **Tech Specs** attribute<br><br>- The **Tech Specs** attribute is now locked down to a value of **8** and cannot be changed without adjusting the **Operating System** attribute|||
|- Find **QB API Management Solution** (SKU: **QB-API**)<br><br>- Select any Purchasing Option|This solution is complete with the products, training, and services at termed subscriptions or one time. My customer needs the API Management Solution and we've agreed upon annual terms. However, this can be sold at monthly or perpetual too at different amounts based on how my customer wants to purchase.|![placeholder][img-PLACEHOLDER-qb-api-purchasing]|
|- If the user chooses to increase the quantity of '**QB API Solution**' the '**Additional API**' product becomes required.||![placeholder][img-PLACEHOLDER-qb-api-additional]|
|- Notice the **message** indicating the rule has fired at the top of the screen<br><br>- Also highlight that the '**Additional API**' product has been auto-selected and is not deselect-able||![placeholder][img-PLACEHOLDER-qb-api-rule-fired]|
|- Find the **Additional API** product and click the configuration icon (gear) aligned to the left<br><br>- Set **API_Type** to **Prod**<br><br>- Click **Save**|My customer needs some additional API's as well, to be charged monthly. I can go a step further and determine the type of API's to be quoted. I can see the associated price updated and the default quantity of 10. Thanks to logic working in the background based off my selections, I can trust that I'm always initially building a technically valid quote.|![placeholder][img-PLACEHOLDER-additional-api-config]|
|- Scroll down to **Services**<br><br>- Deselect **Professional Services Daily Rate**<br><br>- Select **QuantumBit Service Project**<br><br>- Click the configuration icon (gear) aligned to the left|Based on conversations with my customer, I know they're interested in our professional service offerings as well. It's easy for me to add resources at an hourly rate or select from a more predefined scope of work, but for today I'm going to build out a bespoke professional services project for my customer|![placeholder][img-PLACEHOLDER-services-quantum-bit-service-project]|
|- Open **Engineering_Resources**<br><br>- Select **Implementation Engineer**<br><br>- Click **Save**|If I expand this project, I can see some predefined resources already are included for me. I can additionally configure additional resources as needed.|![placeholder][img-PLACEHOLDER-implementation-engineer]|
|- Click **Update Prices**<br><br>* Update Prices does not appear when using Instant Pricing.<br><br>- Click **Save & Exit**<br><br>- Close the Product Selection window (if necessary)<br><br>* Notice the price update in the Quote Summary section.<br><br>- **Refresh** screen to see the Quote Line Items|Finalizing the configurations I've made and updating pricing, I can trust I've built a technically valid quote.|![placeholder][img-PLACEHOLDER-update-prices-1]|
|- In order to show **DERIVED PRICING** be sure to select the '**Software Maintenance**' product in your configuration<br><br>- Including the maintenance product will highlight the ability to price a product off of other factors in the configuration or quote, in this case the '**Software Maintenance**' price will be 20% of the total software included on the quote||![placeholder][img-PLACEHOLDER-software-maintenance-derived]|
|- To show more robust quote line decomposition for **DRO** be sure to include the '**API Access Requests (AEH)**' product in your configuration.||![placeholder][img-PLACEHOLDER-aeh-product]|
|- Click **Update Prices**<br><br>* Update Prices does not appear when using Instant Pricing.<br><br>- Click **Save & Exit**<br><br>- Close the Product Selection window (if necessary)|Finalizing the configurations I've made and updating pricing, I can trust I've built a technically valid quote.|![placeholder][img-PLACEHOLDER-update-prices-2]|
|- Once configuration is complete, click 'Save & Exit' to return to the quote line screen||![placeholder][img-PLACEHOLDER-config-save-exit]|
|## :solution-in-progress: Product Configuration - QuantumBit Q-Rack 750 Rack Server|||
|From the Quote, click **Browse Catalog**|My customer is interested in purchasing our state-of-the-art Server (**QB-QRack-750**) for an AI use-case.||
|Navigate to the "**QuantumBit Hardware**" Catalog<br><br>**Server → QuantumBit Q-Rack 750 Rack Server →** Click the **Gear Icon** to configure|I have access to an Enterprise Product Catalog that contains multiple catalogs to pick and choose from. Since my customer is interested in purchasing state-of-the-art hardware, we will navigate through our **QuantumBit Hardware Catalog.**<br><br>As a seller, I am able to navigate through the various categories giving me an E-Commerce like product browsing experience.<br><br>Once I've found the appropriate product offering, I will proceed with configuring the solution|![placeholder][img-PLACEHOLDER-qrack-browse]|
|Highlight the **Attribute Categories** & **Component Groups**|Our configurator is built on a powerful, constraint-based rules engine. As I select the critical **attributes** and **components** for the customer's solution, the engine automatically filters out all incompatible options. This guarantees we are building a technically valid solution every time.|![placeholder][img-PLACEHOLDER-qrack-attributes]|
|Scroll down & showcase both **Gold & Platinum Processors** available|I am able to pick and choose from both Gold & Platinum level processors since I have a General Workload.|![placeholder][img-PLACEHOLDER-qrack-processors]|
|Scroll down & showcase the options of **CPU Cooling** that are available|Similarly, I also have the option to upgrade to a Liquid Cooling system. However, the air cooling for General Workloads is sufficient for this use-case.|![placeholder][img-PLACEHOLDER-qrack-cooling]|
|Scroll up & navigate to the **Workload** attribute → Select **"AI"**|My customer specified that they are interested in an AI Workload. As I update the attribute, the constraint engine has done all of the heavy lifting for me as a seller.|![placeholder][img-PLACEHOLDER-qrack-workload-ai]|
|Highlight **3D Visual Updating** Dynamically by adding a GPU<br><br>Highlight how constraints update values dynamically → **Socket Configuration = Dual**|First, as you can see it automatically added a GPU which is visually represented in our 3D Visual model that is provided by our Visualization Partner RenderDraw.<br><br>Second, the constraint engine automatically updated the Socket Configuration to Dual, meaning that it must contain two processors.|![placeholder][img-PLACEHOLDER-qrack-3d-gpu]|
|Scroll down to the **Processor Group** → Show that **Gold Level Processors** are **Constrained**|And just like that, you can see the rules engine at work. Notice two things happened automatically: the processor list is now filtered to show only the compatible Platinum-level options. And second, the quantity has been set to 2, because the system knows this is a Dual Socket Configuration. There's no need to cross-reference a manual or worry about mistakes; the system ensures the configuration is valid.|![placeholder][img-PLACEHOLDER-qrack-processor-constrained]|
|*(rest of QB Q-Rack 750 click-path verbatim from 260 — verify against 262 for any UI changes; the constraint engine behavior is unchanged at the model level)*|*(continued — Memory, Storage, PCIe, Power Supply sections from 260 carry over)*|*(image markers continue)*|
|## :solution-needed: Product Configuration - QuantumBit Professional Services Project|||
|*(verbatim from 260 — Services Project configuration is unchanged in 262 unless `feature-index.md` shows otherwise; SME pass to confirm)*|||
|## :price-tag: Pricing|||
|- Find the quote line dropdown to explore more detail about each product||![placeholder][img-PLACEHOLDER-pricing-explore]|
|- Highlight the **DERIVED PRICE** on the '**Software Maintenance**' product||![placeholder][img-PLACEHOLDER-pricing-software-maint-derived]|
|- Modify the discount field & click '**Save**'|After configuring a technically valid solution for my customer, I'm taken to the quote and quote line details where I can adjust my deal. Using RLM, I can add discounts at the individual product level. **NEW in 262:** Decimal Currency Value Scale — you can now configure up to 6 decimal places for unit-level prices and discount fields on Product Discovery, Quote, and Order pages (default and minimum is 2). Note: only Unit Pricing and Unit Adjustment fields support high scale; final total fields still truncate to 2.|![placeholder][img-PLACEHOLDER-pricing-discount]|
|## :ramps: Ramping & Grouping (NEW in 262: Guided Ramp Schedule with Trials)|||
|*(Carry over the 260 ramp click-path; ADD the 262 trial-segment use case below)*|||
|**262 NEW USE CASE — Free Trial Ramp:** From an empty quote → **Create Ramp Schedule** → set Type=Yearly → Start Date today. **Add a Trial Segment** with duration 30 days (no charge). **Add Subscription Segment** of 11 months. Save.|This shows the **Guided Ramp Schedule with Trial Segments** feature new in 262. Replaces slow manual cloning for multi-year ramp deals. Supports free/trial segments + stub periods at start/end.|![placeholder][img-PLACEHOLDER-ramp-trial-segment]|
|*(rest of standard QB ramp click-path: 3-segment yearly ramp, Manage Usage Resources for Quantum Tokens, etc.)*|||
|**Continued in the [Asset Lifecycle](#asset-lifecycle) section**|||
|## :document-3870: Document Generation|||
|- Navigate to the **Quote Document** tab on the quote record and choose the format for your quote document and click "**Next**"|After I've received all the necessary approvals for my quote, I can go and actually generate that customer facing document. **NEW in 262:** DocGen now uses the Client-Side LWC for faster preview, Context-DPE Transformations for richer template binding, and Dynamic Watermarks driven by tokens.|![placeholder][img-PLACEHOLDER-docgen-format]|
|- Add attachments to the quote document and click "**Next**" again||![placeholder][img-PLACEHOLDER-docgen-attachments]|
|- Allow the Quote to generate|It was a breeze to generate a document with terms and pricing I outlined in the quote. This document looks fantastic and is completely on brand. I'm going to close out the preview and send to my future customer.|![placeholder][img-PLACEHOLDER-docgen-preview]|
|- Examine your Quote and scroll to the top to find the download buttons.|Since the deal has been approved, the quote is ready for Customer Delivery. Now I'm also able to download this quote as a PDF or Word file to send to my customer. I can also send it for esignature using Docusign.|![placeholder][img-PLACEHOLDER-docgen-download]|
|## :approval_60-1: Advanced Approvals (NEW in 262: Slack Approvals + Preview UX)|||
|- Add discounts of varying amounts to software lines|Continuing as a sales rep, I want to work with my customer on pricing so I can ensure this deal gets done.|![placeholder][img-PLACEHOLDER-approvals-discounts]|
|- Notice the ability '**Preview**' on the **Approvals** tab. **NEW in 262:** the Preview UX is enhanced — multi-stakeholder serial approvals are visualized.||![placeholder][img-PLACEHOLDER-approvals-preview-ux]|
|- Click **Preview** to understand where the approvals must route.||![placeholder][img-PLACEHOLDER-approvals-preview]|
|- Navigate to down carrot in top right corner and select **Submit for Approval** → **Submit**|I can see the discount changes I've made have triggered a need for an approval before I can send this quote off to my customer.|![placeholder][img-PLACEHOLDER-approvals-submit]|
|**262 NEW: Slack Approval Routing.** Switch to the connected Slack workspace channel for the Approval Process. Approve directly from the Slack message. **Required setup:** see "Slack Approvals Setup" in Demo Setup section above.|This is the **Accelerated Deal Approvals in Slack** feature new in 262. Approvers don't need to log into Salesforce to approve — the approval card is delivered to Slack with full context and inline approve/reject.|![placeholder][img-PLACEHOLDER-approvals-slack]|
|- Navigate to **App Manager** and search & select **Approvals** app<br><br>- Select **Review Pending Approvals**|For the in-Salesforce flow: switching hats to an admin/approver role, in the Approvals app I'm able to see a list view of all the requests that need my attention.|![placeholder][img-PLACEHOLDER-approvals-pending]|
|- Navigate to the down carrot on the line of the approval request<br>- Select **Review**||![placeholder][img-PLACEHOLDER-approvals-review]|
|- Select as **Approved** or **Rejected** → **Confirm** → Refresh browser||![placeholder][img-PLACEHOLDER-approvals-decision]|
|- Navigate to **Home** tab in **Approvals** app<br><br>- Select **Review Submitted Approvals**<br><br>- Highlight the **status** of your approval request reflecting as "*Approved*"|Now switching back to the sales rep view, with the new revenue cloud I'm able to review everything I've submitted for approval and what status it is in.|![placeholder][img-PLACEHOLDER-approvals-status]|
|## :agentforce: AgentForce Quoting Agent (Enhanced in 262)|||
|Ensure you've gone through the setup steps<br><br>Open the Einstein Window, pin it, and select the *Revenue Quote Management* agent||![placeholder][img-PLACEHOLDER-agent-pin]|
|The Revenue Cloud AgentForce Quoting Agent is designed to be used on the Opportunity of any Account in Salesforce.<br><br>Use a prompt like:<br>'Create a new business quote on this opportunity, starting today for 12 months. Add 1 of the QuantumBit Complete Solution'<br>OR<br>'Create a new business quote on this opportunity, starting today for 12 months. Add 5 of the QuantumBit Subscription at a 25% discount and 1 of the QuantumBit Database.'||![placeholder][img-PLACEHOLDER-agent-prompt]|
|Einstein will now automate the creation of the quote and add the appropriate products. Navigate to the quote that was created from the agent's links or by refreshing the opportunity.|||
|If you would like, apply a discount via the agent: 'On the [insert quote name] quote, apply a 15% discount to the QuantumBit Subscription and summarize and open the quote.'|||
|Once you are happy with your quote click the 'Generate PDF' button on the quote. Review the Document.|||
|Use the prompt 'summarize this quote' for a quote summary.||![placeholder][img-PLACEHOLDER-agent-summarize]|
|Continue with 'draft an email using this summary' for the email draft.||![placeholder][img-PLACEHOLDER-agent-email]|

---

## Order Entry, Fulfillment, & DRO

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-dro-hero]
:::
:::

> **What's new in 262:** DRO Templates (Beta), DRO & OMS Interop (Beta), Future-Dated and Backdated Amendments and Renewals support.

|**Click Path/Action**|**Talk Track**|**Screenshot**|
|  ---  |  ---  |  ---  |
|- When ready, click '**Create Order**' to finalize your quote.||![placeholder][img-PLACEHOLDER-dro-create-order]|
|- Click on the newly created Order|Now from the perspective of Beth in Sales Ops, all the information created in the quote is available automatically in the Order details.|![placeholder][img-PLACEHOLDER-dro-order-detail]|
|- Evaluate Order Items|From within the order, I see all the items that were quoted previously, now order items.|![placeholder][img-PLACEHOLDER-dro-order-items]|
|*Make Sure Bill to Contact is entered in Order Details prior to activation*<br><br>- If you're not planning on showing DRO, move chevron to 'Activated'|I'll manually activate this order and this will kick off the creation of the contract to keep track of my customer's active spend.|![placeholder][img-PLACEHOLDER-dro-activate]|
|Start in the Dynamic Revenue Orchestration App. Before starting, make sure you have a pre-staged drafted order. The order should have the QB complete solution ramped over two years.<br><br>**Year 1:** QB-COMPLETE Qty 1, QB Services Project Qty 1, Additional API Qty 10, AEH Qty 100<br>**Year 2:** QB-COMPLETE Qty 1, QB Services Project Qty 1, Additional API Qty 15, AEH Qty 125|As a SalesOps manager, I start my day in the Dynamic Revenue Orchestrator home page.|![placeholder][img-PLACEHOLDER-dro-home]|
|Click into your pre-staged drafted order|I can see I have one draft order that needs my review.|![placeholder][img-PLACEHOLDER-dro-draft-order]|
|Showcase the "Lines" tab on the order to talk through the breakdown of this order|*(verbatim from 260 — order line breakdown narrative is unchanged at the data-model level)*|![placeholder][img-PLACEHOLDER-dro-lines]|
|Click the fulfillment/decomposition details tab|My order provisioning process doesn't have to stop here.|![placeholder][img-PLACEHOLDER-dro-decomposition]|
|*(verbatim 260 click-path for decomposition toggling: Project Service → 1 fulfillment line; Finance Service → All decomposed; AEH 2-line ramp; QB API Management consolidated)*|||
|Click into the **Orchestration Plan**|Another awesome feature is the **Orchestration Plan**, where I can get a quick and visual understanding of what has been green or red-lit in my order process.|![placeholder][img-PLACEHOLDER-dro-orch-plan]|
|*(verbatim 260 click-path for Orchestration Plan: Red Warning hover, Blue Calendar hover for ramp, milestone-based billing step)*|||
|Switch tabs into the **Order Analytics Dashboard**|This order is just one of many. For my orders across the board, I rely on our OOTB Order Analytics Dashboard, powered by Revenue Management Intelligence.|![placeholder][img-PLACEHOLDER-dro-analytics-dashboard]|
|Scroll down to see the order staging report|Instead of digging through multiple systems, I can see the exact source statuses of where my orders are sitting.|![placeholder][img-PLACEHOLDER-dro-staging-report]|
|**262 NEW: DRO Templates (Beta).** Navigate to Setup → Dynamic Revenue Orchestrator → Templates → Browse Pre-built Templates. Apply a template to a draft order to bootstrap orchestration steps.|This shows the **DRO Templates** feature new in 262 (Beta). Pre-built orchestration templates eliminate the need to author orchestration plans from scratch for common order types.|![placeholder][img-PLACEHOLDER-dro-templates]|
|**262 NEW: DRO & OMS Interop (Beta).** Switch to the OMS app. Notice the order is reflected in real-time. Make a status change in OMS — verify it propagates back to DRO without manual reconciliation.|This is the **DRO & OMS Interop** Beta feature — addresses the prior gap where teams had to manage two non-synced platforms. SME pass needed to confirm exact navigation and verify the Beta is enabled in the demo org.|![placeholder][img-PLACEHOLDER-dro-oms-interop]|
|Close out|With Dynamic Revenue Orchestration, my daily manual tasks have become much more automated.||

---

## Asset Lifecycle

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-asset-hero]
:::
:::

> **What's new in 262:** Early Renewal for Ramped Asset (renew a ramped asset ahead of schedule with new ramp segments replacing remainder).

|**Click Path/Action**|**Talk Track**|**Screenshot**|
|  ---  |  ---  |  ---  |
|*(All 260 click-path content for Asset Lifecycle carries over — verify against 262. Add the 262-NEW use case below.)*|||
|**262 NEW: Early Renewal for Ramped Asset.** From the activated 3-year ramp, navigate to the Ramped Asset → Renew Asset → set Renewal Start Date to a future date mid-segment. The renewal quote replaces the remainder of the existing ramp schedule with new ramp segments.|This is the **Early Renewal for Ramped Asset** feature new in 262. Use cases: (a) end a 3-year ramp after 2 years for a renegotiated 2-year contract, (b) consolidate ramped + non-ramped assets in a single renewal quote.|![placeholder][img-PLACEHOLDER-asset-early-renewal]|

---

## Invoicing & Billing

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-invoice-hero]
:::
:::

> **What's new in 262 (RCB headlines):** Upgraded Invoice Batch Run · Streaming Invoice Processing · Billing Settlements Central · Advanced Amendments · Amendments with Milestone Billing · Refund Orchestration.

|**Click Path/Action**|**Talk Track**|**Screenshot**|
|  ---  |  ---  |  ---  |
|App Launcher :app-launcher-81: → Billing app|Revenue Cloud is a cross-functional operating layer. The product catalog, pricing rules, and billing logic all live on the single unified data model — sales can quote with confidence, Finance can reconcile and forecast in real time, and RevOps gains the telemetry to iterate on pricing and packaging every sprint.||
|Billing App → Quote → Order → Billing Schedules|As a billing operations persona I have all the information I need on the billing app what we call billing 360.|![placeholder][img-PLACEHOLDER-billing-360]|
|From Billing App → Navigate to pre-seeded Quote with Bundle of products|Revenue Cloud Billing is designed to work seamlessly with our CPQ engine upstream without the need for extensive integration.||
|Go to order which is generated and Activate the Order. Highlight the Billing schedule groups/schedules generated.|Once the quote is converted to the order. Upon order activation, Revenue Cloud Billing immediately generates an accurate record of my billable products in the Billing Schedules object. **NEW in 262:** Streaming Invoice Processing handles invoice generation as a near-real-time stream rather than batch waits.|![placeholder][img-PLACEHOLDER-billing-schedules]|
|Highlight that invoices can be automated by leveraging the invoice scheduler or you can create ad-hoc invoices.|Automate invoice generation by leveraging the scheduler. **NEW in 262:** the Upgraded Invoice Batch Run improves throughput and observability for large batch runs.|![placeholder][img-PLACEHOLDER-invoice-scheduler]|
|Show the invoice which was generated at the account level and highlight the invoice lines and the template|In addition to generating the invoice data, we can also generate the invoice document and send it via email to your end customer.||
|**262 NEW: Billing Settlements Central.** Navigate to the new Settlements Central app. Show the unified view of settlements across multiple billing schedules.|This is the **Billing Settlements Central** feature new in 262 — a centralized view for billing settlements across orders.|![placeholder][img-PLACEHOLDER-billing-settlements-central]|
|**262 NEW: Advanced Amendments + Amendments with Milestone Billing.** Open an active subscription. Initiate Amendment. Notice the new Advanced Amendment flow with milestone-billing alignment.|This shows the **Advanced Amendments** + **Amendments with Milestone Billing** features new in 262 — covers complex amendment scenarios that previously required manual workarounds.|![placeholder][img-PLACEHOLDER-billing-amendments]|
|Highlight payment scheduler and collect payment using the payment component on the invoice page|RCB supports various payment methods like CC, ACH with payment gateways like Stripe, Adyen.|![placeholder][img-PLACEHOLDER-payment-scheduler]|
|On the invoice page → Write off invoice|In the event the balance is uncollectable, you have the option to write off the invoice balance.||
|**262 NEW: Refund Orchestration.** From a paid invoice, initiate a Refund. Show the new orchestration flow that handles partial / full refunds with downstream system propagation.|This is the **Refund Orchestration** feature new in 262 — refund processing now includes orchestration for downstream propagation.|![placeholder][img-PLACEHOLDER-billing-refund-orchestration]|
|Show collection plans and payment promises|*(verbatim from 260 — collection plans + payment promises behavior is unchanged at the data-model level; SME pass to confirm)*||
|Transaction journal → GL Account period summary|Revenue cloud billing optionally can be configured to act as an AR subledger.||
|Go to Account → Contact → click on experience user|With our Billing Portal built on Experience cloud you are able to expose the billing portal to your end users.||
|Salesforce lightning → Go to invoice → Invoice line with usage → Initiate the billing agent|Revenue cloud which is built on core now can take advantage of Agentic AI capabilities.||
|Click on RMI Dashboard for Billing analytics|Running your business, numbers/KPIs are important to gauge how your billing operations are running. With Tabnext and RMI we are able to expose the key KPIs metrics your organization cares about.||

---

## Payments & Collections

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-payments-hero]
:::
:::

> **What's new in 262:** Collections Agent · OOB Dunning Template.

|**Click Path/Action**|**Talk Track**|**Screenshot**|
|  ---  |  ---  |  ---  |
|App Launcher :app-launcher-81: → Collections app|||
|Highlight payment scheduler and collect payment using the payment component on the invoice page|RCB supports various payment methods like CC, ACH with payment gateways like Stripe, Adyen.||
|On the invoice page → Write off invoice|In the event the balance is uncollectable, you have the option to write off the invoice balance.||
|Show collection plans and payment promises|RCB has full collection and dunning capabilities. As a collection agent or collection manager I can take a look at my assigned collection plans.||
|**262 NEW: Collections Agent.** Initiate the Collections Agent on an overdue invoice. Use a prompt like 'draft a dunning email for this invoice and schedule a follow-up call'. Show the generated dunning artifact.|This is the **Collections Agent** feature new in 262 — Agentforce-powered collections workflow that drafts dunning communications and schedules follow-ups.|![placeholder][img-PLACEHOLDER-collections-agent]|
|**262 NEW: OOB Dunning Template.** Show the new out-of-the-box dunning template (replaces hand-authored templates from 260).|This is the **OOB Dunning Template** new in 262 — pre-built dunning communication template, eliminates the prior need to author from scratch.|![placeholder][img-PLACEHOLDER-collections-dunning-template]|

---

## Usage Management & Rating

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-usage-hero]
:::
:::

> **What's new in 262:** Usage Product Guided Setup (enhanced) · Usage Product Activation API · Consumption Agent (continues from 260).

|**Click Path/Action**|**Talk Track**|**Screenshot**|
|  ---  |  ---  |  ---  |
|*(All 260 click-path content for Usage Management & Rating carries over verbatim. Set QuantumBit DataBase product Start Date to a past date for ratable demo. Add Price By Usage. Process activated Usage. Mature Usage scheduled flow. SME pass to verify against 262.)*|||
|**262 NEW: Usage Product Guided Setup.** From Setup, navigate to the new Usage Product Guided Setup wizard. Walk through the streamlined onboarding flow.|This is the **Usage Product Guided Setup** enhancement new in 262 — replaces multi-step manual setup with a guided wizard.|![placeholder][img-PLACEHOLDER-usage-guided-setup]|

---

## Revenue Management Intelligence

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-rmi-hero]
:::
:::

> **What's new in 262:** *(Verify against `feature-index.md` and `salesforce-release-notes-summer-26-2026-05-07.pdf` Revenue Management Intelligence section. SME pass required.)*

|**Click Path/Action**|**Talk Track**|**Screenshot**|
|  ---  |  ---  |  ---  |
|*(All 260 click-path content for RMI carries over. SME pass to verify dashboards and KPIs match 262 packaging.)*|||

---

## Salesforce Contracts (NEW Capabilities in 262)

::: {.layout}
::: {.column}
![placeholder][img-PLACEHOLDER-contracts-hero]
:::
:::

> **What's new in 262:** AI-Supported Bulk Contract Extraction · Advanced Approvals for Contracts · Contract metadata extraction from legacy PDFs.

|**Click Path/Action**|**Talk Track**|**Screenshot**|
|  ---  |  ---  |  ---  |
|App Launcher → Contracts app|||
|*(All 260 click-path content for Salesforce Contracts carries over. Add the 262-NEW use cases below.)*|||
|**262 NEW: AI-Supported Bulk Contract Extraction.** Navigate to Contracts → Bulk Import → Upload Legacy Contract PDFs. Show the extraction job pulling metadata (parties, terms, renewal dates, line items) from a batch of PDFs.|This is the **AI-Supported Bulk Contract Extraction** feature new in 262 — protect margins and unlock historical data trapped in legacy contract PDFs. Particularly valuable for renewals where pre-Salesforce contracts need to be visible alongside current ones.|![placeholder][img-PLACEHOLDER-contracts-bulk-extraction]|
|**262 NEW: Advanced Approvals for Contracts.** From a contract record, initiate Advanced Approvals. Walk through the multi-stakeholder serial workflow (Legal → Finance → CRO).|This is the **Advanced Approvals for Contracts** feature new in 262 — multi-stakeholder serial approval workflows on Contracts (now leveraging the unified Approvals framework).|![placeholder][img-PLACEHOLDER-contracts-advanced-approvals]|

---

## Image Marker Reference

> All `[img-PLACEHOLDER-*]` markers are placeholder slugs. Real Slack file IDs are substituted at canvas-publish time. SME pass required to capture screenshots against the 262 demo org.

```
img-PLACEHOLDER-quantumbit-hero
img-PLACEHOLDER-demo-setup-hero
img-PLACEHOLDER-build-catalog-index
img-PLACEHOLDER-refresh-decision-tables
img-PLACEHOLDER-approval-emails
img-PLACEHOLDER-billing-portal-1
img-PLACEHOLDER-billing-portal-2
img-PLACEHOLDER-rc-agents
img-PLACEHOLDER-slack-approvals-setup
img-PLACEHOLDER-product-discovery-constraints
img-PLACEHOLDER-tools-hero
img-PLACEHOLDER-account-utilities
img-PLACEHOLDER-usage-management-tool
img-PLACEHOLDER-create-ramp-schedule
img-PLACEHOLDER-quick-quote
img-PLACEHOLDER-bugs-hero
img-PLACEHOLDER-personas-hero
img-PLACEHOLDER-persona-edgar
img-PLACEHOLDER-persona-kristen
img-PLACEHOLDER-persona-anne
img-PLACEHOLDER-persona-shaun
img-PLACEHOLDER-persona-beth
img-PLACEHOLDER-persona-jeane-claude
img-PLACEHOLDER-opp-to-order-hero
img-PLACEHOLDER-account-infinitech
img-PLACEHOLDER-create-opportunity
img-PLACEHOLDER-new-quote
img-PLACEHOLDER-save-quote
img-PLACEHOLDER-browse-catalog
img-PLACEHOLDER-select-catalog
img-PLACEHOLDER-software-catalog
img-PLACEHOLDER-qb-complete-add
img-PLACEHOLDER-qb-complete-configure
img-PLACEHOLDER-configurator-os
img-PLACEHOLDER-qb-api-purchasing
img-PLACEHOLDER-qb-api-additional
img-PLACEHOLDER-qb-api-rule-fired
img-PLACEHOLDER-additional-api-config
img-PLACEHOLDER-services-quantum-bit-service-project
img-PLACEHOLDER-implementation-engineer
img-PLACEHOLDER-update-prices-1
img-PLACEHOLDER-software-maintenance-derived
img-PLACEHOLDER-aeh-product
img-PLACEHOLDER-update-prices-2
img-PLACEHOLDER-config-save-exit
img-PLACEHOLDER-qrack-browse
img-PLACEHOLDER-qrack-attributes
img-PLACEHOLDER-qrack-processors
img-PLACEHOLDER-qrack-cooling
img-PLACEHOLDER-qrack-workload-ai
img-PLACEHOLDER-qrack-3d-gpu
img-PLACEHOLDER-qrack-processor-constrained
img-PLACEHOLDER-pricing-explore
img-PLACEHOLDER-pricing-software-maint-derived
img-PLACEHOLDER-pricing-discount
img-PLACEHOLDER-ramp-trial-segment
img-PLACEHOLDER-docgen-format
img-PLACEHOLDER-docgen-attachments
img-PLACEHOLDER-docgen-preview
img-PLACEHOLDER-docgen-download
img-PLACEHOLDER-approvals-discounts
img-PLACEHOLDER-approvals-preview-ux
img-PLACEHOLDER-approvals-preview
img-PLACEHOLDER-approvals-submit
img-PLACEHOLDER-approvals-slack
img-PLACEHOLDER-approvals-pending
img-PLACEHOLDER-approvals-review
img-PLACEHOLDER-approvals-decision
img-PLACEHOLDER-approvals-status
img-PLACEHOLDER-agent-pin
img-PLACEHOLDER-agent-prompt
img-PLACEHOLDER-agent-summarize
img-PLACEHOLDER-agent-email
img-PLACEHOLDER-dro-hero
img-PLACEHOLDER-dro-create-order
img-PLACEHOLDER-dro-order-detail
img-PLACEHOLDER-dro-order-items
img-PLACEHOLDER-dro-activate
img-PLACEHOLDER-dro-home
img-PLACEHOLDER-dro-draft-order
img-PLACEHOLDER-dro-lines
img-PLACEHOLDER-dro-decomposition
img-PLACEHOLDER-dro-orch-plan
img-PLACEHOLDER-dro-analytics-dashboard
img-PLACEHOLDER-dro-staging-report
img-PLACEHOLDER-dro-templates
img-PLACEHOLDER-dro-oms-interop
img-PLACEHOLDER-asset-hero
img-PLACEHOLDER-asset-early-renewal
img-PLACEHOLDER-invoice-hero
img-PLACEHOLDER-billing-360
img-PLACEHOLDER-billing-schedules
img-PLACEHOLDER-invoice-scheduler
img-PLACEHOLDER-billing-settlements-central
img-PLACEHOLDER-billing-amendments
img-PLACEHOLDER-payment-scheduler
img-PLACEHOLDER-billing-refund-orchestration
img-PLACEHOLDER-payments-hero
img-PLACEHOLDER-collections-agent
img-PLACEHOLDER-collections-dunning-template
img-PLACEHOLDER-usage-hero
img-PLACEHOLDER-usage-guided-setup
img-PLACEHOLDER-rmi-hero
img-PLACEHOLDER-contracts-hero
img-PLACEHOLDER-contracts-bulk-extraction
img-PLACEHOLDER-contracts-advanced-approvals
```

---

## Generation Notes

**Source canvas:** Slack canvas `F09Q04HEC8Y` ("FY27 Revenue Cloud QuantumBit Script", 260 / Spring '26 / v66.0). Saved verbatim source at `.agents/artifacts/qb-canvas-260-source.md` (650 lines) as the structural template.

**262 deltas applied:**
- Updated release identifier in title and "How do I get my own copy" section (TFID placeholder pending)
- Added "What's New in 262" highlights section (RCA + RCB)
- Added Slack Approvals Setup + Product Discovery Constraint Rules to Demo Setup
- Annotated Ramp Schedule section with GA-status update (was preview in 260)
- Updated Pricing section with Decimal Currency Value Scale (262 GA)
- Added "Slack Approval Routing" sub-section under Advanced Approvals
- Annotated Configurator section with Group/Ramp Segment Scope Rules (262 GA)
- Annotated DocGen section with Client-Side LWC, Context-DPE, Dynamic Watermarks
- Added DRO Templates + DRO & OMS Interop sub-sections
- Added Early Renewal for Ramped Asset to Asset Lifecycle
- Added Streaming Invoice Processing, Upgraded Invoice Batch Run, Billing Settlements Central, Advanced Amendments, Amendments with Milestone Billing, Refund Orchestration to Invoicing & Billing
- Added Collections Agent + OOB Dunning Template to Payments & Collections
- Added Usage Product Guided Setup to Usage Management
- Added AI-Supported Bulk Contract Extraction + Advanced Approvals for Contracts to Salesforce Contracts (which expanded materially in 262)
- Annotated personas with 262-specific use cases (Shaun → Early Renewal; Beth → DRO/OMS Interop; Jeane Claude → Streaming/Batch/Refund)

**262 deltas requiring SME pass before publishing:**
- TFID identifier (pending 262 deploy)
- DOT files Drive folder URL (pending 262 deploy)
- Setup UI screenshots (Salesforce Go is heavily updated in 262)
- Known Bugs list (carry-over verification + populate net-new from `salesforce-release-notes-summer-26-2026-05-07.pdf` p. 720+)
- Slack Approvals exact Setup navigation (verify against published 262 Help)
- Product Discovery Constraint Rules toggle label (verify against published 262 Setup UI)
- DRO Templates Beta enablement (verify Beta is gated correctly in demo org)
- DRO & OMS Interop Beta enablement (verify both apps available)
- All `(TBD)` entries in `feature-index.md` (Approval Preview Enhancements, Responsive & Maximized Quoting UX, Increased Display Count of Attributes, Deep Clone Enhancements, Quote Extensibility Enhancements, Future-Dated/Backdated Amendments, RCB-cross-listed items)
- Verbatim 260 sections marked "carry over — verify": Q-Rack 750 detail, Services Project, RMI dashboards, Standard Payments & Collections flow

**Image substitution:** All `[img-PLACEHOLDER-*]` markers must be replaced with real Slack file IDs at canvas-publish time. Recommended: capture screenshots against a 262 demo org spun up via `cci flow run prepare_rlm_org --org beta` with full feature flags, upload via Slack file upload API, substitute the markers via search-replace.

**Skill that produced this:** `.cursor/skills/qb-demo-script/SKILL.md` (Foundations, generation mode = `regenerate`).

**Manifest entry:** This artifact lives at `docs/enablement/262/qb-demo-script.md` and is registered in `.claude/skill-manifest.yml` under `foundations.skills.qb-demo-script` (skill) producing output at `foundations.grounding.qb_demo_script_262` (artifact).
