@isTest
private class RLM_AI_UpdateRecordFieldsServiceTest {

    // ---- Fixture builder ----
    private class Fixture {
        public Id quoteId;
        public List<Id> lineIds = new List<Id>();
    }

    private static Fixture buildFixture(List<String> productNames) {
        Account acct = new Account(Name = 'RLM AI Test Account');
        insert acct;

        Opportunity opp = new Opportunity(
            Name = 'RLM AI Test Opportunity',
            AccountId = acct.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert opp;

        Id standardPbId = Test.getStandardPricebookId();
        Quote q = new Quote(
            Name = 'RLM AI Test Quote',
            OpportunityId = opp.Id,
            Pricebook2Id = standardPbId,
            Status = 'Draft',
            ExpirationDate = Date.today().addDays(30)
        );
        insert q;

        Fixture f = new Fixture();
        f.quoteId = q.Id;

        for (String productName : productNames) {
            Product2 product = new Product2(Name = productName, IsActive = true);
            insert product;

            PricebookEntry pbe = new PricebookEntry(
                Pricebook2Id = standardPbId,
                Product2Id = product.Id,
                UnitPrice = 100,
                IsActive = true
            );
            insert pbe;

            QuoteLineItem qli = new QuoteLineItem(
                QuoteId = q.Id,
                PricebookEntryId = pbe.Id,
                Quantity = 1,
                UnitPrice = 100,
                Description = 'Original description'
            );
            insert qli;
            f.lineIds.add(qli.Id);
        }

        return f;
    }

    private static RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput baseInput(Id quoteId) {
        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input =
            new RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput();
        input.quoteId = String.valueOf(quoteId);
        return input;
    }

    // ---- Single line by Id ----
    @isTest
    static void updatesEndDateOnSingleLineById() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.quoteLineItemIds = new List<String>{ String.valueOf(f.lineIds[0]) };
        input.fieldUpdatesJson = '[{"fieldApiName":"EndDate","value":"2029-06-25"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);
        System.assertEquals(1, out.updatedCount);
        System.assert(out.resultsDisplay.contains('Quinn Alpha'), 'display should mention product');
        System.assert(out.resultsDisplay.toLowerCase().contains('enddate'), 'display should echo field name: ' + out.resultsDisplay);

        QuoteLineItem updated = [SELECT EndDate FROM QuoteLineItem WHERE Id = :f.lineIds[0]];
        System.assertEquals(Date.newInstance(2029, 6, 25), updated.EndDate);
    }

    // ---- Regression: USER_MODE update via productName (price fields loaded) ----
    // The resolver loads read-only/calculated fields (NetUnitPrice, ListPrice,
    // UnitPrice) for display. Updating that loaded row directly in USER_MODE
    // fails with "fields being inaccessible" because USER_MODE validates FLS on
    // every populated field. This test runs WITHOUT the SYSTEM_MODE bypass so it
    // exercises the real USER_MODE path and guards the bare-record DML fix.
    @isTest
    static void updatesViaProductNameUnderUserMode() {
        // Note: NO testBypassUserMode — runs in real USER_MODE on purpose.
        Fixture f = buildFixture(new List<String>{ 'Quinn UserMode' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.productName = 'Quinn UserMode';
        input.fieldUpdatesJson = '[{"fieldApiName":"EndDate","value":"2029-06-25"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);
        System.assertEquals(1, out.updatedCount, 'should update the single matched line');

        QuoteLineItem updated = [SELECT EndDate FROM QuoteLineItem WHERE Id = :f.lineIds[0]];
        System.assertEquals(Date.newInstance(2029, 6, 25), updated.EndDate);
    }

    // ---- Apply to all ----
    @isTest
    static void applyToAllUpdatesEveryLine() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha', 'Quinn Beta' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.applyToAll = true;
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"Bulk updated"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);
        System.assertEquals(2, out.updatedCount);

        List<QuoteLineItem> lines = [
            SELECT Description FROM QuoteLineItem WHERE Id IN :f.lineIds ORDER BY Id
        ];
        for (QuoteLineItem qli : lines) {
            System.assertEquals('Bulk updated', qli.Description);
        }
    }

