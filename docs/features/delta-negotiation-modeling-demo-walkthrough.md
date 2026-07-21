# Delta Term Builder — Round 2 Live Rehearsal Walkthrough

In-browser verification script for the Round 2 modeling workbench in the
`scheck@deltarevcloud.demo` org. Companion to
[delta-negotiation-modeling-demo.md](delta-negotiation-modeling-demo.md) (the design
doc). The programmatic half of the rehearsal (lint, Jest 102/102, LWC deploy, SFDMU
`dl-termbuilder` seed, permset) is already green — **this doc covers only what a browser
can verify**: reactivity, animation, the transient scope toggle, exports, and the
Create-Contract persistence.

Work top-to-bottom. Each stage lists **Do / Expect / ✓ Pass** and a depth tag:

- **DEEP** — a primary Round 2 deliverable; verify carefully.
- **THIN** — functional but talk-track for the demo; a smoke check is enough.
- **DEFERRED** — not built this round; confirm only the placeholder/talk-track.

---

## 0 — Prerequisites & page composition

Before any stage:

1. **Org + access.** Logged into `scheck@deltarevcloud.demo`; the running user has
   `RLM_TermBuilderPermset` (already assigned — verified via SOQL).
2. **Data seeded.** `dl-termbuilder` (PCM + geography attributes) and `dl-pricing`
   (`PricebookEntry` at `UnitPrice = 0`) are loaded. Round 2 added `DL_ScopeType` +
   `DL_MarketGroup` (both confirmed in the org) and the 6 scope-type picklist values.
3. **Compose the modeling page (you own this).** The `DLM_Term_Builder` Lightning page
   currently hosts only three tiles — `dlmNegotiationContext`, `dlmTermsRail`,
   `dlmTermWorkspace`. **Add the shell tile `dlmWorkspaceShell`** (the always-mounted
   tabset that carries the KPI band, the Modeling tab, the Performance placeholder, and
   the Proposal Summary launcher) via **Setup → Lightning App Builder →
   `DLM_Term_Builder` → Edit**. Suggested layout:

   | Region | Tiles (top → bottom) |
   |--------|----------------------|
   | Left / narrow | `dlmNegotiationContext`, `dlmTermsRail` |
   | Main / wide | `dlmWorkspaceShell`, `dlmTermWorkspace` |

   Save + Activate. All tiles talk over the `DLM_TermBuilderChannel__c` message channel,
   so exact region placement is flexible — they don't need to be parent/child.
4. **Reduced-motion toggle (for Stage 3).** macOS **System Settings → Accessibility →
   Display → Reduce motion**. Have it handy to flip mid-stage.

> **Deferred this round (do not chase):** the Configure Data Set modal (G1
> pre-term-building), the Performance tab's CRMA dashboards, and any `dlDataContext`
> wiring. See §Deferred at the end.

---

## Entry points

| From | Quick action | Lands on |
|------|--------------|----------|
| **Account** | `RLM_Launch_Term_Builder` | a new negotiation (Quote) in the Term Builder |
| **Quote** | `RLM_Open_In_Term_Builder` | the existing negotiation |
| **Contract** (assetized) | `DL_Create_Renewal` | a renewal negotiation with re-stamped lines (Stage 1) |

---

## Stage 1 — Renewal on-ramp · THIN (renewal built; Configure Data Set deferred)

**Do:** From an **assetized Contract**, run **`DL_Create_Renewal`**. Open the resulting
renewal negotiation and inspect its fare lines.

**Expect:** Renewal lines carry re-stamped values from the source contract:
- `Discount` (prior negotiated discount),
- `DL_FareCodes__c` (per-line fare/booking codes),
- `DL_PriorDiscount__c` (the read-only prior-discount reference used in Stage 3).

**✓ Pass:** All three fields are populated on the renewed lines (not blank, not zero).

> G1 pre-term-building (the Configure Data Set modal / `dataSetConfig` parameterization)
> is **talk-track only** this round — there is no interactive modal to open.

---

## Stage 2 — Geography scope on a Term · DEEP

**Do:** Select a Term in the rail. In `dlmTermWorkspace`'s inline attribute picker, set:
- **Scope Type** (`DL_ScopeType`) — e.g. `Country`,
- **Market Group** (`DL_MarketGroup`) — e.g. `GB, FR`,
- **Directionality** (`DL_Directionality`) — e.g. `Between`,
- **Measure** (`DL_Measure`) — `Share of Flights`,
- **Requirement Value** (`DL_RequirementValue`) — e.g. `5.0`.

