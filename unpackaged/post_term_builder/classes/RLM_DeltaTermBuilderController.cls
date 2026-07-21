/**
 * Apex controller for the Delta "Term Builder" demo app (dlTermBuilder / dlTermCard /
 * dlAddFareClass LWCs). A rep starts a route-based **Term** (a DL-TERM bundle) under an Account,
 * sets its route attributes, then adds fare-class products (Delta One, Comfort, Main, …) under the
 * Term and discounts each.
 *
 * Self-contained: this feature owns its own copies of the catalog/line/PST/service helpers
 * (RLM_Delta*), so nothing here depends on post_large_stx or post_contracted_pricing_ui. Only
 * platform/managed globals (RevSalesTrxn, the configurator namespaces) are shared.
 *
 * House conventions (mirror the sibling RLM_Delta* controllers):
 *   - @AuraEnabled(cacheable=false) static String method(String inputJson) returning
 *     JSON.serialize(Map<String,Object>); parse the input JSON once inside a try.
 *   - Id.valueOf(...) guarded in try/catch; WITH USER_MODE reads; `as user` / PST DML.
 *   - No SOQL/DML in loops; aggregate/bulk queries keyed by the quote's distinct ids.
 *
 * Writes (Quote create, fare add) go through Place Sales Transaction
 * (RevSalesTrxn.PlaceSalesTransactionExecutor.execute via RLM_DeltaPlaceSalesTransaction) so the
 * pricing procedure runs — a direct insert QuoteLineItem does not. The fare tree is committed with
 * configuration SKIP (persist-verbatim): the platform-derived bundle fields ParentQuoteLineItemId /
 * QuoteLineRelationship.QuoteId are therefore NOT stamped (config FORCE would, but is structurally
 * blocked for component-only fares — see FARE_ADD_FORCE_CONFIGURATION). The Term↔fare link is carried
 * by QuoteLineRelationship.RootQuoteLineId, which is what the builder-state grouping reads.
 */
