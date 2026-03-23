/**
 * @description Test class for RLM_RampScheduleService
 * Tests creation and validation execution
 */
@isTest
private class RLM_RampScheduleServiceTest {
    
    @testSetup
    static void setupTestData() {
        // Create a test Quote
        Account testAccount = new Account(Name = 'Test Account');
        insert testAccount;
        
        Opportunity testOpp = new Opportunity(
            Name = 'Test Opportunity',
            AccountId = testAccount.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30)
        );
        insert testOpp;
        
        Quote testQuote = new Quote(
            Name = 'Test Quote',
            OpportunityId = testOpp.Id,
            Status = 'Draft'
        );
        insert testQuote;
    }
    
    /**
     * @description Get test Quote ID
     */
    private static Id getTestQuoteId() {
        return [SELECT Id FROM Quote LIMIT 1].Id;
    }
    
    /**
     * @description Create a valid request with yearly segments
     */
    private static RLM_RampScheduleRequest createValidYearlyRequest() {
        Id quoteId = getTestQuoteId();
        Date startDate = Date.today().addDays(10);
        
        RLM_RampScheduleRequest request = new RLM_RampScheduleRequest();
        request.quoteId = quoteId;
        request.action = RLM_RampScheduleRequest.ACTION_CREATE;
        
        request.scheduleHeader = new RLM_RampScheduleRequest.ScheduleHeader();
        request.scheduleHeader.scheduleName = 'Test Yearly Schedule';
        request.scheduleHeader.scheduleType = RLM_RampScheduleRequest.SCHEDULE_TYPE_YEARLY;
        
        request.segments = new List<RLM_RampScheduleRequest.SegmentDefinition>();
        
        // Year 1
        RLM_RampScheduleRequest.SegmentDefinition seg1 = new RLM_RampScheduleRequest.SegmentDefinition();
        seg1.sequence = 1;
        seg1.name = 'Year 1';
        seg1.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY;
        seg1.startDate = startDate;
        seg1.endDate = startDate.addMonths(12).addDays(-1);
        seg1.discountPercent = 10;
        seg1.upliftPercent = 5;
        request.segments.add(seg1);
        
        // Year 2
        RLM_RampScheduleRequest.SegmentDefinition seg2 = new RLM_RampScheduleRequest.SegmentDefinition();
        seg2.sequence = 2;
        seg2.name = 'Year 2';
        seg2.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY;
        seg2.startDate = seg1.endDate.addDays(1);
        seg2.endDate = seg2.startDate.addMonths(12).addDays(-1);
        seg2.discountPercent = 5;
        request.segments.add(seg2);
        
        return request;
    }
    
    /**
     * @description Test successful creation of ramp schedule
     */
    @isTest
    static void testSuccessfulCreation() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        RLM_RampScheduleService service = new RLM_RampScheduleService();
        
        Test.setMock(HttpCalloutMock.class, new RampApiMock());
        Test.startTest();
        RLM_RampScheduleResponse response = service.execute(request);
        Test.stopTest();
        
        System.assertEquals(true, response.success, 'Creation should succeed');
        System.assertNotEquals(null, response.data.rampScheduleGroupId, 'Should have parent group ID');
        // Only segment 0 is created synchronously; segments 1..N are created by the
        // async Queueable (CloneSalesTransaction). In unit tests the mock does not
        // actually create QuoteLineGroups, so we assert the synchronous count only.
        System.assertEquals(1, response.data.segmentGroupIds.size(), 'Synchronous response includes segment 0 only');
        
        // Verify records were created
        List<QuoteLineGroup> parentGroups = [
            SELECT Id, Name, Type, StartDate, EndDate 
            FROM QuoteLineGroup 
            WHERE Id = :response.data.rampScheduleGroupId
        ];
        System.assertEquals(1, parentGroups.size(), 'Parent group should be created');
        System.assertEquals('RampScheduleGroup', parentGroups[0].Type, 'Type should be RampScheduleGroup');
        System.assertEquals('Test Yearly Schedule', parentGroups[0].Name, 'Name should match');
        
        List<QuoteLineGroup> segmentGroups = [
            SELECT Id, Name, Type, SegmentType, IsRamped, ParentQuoteLineGroupId,
                   StartDate, EndDate, Discount, RLM_UpliftPercent__c
            FROM QuoteLineGroup
            WHERE ParentQuoteLineGroupId = :response.data.rampScheduleGroupId
            ORDER BY StartDate
        ];
        System.assertEquals(1, segmentGroups.size(), 'Segment 0 created synchronously; others are async');
        System.assertEquals(null, segmentGroups[0].Type, 'Ramp segment Quote Line Group Type should be blank');
        System.assertEquals(true, segmentGroups[0].IsRamped, 'Should be ramped');
        System.assertEquals(10, segmentGroups[0].Discount, 'Discount should match');
        System.assertEquals(5, segmentGroups[0].RLM_UpliftPercent__c, 'Uplift should match the raw percent value');
    }
    
    /**
     * @description Test validation action (no creation)
     */
    @isTest
    static void testValidationAction() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.action = RLM_RampScheduleRequest.ACTION_VALIDATE;
        RLM_RampScheduleService service = new RLM_RampScheduleService();
        
        Test.startTest();
        RLM_RampScheduleResponse response = service.execute(request);
        Test.stopTest();
        
        System.assertEquals(true, response.success, 'Validation should succeed');
        System.assertEquals(null, response.data.rampScheduleGroupId, 'Should not have parent group ID');
        System.assertEquals(0, response.data.segmentGroupIds.size(), 'Should not have segment groups');
        
        // Verify no records were created
        List<QuoteLineGroup> groups = [SELECT Id FROM QuoteLineGroup];
        System.assertEquals(0, groups.size(), 'No groups should be created');
    }
    
    /**
     * @description Test validation failure prevents creation
     */
    @isTest
    static void testValidationFailurePreventsCreation() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.segments[0].endDate = request.segments[0].startDate.addDays(-1); // Invalid date range
        RLM_RampScheduleService service = new RLM_RampScheduleService();
        
        Test.startTest();
        RLM_RampScheduleResponse response = service.execute(request);
        Test.stopTest();
        
        System.assertEquals(false, response.success, 'Should fail validation');
        System.assertNotEquals(0, response.errors.size(), 'Should have errors');
        
        // Verify no records were created
        List<QuoteLineGroup> groups = [SELECT Id FROM QuoteLineGroup];
        System.assertEquals(0, groups.size(), 'No groups should be created');
    }
    
    /**
     * @description Test creation with custom segments
     */
    @isTest
    static void testCreationWithCustomSegments() {
        Id quoteId = getTestQuoteId();
        Date startDate = Date.today().addDays(10);
        
        RLM_RampScheduleRequest request = new RLM_RampScheduleRequest();
        request.quoteId = quoteId;
        request.action = RLM_RampScheduleRequest.ACTION_CREATE;
        
        request.scheduleHeader = new RLM_RampScheduleRequest.ScheduleHeader();
        request.scheduleHeader.scheduleName = 'Test Custom Schedule';
        request.scheduleHeader.scheduleType = RLM_RampScheduleRequest.SCHEDULE_TYPE_CUSTOM;
        
        request.segments = new List<RLM_RampScheduleRequest.SegmentDefinition>();
        
        // Custom segment 1
        RLM_RampScheduleRequest.SegmentDefinition seg1 = new RLM_RampScheduleRequest.SegmentDefinition();
        seg1.sequence = 1;
        seg1.name = 'Custom 1';
        seg1.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_CUSTOM;
        seg1.startDate = startDate;
        seg1.endDate = startDate.addMonths(6).addDays(-1);
        seg1.discountPercent = 15;
        request.segments.add(seg1);
        
        // Custom segment 2
        RLM_RampScheduleRequest.SegmentDefinition seg2 = new RLM_RampScheduleRequest.SegmentDefinition();
        seg2.sequence = 2;
        seg2.name = 'Custom 2';
        seg2.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_CUSTOM;
        seg2.startDate = seg1.endDate.addDays(1);
        seg2.endDate = seg2.startDate.addMonths(6).addDays(-1);
        seg2.discountPercent = 10;
        request.segments.add(seg2);
        
        RLM_RampScheduleService service = new RLM_RampScheduleService();
        
        Test.setMock(HttpCalloutMock.class, new RampApiMock());
        Test.startTest();
        RLM_RampScheduleResponse response = service.execute(request);
        Test.stopTest();
        
        System.assertEquals(true, response.success, 'Creation should succeed');
        System.assertNotEquals(null, response.data.rampScheduleGroupId, 'Should have parent group ID');
        System.assertEquals(1, response.data.segmentGroupIds.size(), 'Synchronous response includes segment 0 only');
    }
    
    /**
     * @description Test creation with trial segment
     */
    @isTest
    static void testCreationWithTrialSegment() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        
        // Add trial segment as first (sequence 1)
        RLM_RampScheduleRequest.SegmentDefinition trialSeg = new RLM_RampScheduleRequest.SegmentDefinition();
        trialSeg.sequence = 1; // Trial must be sequence 1 (first)
        trialSeg.name = 'Trial';
        trialSeg.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_TRIAL;
        Date trialStart = request.segments[0].startDate.addDays(-30);
        trialSeg.startDate = trialStart;
        trialSeg.endDate = trialStart.addDays(29);
        trialSeg.discountPercent = 100;
        
        // Adjust yearly segments sequences and dates
        request.segments[0].sequence = 2;
        request.segments[0].startDate = trialSeg.endDate.addDays(1);
        request.segments[0].endDate = request.segments[0].startDate.addMonths(12).addDays(-1);
        request.segments[1].sequence = 3;
        request.segments[1].startDate = request.segments[0].endDate.addDays(1);
        request.segments[1].endDate = request.segments[1].startDate.addMonths(12).addDays(-1);
        
        // Insert trial as first element
        request.segments.add(0, trialSeg);
        
        RLM_RampScheduleService service = new RLM_RampScheduleService();
        
        Test.setMock(HttpCalloutMock.class, new RampApiMock());
        Test.startTest();
        RLM_RampScheduleResponse response = service.execute(request);
        Test.stopTest();
        
        System.assertEquals(true, response.success, 'Creation should succeed');
        System.assertEquals(1, response.data.segmentGroupIds.size(), 'Synchronous response includes segment 0 only');
    }
    
    /**
     * @description Test creation with pro-rata segment
     */
    @isTest
    static void testCreationWithProRataSegment() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        
        // Add pro-rata as last segment
        RLM_RampScheduleRequest.SegmentDefinition proRata = new RLM_RampScheduleRequest.SegmentDefinition();
        proRata.sequence = 3;
        proRata.name = 'Pro-Rata';
        proRata.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_PRORATA;
        proRata.startDate = request.segments[1].endDate.addDays(1);
        proRata.endDate = proRata.startDate.addDays(9);
        proRata.discountPercent = 0;
        request.segments.add(proRata);
        
        RLM_RampScheduleService service = new RLM_RampScheduleService();
        
        Test.setMock(HttpCalloutMock.class, new RampApiMock());
        Test.startTest();
        RLM_RampScheduleResponse response = service.execute(request);
        Test.stopTest();
        
        System.assertEquals(true, response.success, 'Creation should succeed');
        System.assertEquals(1, response.data.segmentGroupIds.size(), 'Synchronous response includes segment 0 only');
    }
    
    /**
     * @description Test rollback on DML exception
     */
    @isTest
    static void testRollbackOnDMLException() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        // Set invalid Quote ID to cause DML exception
        request.quoteId = '0Q000000000000AAA'; // Non-existent quote
        
        RLM_RampScheduleService service = new RLM_RampScheduleService();
        
        Test.startTest();
        RLM_RampScheduleResponse response = service.execute(request);
        Test.stopTest();
        
        // Should fail validation before DML, but if it gets past validation, DML should rollback
        System.assertEquals(false, response.success, 'Should fail');
        
        // Verify no records were created
        List<QuoteLineGroup> groups = [SELECT Id FROM QuoteLineGroup];
        System.assertEquals(0, groups.size(), 'No groups should be created');
    }
    
    /**
     * @description Test segment type mapping with fallback
     */
    @isTest
    static void testSegmentTypeMapping() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        RLM_RampScheduleService service = new RLM_RampScheduleService();
        
        Test.setMock(HttpCalloutMock.class, new RampApiMock());
        Test.startTest();
        RLM_RampScheduleResponse response = service.execute(request);
        Test.stopTest();
        
        System.assertEquals(true, response.success, 'Creation should succeed');
        
        // Only segment 0 is synchronously created; verify its SegmentType is mapped
        List<QuoteLineGroup> segmentGroups = [
            SELECT Id, SegmentType, Description
            FROM QuoteLineGroup 
            WHERE ParentQuoteLineGroupId = :response.data.rampScheduleGroupId
            ORDER BY StartDate
        ];
        System.assertEquals(1, segmentGroups.size(), 'Segment 0 created synchronously');
        System.assertNotEquals(null, segmentGroups[0].SegmentType, 'SegmentType should be set on segment 0');
    }

    /**
     * @description Mock for HTTP callouts made by RLM_RampMigrationQueueable.
     * Handles both Place Sales Transaction (/place) and Clone Sales Transaction (/clone)
     * endpoints so the Queueable can run in the test context without hitting live APIs.
     * Note: CloneSalesTransaction returns the quote ID as salesTransactionId; the Queueable
     * then uses SOQL to find the new group. In unit tests no group is actually created by
     * the mock, so the SOQL returns nothing and the Queueable exits gracefully.
     */
    private class RampApiMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setStatusCode(200);
            res.setHeader('Content-Type', 'application/json');
            if (req.getEndpoint().contains('/clone')) {
                res.setBody('{"success":true,"errors":[],"requestId":null,"salesTransactionId":"mockQuoteId"}');
            } else {
                res.setBody('{"isSuccess":true,"errorResponse":[],"contextDetails":{"contextId":"","isBuiltInTransaction":false},"salesTransactionId":"mockQuoteId"}');
            }
            return res;
        }
    }

    /**
     * @description Verifies that existing QuoteLineItems are moved to segment 0 via DML,
     * and that the Queueable is enqueued and completes without error.
     *
     * Phase 1 (sync): QLI is moved to segment 0 with correct dates, discount, PeriodBoundary.
     * Phase 2 (async Queueable): EditGroup + CloneSalesTransaction × 1 + EditRampSchedule.
     *   The mock handles /place and /clone. CloneSalesTransaction does not create real groups
     *   in unit tests, so the Queueable logs a warning and exits after the clone call — this
     *   is expected and safe. Full multi-segment creation is verified in integration tests.
     */
    @isTest
    static void testExistingLineItemsMigratedToFirstSegment() {
        Id quoteId = getTestQuoteId();

        // Minimal product hierarchy required for QuoteLineItem
        Id standardPricebookId = Test.getStandardPricebookId();
        Product2 product = new Product2(Name = 'Test Product', IsActive = true);
        insert product;
        PricebookEntry pbe = new PricebookEntry(
            Pricebook2Id = standardPricebookId,
            Product2Id = product.Id,
            UnitPrice = 100,
            IsActive = true
        );
        insert pbe;
        update new Quote(Id = quoteId, Pricebook2Id = standardPricebookId);

        QuoteLineItem qli = new QuoteLineItem(
            QuoteId = quoteId,
            PricebookEntryId = pbe.Id,
            Quantity = 1,
            UnitPrice = 100
        );
        insert qli;

        System.assertEquals(
            null,
            [SELECT QuoteLineGroupId FROM QuoteLineItem WHERE Id = :qli.Id].QuoteLineGroupId,
            'Line item should start ungrouped'
        );

        // Register mock before startTest so it's available to the Queueable
        Test.setMock(HttpCalloutMock.class, new RampApiMock());

        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.quoteId = quoteId;
        RLM_RampScheduleService service = new RLM_RampScheduleService();

        Test.startTest();
        RLM_RampScheduleResponse response = service.execute(request);
        // stopTest flushes the enqueued Queueable synchronously
        Test.stopTest();

        System.assertEquals(true, response.success, 'Creation should succeed');

        // Phase 1 assertions: original QLI must be in segment 0 with correct fields
        QuoteLineItem updatedQli = [
            SELECT QuoteLineGroupId, StartDate, EndDate, Discount, PeriodBoundary
            FROM QuoteLineItem WHERE Id = :qli.Id
        ];

        // Segment 0 is the only synchronously-created group under the parent
        List<QuoteLineGroup> segs = [
            SELECT Id, StartDate, EndDate FROM QuoteLineGroup
            WHERE ParentQuoteLineGroupId = :response.data.rampScheduleGroupId
            ORDER BY StartDate
        ];
        System.assertEquals(1, segs.size(), 'Segment 0 created synchronously');

        System.assertNotEquals(null, updatedQli.QuoteLineGroupId,
            'Original QLI must be assigned to a segment group');
        System.assertEquals(segs[0].Id, updatedQli.QuoteLineGroupId,
            'Original QLI must be in segment 0');
        System.assertEquals(segs[0].StartDate, updatedQli.StartDate,
            'QLI StartDate must match segment 0 StartDate');
        System.assertEquals(segs[0].EndDate, updatedQli.EndDate,
            'QLI EndDate must match segment 0 EndDate');
        System.assertEquals('Anniversary', updatedQli.PeriodBoundary,
            'PeriodBoundary must default to Anniversary');

        // Phase 2 (Queueable) called EditGroup and attempted CloneSalesTransaction.
        // RampIdentifier/SegmentIdentifier and multi-segment creation are
        // verified in integration tests against the live org.
    }
}