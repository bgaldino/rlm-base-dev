public with sharing class RLM_AmendmentRenewalService {

    // --------------------------------------------------------
    // Shared context — built once, used by both public methods
    // --------------------------------------------------------
    private class AmendmentContext {
        Quote q;
        Boolean isAmendment;
        Set<Id> productIds                              = new Set<Id>();
        Map<Id, Decimal> productCurrentAmounts          = new Map<Id, Decimal>();
        Map<Id, Decimal> productPreviousAmounts         = new Map<Id, Decimal>();
        Map<Id, Decimal> productCurrentQuantities       = new Map<Id, Decimal>();
        Map<Id, Decimal> productPreviousQuantities      = new Map<Id, Decimal>();
        Map<Id, List<Asset>> assetsByProduct            = new Map<Id, List<Asset>>();
        Decimal netNewAddsAmount                        = 0;
        Set<Id> assetIds                                = new Set<Id>();
        Map<Id, String>  assetNames                     = new Map<Id, String>();
        Map<Id, Decimal> assetCurrentAmounts            = new Map<Id, Decimal>();
        Map<Id, Decimal> assetPreviousAmounts           = new Map<Id, Decimal>(); // Asset.CurrentAmount/CurrentMrr fallback
        Map<Id, Decimal> assetPreviousQuantities        = new Map<Id, Decimal>();
        Map<Id, Integer> assetTermMonths                = new Map<Id, Integer>();
        Map<Id, Id>      assetToProduct                 = new Map<Id, Id>();
        Map<Id, AssetStatePeriod> latestPeriodsByAsset  = new Map<Id, AssetStatePeriod>();
        Map<Id, String>  assetActionTypesByAsset        = new Map<Id, String>();
    }

    // --------------------------------------------------------
    // Helper predicates
    // --------------------------------------------------------
    private static Boolean isAmendmentOrRenewal(String actionType) {
        if (actionType == null) return false;
        String n = actionType.trim();
        return n == 'Amendment' || n == 'Amend' || n == 'Renewal' || n == 'Renew';
    }

    private static Boolean isAmendment(String actionType) {
        if (actionType == null) return false;
        String n = actionType.trim();
        return n == 'Amendment' || n == 'Amend';
    }

    private static Integer toMonths(Integer term, String unit) {
        if (term == null || unit == null) return 12;
        if (unit == 'Month' || unit == 'Months') return term;
        if (unit == 'Year'  || unit == 'Years')  return term * 12;
        if (unit == 'Day'   || unit == 'Days')   return Integer.valueOf(Math.ceil(term / 30.0));
        return term; // unknown unit — treat as months
    }

    // --------------------------------------------------------
    // Context builder — all SOQL lives here, called once per request
    // --------------------------------------------------------
    @TestVisible
    private static AmendmentContext buildContext(Id quoteId) {
        AmendmentContext ctx = new AmendmentContext();
        ctx.q = RLM_AmendmentRenewalRepository.getQuote(quoteId);
        ctx.isAmendment = isAmendment(ctx.q.RLM_OriginalActionType__c);

        if (!isAmendmentOrRenewal(ctx.q.RLM_OriginalActionType__c)) return ctx;

        List<QuoteLineItem> qlis =
            RLM_AmendmentRenewalRepository.getQuoteLineItemsWithAssets(quoteId);
        if (qlis.isEmpty()) return ctx;

        // --------------------------------------------------
        // QLI pass — product-level aggregates
        // --------------------------------------------------
        Map<Id, Integer> productTerms     = new Map<Id, Integer>();
        Map<Id, String>  productTermUnits = new Map<Id, String>();

        for (QuoteLineItem qli : qlis) {
            if (qli.Product2Id == null) continue;
            Id pid = qli.Product2Id;
            ctx.productIds.add(pid);

            // Current amount
            Decimal amt = qli.TotalPrice != null ? qli.TotalPrice : 0;
            ctx.productCurrentAmounts.put(pid,
                (ctx.productCurrentAmounts.containsKey(pid) ? ctx.productCurrentAmounts.get(pid) : 0) + amt);

            // Current quantity: EndQuantity > StartQty+Qty > Qty
            Decimal qty = 0;
            if      (qli.EndQuantity   != null)                          qty = qli.EndQuantity;
            else if (qli.StartQuantity != null && qli.Quantity != null)  qty = qli.StartQuantity + qli.Quantity;
            else if (qli.Quantity      != null)                          qty = qli.Quantity;
            ctx.productCurrentQuantities.put(pid,
                (ctx.productCurrentQuantities.containsKey(pid) ? ctx.productCurrentQuantities.get(pid) : 0) + qty);

            // Previous amount from RLM_PreviousAmount__c (populated by RLM_PopulatePreviousAmount flow)
            if (qli.RLM_PreviousAmount__c != null && qli.RLM_PreviousAmount__c != 0) {
                ctx.productPreviousAmounts.put(pid,
                    (ctx.productPreviousAmounts.containsKey(pid) ? ctx.productPreviousAmounts.get(pid) : 0)
                    + qli.RLM_PreviousAmount__c);
            }

            // Subscription term — first non-null wins per product
            if (!productTerms.containsKey(pid) && qli.SubscriptionTerm != null)
                productTerms.put(pid, Integer.valueOf(qli.SubscriptionTerm));
            if (!productTermUnits.containsKey(pid) && qli.SubscriptionTermUnit != null)
                productTermUnits.put(pid, qli.SubscriptionTermUnit);
        }

        if (ctx.productIds.isEmpty()) return ctx;

        // --------------------------------------------------
        // Account resolution
        // --------------------------------------------------
        Id accountId = ctx.q.AccountId;
        if (accountId == null)
            accountId = RLM_AmendmentRenewalRepository.getAccountIdFromAssets(ctx.productIds);
        ctx.assetsByProduct =
            RLM_AmendmentRenewalRepository.getAssetsByProduct(ctx.productIds, accountId);

        // --------------------------------------------------
        // Net-new adds — products with no matching assets
        // --------------------------------------------------
        Set<Id> productsWithAssets = new Set<Id>();
        for (Id pid : ctx.assetsByProduct.keySet()) {
            List<Asset> assets = ctx.assetsByProduct.get(pid);
            if (assets != null && !assets.isEmpty()) productsWithAssets.add(pid);
        }
        for (Id pid : ctx.productIds) {
            if (!productsWithAssets.contains(pid) && ctx.productCurrentAmounts.containsKey(pid))
                ctx.netNewAddsAmount += ctx.productCurrentAmounts.get(pid);
        }

        // --------------------------------------------------
        // Asset pass — distribute product amounts to asset level
        // --------------------------------------------------
        for (Id pid : ctx.productIds) {
            List<Asset> assets = ctx.assetsByProduct.get(pid);
            if (assets == null || assets.isEmpty()) continue;

            Integer termMonths = toMonths(productTerms.get(pid), productTermUnits.get(pid));
            Integer assetCount = assets.size();

            // Seed product previous quantity from Asset.CurrentQuantity (may be refined by ASP later)
            Decimal prevProductQty = 0;
            for (Asset a : assets)
                prevProductQty += (a.CurrentQuantity != null ? a.CurrentQuantity : 0);
            ctx.productPreviousQuantities.put(pid, prevProductQty);

            Decimal productAmt = ctx.productCurrentAmounts.get(pid);

            for (Asset a : assets) {
                ctx.assetIds.add(a.Id);
                ctx.assetNames.put(a.Id, a.Name != null ? a.Name : '');
                ctx.assetTermMonths.put(a.Id, termMonths);
                ctx.assetToProduct.put(a.Id, pid);

                // Previous quantity seed — may be overridden by AssetStatePeriod
                ctx.assetPreviousQuantities.put(a.Id, a.CurrentQuantity != null ? a.CurrentQuantity : 0);

                // Asset fallback amount: CurrentAmount or CurrentMrr × term
                Decimal fallback = 0;
                if      (a.CurrentAmount != null && a.CurrentAmount != 0) fallback = a.CurrentAmount;
                else if (a.CurrentMrr    != null && a.CurrentMrr    != 0) fallback = a.CurrentMrr * termMonths;
                ctx.assetPreviousAmounts.put(a.Id, fallback);

                // Equal distribution of current amount across assets for this product
                ctx.assetCurrentAmounts.put(a.Id, productAmt / assetCount);
            }
        }

        if (ctx.assetIds.isEmpty()) return ctx;

        // --------------------------------------------------
        // AssetStatePeriods — latest period per asset
        // Prioritize active (EndDate = null), then most recently ended
        // --------------------------------------------------
        List<AssetStatePeriod> statePeriods =
            RLM_AmendmentRenewalRepository.getAssetStatePeriods(ctx.assetIds);

        for (AssetStatePeriod asp : statePeriods) {
            if (!ctx.latestPeriodsByAsset.containsKey(asp.AssetId)) {
                ctx.latestPeriodsByAsset.put(asp.AssetId, asp);
                if (asp.Quantity != null) ctx.assetPreviousQuantities.put(asp.AssetId, asp.Quantity);
            } else {
                AssetStatePeriod existing = ctx.latestPeriodsByAsset.get(asp.AssetId);
                Boolean replaceWithActive = (asp.EndDate == null && existing.EndDate != null);
                Boolean replaceWithNewer  = (asp.EndDate != null && existing.EndDate != null
                                             && asp.EndDate > existing.EndDate);
                if (replaceWithActive || replaceWithNewer) {
                    ctx.latestPeriodsByAsset.put(asp.AssetId, asp);
                    if (asp.Quantity != null) ctx.assetPreviousQuantities.put(asp.AssetId, asp.Quantity);
                }
            }
        }

        // Recompute product-level previous quantities after ASP quantity overrides
        Map<Id, Decimal> recalcPrevQty = new Map<Id, Decimal>();
        for (Id aid : ctx.assetIds) {
            Id pid = ctx.assetToProduct.get(aid);
            if (pid != null && ctx.assetPreviousQuantities.containsKey(aid)) {
                recalcPrevQty.put(pid,
                    (recalcPrevQty.containsKey(pid) ? recalcPrevQty.get(pid) : 0)
                    + ctx.assetPreviousQuantities.get(aid));
            }
        }
        ctx.productPreviousQuantities.putAll(recalcPrevQty);

        // --------------------------------------------------
        // AssetActions — capture latest action type per asset
        // --------------------------------------------------
        List<AssetAction> actions =
            RLM_AmendmentRenewalRepository.getAssetActions(ctx.assetIds, quoteId);
        for (AssetAction aa : actions) {
            if (!ctx.assetActionTypesByAsset.containsKey(aa.AssetId))
                ctx.assetActionTypesByAsset.put(aa.AssetId, aa.Type != null ? aa.Type : '');
        }

        return ctx;
    }

    // --------------------------------------------------------
    // Resolve previous amount — 3-priority fallback + renewal normalization
    // --------------------------------------------------------
    private static Decimal resolvePreviousAmount(
            Id assetId, AmendmentContext ctx,
            Decimal currentAmount, String originalActionType) {

        Decimal previousAmount = 0;
        Boolean hasPriority1   = false;
        Boolean hasPriority2   = false;

        Id productId = ctx.assetToProduct.get(assetId);

        // Priority 1: RLM_PreviousAmount__c on QLI — most authoritative, set before quote saves
        if (productId != null && ctx.productPreviousAmounts.containsKey(productId)) {
            Integer assetCount = (ctx.assetsByProduct.get(productId) != null)
                ? ctx.assetsByProduct.get(productId).size() : 1;
            previousAmount = ctx.productPreviousAmounts.get(productId) / assetCount;
            hasPriority1 = true;
        }

        // Priority 2: AssetStatePeriod.Amount normalized to the quote's subscription term
        if (!hasPriority1 && ctx.latestPeriodsByAsset.containsKey(assetId)) {
            AssetStatePeriod asp = ctx.latestPeriodsByAsset.get(assetId);
            if (asp.Amount != null && asp.Amount != 0) {
                Integer quoteTermMonths =
                    ctx.assetTermMonths.containsKey(assetId) ? ctx.assetTermMonths.get(assetId) : 12;
                Integer periodMonths = 12;
                if (asp.StartDate != null && asp.EndDate != null) {
                    Date sd = asp.StartDate.date();
                    Date ed = asp.EndDate.date();
                    Integer md = sd.monthsBetween(ed);
                    Integer dd = sd.daysBetween(ed);
                    periodMonths = (md > 0)
                        ? (dd > md * 30 ? md + 1 : md)
                        : Integer.valueOf(Math.max(1, Math.ceil(dd / 30.0)));
                } else if (asp.StartDate != null) { // EndDate == null → active period
                    periodMonths = quoteTermMonths;
                }
                previousAmount = (periodMonths > 0 && periodMonths != quoteTermMonths)
                    ? (asp.Amount / periodMonths) * quoteTermMonths
                    : asp.Amount;
                hasPriority2 = true;
            }
        }

        // Priority 3: Asset.CurrentAmount or CurrentMrr (already term-adjusted during context build)
        if (!hasPriority1 && !hasPriority2 && ctx.assetPreviousAmounts.containsKey(assetId))
            previousAmount = ctx.assetPreviousAmounts.get(assetId);

        // Renewal normalization — only when priority 1 (authoritative QLI field) wasn't available
        if (!hasPriority1 && (originalActionType == 'Renewal' || originalActionType == 'Renew')) {
            if (previousAmount == 0 && currentAmount > 0) {
                previousAmount = currentAmount;
            } else if (previousAmount > 0 && currentAmount > 0) {
                Decimal pct = Math.abs((currentAmount - previousAmount) / previousAmount) * 100;
                if (pct > 10) previousAmount = currentAmount; // likely term mismatch — treat as no change
            }
        }

        return previousAmount;
    }

    // --------------------------------------------------------
    // Classify an asset: 'No Change', 'Expansion', or 'Attrition'
    // --------------------------------------------------------
    private static String resolveChangeType(
            Id assetId, Decimal currentAmount, Decimal previousAmount, AmendmentContext ctx) {

        Id productId = ctx.assetToProduct.get(assetId);

        // Quantity-change detection (amendment quotes only)
        Boolean quantityChanged   = false;
        Decimal quantityChangeDir = 0;
        if (ctx.isAmendment && productId != null) {
            Decimal curQty  = ctx.productCurrentQuantities.containsKey(productId)
                ? ctx.productCurrentQuantities.get(productId) : 0;
            Decimal prevQty = ctx.productPreviousQuantities.containsKey(productId)
                ? ctx.productPreviousQuantities.get(productId) : 0;
            if (curQty > 0.01) {
                Decimal diff    = curQty - prevQty;
                quantityChanged = Math.abs(diff) > 0.01;
                if (quantityChanged) quantityChangeDir = diff;
            }
        }

        // Change amount: amendments mirror currentAmount; renewals use the net difference
        Decimal changeAmount = ctx.isAmendment ? currentAmount : (currentAmount - previousAmount);

        if (Math.abs(changeAmount)      < 0.01) return 'No Change';
        if (ctx.isAmendment && !quantityChanged) return 'No Change';
        if (ctx.isAmendment)  return quantityChangeDir > 0 ? 'Expansion' : 'Attrition';
        return changeAmount > 0 ? 'Expansion' : 'Attrition';
    }

    // --------------------------------------------------------
    // Public API
    // --------------------------------------------------------

    public static RLM_AmendmentRenewalDTO getAmendmentRenewalSummary(Id quoteId) {
        AmendmentContext ctx = buildContext(quoteId);
        Quote q = ctx.q;

        RLM_AmendmentRenewalDTO empty = new RLM_AmendmentRenewalDTO(
            q.Subtotal != null ? q.Subtotal : 0,
            q.RLM_TotalDiscountAmount__c != null ? q.RLM_TotalDiscountAmount__c : 0,
            q.TotalPrice != null ? q.TotalPrice : 0,
            q.RLM_OriginalActionType__c, 0, 0, 0, 0, 0);

        if (!isAmendmentOrRenewal(q.RLM_OriginalActionType__c) || ctx.assetIds.isEmpty())
            return empty;

        Decimal renewalAmount = 0, expansionAmount = 0, attritionAmount = 0;

        for (Id assetId : ctx.assetIds) {
            Decimal currentAmount  = ctx.assetCurrentAmounts.containsKey(assetId)
                ? ctx.assetCurrentAmounts.get(assetId) : 0;
            Decimal previousAmount = resolvePreviousAmount(
                assetId, ctx, currentAmount, q.RLM_OriginalActionType__c);
            String  changeType     = resolveChangeType(assetId, currentAmount, previousAmount, ctx);

            if      (changeType == 'No Change')  renewalAmount   += currentAmount;
            else if (changeType == 'Expansion')  expansionAmount +=
                ctx.isAmendment ? currentAmount : (currentAmount - previousAmount);
            else if (changeType == 'Attrition')  attritionAmount +=
                ctx.isAmendment ? currentAmount : Math.abs(currentAmount - previousAmount);
        }

        Decimal netChange = expansionAmount - attritionAmount + ctx.netNewAddsAmount;

        return new RLM_AmendmentRenewalDTO(
            q.Subtotal != null ? q.Subtotal : 0,
            q.RLM_TotalDiscountAmount__c != null ? q.RLM_TotalDiscountAmount__c : 0,
            q.TotalPrice != null ? q.TotalPrice : 0,
            q.RLM_OriginalActionType__c,
            renewalAmount, expansionAmount, attritionAmount, ctx.netNewAddsAmount, netChange);
    }

    public static List<RLM_ExpansionAttritionDTO> getExpansionAttritionDetails(Id quoteId) {
        AmendmentContext ctx = buildContext(quoteId);
        Quote q = ctx.q;

        if (!isAmendmentOrRenewal(q.RLM_OriginalActionType__c) || ctx.assetIds.isEmpty())
            return new List<RLM_ExpansionAttritionDTO>();

        List<RLM_ExpansionAttritionDTO> results = new List<RLM_ExpansionAttritionDTO>();

        for (Id assetId : ctx.assetIds) {
            Decimal currentAmount  = ctx.assetCurrentAmounts.containsKey(assetId)
                ? ctx.assetCurrentAmounts.get(assetId) : 0;
            Decimal previousAmount = resolvePreviousAmount(
                assetId, ctx, currentAmount, q.RLM_OriginalActionType__c);
            String  changeType     = resolveChangeType(assetId, currentAmount, previousAmount, ctx);

            Decimal displayChangeAmount;
            if      (changeType == 'No Change') displayChangeAmount = 0;
            else if (ctx.isAmendment)           displayChangeAmount = currentAmount;
            else                                displayChangeAmount = currentAmount - previousAmount;

            results.add(new RLM_ExpansionAttritionDTO(
                assetId,
                ctx.assetNames.containsKey(assetId) ? ctx.assetNames.get(assetId) : '',
                previousAmount,
                currentAmount,
                displayChangeAmount,
                changeType,
                ctx.assetActionTypesByAsset.containsKey(assetId)
                    ? ctx.assetActionTypesByAsset.get(assetId) : ''));
        }

        return results;
    }
}
