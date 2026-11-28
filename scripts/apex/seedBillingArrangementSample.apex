/**
 * Seed the split-billing and invoice-grouping samples (264 Billing).
 *
 * Idempotent: every record is found by name or reference first, so a rerun creates nothing.
 * Wired into prepare_billing (billing, qb, tax and sample_data on; refresh off). It creates no
 * invoice and starts no run: a demo previews or invoices on demand
 * (datasets/sfdmu/qb/en-US/qb-billing/README.md, "Split billing and invoice grouping samples").
 *
 * 1. Four sample accounts, each with a contact and a default billing account (billing profile).
 *    They are created here because the shared sample accounts load later in the build
 *    (prepare_scratch), and because the harness relies on Global Media having no billing account.
 * 2. A billing arrangement modelled on the Help example (Examples: Flexible Invoicing for Complex
 *    Business Models): owned by one account and billed to three, 40% (with any remainder), 30% and
 *    30%. It is Active and attached to nothing; a demo attaches it to an order or schedule group.
 * 3. A standalone invoice-grouping case: three billing schedules for one account made by the
 *    Create Standalone Billing Schedules action (no order), with invoice group type Custom and
 *    keys POLICY_1001 (two schedules) and POLICY_1002 (one), so a preview or an invoice run makes
 *    one invoice per key. The schedules are Ready for Invoicing from the day of the build.
 */

// ── 1. Sample accounts, contacts and billing accounts ───────────────────────
// Name => { street, contact first name, contact last name }; all San Francisco, CA, US.
Map<String, List<String>> sampleAccounts = new Map<String, List<String>>{
    'Sample Split Billing Owner'     => new List<String>{ '415 California Street', 'Dana', 'Owens' },
    'Sample Split Billing Partner A' => new List<String>{ '1 Market Street', 'Riley', 'Park' },
    'Sample Split Billing Partner B' => new List<String>{ '500 Howard Street', 'Jordan', 'Lee' },
    'Sample Standalone Policyholder' => new List<String>{ '50 Fremont Street', 'Casey', 'Morgan' }
};

Map<String, Account> accountByName = new Map<String, Account>();
for (Account a : [SELECT Id, Name, BillingCity, ShippingCity FROM Account WHERE Name IN :sampleAccounts.keySet()]) {
    accountByName.put(a.Name, a);
}
List<Account> accountsToInsert = new List<Account>();
for (String name : sampleAccounts.keySet()) {
    if (accountByName.containsKey(name)) {
        continue;
    }
    String street = sampleAccounts.get(name)[0];
    accountsToInsert.add(new Account(
        Name = name,
        Type = 'Customer',
        Description = 'Sample account for the split billing and invoice grouping demos (qb-billing README).',
        BillingStreet = street, BillingCity = 'San Francisco', BillingState = 'CA',
        BillingPostalCode = '94105', BillingCountry = 'US',
        ShippingStreet = street, ShippingCity = 'San Francisco', ShippingState = 'CA',
        ShippingPostalCode = '94105', ShippingCountry = 'US'
    ));
}
if (!accountsToInsert.isEmpty()) {
    insert accountsToInsert;
    for (Account a : accountsToInsert) {
        accountByName.put(a.Name, a);
    }
}
Set<Id> sampleAccountIds = new Set<Id>();
for (Account a : accountByName.values()) {
    sampleAccountIds.add(a.Id);
}

Map<Id, Contact> contactByAccount = new Map<Id, Contact>();
for (Contact c : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :sampleAccountIds ORDER BY CreatedDate]) {
    if (!contactByAccount.containsKey(c.AccountId)) {
        contactByAccount.put(c.AccountId, c);
    }
}
List<Contact> contactsToInsert = new List<Contact>();
for (String name : sampleAccounts.keySet()) {
    Id accountId = accountByName.get(name).Id;
    if (!contactByAccount.containsKey(accountId)) {
        contactsToInsert.add(new Contact(AccountId = accountId,
            FirstName = sampleAccounts.get(name)[1], LastName = sampleAccounts.get(name)[2]));
    }
}
if (!contactsToInsert.isEmpty()) {
    insert contactsToInsert;
    for (Contact c : contactsToInsert) {
        contactByAccount.put(c.AccountId, c);
    }
}