Then, on the Term's **rail card**, use the **Includes / Excludes toggle** (it appears
only once the Term has a Market Group).

**Expect:**
- The attribute values **persist** on the Term (survive reload) — these are real
  `DL_*` attributes.
- The rail card shows a one-line **scope label** (`Country · Includes GB, FR · Between`)
  and a **specificity rank badge** (`Country`) tinted by scope granularity.
- Flipping the toggle to **Excludes** rewords the label live (`Country · Excludes GB,
  FR · Between`). **This toggle is transient/UI-only** — it does **not** persist; after a
  reload the card is back to **Includes**.
- With two Terms whose scopes overlap (e.g. a `Region: EMEA` Term and a `Country: GB, FR`
  Term), a market that fits both (e.g. `GB`) resolves to the **more specific** (Country)
  Term.

**✓ Pass:** Attributes persist across reload; scope label + rank badge render; the
Includes/Excludes toggle rewords the label but is gone after reload; overlap resolves to
the most specific Term.

> **Why the operator doesn't persist:** by design, Includes/Excludes is a client-only
> display/filter toggle — it is not a `DL_*` attribute, not in the Contract geography
> EAV, and not read by the engine after reload. If the demo needs persisted
> include/exclude semantics, that's a future change (add a `DL_ScopeOperator` attribute).

---

## Stage 3 — Modeling workbench · DEEP

This is the core Round 2 surface. It lives on the **Modeling** tab of `dlmWorkspaceShell`.

### 3a — Container / props (tab switching)

**Do:** Switch tabs **Shell Creation ↔ Modeling ↔ Performance** in any order. Make a
model edit on the Modeling tab, switch away, switch back.

**Expect:** Each tab renders immediately with the correct current quote/Term (shell
drives props down; no blank or stale tab, no handshake needed). In-session model edits
**persist across tab switches**. The Performance tab shows the **static placeholder**.

**✓ Pass:** No blank/stale tabs; edits survive tab switches; Performance shows the
placeholder copy.

### 3b — Modeling grid

**Do:** On the Modeling tab, review the grid. Toggle the **Fare-Class** view. Edit the
**Discount Name** and **Alliance Permissions** cells. Locate the partner rows (**AF /
KL / VS**) and the **Prior Discount** column.

**Expect:**
- 5 **Product** rows; **Fare-Class** rows appear on toggle.
- Partner rows **AF, KL, VS** present.
- **Discount Name** and **Alliance Permissions** are editable.
- **Prior Discount** is a **read-only** column showing renewal values (from Stage 1's
  `DL_PriorDiscount__c`) — and it **persists after moving a fare to a different
  geography/Term**.

**✓ Pass:** Row counts + partner rows correct; the two editable columns save; Prior
Discount is read-only, shows renewal values, and survives a geography move.

### 3c — Rounds + animation

**Do:** Confirm there are **≥4 rounds** with a per-round **EDR**. Click **Set Current
Round** and watch Share / Gap / EDR.

**Expect:** With motion enabled, Share/Gap/EDR **animate** (count-up) to the new round's
values. Now enable **Reduce motion** (§0.4) and repeat: the values **snap** instantly
(no count-up).

**✓ Pass:** ≥4 rounds each with an EDR; values animate with motion on and snap with
Reduce motion on.

### 3d — KPI band (shell-owned)

**Do:** With a Term selected and edits made, read the KPI band above the tabs.

**Expect:** Shows **Industry Revenue, Host Revenue, Industry Passengers, Host
Passengers, FMS (weighted), Share, Gap, EDR** — both a **contract rollup** and
**per-Term**, updating **live** as the modeling child emits changes.

**✓ Pass:** All eight KPIs render; contract-rollup + per-Term both update live.

### 3e — Spend distribution guards

**Do:** Edit the spend-distribution cells inline; try to make them sum to ≠ 100%; force
a zero denominator.

**Expect:** Totals row **flags ≠ 100%**; a zero denominator shows **N/A**, never `NaN`.

**✓ Pass:** Off-100% is flagged; no `NaN` anywhere.

---

## Stage 3f — Proposal Summary + exports · DEEP

**Do:** Open **Proposal Summary** from the shell. Note the recommended Final Offer.
Download **Summary CSV** and **Detailed CSV**. Then **Print / Save as PDF**.

**Expect:**
- The **recommended Final Offer** is marked.
- **Summary CSV** — one row per Term (route/method/status + KPI columns), a Contract
  rollup row, the Projected Host Revenue line; empty cells for null KPIs.