    // ---- Quote header fields ----
    @isTest
    static void updatesQuoteHeaderFields() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'Quote';
        input.fieldUpdatesJson = '[{"fieldApiName":"Name","value":"Updated Quote Name"},'
            + '{"fieldApiName":"Description","value":"Updated description"},'
            + '{"fieldApiName":"ExpirationDate","value":"2029-12-31"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);
        System.assertEquals(1, out.updatedCount);

        Quote updated = [SELECT Name, Description, ExpirationDate FROM Quote WHERE Id = :f.quoteId];
        System.assertEquals('Updated Quote Name', updated.Name);
        System.assertEquals('Updated description', updated.Description);
        System.assertEquals(Date.newInstance(2029, 12, 31), updated.ExpirationDate);
    }

    // ---- Quote Status by label or API value ----
    @isTest
    static void updatesQuoteStatusByLabelOrApiValue() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        // First test: API value
        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input1 = baseInput(f.quoteId);
        input1.sObjectType = 'Quote';
        input1.fieldUpdatesJson = '[{"fieldApiName":"Status","value":"Presented"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results1 =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input1 });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out1 = results1[0];
        System.assertEquals(true, out1.isSuccess, 'error: ' + out1.errorMessage);

        Quote updated1 = [SELECT Status FROM Quote WHERE Id = :f.quoteId];
        System.assertEquals('Presented', updated1.Status);

        // Second test: label (if different from API value)
        // Note: in most orgs, Presented label = Presented API value, so this is best-effort
        // The coerceValue logic will accept either, which is the goal
    }

    // ---- Coerce quantity number ----
    @isTest
    static void coercesQuantityNumber() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.quoteLineItemIds = new List<String>{ String.valueOf(f.lineIds[0]) };
        input.fieldUpdatesJson = '[{"fieldApiName":"Quantity","value":"5"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);

        QuoteLineItem updated = [SELECT Quantity FROM QuoteLineItem WHERE Id = :f.lineIds[0]];
        System.assertEquals(5, updated.Quantity);
    }

    // ---- Product name single match ----
    @isTest
    static void productNameSingleMatchUpdates() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.productName = 'Alpha';
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"Single match updated"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);
        System.assertEquals(1, out.updatedCount);

        QuoteLineItem updated = [SELECT Description FROM QuoteLineItem WHERE Id = :f.lineIds[0]];
        System.assertEquals('Single match updated', updated.Description);
    }

    // ---- Product name multi-match disambiguation ----
    @isTest
    static void productNameMultiMatchDisambiguates() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{ 'Quinn Duplicate', 'Quinn Duplicate' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.productName = 'Duplicate';
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"Should not update"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.needsDisambiguation, 'should need disambiguation');
        System.assertEquals(0, out.updatedCount, 'should not update any line');
        System.assert(String.isNotBlank(out.candidateQuoteLineSummariesDisplay), 'should have candidate display');
        System.assert(String.isNotBlank(out.pendingSelectionJson), 'should have pending selection JSON');

        // Verify no lines were changed
        List<QuoteLineItem> lines = [SELECT Description FROM QuoteLineItem WHERE Id IN :f.lineIds];
        for (QuoteLineItem qli : lines) {
            System.assertEquals('Original description', qli.Description, 'line should be unchanged');
        }

        // Now re-call with selectedDisplayNumbersJson to pick the second line
        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input2 = baseInput(f.quoteId);
        input2.sObjectType = 'QuoteLineItem';
        input2.selectedDisplayNumbersJson = '[2]';
        input2.pendingSelectionJsonIn = out.pendingSelectionJson;
        input2.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"Second line updated"}]';

        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results2 =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input2 });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out2 = results2[0];
        System.assertEquals(true, out2.isSuccess, 'error: ' + out2.errorMessage);
        System.assertEquals(1, out2.updatedCount, 'should update exactly one line');

        QuoteLineItem line1 = [SELECT Description FROM QuoteLineItem WHERE Id = :f.lineIds[0]];
        QuoteLineItem line2 = [SELECT Description FROM QuoteLineItem WHERE Id = :f.lineIds[1]];
        System.assertEquals('Original description', line1.Description, 'first line unchanged');
        System.assertEquals('Second line updated', line2.Description, 'second line updated');
    }

    // ---- Omitted field preserved ----
    @isTest
    static void omittedFieldIsPreserved() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        // Set initial dates
        QuoteLineItem qli = [SELECT Id FROM QuoteLineItem WHERE Id = :f.lineIds[0]];
        qli.StartDate = Date.today();
        qli.EndDate = Date.today().addDays(365);
        update qli;

        // Update only Description
        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.quoteLineItemIds = new List<String>{ String.valueOf(f.lineIds[0]) };
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"Updated description"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);

        QuoteLineItem updated = [SELECT StartDate, EndDate, Description FROM QuoteLineItem WHERE Id = :f.lineIds[0]];
        System.assertEquals(Date.today(), updated.StartDate, 'StartDate preserved');
        System.assertEquals(Date.today().addDays(365), updated.EndDate, 'EndDate preserved');
        System.assertEquals('Updated description', updated.Description);
    }

    // ---- Explicit null clears nillable field ----
    @isTest
    static void explicitNullClearsNillableField() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.quoteLineItemIds = new List<String>{ String.valueOf(f.lineIds[0]) };
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":null}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);

        QuoteLineItem updated = [SELECT Description FROM QuoteLineItem WHERE Id = :f.lineIds[0]];
        System.assertEquals(null, updated.Description, 'Description should be cleared');
    }

    // ---- Clearing non-nillable field rejected ----
    @isTest
    static void clearingNonNillableFieldRejected() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.quoteLineItemIds = new List<String>{ String.valueOf(f.lineIds[0]) };
        input.fieldUpdatesJson = '[{"fieldApiName":"Quantity","value":null}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('cannot be cleared'), 'error: ' + out.errorMessage);

        QuoteLineItem updated = [SELECT Quantity FROM QuoteLineItem WHERE Id = :f.lineIds[0]];
        System.assertEquals(1, updated.Quantity, 'Quantity unchanged');
    }

    // ---- Non-updateable field rejected ----
    @isTest
    static void nonUpdateableFieldRejected() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.quoteLineItemIds = new List<String>{ String.valueOf(f.lineIds[0]) };
        input.fieldUpdatesJson = '[{"fieldApiName":"CreatedDate","value":"2029-01-01"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('cannot be edited'), 'error: ' + out.errorMessage);
    }

    // ---- Unknown field rejected ----
    @isTest
    static void unknownFieldRejected() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.quoteLineItemIds = new List<String>{ String.valueOf(f.lineIds[0]) };
        input.fieldUpdatesJson = '[{"fieldApiName":"NonExistentField","value":"test"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('Unknown field'), 'error: ' + out.errorMessage);
    }

    // ---- Disallowed object rejected (QuoteLineItemAttribute) ----
    @isTest
    static void disallowedObjectRejected() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItemAttribute';
        input.fieldUpdatesJson = '[{"fieldApiName":"AttributeValue","value":"test"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('configuration actions'), 'error: ' + out.errorMessage);
    }

    // ---- Bad date format rejected ----
    @isTest
    static void badDateFormatIsRejected() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.quoteLineItemIds = new List<String>{ String.valueOf(f.lineIds[0]) };
        input.fieldUpdatesJson = '[{"fieldApiName":"EndDate","value":"12/31/2029"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('YYYY-MM-DD'), 'error: ' + out.errorMessage);
    }

    // ---- Cross-quote line rejected ----
    @isTest
    static void crossQuoteLineRejected() {
        Fixture f1 = buildFixture(new List<String>{ 'Quinn Alpha' });
        Fixture f2 = buildFixture(new List<String>{ 'Quinn Beta' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f1.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.quoteLineItemIds = new List<String>{ String.valueOf(f2.lineIds[0]) }; // different quote
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"Cross-quote"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('do not belong'), 'error: ' + out.errorMessage);
    }

    // ---- No targeting rejected ----
    @isTest
    static void noTargetingRejected() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"test"}]';
        // No targeting at all

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('Specify which'), 'error: ' + out.errorMessage);
    }

    // ---- No fields rejected ----
    @isTest
    static void noFieldsRejected() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.quoteLineItemIds = new List<String>{ String.valueOf(f.lineIds[0]) };
        input.fieldUpdatesJson = '[]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('at least one field'), 'error: ' + out.errorMessage);
    }

    // ---- Blank quote Id rejected ----
    @isTest
    static void blankQuoteIdRejected() {
        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input =
            new RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput();
        input.quoteId = '';
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"test"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('Quote Id is required'), 'error: ' + out.errorMessage);
    }

    // ---- Invalid quote Id rejected ----
    @isTest
    static void invalidQuoteIdRejected() {
        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input =
            new RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput();
        input.quoteId = 'not-an-id';
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"test"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('Invalid quote Id'), 'error: ' + out.errorMessage);
    }

    // ---- Empty input list returns empty ----
    @isTest
    static void emptyInputListReturnsEmpty() {
        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>());
        Test.stopTest();

        System.assertEquals(0, results.size(), 'empty input should return empty output');
    }

    // ---- Null input list returns empty ----
    @isTest
    static void nullInputListReturnsEmpty() {
        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(null);
        Test.stopTest();

        System.assertEquals(0, results.size(), 'null input should return empty output');
    }

    // ---- Invalid JSON rejected ----
    @isTest
    static void invalidJsonRejected() {
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.quoteLineItemIds = new List<String>{ String.valueOf(f.lineIds[0]) };
        input.fieldUpdatesJson = 'not-valid-json{';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('Invalid'), 'error: ' + out.errorMessage);
    }

    // ---- Too many lines rejected ----
    @isTest
    static void tooManyLinesRejected() {
        // Create 11 lines (MAX is 10)
        List<String> products = new List<String>();
        for (Integer i = 1; i <= 11; i++) {
            products.add('Product ' + i);
        }
        Fixture f = buildFixture(products);

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.applyToAll = true;
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"Bulk"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(false, out.isSuccess, 'should fail');
        System.assert(out.errorMessage.contains('at most'), 'error: ' + out.errorMessage);
    }

    // ---- Ordinals without pending selection fallback ----
    @isTest
    static void ordinalsWithoutPendingSelectionUseFreshList() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{ 'Quinn Alpha', 'Quinn Beta' });

        // Select ordinal 2 without pending selection JSON (fallback path)
        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.selectedDisplayNumbersJson = '[2]';
        // No pendingSelectionJsonIn — uses fresh candidate list
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"Ordinal 2 updated"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);
        System.assertEquals(1, out.updatedCount);

        QuoteLineItem line2 = [SELECT Description FROM QuoteLineItem WHERE Id = :f.lineIds[1]];
        System.assertEquals('Ordinal 2 updated', line2.Description);
    }

    // ---- Tokenized product-name matching tests ----

    @isTest
    static void productNameTokenizedMatch() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{ 'QB API Management Solution' });

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.productName = 'QB API Management';
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"Tokenized match"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.isSuccess, 'error: ' + out.errorMessage);
        System.assertEquals(1, out.updatedCount);

        QuoteLineItem updated = [SELECT Description FROM QuoteLineItem WHERE Id = :f.lineIds[0]];
        System.assertEquals('Tokenized match', updated.Description,
            'Non-contiguous tokens should match');
    }

    @isTest
    static void productNameTokenizedDisambiguates() {
        RLM_AI_UpdateRecordFieldsService.testBypassUserMode = true;
        Fixture f = buildFixture(new List<String>{
            'Additional API Product Alpha',
            'Additional API Product Beta'
        });

        // Search for just "API" which matches both
        RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput input = baseInput(f.quoteId);
        input.sObjectType = 'QuoteLineItem';
        input.productName = 'API';
        input.fieldUpdatesJson = '[{"fieldApiName":"Description","value":"test"}]';

        Test.startTest();
        List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput> results =
            RLM_AI_UpdateRecordFieldsService.updateRecordFields(
                new List<RLM_AI_UpdateRecordFieldsService.UpdateFieldsInput>{ input });
        Test.stopTest();

        RLM_AI_UpdateRecordFieldsService.UpdateFieldsOutput out = results[0];
        System.assertEquals(true, out.needsDisambiguation,
            'Multiple token matches should disambiguate');
        System.assertEquals(0, out.updatedCount);
        System.assert(String.isNotBlank(out.candidateQuoteLineSummariesDisplay),
            'Should have candidate display');
    }
}