List<PaymentTerm> defaultTerms = [SELECT Id FROM PaymentTerm WHERE IsDefault = true AND Status = 'Active' LIMIT 1];
if (defaultTerms.isEmpty()) {
    throw new System.AsyncException('No active default PaymentTerm. Run prepare_billing (activate_default_payment_term) before this seed.');
}
Map<Id, BillingAccount> billingAccountByAccount = new Map<Id, BillingAccount>();
for (BillingAccount ba : [SELECT Id, AccountId FROM BillingAccount WHERE AccountId IN :sampleAccountIds ORDER BY CreatedDate]) {
    if (!billingAccountByAccount.containsKey(ba.AccountId)) {
        billingAccountByAccount.put(ba.AccountId, ba);
    }
}
List<BillingAccount> billingAccountsToInsert = new List<BillingAccount>();
for (String name : sampleAccounts.keySet()) {
    Id accountId = accountByName.get(name).Id;
    if (billingAccountByAccount.containsKey(accountId)) {
        continue;
    }
    String street = sampleAccounts.get(name)[0];
    billingAccountsToInsert.add(new BillingAccount(
        Name = name + ' Billing Account',
        AccountId = accountId,
        BillToContactId = contactByAccount.get(accountId).Id,
        PaymentTermId = defaultTerms[0].Id,
        IsDefaultBillingProfile = true,
        PrimaryBillAddrStreet = street, PrimaryBillAddrCity = 'San Francisco', PrimaryBillAddrState = 'CA',
        PrimaryBillAddrPostalCode = '94105', PrimaryBillAddrCountry = 'US'
    ));
}
if (!billingAccountsToInsert.isEmpty()) {
    insert billingAccountsToInsert;
    for (BillingAccount ba : billingAccountsToInsert) {
        billingAccountByAccount.put(ba.AccountId, ba);
    }
}
System.debug('SEED_SPLIT_ACCOUNTS accounts=' + accountsToInsert.size() + ' contacts=' + contactsToInsert.size()
    + ' billingAccounts=' + billingAccountsToInsert.size());

// ── 2. Billing arrangement: 40% (with any remainder) / 30% / 30% ────────────
String arrangementName = 'Sample Split Billing 40-30-30';
// Account name => { percentage, bills the remainder (1) or not (0) }.
Map<String, List<Integer>> arrangementLines = new Map<String, List<Integer>>{
    'Sample Split Billing Owner'     => new List<Integer>{ 40, 1 },
    'Sample Split Billing Partner A' => new List<Integer>{ 30, 0 },
    'Sample Split Billing Partner B' => new List<Integer>{ 30, 0 }
};
Integer arrangementsCreated = 0;
if ([SELECT COUNT() FROM BillingArrangement WHERE Name = :arrangementName] == 0) {
    // Lines are added while the arrangement is Draft, then it is activated (Help: Create Billing
    // Arrangements and Billing Arrangement Lines).
    BillingArrangement arrangement = new BillingArrangement(Name = arrangementName, Status = 'Draft',
        ShouldBillRemainderToAccount = false);
    insert arrangement;
    List<BillingArrangementLine> lines = new List<BillingArrangementLine>();
    for (String name : arrangementLines.keySet()) {
        Id accountId = accountByName.get(name).Id;
        lines.add(new BillingArrangementLine(
            BillingArrangementId = arrangement.Id,
            AccountId = accountId,
            BillingAccountId = billingAccountByAccount.get(accountId).Id,
            BillingPercentage = arrangementLines.get(name)[0],
            ShouldBillRemainder = arrangementLines.get(name)[1] == 1
        ));
    }
    insert lines;
    arrangement.Status = 'Active';
    update arrangement;
    arrangementsCreated = 1;
}
System.debug('SEED_SPLIT_ARRANGEMENT created=' + arrangementsCreated);