- **Detailed CSV** — flat per-fare rows across all Terms, each projected at its own
  final-offer round; includes **Discount Name, Alliance, Prior Disc %, Final Offer
  Disc %**; **partner rows present**.
- **Print / Save as PDF** hides the Lightning shell chrome (only the proposal prints).

**✓ Pass:** Both CSVs download with the expected columns + partner rows; the print view
hides the Lightning chrome.

---

## Stage 4 — Apply Final Offer + Create Contract · THIN (functional)

**Do:** Click **Apply Final Offer**. Check the **Fares tab / Quote**. Then **Create
Contract** from the negotiation header (`dlmNegotiationContext`). Inspect the created
Contract.

**Expect:**
- Apply Final Offer **toasts an updated count**; the Fares tab + Quote reflect the
  Final-Offer discounts.
- Create Contract persists the lines as **ContractItemPrices** plus the geography
  attributes as **`DL_Contract_Item_Price_Attribute__c`** rows.

**✓ Pass:** Toast fires with a count; discounts land on the Quote; the Contract has
ContractItemPrices + `DL_Contract_Item_Price_Attribute__c` carrying geography + discount.

---

## Stage 5 — Contract redline · DEFERRED / talk-track

**Do:** Talk-track only. Optionally show a link/quick-action stub from the created
Contract into `post_clm` if present.

**✓ Pass:** N/A — narrate the redline step; nothing new to verify.

---

## Stage 6 — Performance surface · DEFERRED (placeholder only)

**Do:** Open the **Performance** tab.

**Expect:** The **static placeholder** ("performance rollups land here in a later
round…"). The **CRMA dashboards are a separate stream** and are not wired this round.

**✓ Pass:** Placeholder renders; no broken/blank dashboard region.

> **Stage-6 data seam (for the CRMA stream, not a UI check):** the created Contract /
> ContractItemPrice + `DL_Contract_Item_Price_Attribute__c` carry the geography + discount
> the CRMA read model will consume. The adapter contract is documented in the design doc.

---

## Sign-off checklist

- [ ] 0 — `dlmWorkspaceShell` added to `DLM_Term_Builder` page; page activated
- [ ] 1 — Renewal re-stamps Discount + `DL_FareCodes__c` + `DL_PriorDiscount__c`
- [ ] 2 — Geography attributes persist; scope label + rank badge; Includes/Excludes
      toggle rewords live but is transient (gone on reload); overlap → most specific
- [ ] 3a — Tab switching: no blank/stale tab; edits persist; Performance placeholder
- [ ] 3b — Grid: 5 products + fare-class toggle; AF/KL/VS; editable Discount Name +
      Alliance; Prior Discount read-only + survives geography move
- [ ] 3c — ≥4 rounds w/ EDR; animate with motion, snap with Reduce motion
- [ ] 3d — All 8 KPIs; rollup + per-Term update live
- [ ] 3e — ≠100% flagged; zero denominator → N/A not NaN
- [ ] 3f — Proposal Summary; Summary + Detailed CSV (partner rows); Print hides chrome
- [ ] 4 — Apply Final Offer toast; Quote reflects discounts; Contract persists CIP +
      `DL_Contract_Item_Price_Attribute__c`
- [ ] 5 — Redline talk-track (deferred)
- [ ] 6 — Performance placeholder (deferred)

When every non-deferred box is checked, the branch is clear to push + open the PR.

---

## Quick troubleshooting

| Symptom | Likely cause / fix |
|---------|-------------------|
| Scope attributes don't appear in the picker | The `DL_*` AttributeDefinition isn't in the org, or not in `dlmTermWorkspace.DEFAULT_ATTRIBUTE_CODES`. Re-run the `dl-termbuilder` SFDMU load; confirm `DL_ScopeType` / `DL_MarketGroup` exist. |
| Includes/Excludes toggle missing on a card | It only shows when the Term has a **Market Group** — set `DL_MarketGroup` first. |
| Toggle resets to Includes after reload | Expected — it's a transient UI toggle, not persisted. |
| Tiles don't react to each other | They sync over `DLM_TermBuilderChannel__c`; make sure all four tiles are on the **same** Lightning page and it's activated. |
| KPI band blank | No Term selected, or the shell tile isn't on the page (§0.3). |
| Fare line dropped `DL_FareCodes__c` on load | The loading user needs FLS on the field — assign `RLM_TermBuilderPermset` before the SFDMU run. |