public with sharing class RLM_DeltaTermBuilderController {
    public class TermBuilderException extends Exception {}

    // Stable demo codes — resolved to org ids at runtime so no Salesforce ids leak into metadata.
    @TestVisible private static final String TERM_SKU = 'DL-TERM';
    @TestVisible private static final String FARE_CLASSIFICATION_CODE = 'PC-DL-FARE';
    @TestVisible private static final String CATALOG_CODE = 'DL-CONTRACTS';
    @TestVisible private static final String CATEGORY_CODE = 'DL-TERMS';

    // Demo safety cap: at most 20 fare children per Term (matches the ProductComponentGroup Max).
    @TestVisible private static final Integer MAX_FARES_PER_TERM = 20;

    // Demo safety cap: at most 10 Terms added in a single "Add Term" bar action.
    @TestVisible private static final Integer MAX_TERMS_PER_ADD = 10;

    // Commit mode for the fare-add path (see commitFareGraph). ONE-LINE TOGGLE:
    //   FALSE = configuration SKIP (commitConfigured). Persists the hand-built Term→fare tree verbatim
    //           WITHOUT platform derivation — the working behavior. The Term↔fare link lives on
    //           QuoteLineRelationship.RootQuoteLineId (which the app's own grouping reads); the
    //           platform-derived QuoteLineRelationship.QuoteId and QuoteLineItem.ParentQuoteLineItemId
    //           (both createable=False) stay null, so they don't populate the standard bundle-parent
    //           related lists/reports.
    //   TRUE  = configuration FORCE (commitWithExpansion). Would let the platform's configuration step
    //           (Bundle Expansion, internal W-17627343) stamp those derived fields — BUT it is
    //           NON-FUNCTIONAL for the fares as modeled, and this is a structural platform constraint,
    //           not a duplicate-line risk. Config FORCE resolves EVERY product in the graph through the
    //           ProductDiscovery Service / Decision Table, which only returns catalog-published
    //           products (ProductCategoryProduct). The fares carry IsSoldOnlyWithOtherProds=true
    //           (component-only), and the platform REFUSES to publish such a product to a category
    //           ("Sell only with other products … can't be assigned to the category").
    //   Live-verified on Delta 2026-07-16 (all reverted afterward):
    //     - FORCE commits fail with "Could not find product … from ProductDiscovery Service"; each
    //       failed commit rolled back ATOMICALLY — no duplicate lines (the DL-TERM bundle has no
    //       default included components; a catalog-published DL-TERM added under FORCE expanded to
    //       zero extra lines, confirming the no-dupe expectation).
    //     - Even after flipping IsSoldOnlyWithOtherProds=false, publishing a fare to the Terms
    //       category, refreshing the RLM_ProductQualification / RLM_ProductCategoryQualification
    //       decision tables, AND a full catalog index rebuild, the fare still did not resolve —
    //       so this path is not viable for component-only fares without deeper catalog modeling.
    //     - validateProductCatalog=false does NOT bypass the gate ("Product details not found …
    //       refresh the Decision Table").
    //   Kept as a documented, one-line switch for if/when the fares are modeled as standalone
    //   catalog-sellable products (which would also make them appear in product-search/add flows).
    @TestVisible private static Boolean FARE_ADD_FORCE_CONFIGURATION = false;

    // Selling-model → BillingFrequency (mirrors RLM_DeltaCatalogController). Term and fare products
    // default to Term Annual in the demo dataset; keep OneTime/Evergreen mapped too in case a
    // product's selling model changes.
    private static final Map<String, String> PRICING_TERM_TO_BILLING_FREQUENCY = new Map<String, String>{
        'Months' => 'Monthly', 'Annual' => 'Annual', 'Quarterly' => 'Quarterly', 'Semi-Annual' => 'Semi-Annual'
    };

    // ---------- Account & Quote workflow (header) ----------

    /**
     * Create a negotiation Quote for an Account via Place Sales Transaction on the Standard Price
     * Book. Input: { accountId, quoteName?, billToContactId? }. The name defaults to
     * "<Account Name> – Delta Negotiation – <yyyy-MM-dd>" when blank. Stamps the Account as
     * QuoteAccountId.
     *
     * ORDER-READINESS SEED. Also seeds the Bill To contact + Bill To / Ship To addresses so a
     * contracted negotiation flows straight through to order activation: the standard "Create Orders
     * From Quote" path (RLM_CreateOrdersFromQuote) gates order creation on the Quote having
     * BillToContactId AND Bill To/Ship To street+city+country populated. We mirror the standard
     * RLM_QuickQuote flow — Bill To/Ship To addresses copied from the Account, and the Bill To
     * contact resolved from an explicit billToContactId (UI override) or the account's oldest Contact.
     * Blank source data simply leaves a field unset; the readiness gate then flags it, which is the
     * correct signal (not a silent skip). All seeded fields are standard Quote fields and ride in the
     * same header POST as QuoteAccountId.
     *
     * Returns { isSuccess, quoteId, quoteName, accountId, billToContactId, errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String createNegotiation(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id accountId = parseId(asString(in0.get('accountId')), 'accountId');

            // Load the account (WITH USER_MODE = access guard) for the default name / existence and
            // the Bill To / Ship To address seed.
            List<Account> accts = [
                SELECT Id, Name,
                       BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry,
                       ShippingStreet, ShippingCity, ShippingState, ShippingPostalCode, ShippingCountry
                FROM Account WHERE Id = :accountId WITH USER_MODE LIMIT 1
            ];
            if (accts.isEmpty()) {
                throw new TermBuilderException('Account not found or not accessible.');
            }
            Account acct = accts[0];
            String accountName = String.isNotBlank(acct.Name) ? acct.Name : 'Account';

            String quoteName = asString(in0.get('quoteName'));
            if (String.isBlank(quoteName)) {
                quoteName = accountName + ' – Delta Negotiation – ' + String.valueOf(Date.today());
            }
            quoteName = quoteName.trim();
            if (quoteName.length() > 80) {
                quoteName = quoteName.substring(0, 80);
            }

            // Resolve the Bill To contact: an explicit billToContactId (UI override) wins; otherwise
            // fall back to the account's oldest Contact (RLM_QuickQuote's rule).
            Contact billToContact = resolveBillToContact(accountId, optionalId(in0.get('billToContactId')));

            Id pbId = RLM_DeltaCatalogService.resolveStandardPricebook2Id();

            // Header-only PST graph. commitConfigured = pricing FORCE + configuration SKIP; there are
            // no lines to price/expand, so SKIP config is correct and pricing FORCE is a no-op.
            Map<String, Object> headerFields = new Map<String, Object>{
                'Name' => quoteName,
                'Pricebook2Id' => pbId,
                'QuoteAccountId' => accountId,
                'Status' => 'Draft'
            };
            // Seed order-readiness fields — only put a key when we have a value (see method comment).
            Id billToContactId = (billToContact != null) ? billToContact.Id : null;
            putSeedField(headerFields, 'BillToContactId', billToContactId);
            putSeedField(headerFields, 'ContactId', billToContactId);
            putSeedField(headerFields, 'Email', (billToContact != null) ? billToContact.Email : null);
            putSeedField(headerFields, 'Phone', (billToContact != null) ? billToContact.Phone : null);
            putSeedField(headerFields, 'BillingStreet', acct.BillingStreet);
            putSeedField(headerFields, 'BillingCity', acct.BillingCity);
            putSeedField(headerFields, 'BillingState', acct.BillingState);
            putSeedField(headerFields, 'BillingPostalCode', acct.BillingPostalCode);
            putSeedField(headerFields, 'BillingCountry', acct.BillingCountry);
            putSeedField(headerFields, 'ShippingStreet', acct.ShippingStreet);
            putSeedField(headerFields, 'ShippingCity', acct.ShippingCity);
            putSeedField(headerFields, 'ShippingState', acct.ShippingState);
            putSeedField(headerFields, 'ShippingPostalCode', acct.ShippingPostalCode);
            putSeedField(headerFields, 'ShippingCountry', acct.ShippingCountry);

            List<RevSalesTrxn.RecordWithReferenceRequest> records = new List<RevSalesTrxn.RecordWithReferenceRequest>{
                RLM_DeltaPlaceSalesTransaction.post('refHeader', Quote.getSObjectType(), headerFields)
            };
            RLM_DeltaPlaceSalesTransaction.Result res =
                RLM_DeltaPlaceSalesTransaction.commitConfigured('DeltaTermBuilderCreate', records);
            if (!res.isSuccess) {
                return errorResult(res.errorMessage);
            }
            Id quoteId = (res.response != null) ? (Id) res.response.salesTransactionId : null;
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'quoteId' => quoteId,
                'quoteName' => quoteName,
                'accountId' => accountId,
                'billToContactId' => billToContactId,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Resolve the Bill To contact for a new negotiation. An explicit billToContactId (from the UI)
     * wins when it exists and is accessible; otherwise fall back to the account's oldest Contact,
     * which is what the standard RLM_QuickQuote flow seeds. Returns null when the account has no
     * contact — the order-readiness gate then flags the missing Bill To (the correct signal, not a
     * silent skip). Email / Phone are read for the header seed (RLM_QuickQuote copies them too).
     */
    private static Contact resolveBillToContact(Id accountId, Id explicitContactId) {
        if (explicitContactId != null) {
            List<Contact> chosen = [
                SELECT Id, Email, Phone FROM Contact WHERE Id = :explicitContactId WITH USER_MODE LIMIT 1
            ];
            if (chosen.isEmpty()) {
                throw new TermBuilderException('The selected Bill To contact was not found or is not accessible.');
            }
            return chosen[0];
        }
        List<Contact> firsts = [
            SELECT Id, Email, Phone FROM Contact
            WHERE AccountId = :accountId WITH USER_MODE ORDER BY CreatedDate ASC, Id ASC LIMIT 1
        ];
        return firsts.isEmpty() ? null : firsts[0];
    }

    /** Put a seed field on the header map only when the value is non-blank (skip null/empty). */
    private static void putSeedField(Map<String, Object> fields, String key, Object value) {
        if (value != null && String.isNotBlank(String.valueOf(value))) {
            fields.put(key, value);
        }
    }

    // Suffix appended to a source negotiation's name when it's renewed. The 80-char Quote.Name cap
    // (see buildRenewalName) truncates the base, never this suffix.
    @TestVisible private static final String RENEWAL_NAME_SUFFIX = ' - Renewal';

    /**
     * Create a Renewal negotiation from a Contract by deep-cloning the Contract's source Quote (the
     * standard Contract.SourceQuoteId that the create-contract flows stamp). The clone carries the
     * full quote graph — Terms, fares, lines, DL_FareCodes__c, negotiation dates — verbatim; the rep
     * adjusts dates in Term Builder afterward. The clone is renamed "&lt;source name&gt; - Renewal" and
     * reset to Draft (Term Builder doesn't persist an in-app header rename, so stamping Name here is
     * what makes the renewal name stick). Input: { contractId }. Returns
     * { isSuccess, renewalQuoteId, renewalName, accountId, errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String createRenewalFromContract(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id contractId = parseId(asString(in0.get('contractId')), 'contractId');

            List<Contract> contracts = [
                SELECT Id, SourceQuoteId FROM Contract WHERE Id = :contractId WITH USER_MODE LIMIT 1
            ];
            if (contracts.isEmpty()) {
                throw new TermBuilderException('Contract not found or not accessible.');
            }
            Id sourceQuoteId = contracts[0].SourceQuoteId;
            if (sourceQuoteId == null) {
                throw new TermBuilderException('This contract has no source quote to renew from.');
            }

            // Load the source quote for its name + account (existence/access guard). The account
            // scopes the post-clone id-diff that identifies the quote the clone mints.
            List<Quote> sources = [
                SELECT Id, Name, QuoteNumber, AccountId, QuoteAccountId
                FROM Quote WHERE Id = :sourceQuoteId WITH USER_MODE LIMIT 1
            ];
            if (sources.isEmpty()) {
                throw new TermBuilderException('Source quote not found or not accessible.');
            }
            Quote source = sources[0];
            Id scopeAccountId = (source.QuoteAccountId != null) ? source.QuoteAccountId : source.AccountId;
            String sourceName = String.isNotBlank(source.Name)
                ? source.Name
                : (String.isNotBlank(source.QuoteNumber) ? source.QuoteNumber : 'Negotiation');
            String renewalName = buildRenewalName(sourceName);

            // Full-graph deep clone via the standard Deep Clone Sales Transaction core action, run
            // in-transaction through the DL_DeepCloneSalesTransaction flow (no HTTP callout).
            Id renewalQuoteId = deepCloneSalesTransaction(sourceQuoteId, scopeAccountId);

            // The deep clone drops two fidelity-sensitive line fields — DL_FareCodes__c (never mapped
            // in the context definition) and Discount (mapped, but repriced to 0 on the Draft clone).
            // Re-stamp both from the source quote's own lines before we hand the renewal to the rep.
            restoreClonedLineFidelity(sourceQuoteId, renewalQuoteId);

            // Stamp the renewal name + reset to Draft on the clone, and null ContractId so the renewal
            // is a fresh negotiation (the clone inherits the source's ContractId, which would make Term
            // Builder treat it as already contracted). Name is copied verbatim by the clone; overwrite
            // it. Read the account back for an optional client deep-link.
            Quote renewal = loadQuote(renewalQuoteId);
            update as user new Quote(
                Id = renewalQuoteId, Name = renewalName, Status = 'Draft', ContractId = null
            );
            Id accountId = (renewal.QuoteAccountId != null) ? renewal.QuoteAccountId : renewal.AccountId;

            // The clone + fidelity restore + rename above all ran through direct DML, so the renewal
            // quote carries a TransactionIncomplete stamp. Reprice once through PST to hand the rep a
            // validated renewal (best-effort; the renewal is already fully built).
            RLM_DeltaPlaceSalesTransaction.revalidate(renewalQuoteId);

            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'renewalQuoteId' => renewalQuoteId,
                'renewalName' => renewalName,
                'accountId' => accountId,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Create a Renewal negotiation from a Contract via the STANDARD asset-based renewal — the
     * initiateRenewal core action against the Contract's activated Assets — rather than deep-cloning
     * the source Quote. This is the idiomatic renewal path: the platform builds the renewal Quote's
     * full line structure and asset linkage from the Contract's Assets + Asset Contract Relationships.
     *
     * initiateRenewal does the bulk of the work, but (confirmed live on a fully-assetized contract) it
     * does NOT re-derive the negotiated per-fare discount — the renewal lines come back Discount=0 and
     * DL_FareCodes__c=null. So we layer on the same thin, structural-match re-stamp the deep-clone path
     * uses (restoreClonedLineFidelity), sourcing Discount + DL_FareCodes__c from the Contract's source
     * quote lines. The renewal is renamed "&lt;source name&gt; - Renewal", reset to Draft, and its
     * ContractId nulled so Term Builder treats it as a fresh negotiation. Input:
     * { contractId, renewStartDate?, renewEndDate? }. Returns
     * { isSuccess, renewalQuoteId, renewalName, accountId, errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String createRenewalFromContractViaAssets(String inputJson) {
        try {
            // Thin flow-launcher (ARC pattern): the DL_InitiateRenewalFromContract flow now OWNS the
            // orchestration — ResolveInputs (contract/quote/asset resolution + date derivation) → standard
            // initiateRenewal → FinalizeRenewal (line re-stamp, rename/Draft/EndDate, reprice). This Apex
            // only parses the request, runs the flow synchronously in-transaction, and shapes the response.
            Map<String, Object> in0 = parseInput(inputJson);
            Id contractId = parseId(asString(in0.get('contractId')), 'contractId');
            Date renewStartDate = asDate(in0.get('renewStartDate')); // optional; null → derive
            Date renewEndDate = asDate(in0.get('renewEndDate'));     // optional; null → derive

            Flow.Interview interview = Flow.Interview.createInterview(
                RENEW_FLOW,
                new Map<String, Object>{
                    'renewContractId' => String.valueOf(contractId),
                    'renewStartDate' => renewStartDate,
                    'renewEndDate' => renewEndDate
                }
            );
            interview.start();

            // The flow surfaces validation + fault errors through the errorMessage output (an
            // Assignment-populated plain variable, which round-trips through getVariableValue reliably —
            // unlike a manually-bound core-action output). Any non-blank value means the renewal failed.
            String flowError = String.valueOf(interview.getVariableValue('errorMessage'));
            if (String.isNotBlank(flowError) && flowError != 'null') {
                return errorResult(flowError);
            }

            String renewalQuoteId = String.valueOf(interview.getVariableValue('newQuoteId'));
            if (String.isBlank(renewalQuoteId) || renewalQuoteId == 'null') {
                return errorResult('Initiate renewal did not produce a new quote.');
            }
            String accountId = String.valueOf(interview.getVariableValue('accountId'));

            // The flow stamps the "<source> - Renewal" name on the quote; read it back for the response
            // (toast subtitle) rather than adding a third flow output.
            String renewalName = loadQuote((Id) renewalQuoteId).Name;

            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'renewalQuoteId' => renewalQuoteId,
                'renewalName' => renewalName,
                'accountId' => (String.isNotBlank(accountId) && accountId != 'null') ? accountId : null,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Append RENEWAL_NAME_SUFFIX to a source name, capped at the 80-char Quote.Name limit. When the
     * combined length exceeds 80 the BASE is truncated so the suffix always survives (mirrors the
     * 80-char handling in createNegotiation).
     */
    public static String buildRenewalName(String sourceName) {
        String base = String.isBlank(sourceName) ? 'Negotiation' : sourceName.trim();
        Integer maxBase = 80 - RENEWAL_NAME_SUFFIX.length();
        if (base.length() > maxBase) {
            base = base.substring(0, maxBase);
        }
        return base + RENEWAL_NAME_SUFFIX;
    }

    // Autolaunched flow that wraps the standard Deep Clone Sales Transaction core action. The action
    // is registered in Flow Builder's core-action registry but NOT the REST /actions/standard
    // registry, so Invocable.Action.createStandardAction('deepCloneSalesTransaction') fails — the flow
    // is the callout-free path to run it in-transaction from Apex.
    @TestVisible private static final String DEEP_CLONE_FLOW = 'DL_DeepCloneSalesTransaction';

    /**
     * Deep-clone a Quote (full object graph: lines, groups, bundle configs, mapped custom fields) by
     * running the DL_DeepCloneSalesTransaction flow synchronously in this transaction, and return the
     * new Quote id.
     *
     * The flow's newRecordId output binds null back through Flow.Interview.getVariableValue (the core
     * action's output-parameter name differs from the MDAPI binding), so we don't trust it. Instead we
     * snapshot the account's quote ids before the clone and diff after: the clone mints exactly one new
     * quote under the same account, which is deterministic for this single-source, in-transaction call.
     */
    private static Id deepCloneSalesTransaction(Id sourceQuoteId, Id scopeAccountId) {
        Set<Id> before = quoteIdsForAccount(scopeAccountId);

        Flow.Interview interview = Flow.Interview.createInterview(
            DEEP_CLONE_FLOW,
            new Map<String, Object>{ 'sourceQuoteId' => String.valueOf(sourceQuoteId) }
        );
        interview.start();

        String flowError = String.valueOf(interview.getVariableValue('errorMessage'));
        if (String.isNotBlank(flowError) && flowError != 'null') {
            throw new TermBuilderException('Deep clone failed: ' + flowError);
        }

        // Identify the minted quote by set difference (account-scoped; exactly one expected).
        List<Id> added = new List<Id>();
        for (Id qId : quoteIdsForAccount(scopeAccountId)) {
            if (!before.contains(qId)) {
                added.add(qId);
            }
        }
        if (added.isEmpty()) {
            throw new TermBuilderException('Deep clone did not produce a new quote.');
        }
        if (added.size() > 1) {
            throw new TermBuilderException('Deep clone produced multiple new quotes; cannot identify the renewal.');
        }
        return added[0];
    }

    // Autolaunched flow that wraps the standard Initiate Renewal core action (renewOutputType=Quote).
    // Like deepCloneSalesTransaction, initiateRenewal is in Flow Builder's core-action registry but NOT
    // the REST /actions/standard registry, so the flow is the callout-free path to run it in-transaction.
    @TestVisible private static final String RENEW_FLOW = 'DL_InitiateRenewalFromContract';

    /**
     * The Contract's TOP-LEVEL ("parent") renewable Asset ids, resolved from AssetContractRelationship.
     * initiateRenewal expands each parent's child assets automatically, so ONLY the top-level parents
     * are passed — passing the children too would double them in the renewal.
     *
     * "Top-level" is determined structurally by Asset.ParentId: the standard O2A path stamps each fare
     * asset's ParentId to its Term asset, leaving the Term (parent) assets with a null ParentId. So the
     * null-parent assets are the parents (live-confirmed on the assetized Delta contract: the two
     * DL-TERM assets have ParentId=null; the three fares point at their Term). If NO contract asset is
     * parented (nesting not modeled via Asset.ParentId), fall back to the Term SKU (DL-TERM) as the
     * parent discriminator. Returned as List&lt;String&gt; for the flow's text-collection input.
     */
    public static List<String> topLevelParentAssetIds(Id contractId) {
        List<String> nullParentAssetIds = new List<String>();
        List<String> termSkuAssetIds = new List<String>();
        Boolean anyParented = false;
        for (AssetContractRelationship acr : [
            SELECT AssetId, Asset.ParentId, Asset.Product2.ProductCode, Asset.Product2.StockKeepingUnit
            FROM AssetContractRelationship
            WHERE ContractId = :contractId AND AssetId != null
            WITH USER_MODE
        ]) {
            if (acr.Asset.ParentId != null) {
                anyParented = true; // a child asset nested under a parent
            } else {
                nullParentAssetIds.add(String.valueOf(acr.AssetId));
            }
            String code = acr.Asset.Product2.ProductCode;
            String sku = acr.Asset.Product2.StockKeepingUnit;
            if (TERM_SKU.equals(code) || TERM_SKU.equals(sku)) {
                termSkuAssetIds.add(String.valueOf(acr.AssetId));
            }
        }
        // When any asset is parented, Asset.ParentId is the reliable nesting signal → the null-parent
        // set is the top-level parents. Otherwise fall back to the Term SKU.
        return anyParented ? nullParentAssetIds : termSkuAssetIds;
    }

    /** The renewal term window passed to initiateRenewal (start/end are the action's own inputs).
     *  Public so the flow-invocable RLM_DeltaRenewalInputsResolver can read the derived window. */
    public class RenewalWindow {
        public Date startDate;
        public Date endDate;
    }

    /**
     * Derive the renewal term window. Given null dates, the standard initiateRenewal mis-derives the
     * term — a 12-MONTH source asset produced a 12-YEAR renewal on this org (start 2027-07-21, end
     * 2039-07-20). So we compute explicit dates and pass them as the action's own renewStartDate/
     * renewEndDate inputs (no post-creation date surgery):
     *   - start = the day after the prior asset term ends (mirrors what the platform derives for start),
     *             anchored on the GMT date of Asset.LifecycleEndDate (an end-of-day GMT datetime).
     *   - end   = start + the Contract's renewal term (RenewalTerm2 / RenewalTermUnit), minus one day
     *             so the term end is inclusive (a 12-month renewal from 2027-07-21 ends 2028-07-20).
     * A caller-supplied date always wins; if the assets carry no lifecycle end we leave the date null
     * and defer to the platform default rather than guessing.
     */
    public static RenewalWindow deriveRenewalWindow(
        List<String> assetIds, Contract contract, Date requestedStart, Date requestedEnd
    ) {
        RenewalWindow w = new RenewalWindow();
        w.startDate = requestedStart;
        w.endDate = requestedEnd;
        if (w.startDate != null && w.endDate != null) {
            return w; // both supplied by the caller — nothing to derive
        }

        Set<Id> ids = new Set<Id>();
        for (String s : assetIds) {
            if (String.isNotBlank(s)) {
                ids.add((Id) s);
            }
        }

        Date priorEnd = null;
        for (Asset a : [
            SELECT LifecycleEndDate FROM Asset WHERE Id IN :ids WITH USER_MODE
        ]) {
            if (a.LifecycleEndDate != null) {
                Date e = a.LifecycleEndDate.dateGmt();
                if (priorEnd == null || e > priorEnd) {
                    priorEnd = e;
                }
            }
        }

        if (w.startDate == null) {
            if (priorEnd == null) {
                return w; // no prior term to anchor the start → defer to the platform default
            }
            w.startDate = priorEnd.addDays(1);
        }
        if (w.endDate == null) {
            // Run for the Contract's declared renewal term; the end day is inclusive, hence -1 day.
            w.endDate = w.startDate.addMonths(renewalTermMonths(contract)).addDays(-1);
        }
        return w;
    }

    /**
     * The Contract's renewal term expressed in months, from RenewalTerm2 + RenewalTermUnit. Defaults
     * to a one-year (12-month) renewal when the term is unset. RenewalTermUnit is a picklist of
     * Months / Quarterly / Semi-Annual / Annual.
     */
    public static Integer renewalTermMonths(Contract contract) {
        if (contract == null || contract.RenewalTerm2 == null || contract.RenewalTerm2 <= 0) {
            return 12; // default to a one-year renewal
        }
        String unit = String.isNotBlank(contract.RenewalTermUnit) ? contract.RenewalTermUnit : 'Months';
        Integer multiplier;
        switch on unit {
            when 'Annual' { multiplier = 12; }
            when 'Semi-Annual' { multiplier = 6; }
            when 'Quarterly' { multiplier = 3; }
            when else { multiplier = 1; } // Months
        }
        return (Integer) (contract.RenewalTerm2 * multiplier);
    }

    /** Quote ids under an account (either AccountId or the builder's QuoteAccountId) — the pre/post
     *  snapshot scope for the deep-clone id-diff. */
    public static Set<Id> quoteIdsForAccount(Id accountId) {
        Set<Id> ids = new Set<Id>();
        for (Quote q : [
            SELECT Id FROM Quote
            WHERE AccountId = :accountId OR QuoteAccountId = :accountId
            WITH USER_MODE
        ]) {
            ids.add(q.Id);
        }
        return ids;
    }

    /**
     * Re-stamp the fidelity-sensitive line fields the deep clone drops. The clone hydrates + persists
     * through the SalesTransaction context definition: DL_FareCodes__c has no mapping (so it never
     * carries over), and Discount, though mapped hydrate+persist, is repriced to 0 on the Draft clone.
     * The source quote's own lines are the faithful 1:1 record of both (the clone is a copy OF them),
     * so we copy DL_FareCodes__c and Discount back onto the matching clone lines. We also snapshot the
     * source line's Discount into DL_PriorDiscount__c (frozen, read-only) so Term Builder can display
     * the previous contract's discount for comparison against the renewal's new, editable Discount.
     *
     * Matching (STRUCTURAL, not positional) — the clone renumbers AND reorders lines and carries no
     * source-line pointer (all three QLI self-refs come back null), so LineNumber/order can't key. But
     * two things DO survive the clone verbatim: the Term's route name (CustomProductName) and the
     * QuoteLineRelationship Term↔fare grouping. So each line keys on its STRUCTURAL identity:
     *   - a Term root  → "T|<route>"                (route = the Term's CustomProductName)
     *   - a fare/child → "F|<parentRoute>|<Product2Id>|<fareName>"  (parent Term resolved via
     *                     ParentQuoteLineItemId, else QuoteLineRelationship.RootQuoteLineId — the same
     *                     grouping fallback getNegotiation uses; fareName = the fare's CustomProductName,
     *                     which is auto-derived from its selected fare codes)
     * This is exact even with the same fare class (same Product2Id) under different routes, AND with the
     * same fare class TWICE under ONE Term when the two carry different fare codes (their auto-derived
     * names differ, e.g. "Comfort (J C)" vs "Comfort (J C I)"). The only residual ambiguity is two lines
     * that are genuinely interchangeable — same product, same route, same name/codes — which collide
     * into one key bucket and fall back to positional pairing within that (small) bucket; since those
     * lines are identical for the two restored fields, the pairing is immaterial.
     */
    public static void restoreClonedLineFidelity(Id sourceQuoteId, Id renewalQuoteId) {
        Map<String, List<QuoteLineItem>> sourceByKey = fidelityKeyMap(sourceQuoteId);
        Map<String, List<QuoteLineItem>> cloneByKey = fidelityKeyMap(renewalQuoteId);

        List<QuoteLineItem> updates = new List<QuoteLineItem>();
        for (String key : cloneByKey.keySet()) {
            List<QuoteLineItem> clonePeers = cloneByKey.get(key);
            List<QuoteLineItem> srcPeers = sourceByKey.get(key);
            if (srcPeers == null) {
                continue; // clone-only structure (shouldn't happen for a faithful clone) — leave as-is
            }
            // Pair within the key bucket by index; unique keys have one element each (exact match),
            // collisions degrade to positional within the bucket.
            Integer pairs = Math.min(clonePeers.size(), srcPeers.size());
            for (Integer i = 0; i < pairs; i++) {
                QuoteLineItem cl = clonePeers[i];
                QuoteLineItem src = srcPeers[i];

                // Build a fresh shell carrying only Id + the two fields we write. `update as user`
                // enforces field updateability on EVERY populated field, so we must not carry the
                // non-updateable Product2Id/CustomProductName we queried for matching into the DML.
                Boolean changed = false;
                QuoteLineItem patch = new QuoteLineItem(Id = cl.Id);
                if (cl.DL_FareCodes__c != src.DL_FareCodes__c) {
                    patch.DL_FareCodes__c = src.DL_FareCodes__c;
                    changed = true;
                }
                if (cl.Discount != src.Discount) {
                    patch.Discount = src.Discount;
                    changed = true;
                }
                // Snapshot the source line's negotiated discount as the frozen "prior" value so Term
                // Builder can show it read-only alongside the rep's live, editable Discount. Written once
                // here (idempotent: re-running the restore leaves it unchanged), never re-priced — it must
                // NOT drift when the rep edits Discount downstream.
                if (cl.DL_PriorDiscount__c != src.Discount) {
                    patch.DL_PriorDiscount__c = src.Discount;
                    changed = true;
                }
                if (changed) {
                    updates.add(patch);
                }
            }
        }
        if (!updates.isEmpty()) {
            update as user updates;
        }
    }

    /**
     * Bucket a quote's lines by their structural fidelity key (see restoreClonedLineFidelity). Term
     * roots key on their route (CustomProductName); fares key on their parent Term's route + Product2Id.
     * Lists preserve LineNumber order so same-key collisions pair deterministically within the bucket.
     */
    public static Map<String, List<QuoteLineItem>> fidelityKeyMap(Id quoteId) {
        List<QuoteLineItem> lines = [
            SELECT Id, Product2Id, Product2.ProductCode, Product2.StockKeepingUnit,
                   CustomProductName, ParentQuoteLineItemId, Discount, DL_FareCodes__c,
                   DL_PriorDiscount__c
            FROM QuoteLineItem WHERE QuoteId = :quoteId WITH USER_MODE ORDER BY LineNumber
        ];

        // Identify Term roots and their route names.
        Set<Id> termIds = new Set<Id>();
        Map<Id, String> routeByTerm = new Map<Id, String>();
        for (QuoteLineItem l : lines) {
            if (isTermSku(l)) {
                termIds.add(l.Id);
                routeByTerm.put(l.Id, l.CustomProductName == null ? '' : l.CustomProductName);
            }
        }

        // child→root fallback via QuoteLineRelationship (when ParentQuoteLineItemId isn't stamped —
        // the fare-add path commits config SKIP, so the link lives on RootQuoteLineId).
        Map<Id, Id> rootByChild = new Map<Id, Id>();
        if (!termIds.isEmpty()) {
            for (QuoteLineRelationship r : [
                SELECT AssociatedQuoteLineId, RootQuoteLineId
                FROM QuoteLineRelationship
                WHERE RootQuoteLineId IN :termIds AND AssociatedQuoteLineId != null
                WITH USER_MODE
            ]) {
                if (r.AssociatedQuoteLineId != null && r.RootQuoteLineId != null) {
                    rootByChild.put(r.AssociatedQuoteLineId, r.RootQuoteLineId);
                }
            }
        }

        Map<String, List<QuoteLineItem>> byKey = new Map<String, List<QuoteLineItem>>();
        for (QuoteLineItem l : lines) {
            String key;
            if (termIds.contains(l.Id)) {
                key = 'T|' + routeByTerm.get(l.Id);
            } else {
                Id parentTerm = (l.ParentQuoteLineItemId != null && termIds.contains(l.ParentQuoteLineItemId))
                    ? l.ParentQuoteLineItemId
                    : rootByChild.get(l.Id);
                String route = (parentTerm != null && routeByTerm.containsKey(parentTerm))
                    ? routeByTerm.get(parentTerm)
                    : '';
                // Include the fare's CustomProductName in the key: a fare line's name is auto-derived
                // from its selected fare codes (buildFareDisplayName → e.g. "Comfort (J C)"), and the
                // clone carries CustomProductName verbatim even though it drops DL_FareCodes__c. So the
                // name distinguishes two same-product fares under one Term that carry DIFFERENT codes
                // (the only case that mispairs) — giving each an exact 1:1 match instead of colliding
                // into one bucket paired positionally by LineNumber (which the clone reorders). When
                // names are absent or identical the lines are genuinely interchangeable, so the key
                // degrades to the prior product-only behavior with no data loss.
                String fareName = (l.CustomProductName == null) ? '' : l.CustomProductName;
                key = 'F|' + route + '|' + l.Product2Id + '|' + fareName;
            }
            if (!byKey.containsKey(key)) {
                byKey.put(key, new List<QuoteLineItem>());
            }
            byKey.get(key).add(l);
        }
        return byKey;
    }

    /**
     * Quotes for an Account (for the existing-Quote selector). Input: { accountId }. Matches on
     * either AccountId or QuoteAccountId (a builder quote stamps the latter). Returns
     * { isSuccess, quotes:[{ id, name, quoteNumber, status, lastModified }], errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String getNegotiationsForAccount(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id accountId = parseId(asString(in0.get('accountId')), 'accountId');

            List<Map<String, Object>> quotes = new List<Map<String, Object>>();
            for (Quote q : [
                SELECT Id, Name, QuoteNumber, Status, LastModifiedDate
                FROM Quote
                WHERE AccountId = :accountId OR QuoteAccountId = :accountId
                WITH USER_MODE
                ORDER BY LastModifiedDate DESC
                LIMIT 50
            ]) {
                quotes.add(new Map<String, Object>{
                    'id' => q.Id,
                    'name' => String.isNotBlank(q.Name) ? q.Name : q.QuoteNumber,
                    'quoteNumber' => q.QuoteNumber,
                    'status' => String.valueOf(q.Status),
                    'lastModified' => String.valueOf(q.LastModifiedDate)
                });
            }
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'quotes' => quotes,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Set the negotiation's header-level default Start/End Date (DL_NegotiationStartDate__c /
     * DL_NegotiationEndDate__c). These seed new Term/fare lines as they're added (see
     * buildTermLineFields / buildFareLineFields) — changing them does NOT rewrite dates already on
     * existing lines. Input: { quoteId, negotiationStartDate?, negotiationEndDate? } (ISO date
     * strings; blank/absent clears that field). Plain field update, not a PST commit — these fields
     * aren't priced/derived. Returns { isSuccess, errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String updateNegotiationDates(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');
            loadQuote(qId); // access + existence

            Date startDate = asDate(in0.get('negotiationStartDate'));
            Date endDate = asDate(in0.get('negotiationEndDate'));
            if (startDate != null && endDate != null && endDate < startDate) {
                throw new TermBuilderException('Negotiation end date must be on or after the start date.');
            }

            update as user new Quote(
                Id = qId,
                DL_NegotiationStartDate__c = startDate,
                DL_NegotiationEndDate__c = endDate
            );

            // Header-field edits go through direct DML like every other mutation here; reprice so the
            // quote stays validated (best-effort; safe on an empty quote — createNegotiation does the
            // same header-only PST commit on a brand-new quote).
            RLM_DeltaPlaceSalesTransaction.revalidate(qId);

            return JSON.serialize(new Map<String, Object>{ 'isSuccess' => true, 'errorMessage' => null });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Add one or more route-based Terms (DL-TERM bundles) to the quote via Place Sales Transaction.
     * Input: { quoteId, count? }. The Term product is resolved server-side by its stable SKU
     * (DL-TERM) — never client-supplied, so the rail's "Add Term" bar needs no catalog/search. `count`
     * (default 1, floored at 1, capped at MAX_TERMS_PER_ADD) emits that many independent Quantity-1
     * Term lines. Returns { isSuccess, addedCount, errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String addTerm(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');
            Quote q = loadQuote(qId);
            Id pbId = (q.Pricebook2Id != null) ? q.Pricebook2Id : RLM_DeltaCatalogService.resolveStandardPricebook2Id();

            Integer count = resolveTermCount(in0.get('count'));

            // Resolve the DL-TERM product + its active PBE on the quote's book (server authority).
            List<Product2> termProducts = [
                SELECT Id FROM Product2
                WHERE (ProductCode = :TERM_SKU OR StockKeepingUnit = :TERM_SKU) AND IsActive = true
                WITH USER_MODE
                LIMIT 1
            ];
            if (termProducts.isEmpty()) {
                throw new TermBuilderException('The Term product (' + TERM_SKU + ') is not available.');
            }
            List<PricebookEntry> pbes = RLM_DeltaCatalogService.queryPBEsByProductIds(new Set<Id>{ termProducts[0].Id }, pbId);
            if (pbes.isEmpty()) {
                throw new TermBuilderException('No active price book entry for the Term product on this quote\'s price book.');
            }
            PricebookEntry pbe = pbes[0];

            // PST graph: Quote PATCH header + one QLI POST per requested instance (each an independent Term).
            String quoteIdRef = String.valueOf(qId);
            List<RevSalesTrxn.RecordWithReferenceRequest> records = new List<RevSalesTrxn.RecordWithReferenceRequest>();
            records.add(RLM_DeltaPlaceSalesTransaction.patch('refHeader', Quote.getSObjectType(), qId, new Map<String, Object>()));
            for (Integer i = 0; i < count; i++) {
                records.add(RLM_DeltaPlaceSalesTransaction.post(
                    'refTerm' + i, QuoteLineItem.getSObjectType(),
                    buildTermLineFields(pbe, quoteIdRef, q.DL_NegotiationStartDate__c, q.DL_NegotiationEndDate__c)
                ));
            }
            RLM_DeltaPlaceSalesTransaction.Result res =
                RLM_DeltaPlaceSalesTransaction.commitConfigured('DeltaTermBuilderAddTerm', records);
            if (!res.isSuccess) {
                return errorResult(res.errorMessage);
            }
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true, 'addedCount' => count, 'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    // ---------- Builder-state API (single bulk round trip) ----------

    /**
     * The whole Terms-rail state for a quote in one round trip. Input is a plain quoteId String.
     * Returns quote info (including the header-level negotiationStartDate/negotiationEndDate
     * defaults — see updateNegotiationDates); the DL-TERM root lines (name, dates, discount,
     * route-attribute values); the fare-line count + child fares per Term; the default/selected
     * Term; and the DL-CONTRACTS / DL-TERMS catalog+category ids (resolved by code so the finder
     * can scope without hardcoding ids).
     *
     * Works on an empty quote too (zero terms), so the app can call it right after createNegotiation
     * to obtain the catalog/category refs before the first Term is added.
     */
    @AuraEnabled(cacheable=false)
    public static String getBuilderState(String quoteId) {
        try {
            Id qId = parseId(quoteId, 'quoteId');
            Quote q = loadQuote(qId);

            // All lines in one query. ProductCode identifies Term roots; ParentQuoteLineItemId +
            // QuoteLineRelationship link fares to their Term.
            List<QuoteLineItem> allLines = [
                SELECT Id, ParentQuoteLineItemId, CustomProductName, Discount, StartDate, EndDate,
                       NetUnitPrice, UnitPrice, Quantity, Product2Id, Product2.Name,
                       Product2.ProductCode, Product2.StockKeepingUnit, Product2.BasedOnId,
                       DL_FareCodes__c
                FROM QuoteLineItem
                WHERE QuoteId = :qId
                WITH USER_MODE
                ORDER BY CreatedDate, Id
            ];

            // Partition into Term roots (by SKU) and everything else (candidate fares).
            List<QuoteLineItem> termLines = new List<QuoteLineItem>();
            List<QuoteLineItem> otherLines = new List<QuoteLineItem>();
            Set<Id> termIds = new Set<Id>();
            for (QuoteLineItem qli : allLines) {
                if (isTermSku(qli)) {
                    termLines.add(qli);
                    termIds.add(qli.Id);
                } else {
                    otherLines.add(qli);
                }
            }

            // Fallback child→root map from QuoteLineRelationship (in case the platform hasn't stamped
            // ParentQuoteLineItemId, or a child links to the Term only via the relationship root).
            Map<Id, Id> rootByChild = new Map<Id, Id>();
            if (!termIds.isEmpty()) {
                for (QuoteLineRelationship r : [
                    SELECT AssociatedQuoteLineId, RootQuoteLineId, MainQuoteLineId
                    FROM QuoteLineRelationship
                    WHERE RootQuoteLineId IN :termIds AND AssociatedQuoteLineId != null
                    WITH USER_MODE
                ]) {
                    if (r.AssociatedQuoteLineId != null && r.RootQuoteLineId != null) {
                        rootByChild.put(r.AssociatedQuoteLineId, r.RootQuoteLineId);
                    }
                }
            }

            // Group fares under their Term (ParentQuoteLineItemId first, then relationship root).
            Map<Id, List<Map<String, Object>>> faresByTerm = new Map<Id, List<Map<String, Object>>>();
            for (Id tId : termIds) {
                faresByTerm.put(tId, new List<Map<String, Object>>());
            }
            for (QuoteLineItem qli : otherLines) {
                Id parentId = (qli.ParentQuoteLineItemId != null && termIds.contains(qli.ParentQuoteLineItemId))
                    ? qli.ParentQuoteLineItemId
                    : rootByChild.get(qli.Id);
                if (parentId != null && faresByTerm.containsKey(parentId)) {
                    faresByTerm.get(parentId).add(fareDto(qli));
                }
            }

            // Bulk-load the route-attribute values on all Term lines (one attr query + one def query +
            // one picklist-value query), keyed back to each Term.
            Map<Id, List<Map<String, Object>>> attrsByTerm = loadTermAttributes(termIds);

            List<Map<String, Object>> terms = new List<Map<String, Object>>();
            for (QuoteLineItem qli : termLines) {
                List<Map<String, Object>> fares = faresByTerm.get(qli.Id);
                terms.add(new Map<String, Object>{
                    'id' => qli.Id,
                    'customProductName' => qli.CustomProductName,
                    'productName' => (qli.Product2 != null) ? qli.Product2.Name : null,
                    'displayName' => String.isNotBlank(qli.CustomProductName)
                        ? qli.CustomProductName
                        : ((qli.Product2 != null) ? qli.Product2.Name : null),
                    'discount' => qli.Discount,
                    'startDate' => (qli.StartDate != null) ? String.valueOf(qli.StartDate) : null,
                    'endDate' => (qli.EndDate != null) ? String.valueOf(qli.EndDate) : null,
                    'netUnitPrice' => qli.NetUnitPrice,
                    'attributes' => (attrsByTerm.containsKey(qli.Id)) ? attrsByTerm.get(qli.Id) : new List<Map<String, Object>>(),
                    'fareCount' => (fares != null) ? fares.size() : 0,
                    'fares' => (fares != null) ? fares : new List<Map<String, Object>>()
                });
            }

            // Default/selected Term = the first one (client tracks selection thereafter).
            Id selectedTermId = termLines.isEmpty() ? null : termLines[0].Id;

            // Catalog/category refs (resolved by stable code, not stored ids).
            Map<String, Object> catalogRefs = resolveTermCatalogRefs();

            // Existing-contract link: a Quote already related to a Contract (ContractId) cannot be
            // contracted again (the standard createContract action rejects it). Surface the contract
            // so the header offers "View Contract" instead of a doomed "Create Contract".
            Map<String, Object> contract = resolveExistingContract(q.ContractId);

            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'quote' => new Map<String, Object>{
                    'id' => q.Id,
                    'name' => q.Name,
                    'accountId' => q.QuoteAccountId != null ? q.QuoteAccountId : q.AccountId,
                    'accountName' => (q.QuoteAccount != null) ? q.QuoteAccount.Name
                                     : ((q.Account != null) ? q.Account.Name : null),
                    'pricebook2Id' => q.Pricebook2Id,
                    'currencyCode' => readCurrency(q),
                    'negotiationStartDate' => (q.DL_NegotiationStartDate__c != null) ? String.valueOf(q.DL_NegotiationStartDate__c) : null,
                    'negotiationEndDate' => (q.DL_NegotiationEndDate__c != null) ? String.valueOf(q.DL_NegotiationEndDate__c) : null
                },
                'terms' => terms,
                'selectedTermId' => selectedTermId,
                'catalogId' => catalogRefs.get('catalogId'),
                'categoryId' => catalogRefs.get('categoryId'),
                'termSku' => TERM_SKU,
                'contractId' => contract.get('contractId'),
                'contractNumber' => contract.get('contractNumber'),
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    // ---------- Adding fare classes ----------

    /**
     * The fare-class products (classification PC-DL-FARE) with a resolved active PricebookEntry on
     * the quote's price book. Input: { quoteId }. Only products with a resolvable PBE are returned.
     * Returns { isSuccess, fares:[{ productId, productName, productCode, pbeId, unitPrice,
     * productSellingModelId }], errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String getFareChoices(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');
            Quote q = loadQuote(qId);
            Id pbId = (q.Pricebook2Id != null) ? q.Pricebook2Id : RLM_DeltaCatalogService.resolveStandardPricebook2Id();

            Id fareClassId = resolveClassificationId(FARE_CLASSIFICATION_CODE);
            List<Map<String, Object>> fares = new List<Map<String, Object>>();
            if (fareClassId != null) {
                // Fare products (BasedOn the PC-DL-FARE classification), then their active PBEs on
                // this book — resolved in bulk (one product query, one PBE query).
                Map<Id, Product2> fareProducts = new Map<Id, Product2>([
                    SELECT Id, Name, ProductCode, DL_DefaultFareCodes__c
                    FROM Product2
                    WHERE BasedOnId = :fareClassId AND IsActive = true
                    WITH USER_MODE
                    ORDER BY Name
                ]);
                if (!fareProducts.isEmpty()) {
                    Map<Id, PricebookEntry> pbeByProduct = new Map<Id, PricebookEntry>();
                    for (PricebookEntry pe : RLM_DeltaCatalogService.queryPBEsByProductIds(fareProducts.keySet(), pbId)) {
                        PricebookEntry existing = pbeByProduct.get(pe.Product2Id);
                        if (existing == null || sellingModelRank(pe) < sellingModelRank(existing)) {
                            pbeByProduct.put(pe.Product2Id, pe);
                        }
                    }
                    for (Product2 p : fareProducts.values()) {
                        PricebookEntry pbe = pbeByProduct.get(p.Id);
                        if (pbe == null) {
                            continue; // no active PBE on this book → not addable
                        }
                        fares.add(new Map<String, Object>{
                            'productId' => p.Id,
                            'productName' => p.Name,
                            'productCode' => p.ProductCode,
                            'fareCodes' => fareCodeList(p.DL_DefaultFareCodes__c),
                            'pbeId' => pbe.Id,
                            'unitPrice' => pbe.UnitPrice,
                            'productSellingModelId' => pbe.ProductSellingModelId
                        });
                    }
                }
            }
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'fares' => fares,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Add a fare-class product as a Quantity-1 child of a Term via Place Sales Transaction. Input:
     * { quoteId, termLineId, pbeId?, productId?, quantity? }.
     *
     * Server validation (fail-closed, all before any PST commit):
     *   - quoteId / termLineId / pbeId valid ids; Term belongs to the quote; Term product IS DL-TERM;
     *   - the resolved PBE belongs to the quote's price book and is active;
     *   - the fare product's classification IS PC-DL-FARE (claimed productId, if sent, must match);
     *   - the Term is under its 20-child cap.
     * The dynamic ProductRelatedComponent (DL-TERM ↔ PC-DL-FARE) is resolved server-side (never
     * client-supplied) and stamped on the QuoteLineRelationship when found.
     *
     * Builds: PATCH Quote header + POST fare QuoteLineItem + POST QuoteLineRelationship (Main/Root =
     * the persisted Term's real id, Associated = the new fare's graph token). Committed via
     * commitFareGraph, whose mode is set by FARE_ADD_FORCE_CONFIGURATION (config SKIP by default —
     * persist-verbatim; config FORCE would stamp the createable=False derived fields
     * QuoteLineRelationship.QuoteId / QuoteLineItem.ParentQuoteLineItemId but is structurally blocked
     * for component-only fares, see that constant). Duplicate fares are allowed: each call is an
     * independent Quantity-1 line, no de-dup.
     *
     * Returns { isSuccess, addedLineId, errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String addFareClassToTerm(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');
            Id termLineId = parseId(asString(in0.get('termLineId')), 'termLineId');
            Quote q = loadQuote(qId); // access + existence + negotiation default dates

            // Term must belong to the quote AND be a DL-TERM product (server authority).
            List<QuoteLineItem> terms = [
                SELECT Id, Product2.ProductCode, Product2.StockKeepingUnit
                FROM QuoteLineItem
                WHERE Id = :termLineId AND QuoteId = :qId
                WITH USER_MODE
                LIMIT 1
            ];
            if (terms.isEmpty()) {
                throw new TermBuilderException('The Term line does not belong to this quote.');
            }
            if (!isTermSku(terms[0])) {
                throw new TermBuilderException('The selected line is not a Term (' + TERM_SKU + ').');
            }

            // Cap: at most MAX_FARES_PER_TERM children (count line instances under this Term).
            Integer existingFares = countFaresUnderTerm(qId, termLineId);
            if (existingFares >= MAX_FARES_PER_TERM) {
                throw new TermBuilderException('This Term already has the maximum of ' + MAX_FARES_PER_TERM + ' fare classes.');
            }

            // Resolve + revalidate the PBE against the quote's book (tamper guard).
            Id pbId = RLM_DeltaCatalogService.resolveStandardPricebook2Id();
            List<Quote> qb = [SELECT Pricebook2Id FROM Quote WHERE Id = :qId WITH USER_MODE LIMIT 1];
            if (!qb.isEmpty() && qb[0].Pricebook2Id != null) {
                pbId = qb[0].Pricebook2Id;
            }

            PricebookEntry pbe = resolveFarePbe(in0, pbId);

            // The fare product's classification must be PC-DL-FARE.
            Id fareClassId = resolveClassificationId(FARE_CLASSIFICATION_CODE);
            List<Product2> prods = [
                SELECT Id, BasedOnId, DL_DefaultFareCodes__c FROM Product2 WHERE Id = :pbe.Product2Id WITH USER_MODE LIMIT 1
            ];
            if (prods.isEmpty() || fareClassId == null || prods[0].BasedOnId != fareClassId) {
                throw new TermBuilderException('The selected product is not a fare class (' + FARE_CLASSIFICATION_CODE + ').');
            }

            // Resolve the canonical dynamic component (DL-TERM ↔ PC-DL-FARE) server-side.
            ProductRelatedComponent prc = resolveDynamicFareComponent(fareClassId);

            // Build the PST graph: Quote PATCH header, fare QLI POST, relationship POST.
            Decimal qty = asDecimal(in0.get('quantity'));
            String quoteIdRef = String.valueOf(qId);
            List<RevSalesTrxn.RecordWithReferenceRequest> records = new List<RevSalesTrxn.RecordWithReferenceRequest>();
            records.add(RLM_DeltaPlaceSalesTransaction.patch('refHeader', Quote.getSObjectType(), qId, new Map<String, Object>()));
            records.add(RLM_DeltaPlaceSalesTransaction.post(
                'refFare', QuoteLineItem.getSObjectType(),
                buildFareLineFields(pbe, quoteIdRef, qty, prods[0].DL_DefaultFareCodes__c, q.DL_NegotiationStartDate__c, q.DL_NegotiationEndDate__c)
            ));
            records.add(RLM_DeltaPlaceSalesTransaction.post(
                'refRel', QuoteLineRelationship.getSObjectType(),
                buildFareRelationshipFields(termLineId, 'refFare', prc)
            ));

            // Snapshot pre-existing line ids so the post-commit diff can name the added fare
            // authoritatively (the PST reference map is best-effort).
            Set<Id> preexisting = new Set<Id>();
            for (QuoteLineItem existing : [SELECT Id FROM QuoteLineItem WHERE QuoteId = :qId WITH USER_MODE]) {
                preexisting.add(existing.Id);
            }

            RLM_DeltaPlaceSalesTransaction.Result res = commitFareGraph('DeltaTermBuilderFare', records);
            if (!res.isSuccess) {
                return errorResult(res.errorMessage);
            }

            Id addedLineId = null;
            for (QuoteLineItem added : [
                SELECT Id FROM QuoteLineItem
                WHERE QuoteId = :qId AND Id NOT IN :preexisting AND Product2Id = :pbe.Product2Id
                WITH USER_MODE
                ORDER BY CreatedDate DESC, Id DESC
                LIMIT 1
            ]) {
                addedLineId = added.Id;
            }
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'addedLineId' => addedLineId,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    /**
     * Add several fare-class products under a Term in ONE Place Sales Transaction, so a rep can
     * multi-select in the Add Fare Class picker and commit them together. Input:
     * { quoteId, termLineId, fares: [{ pbeId?, productId? }, ...] }.
     *
     * Same fail-closed guards as addFareClassToTerm, applied to the whole batch before any commit
     * (so the add is atomic — no partial adds): quote access; Term belongs to the quote and IS
     * DL-TERM; each fare's PBE belongs to the quote's price book and is active; each fare product's
     * classification IS PC-DL-FARE. The 20-child cap is checked ONCE up front against the batch size
     * (existing + requested must not exceed MAX_FARES_PER_TERM). PBEs and classifications are
     * resolved in bulk (constant SOQL regardless of fare count — no queries in loops).
     *
     * Builds one Quote PATCH header + one QLI POST + one QuoteLineRelationship POST per fare (ref
     * tokens refFare{i}/refRel{i}), committed via commitFareGraph. Duplicate fares are allowed.
     * Returns { isSuccess, addedCount, addedLineIds:[...], errorMessage }.
     */
    @AuraEnabled(cacheable=false)
    public static String addFareClassesToTerm(String inputJson) {
        try {
            Map<String, Object> in0 = parseInput(inputJson);
            Id qId = parseId(asString(in0.get('quoteId')), 'quoteId');
            Id termLineId = parseId(asString(in0.get('termLineId')), 'termLineId');
            Quote q = loadQuote(qId); // access + existence + negotiation default dates

            // At least one fare entry is required.
            List<Object> fareEntries = (in0.get('fares') instanceof List<Object>)
                ? (List<Object>) in0.get('fares')
                : null;
            if (fareEntries == null || fareEntries.isEmpty()) {
                throw new TermBuilderException('Select at least one fare class to add.');
            }

            // Term must belong to the quote AND be a DL-TERM product (server authority).
            List<QuoteLineItem> terms = [
                SELECT Id, Product2.ProductCode, Product2.StockKeepingUnit
                FROM QuoteLineItem
                WHERE Id = :termLineId AND QuoteId = :qId
                WITH USER_MODE
                LIMIT 1
            ];
            if (terms.isEmpty()) {
                throw new TermBuilderException('The Term line does not belong to this quote.');
            }
            if (!isTermSku(terms[0])) {
                throw new TermBuilderException('The selected line is not a Term (' + TERM_SKU + ').');
            }

            // Cap: existing + requested must fit under MAX_FARES_PER_TERM. Checked once up front so
            // the whole batch is atomic (either every selected fare is added, or none is).
            Integer existingFares = countFaresUnderTerm(qId, termLineId);
            if (existingFares + fareEntries.size() > MAX_FARES_PER_TERM) {
                Integer remaining = MAX_FARES_PER_TERM - existingFares;
                throw new TermBuilderException(
                    remaining <= 0
                        ? 'This Term already has the maximum of ' + MAX_FARES_PER_TERM + ' fare classes.'
                        : 'This Term can take only ' + remaining + ' more fare class'
                          + (remaining == 1 ? '' : 'es') + ' (max ' + MAX_FARES_PER_TERM + ').'
                );
            }

            // Resolve + revalidate against the quote's book (tamper guard), in bulk.
            Id pbId = RLM_DeltaCatalogService.resolveStandardPricebook2Id();
            List<Quote> qb = [SELECT Pricebook2Id FROM Quote WHERE Id = :qId WITH USER_MODE LIMIT 1];
            if (!qb.isEmpty() && qb[0].Pricebook2Id != null) {
                pbId = qb[0].Pricebook2Id;
            }
            List<PricebookEntry> pbes = resolveFarePbesBulk(fareEntries, pbId);

            // Every resolved fare product's classification must be PC-DL-FARE (one bulk query).
            Id fareClassId = resolveClassificationId(FARE_CLASSIFICATION_CODE);
            Set<Id> productIds = new Set<Id>();
            for (PricebookEntry pbe : pbes) {
                productIds.add(pbe.Product2Id);
            }
            Map<Id, Product2> prodById = new Map<Id, Product2>([
                SELECT Id, BasedOnId, DL_DefaultFareCodes__c
                FROM Product2 WHERE Id IN :productIds WITH USER_MODE
            ]);
            for (PricebookEntry pbe : pbes) {
                Product2 p = prodById.get(pbe.Product2Id);
                if (p == null || fareClassId == null || p.BasedOnId != fareClassId) {
                    throw new TermBuilderException('The selected product is not a fare class (' + FARE_CLASSIFICATION_CODE + ').');
                }
            }

            // Resolve the canonical dynamic component (DL-TERM ↔ PC-DL-FARE) server-side, once.
            ProductRelatedComponent prc = resolveDynamicFareComponent(fareClassId);

            // PST graph: Quote PATCH header + one QLI POST + one relationship POST per fare.
            String quoteIdRef = String.valueOf(qId);
            List<RevSalesTrxn.RecordWithReferenceRequest> records = new List<RevSalesTrxn.RecordWithReferenceRequest>();
            records.add(RLM_DeltaPlaceSalesTransaction.patch('refHeader', Quote.getSObjectType(), qId, new Map<String, Object>()));
            for (Integer i = 0; i < pbes.size(); i++) {
                PricebookEntry pbe = pbes[i];
                String fareRef = 'refFare' + i;
                records.add(RLM_DeltaPlaceSalesTransaction.post(
                    fareRef, QuoteLineItem.getSObjectType(),
                    buildFareLineFields(pbe, quoteIdRef, null, prodById.get(pbe.Product2Id).DL_DefaultFareCodes__c,
                        q.DL_NegotiationStartDate__c, q.DL_NegotiationEndDate__c)
                ));
                records.add(RLM_DeltaPlaceSalesTransaction.post(
                    'refRel' + i, QuoteLineRelationship.getSObjectType(),
                    buildFareRelationshipFields(termLineId, fareRef, prc)
                ));
            }

            // Snapshot pre-existing line ids so the post-commit diff can name the added fares
            // authoritatively (the PST reference map is best-effort).
            Set<Id> preexisting = new Set<Id>();
            for (QuoteLineItem existing : [SELECT Id FROM QuoteLineItem WHERE QuoteId = :qId WITH USER_MODE]) {
                preexisting.add(existing.Id);
            }

            RLM_DeltaPlaceSalesTransaction.Result res = commitFareGraph('DeltaTermBuilderFares', records);
            if (!res.isSuccess) {
                return errorResult(res.errorMessage);
            }

            List<Id> addedLineIds = new List<Id>();
            for (QuoteLineItem added : [
                SELECT Id FROM QuoteLineItem
                WHERE QuoteId = :qId AND Id NOT IN :preexisting AND Product2Id IN :productIds
                WITH USER_MODE
                ORDER BY CreatedDate ASC, Id ASC
            ]) {
                addedLineIds.add(added.Id);
            }
            return JSON.serialize(new Map<String, Object>{
                'isSuccess' => true,
                'addedCount' => pbes.size(),
                'addedLineIds' => addedLineIds,
                'errorMessage' => null
            });
        } catch (Exception e) {
            return errorResult(e.getMessage());
        }
    }

    // ---------- helpers ----------

    /** A Term root is a line whose product ProductCode or StockKeepingUnit is DL-TERM. */
    private static Boolean isTermSku(QuoteLineItem qli) {
        if (qli.Product2 == null) {
            return false;
        }
        return TERM_SKU.equals(qli.Product2.ProductCode) || TERM_SKU.equals(qli.Product2.StockKeepingUnit);
    }

    /** Fare-line DTO for the rail's child list. */
    private static Map<String, Object> fareDto(QuoteLineItem qli) {
        return new Map<String, Object>{
            'id' => qli.Id,
            'productName' => (qli.Product2 != null) ? qli.Product2.Name : null,
            'productCode' => (qli.Product2 != null) ? qli.Product2.ProductCode : null,
            'fareCodes' => fareCodeList(qli.DL_FareCodes__c),
            'discount' => qli.Discount,
            'netUnitPrice' => qli.NetUnitPrice
        };
    }

    /**
     * Split a multiselect DL fare-codes string (`;`-delimited, the platform's multiselect storage
     * format) into an ordered list of codes for the client. Blank / null → empty list.
     */
    private static List<String> fareCodeList(String multiselect) {
        List<String> out = new List<String>();
        if (String.isBlank(multiselect)) {
            return out;
        }
        for (String code : multiselect.split(';')) {
            String trimmed = (code != null) ? code.trim() : '';
            if (String.isNotBlank(trimmed)) {
                out.add(trimmed);
            }
        }
        return out;
    }

    /**
     * Bulk-load the current attribute values on the given Term lines. One QuoteLineItemAttribute
     * query, one AttributeDefinition query, one AttributePicklistValue query — no SOQL in loops.
     * Returns termId → [{ code, label, dataType, value }] (picklist values resolved to their display).
     */
    private static Map<Id, List<Map<String, Object>>> loadTermAttributes(Set<Id> termIds) {
        Map<Id, List<Map<String, Object>>> byTerm = new Map<Id, List<Map<String, Object>>>();
        if (termIds == null || termIds.isEmpty()) {
            return byTerm;
        }
        List<QuoteLineItemAttribute> qlias = [
            SELECT Id, QuoteLineItemId, AttributeDefinitionId, AttributePicklistValueId, AttributeValue
            FROM QuoteLineItemAttribute
            WHERE QuoteLineItemId IN :termIds AND AttributeDefinitionId != null
            WITH USER_MODE
        ];
        if (qlias.isEmpty()) {
            return byTerm;
        }
        Set<Id> defIds = new Set<Id>();
        Set<Id> pickValueIds = new Set<Id>();
        for (QuoteLineItemAttribute a : qlias) {
            defIds.add(a.AttributeDefinitionId);
            if (a.AttributePicklistValueId != null) {
                pickValueIds.add(a.AttributePicklistValueId);
            }
        }
        Map<Id, AttributeDefinition> defById = new Map<Id, AttributeDefinition>([
            SELECT Id, Code, Label, Name, DataType FROM AttributeDefinition WHERE Id IN :defIds WITH USER_MODE
        ]);
        Map<Id, String> pickDisplayById = new Map<Id, String>();
        if (!pickValueIds.isEmpty()) {
            for (AttributePicklistValue pv : [
                SELECT Id, Value, DisplayValue FROM AttributePicklistValue WHERE Id IN :pickValueIds WITH USER_MODE
            ]) {
                pickDisplayById.put(pv.Id, String.isNotBlank(pv.DisplayValue) ? pv.DisplayValue : pv.Value);
            }
        }
        for (QuoteLineItemAttribute a : qlias) {
            AttributeDefinition d = defById.get(a.AttributeDefinitionId);
            String value = (a.AttributePicklistValueId != null && pickDisplayById.containsKey(a.AttributePicklistValueId))
                ? pickDisplayById.get(a.AttributePicklistValueId)
                : a.AttributeValue;
            if (!byTerm.containsKey(a.QuoteLineItemId)) {
                byTerm.put(a.QuoteLineItemId, new List<Map<String, Object>>());
            }
            byTerm.get(a.QuoteLineItemId).add(new Map<String, Object>{
                'code' => (d != null) ? d.Code : null,
                'label' => (d != null) ? (String.isNotBlank(d.Label) ? d.Label : d.Name) : null,
                'dataType' => (d != null) ? String.valueOf(d.DataType) : null,
                'value' => value
            });
        }
        return byTerm;
    }

    /** Count the fare children under a Term (line instances via ParentQuoteLineItemId or relationship root). */
    private static Integer countFaresUnderTerm(Id qId, Id termLineId) {
        Set<Id> childIds = new Set<Id>();
        for (QuoteLineItem qli : [
            SELECT Id FROM QuoteLineItem WHERE QuoteId = :qId AND ParentQuoteLineItemId = :termLineId WITH USER_MODE
        ]) {
            childIds.add(qli.Id);
        }
        for (QuoteLineRelationship r : [
            SELECT AssociatedQuoteLineId FROM QuoteLineRelationship
            WHERE RootQuoteLineId = :termLineId AND AssociatedQuoteLineId != null WITH USER_MODE
        ]) {
            childIds.add(r.AssociatedQuoteLineId);
        }
        childIds.remove(termLineId); // never count the Term itself
        return childIds.size();
    }

    /** Resolve a fare PBE from the request (explicit pbeId, else by productId) constrained to the book. */
    private static PricebookEntry resolveFarePbe(Map<String, Object> in0, Id pbId) {
        Id pbeId = optionalId(in0.get('pbeId'));
        Id productId = optionalId(in0.get('productId'));
        if (pbeId != null) {
            List<PricebookEntry> pbes = [
                SELECT Id, Product2Id, ProductSellingModelId, UnitPrice,
                       ProductSellingModel.SellingModelType, ProductSellingModel.PricingTermUnit
                FROM PricebookEntry
                WHERE Id = :pbeId AND Pricebook2Id = :pbId AND IsActive = true AND Product2.IsActive = true
                WITH USER_MODE
                LIMIT 1
            ];
            if (pbes.isEmpty()) {
                throw new TermBuilderException('Price book entry is not valid for this quote\'s price book.');
            }
            // Tamper guard: a claimed productId must match the PBE's product.
            if (productId != null && productId != pbes[0].Product2Id) {
                throw new TermBuilderException('Product does not match the selected price book entry.');
            }
            return pbes[0];
        }
        if (productId == null) {
            throw new TermBuilderException('A pbeId or productId is required.');
        }
        List<PricebookEntry> byProduct = RLM_DeltaCatalogService.queryPBEsByProductIds(new Set<Id>{ productId }, pbId);
        if (byProduct.isEmpty()) {
            throw new TermBuilderException('No active price book entry for the fare product on this quote\'s price book.');
        }
        PricebookEntry chosen = byProduct[0];
        for (Integer i = 1; i < byProduct.size(); i++) {
            if (sellingModelRank(byProduct[i]) < sellingModelRank(chosen)) {
                chosen = byProduct[i];
            }
        }
        return chosen;
    }

    /**
     * Resolve a PBE for each fare entry ({ pbeId?, productId? }) constrained to the book, in BULK —
     * constant SOQL regardless of fare count (one query for explicit pbeIds, one for products by id).
     * Mirrors resolveFarePbe's rules per entry: explicit pbeId wins (with the productId tamper guard),
     * else the lowest selling-model-ranked active PBE for the productId. Preserves the requested order.
     */
    private static List<PricebookEntry> resolveFarePbesBulk(List<Object> fareEntries, Id pbId) {
        // Partition entries into explicit-pbeId vs product-id lookups (validated per entry).
        List<Id> pbeIdByIndex = new List<Id>();
        List<Id> productIdByIndex = new List<Id>();
        Set<Id> pbeIds = new Set<Id>();
        Set<Id> productIds = new Set<Id>();
        for (Object o : fareEntries) {
            Map<String, Object> entry = (o instanceof Map<String, Object>)
                ? (Map<String, Object>) o
                : new Map<String, Object>();
            Id pbeId = optionalId(entry.get('pbeId'));
            Id productId = optionalId(entry.get('productId'));
            if (pbeId == null && productId == null) {
                throw new TermBuilderException('Each fare requires a pbeId or productId.');
            }
            pbeIdByIndex.add(pbeId);
            productIdByIndex.add(productId);
            if (pbeId != null) {
                pbeIds.add(pbeId);
            } else {
                productIds.add(productId);
            }
        }

        // One query for all explicit PBEs on the book.
        Map<Id, PricebookEntry> pbeById = new Map<Id, PricebookEntry>();
        if (!pbeIds.isEmpty()) {
            for (PricebookEntry pe : [
                SELECT Id, Product2Id, ProductSellingModelId, UnitPrice,
                       ProductSellingModel.SellingModelType, ProductSellingModel.PricingTermUnit
                FROM PricebookEntry
                WHERE Id IN :pbeIds AND Pricebook2Id = :pbId AND IsActive = true AND Product2.IsActive = true
                WITH USER_MODE
            ]) {
                pbeById.put(pe.Id, pe);
            }
        }

        // One query for all product-id lookups on the book; keep the lowest-ranked PBE per product.
        Map<Id, PricebookEntry> pbeByProduct = new Map<Id, PricebookEntry>();
        if (!productIds.isEmpty()) {
            for (PricebookEntry pe : RLM_DeltaCatalogService.queryPBEsByProductIds(productIds, pbId)) {
                PricebookEntry existing = pbeByProduct.get(pe.Product2Id);
                if (existing == null || sellingModelRank(pe) < sellingModelRank(existing)) {
                    pbeByProduct.put(pe.Product2Id, pe);
                }
            }
        }

        // Reassemble in request order, applying the same guards resolveFarePbe uses per entry.
        List<PricebookEntry> out = new List<PricebookEntry>();
        for (Integer i = 0; i < fareEntries.size(); i++) {
            Id pbeId = pbeIdByIndex[i];
            Id productId = productIdByIndex[i];
            if (pbeId != null) {
                PricebookEntry pe = pbeById.get(pbeId);
                if (pe == null) {
                    throw new TermBuilderException('Price book entry is not valid for this quote\'s price book.');
                }
                if (productId != null && productId != pe.Product2Id) {
                    throw new TermBuilderException('Product does not match the selected price book entry.');
                }
                out.add(pe);
            } else {
                PricebookEntry pe = pbeByProduct.get(productId);
                if (pe == null) {
                    throw new TermBuilderException('No active price book entry for the fare product on this quote\'s price book.');
                }
                out.add(pe);
            }
        }
        return out;
    }

    /**
     * The canonical dynamic classification-component linking the Term bundle to the fare
     * classification: ParentProduct = DL-TERM, ChildProductClassification = PC-DL-FARE. Returns null
     * when absent (the demo dataset loads it; the relationship still links via Root/Main without it).
     */
    private static ProductRelatedComponent resolveDynamicFareComponent(Id fareClassId) {
        if (fareClassId == null) {
            return null;
        }
        List<ProductRelatedComponent> prcs = [
            SELECT Id, ProductRelationshipTypeId
            FROM ProductRelatedComponent
            WHERE ChildProductClassificationId = :fareClassId
              AND (ParentProduct.ProductCode = :TERM_SKU OR ParentProduct.StockKeepingUnit = :TERM_SKU)
            WITH USER_MODE
            LIMIT 1
        ];
        return prcs.isEmpty() ? null : prcs[0];
    }

    /**
     * Commit the fare-add graph in whichever mode FARE_ADD_FORCE_CONFIGURATION selects. Kept as a
     * single dispatch point so the config-FORCE-vs-SKIP choice lives in one flag (see that constant):
     *   - FORCE (commitWithExpansion): the platform's configuration step stamps the derived bundle
     *     fields (QuoteLineRelationship.QuoteId, QuoteLineItem.ParentQuoteLineItemId). Safe here
     *     because DL-TERM has no default included components to re-expand into duplicate lines.
     *   - SKIP  (commitConfigured): persists the hand-built tree verbatim (the prior behavior).
     */
    private static RLM_DeltaPlaceSalesTransaction.Result commitFareGraph(
        String graphName, List<RevSalesTrxn.RecordWithReferenceRequest> records
    ) {
        return FARE_ADD_FORCE_CONFIGURATION
            ? RLM_DeltaPlaceSalesTransaction.commitWithExpansion(graphName, records)
            : RLM_DeltaPlaceSalesTransaction.commitConfigured(graphName, records);
    }

    /**
     * QuoteLineRelationship field map for a new fare child. Main/Root point at the persisted Term's
     * REAL id; Associated points at the fare's graph token (created earlier in this graph). Stamps
     * the resolved ProductRelatedComponent (+ its relationship type) when found.
     */
    private static Map<String, Object> buildFareRelationshipFields(Id termLineId, String fareRef, ProductRelatedComponent prc) {
        Map<String, Object> f = new Map<String, Object>{
            'MainQuoteLineId' => String.valueOf(termLineId),
            'RootQuoteLineId' => String.valueOf(termLineId),
            'AssociatedQuoteLineId' => RLM_DeltaPlaceSalesTransaction.referenceToken(fareRef),
            // Required on create. Fares are $0 and priced/discounted independently, so the fare's
            // price is NOT included in the Term's bundle price.
            'AssociatedQuoteLinePricing' => 'NotIncludedInBundlePrice'
        };
        // Runtime type MUST be the bundle-component type, NOT the design-time classification type on
        // the PRC (which OrderItemRelationship can't represent → blocks quote→order). See
        // RLM_DeltaCatalogService.resolveBundleComponentRelationshipTypeId. Required field on create.
        Id runtimePrtId = RLM_DeltaCatalogService.resolveBundleComponentRelationshipTypeId();
        if (runtimePrtId != null) {
            f.put('ProductRelationshipTypeId', runtimePrtId);
        }
        // Keep the design-time PRC linkage for traceability of the dynamic fare slot (optional field).
        if (prc != null) {
            f.put('ProductRelatedComponentId', prc.Id);
        }
        return f;
    }

    /**
     * QuoteLineItem field map for a fare line (mirrors RLM_DeltaCatalogController.buildQuoteLineItemFields).
     * StartDate/EndDate are route/booking-window dates, not billing dates, so they're seeded from the
     * negotiation's header-level DL_NegotiationStartDate__c / DL_NegotiationEndDate__c regardless of
     * selling model (falling back to today / +1 year otherwise — the prior default), matching the
     * line grid, which lets these be edited on any line. This only seeds the NEW line being created;
     * it never rewrites dates already on other lines. BillingFrequency/PeriodBoundary remain
     * TermDefined/Evergreen-only — those are billing-cadence fields, not booking-window dates.
     *
     * defaultFareCodes seeds the editable per-line DL_FareCodes__c from the fare product's canonical
     * Default Fare Codes (a `;`-delimited multiselect string). A direct QLI field, so PST persists it
     * inline — no Context Definition mapping is required for it to round-trip. Non-price-impacting.
     */
    private static Map<String, Object> buildFareLineFields(
        PricebookEntry pbe, String quoteIdRef, Decimal quantity, String defaultFareCodes,
        Date negotiationStartDate, Date negotiationEndDate
    ) {
        Decimal unitPrice = (pbe.UnitPrice != null) ? pbe.UnitPrice : 0;
        String sellingModelType = (pbe.ProductSellingModel != null) ? String.valueOf(pbe.ProductSellingModel.SellingModelType) : null;
        String pricingTermUnit = (pbe.ProductSellingModel != null) ? String.valueOf(pbe.ProductSellingModel.PricingTermUnit) : null;
        String billingFrequency = (String.isNotBlank(pricingTermUnit) && PRICING_TERM_TO_BILLING_FREQUENCY.containsKey(pricingTermUnit))
            ? PRICING_TERM_TO_BILLING_FREQUENCY.get(pricingTermUnit) : null;
        Date startDate = (negotiationStartDate != null) ? negotiationStartDate : Date.today();
        Date endDate = (negotiationEndDate != null) ? negotiationEndDate : startDate.addYears(1);
        Map<String, Object> fields = new Map<String, Object>{
            'QuoteId' => quoteIdRef,
            'Product2Id' => pbe.Product2Id,
            'PricebookEntryId' => pbe.Id,
            'Quantity' => (quantity != null && quantity > 0) ? quantity : 1,
            'UnitPrice' => unitPrice,
            'StartDate' => isoTimestamp(startDate)
        };
        if (String.isNotBlank(defaultFareCodes)) {
            fields.put('DL_FareCodes__c', defaultFareCodes);
        }
        if ('Evergreen' == sellingModelType && String.isNotBlank(billingFrequency)) {
            fields.put('PeriodBoundary', 'Anniversary');
            fields.put('BillingFrequency', billingFrequency);
        } else {
            fields.put('EndDate', isoTimestamp(endDate));
            if ('TermDefined' == sellingModelType && String.isNotBlank(billingFrequency)) {
                fields.put('PeriodBoundary', 'Anniversary');
                fields.put('BillingFrequency', billingFrequency);
            }
        }
        return fields;
    }

    /** Clamp the requested Term count to [1, MAX_TERMS_PER_ADD]; blank/invalid → 1. */
    private static Integer resolveTermCount(Object raw) {
        Decimal d = asDecimal(raw);
        Integer n = (d != null) ? (Integer) d.round(System.RoundingMode.DOWN) : 1;
        if (n < 1) {
            n = 1;
        }
        if (n > MAX_TERMS_PER_ADD) {
            n = MAX_TERMS_PER_ADD;
        }
        return n;
    }

    /**
     * QuoteLineItem field map for a Term root line (mirrors buildFareLineFields without the
     * fare-code seed). StartDate/EndDate are route/booking-window dates, not billing dates, so
     * they're seeded from the negotiation's header-level DL_NegotiationStartDate__c /
     * DL_NegotiationEndDate__c regardless of selling model (falling back to today / +1 year
     * otherwise — the prior default), matching the line grid, which lets these be edited on any
     * line. This only seeds the NEW line being created; it never rewrites dates already on other
     * lines. BillingFrequency/PeriodBoundary remain TermDefined/Evergreen-only — those are
     * billing-cadence fields, not booking-window dates.
     */
    private static Map<String, Object> buildTermLineFields(PricebookEntry pbe, String quoteIdRef, Date negotiationStartDate, Date negotiationEndDate) {
        Decimal unitPrice = (pbe.UnitPrice != null) ? pbe.UnitPrice : 0;
        String sellingModelType = (pbe.ProductSellingModel != null) ? String.valueOf(pbe.ProductSellingModel.SellingModelType) : null;
        String pricingTermUnit = (pbe.ProductSellingModel != null) ? String.valueOf(pbe.ProductSellingModel.PricingTermUnit) : null;
        String billingFrequency = (String.isNotBlank(pricingTermUnit) && PRICING_TERM_TO_BILLING_FREQUENCY.containsKey(pricingTermUnit))
            ? PRICING_TERM_TO_BILLING_FREQUENCY.get(pricingTermUnit) : null;
        Date startDate = (negotiationStartDate != null) ? negotiationStartDate : Date.today();
        Date endDate = (negotiationEndDate != null) ? negotiationEndDate : startDate.addYears(1);
        Map<String, Object> fields = new Map<String, Object>{
            'QuoteId' => quoteIdRef,
            'Product2Id' => pbe.Product2Id,
            'PricebookEntryId' => pbe.Id,
            'Quantity' => 1,
            'UnitPrice' => unitPrice,
            'StartDate' => isoTimestamp(startDate)
        };
        if ('Evergreen' == sellingModelType && String.isNotBlank(billingFrequency)) {
            fields.put('PeriodBoundary', 'Anniversary');
            fields.put('BillingFrequency', billingFrequency);
        } else {
            fields.put('EndDate', isoTimestamp(endDate));
            if ('TermDefined' == sellingModelType && String.isNotBlank(billingFrequency)) {
                fields.put('PeriodBoundary', 'Anniversary');
                fields.put('BillingFrequency', billingFrequency);
            }
        }
        return fields;
    }

    /** Resolve the DL-CONTRACTS catalog + DL-TERMS category ids by their stable codes (never stored). */
    private static Map<String, Object> resolveTermCatalogRefs() {
        Id catalogId = null;
        for (ProductCatalog pc : [SELECT Id FROM ProductCatalog WHERE Code = :CATALOG_CODE WITH USER_MODE LIMIT 1]) {
            catalogId = pc.Id;
        }
        Id categoryId = null;
        for (ProductCategory cat : [SELECT Id FROM ProductCategory WHERE Code = :CATEGORY_CODE WITH USER_MODE LIMIT 1]) {
            categoryId = cat.Id;
        }
        return new Map<String, Object>{ 'catalogId' => catalogId, 'categoryId' => categoryId };
    }

    /** Resolve a ProductClassification id by Code (null when absent). */
    private static Id resolveClassificationId(String code) {
        for (ProductClassification pc : [SELECT Id FROM ProductClassification WHERE Code = :code WITH USER_MODE LIMIT 1]) {
            return pc.Id;
        }
        return null;
    }

    // Runtime bundle-component relationship type resolution lives in RLM_DeltaCatalogService
    // (resolveBundleComponentRelationshipTypeId) so the fare-add path and the configurator-commit
    // path share one source of truth. See buildFareRelationshipFields.

    private static Integer sellingModelRank(PricebookEntry pbe) {
        String st = (pbe.ProductSellingModel != null) ? String.valueOf(pbe.ProductSellingModel.SellingModelType) : null;
        if (st == 'OneTime') return 1;
        if (st == 'Evergreen') return 2;
        if (st == 'TermDefined') return 3;
        return 99;
    }

    public static Quote loadQuote(Id qId) {
        List<Quote> quotes = [
            SELECT Id, Name, Pricebook2Id, AccountId, QuoteAccountId, ContractId, Account.Name, QuoteAccount.Name,
                   DL_NegotiationStartDate__c, DL_NegotiationEndDate__c
            FROM Quote WHERE Id = :qId WITH USER_MODE LIMIT 1
        ];
        if (quotes.isEmpty()) {
            throw new TermBuilderException('Quote not found or not accessible.');
        }
        return quotes[0];
    }

    /**
     * Resolve the Contract the negotiation Quote is already related to (its ContractId), returning
     * { contractId, contractNumber }. Both null when the quote isn't contracted yet or the contract
     * isn't accessible — the header treats that as "not contracted" and offers Create Contract.
     */
    private static Map<String, Object> resolveExistingContract(Id contractId) {
        Map<String, Object> out = new Map<String, Object>{ 'contractId' => null, 'contractNumber' => null };
        if (contractId == null) {
            return out;
        }
        for (Contract c : [SELECT Id, ContractNumber FROM Contract WHERE Id = :contractId WITH USER_MODE LIMIT 1]) {
            out.put('contractId', c.Id);
            out.put('contractNumber', c.ContractNumber);
        }
        return out;
    }

    private static String readCurrency(Quote q) {
        if (!UserInfo.isMultiCurrencyOrganization()) {
            return UserInfo.getDefaultCurrency();
        }
        try {
            return String.valueOf(q.get('CurrencyIsoCode'));
        } catch (Exception e) {
            return UserInfo.getDefaultCurrency();
        }
    }

    private static String isoTimestamp(Date d) {
        return DateTime.newInstanceGmt(d, Time.newInstance(0, 0, 0, 0)).formatGmt('yyyy-MM-dd') + 'T00:00:00.000Z';
    }

    private static Map<String, Object> parseInput(String inputJson) {
        if (String.isBlank(inputJson)) {
            throw new TermBuilderException('Request body is required.');
        }
        try {
            return (Map<String, Object>) JSON.deserializeUntyped(inputJson);
        } catch (Exception e) {
            throw new TermBuilderException('Invalid request: malformed JSON.');
        }
    }

    private static Id parseId(String raw, String label) {
        if (String.isBlank(raw)) {
            throw new TermBuilderException(label + ' is required.');
        }
        try {
            return Id.valueOf(raw.trim());
        } catch (Exception e) {
            throw new TermBuilderException('Invalid ' + label + '.');
        }
    }

    private static Id optionalId(Object raw) {
        if (raw == null || String.isBlank(String.valueOf(raw))) {
            return null;
        }
        try {
            return Id.valueOf(String.valueOf(raw).trim());
        } catch (Exception e) {
            throw new TermBuilderException('Invalid id: ' + raw);
        }
    }

    private static String asString(Object o) {
        return (o == null) ? null : String.valueOf(o);
    }

    private static Decimal asDecimal(Object o) {
        if (o == null || String.isBlank(String.valueOf(o))) return null;
        try {
            if (o instanceof Decimal) return (Decimal) o;
            if (o instanceof Integer) return (Decimal) ((Integer) o);
            if (o instanceof Long) return (Decimal) ((Long) o);
            if (o instanceof Double) return Decimal.valueOf((Double) o);
            return Decimal.valueOf(String.valueOf(o));
        } catch (Exception e) {
            throw new TermBuilderException('Invalid number: ' + o);
        }
    }

    private static Date asDate(Object o) {
        if (o == null || String.isBlank(String.valueOf(o))) return null;
        String s = String.valueOf(o).trim();
        try {
            // Accept ISO date (yyyy-MM-dd) or full datetime; take the date part.
            return Date.valueOf(s.length() >= 10 ? s.substring(0, 10) : s);
        } catch (Exception e) {
            throw new TermBuilderException('Invalid date: ' + o);
        }
    }

    private static String errorResult(String message) {
        return JSON.serialize(new Map<String, Object>{ 'isSuccess' => false, 'errorMessage' => message });
    }
}