// ── 3. Standalone invoice-grouping case ──────────────────────────────────────
// Transaction reference (BillingSchedule.Reference) => custom invoice group key. The key allows only
// letters, digits, underscores and periods.
Map<String, String> groupKeyByReference = new Map<String, String>{
    'SAMPLE-POLICY-1001-A' => 'POLICY_1001',
    'SAMPLE-POLICY-1001-B' => 'POLICY_1001',
    'SAMPLE-POLICY-1002-A' => 'POLICY_1002'
};
Account policyholder = accountByName.get('Sample Standalone Policyholder');
Set<String> existingReferences = new Set<String>();
for (BillingSchedule bs : [SELECT Reference FROM BillingSchedule
                           WHERE Reference IN :groupKeyByReference.keySet() AND BillingAccountId = :policyholder.Id]) {
    existingReferences.add(bs.Reference);
}
List<Object> transactions = new List<Object>();
List<String> missingReferences = new List<String>();
for (String reference : groupKeyByReference.keySet()) {
    if (!existingReferences.contains(reference)) {
        missingReferences.add(reference);
    }
}
if (!missingReferences.isEmpty()) {
    List<LegalEntity> legalEntities = [SELECT Id FROM LegalEntity WHERE Name = 'Default Legal Entity - US' AND Status = 'Active' LIMIT 1];
    List<TaxTreatment> taxTreatments = [SELECT Id FROM TaxTreatment WHERE Name = 'Tax Treatment for US LE' AND Status = 'Active' LIMIT 1];
    List<BillingTreatment> billingTreatments = [SELECT Id FROM BillingTreatment WHERE Name = 'Billing Treatment - USA - Advance' AND Status = 'Active' LIMIT 1];
    List<Product2> products = [SELECT Id, Name FROM Product2 WHERE StockKeepingUnit = 'QB-API-FLEX' AND IsActive = true LIMIT 1];
    if (legalEntities.isEmpty() || taxTreatments.isEmpty() || billingTreatments.isEmpty() || products.isEmpty()) {
        throw new System.AsyncException('Standalone grouping sample needs the active US legal entity, its tax treatment '
            + '(qb-tax), the active Billing Treatment - USA - Advance (qb-billing) and the QB-API-FLEX product. Found: '
            + 'legalEntity=' + legalEntities.size() + ' taxTreatment=' + taxTreatments.size()
            + ' billingTreatment=' + billingTreatments.size() + ' product=' + products.size());
    }
    Date startDate = Date.today();
    for (String reference : missingReferences) {
        // A 12-month term billed monthly in advance: 100 a month.
        transactions.add(new Map<String, Object>{
            'TransactionId__std' => reference,
            'SellingModelType__std' => 'TermDefined',
            'ProductId__std' => products[0].Id,
            'ProductName__std' => products[0].Name,
            'StartDate__std' => String.valueOf(startDate),
            'EndDate__std' => String.valueOf(startDate.addYears(1).addDays(-1)),
            'PeriodBoundary__std' => 'Anniversary',
            'BillingDayOfMonth__std' => startDate.day(),
            'BillingTermUnit__std' => 'Month',
            'UnitPrice__std' => 100,
            'Quantity__std' => 1,
            'TotalPrice__std' => 1200,
            'CurrencyIsoCode__std' => 'USD',
            'LegalEntityId__std' => legalEntities[0].Id,
            'TaxTreatmentId__std' => taxTreatments[0].Id,
            'BillingTreatmentId__std' => billingTreatments[0].Id,
            'AccountId__std' => policyholder.Id,
            'BillingProfileId__std' => billingAccountByAccount.get(policyholder.Id).Id,
            'BillingCity__std' => policyholder.BillingCity,
            'ShippingCity__std' => policyholder.ShippingCity,
            'BillingActionType__std' => 'Add'
        });
    }
    Invocable.Action action = Invocable.Action.createStandardAction('createBillingSchedulesFromTrxn');
    action.setInvocationParameter('transactionDetails', JSON.serialize(new Map<String, Object>{ 'Transaction' => transactions }));
    action.setInvocationParameter('contextDefinitionName', 'StandaloneBillingContext__stdctx');
    action.setInvocationParameter('readContextMappingName', 'TransactionMapping');
    action.setInvocationParameter('saveContextMappingName', 'BSGEntitiesMapping');
    Invocable.Action.Result result = action.invoke()[0];
    if (!result.isSuccess()) {
        List<String> messages = new List<String>();
        for (Invocable.Action.Error err : result.getErrors()) {
            messages.add(err.getCode() + ': ' + err.getMessage());
        }
        throw new System.AsyncException('Create Standalone Billing Schedules failed: ' + String.join(messages, '; '));
    }
}

// Set the group type and key on every sample schedule (new ones, and any a user changed).
List<BillingSchedule> schedulesToKey = new List<BillingSchedule>();
Integer sampleSchedules = 0;
for (BillingSchedule bs : [SELECT Id, Reference, InvoiceGroupType, CustomInvoiceGroupKey FROM BillingSchedule
                           WHERE Reference IN :groupKeyByReference.keySet() AND BillingAccountId = :policyholder.Id]) {
    sampleSchedules++;
    String key = groupKeyByReference.get(bs.Reference);
    if (bs.InvoiceGroupType != 'Custom' || bs.CustomInvoiceGroupKey != key) {
        schedulesToKey.add(new BillingSchedule(Id = bs.Id, InvoiceGroupType = 'Custom', CustomInvoiceGroupKey = key));
    }
}
if (sampleSchedules != groupKeyByReference.size()) {
    throw new System.AsyncException('Expected ' + groupKeyByReference.size() + ' standalone sample billing schedules, found '
        + sampleSchedules + '. The action creates them synchronously on 264; check its AsyncOperationTracker.');
}
if (!schedulesToKey.isEmpty()) {
    update schedulesToKey;
}
System.debug('SEED_GROUPING_SCHEDULES created=' + transactions.size() + ' keyed=' + schedulesToKey.size());
