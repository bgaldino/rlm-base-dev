/**
 * @description Test class for RLM_RampScheduleFlowAction
 * Tests @InvocableMethod for Flow integration
 */
@isTest
private class RLM_RampScheduleFlowActionTest {
    
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
     * @description Test successful execution via Flow action
     */
    @isTest
    static void testSuccessfulExecution() {
        Id quoteId = getTestQuoteId();
        Date startDate = Date.today().addDays(10);
        
        List<Map<String, Object>> segments = new List<Map<String, Object>>();
        Map<String, Object> seg1 = new Map<String, Object>();
        seg1.put('sequence', 1);
        seg1.put('name', 'Year 1');
        seg1.put('segmentType', RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY);
        seg1.put('startDate', String.valueOf(startDate));
        seg1.put('endDate', String.valueOf(startDate.addMonths(12).addDays(-1)));
        seg1.put('discountPercent', 10);
        seg1.put('upliftPercent', 5);
        segments.add(seg1);
        
        Map<String, Object> seg2 = new Map<String, Object>();
        seg2.put('sequence', 2);
        seg2.put('name', 'Year 2');
        seg2.put('segmentType', RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY);
        seg2.put('startDate', String.valueOf(startDate.addMonths(12)));
        seg2.put('endDate', String.valueOf(startDate.addMonths(24).addDays(-1)));
        seg2.put('discountPercent', 5);
        segments.add(seg2);
        
        String segmentsJson = JSON.serialize(segments);
        
        RLM_RampScheduleFlowAction.FlowInput input = new RLM_RampScheduleFlowAction.FlowInput();
        input.quoteId = quoteId;
        input.scheduleName = 'Test Flow Schedule';
        input.scheduleType = RLM_RampScheduleRequest.SCHEDULE_TYPE_YEARLY;
        input.segmentsJson = segmentsJson;
        input.action = RLM_RampScheduleRequest.ACTION_CREATE;
        
        List<RLM_RampScheduleFlowAction.FlowInput> inputs = new List<RLM_RampScheduleFlowAction.FlowInput>();
        inputs.add(input);
        
        Test.startTest();
        List<RLM_RampScheduleFlowAction.FlowOutput> outputs = RLM_RampScheduleFlowAction.execute(inputs);
        Test.stopTest();
        
        System.assertEquals(1, outputs.size(), 'Should have one output');
        System.assertEquals(true, outputs[0].success, 'Should succeed');
        System.assertNotEquals(null, outputs[0].rampScheduleGroupId, 'Should have parent group ID');
        System.assertNotEquals(null, outputs[0].segmentGroupIds, 'Should have segment group IDs');
        System.assertNotEquals(null, outputs[0].message, 'Should have message');
        
        // Verify records were created
        List<QuoteLineGroup> parentGroups = [
            SELECT Id FROM QuoteLineGroup 
            WHERE Id = :outputs[0].rampScheduleGroupId
        ];
        System.assertEquals(1, parentGroups.size(), 'Parent group should be created');
    }
    
    /**
     * @description Test validation action via Flow
     */
    @isTest
    static void testValidationAction() {
        Id quoteId = getTestQuoteId();
        Date startDate = Date.today().addDays(10);
        
        List<Map<String, Object>> segments = new List<Map<String, Object>>();
        Map<String, Object> seg1 = new Map<String, Object>();
        seg1.put('sequence', 1);
        seg1.put('name', 'Year 1');
        seg1.put('segmentType', RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY);
        seg1.put('startDate', String.valueOf(startDate));
        seg1.put('endDate', String.valueOf(startDate.addMonths(12).addDays(-1)));
        seg1.put('discountPercent', 10);
        segments.add(seg1);
        
        String segmentsJson = JSON.serialize(segments);
        
        RLM_RampScheduleFlowAction.FlowInput input = new RLM_RampScheduleFlowAction.FlowInput();
        input.quoteId = quoteId;
        input.scheduleName = 'Test Flow Schedule';
        input.scheduleType = RLM_RampScheduleRequest.SCHEDULE_TYPE_YEARLY;
        input.segmentsJson = segmentsJson;
        input.action = RLM_RampScheduleRequest.ACTION_VALIDATE;
        
        List<RLM_RampScheduleFlowAction.FlowInput> inputs = new List<RLM_RampScheduleFlowAction.FlowInput>();
        inputs.add(input);
        
        Test.startTest();
        List<RLM_RampScheduleFlowAction.FlowOutput> outputs = RLM_RampScheduleFlowAction.execute(inputs);
        Test.stopTest();
        
        System.assertEquals(1, outputs.size(), 'Should have one output');
        System.assertEquals(true, outputs[0].success, 'Validation should succeed');
        System.assertEquals(null, outputs[0].rampScheduleGroupId, 'Should not have parent group ID');
        
        // Verify no records were created
        List<QuoteLineGroup> groups = [SELECT Id FROM QuoteLineGroup];
        System.assertEquals(0, groups.size(), 'No groups should be created');
    }
    
    /**
     * @description Test failure scenario via Flow - throws so Flow fault connector shows Error screen
     */
    @isTest
    static void testFailureScenario() {
        Id quoteId = getTestQuoteId();
        
        List<Map<String, Object>> segments = new List<Map<String, Object>>();
        Map<String, Object> seg1 = new Map<String, Object>();
        seg1.put('sequence', 1);
        seg1.put('name', 'Year 1');
        seg1.put('segmentType', RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY);
        seg1.put('startDate', String.valueOf(Date.today()));
        seg1.put('endDate', String.valueOf(Date.today().addDays(-1))); // Invalid: end before start
        seg1.put('discountPercent', 10);
        segments.add(seg1);
        
        String segmentsJson = JSON.serialize(segments);
        
        RLM_RampScheduleFlowAction.FlowInput input = new RLM_RampScheduleFlowAction.FlowInput();
        input.quoteId = quoteId;
        input.scheduleName = 'Test Flow Schedule';
        input.scheduleType = RLM_RampScheduleRequest.SCHEDULE_TYPE_YEARLY;
        input.segmentsJson = segmentsJson;
        input.action = RLM_RampScheduleRequest.ACTION_CREATE;
        
        List<RLM_RampScheduleFlowAction.FlowInput> inputs = new List<RLM_RampScheduleFlowAction.FlowInput>();
        inputs.add(input);
        
        Test.startTest();
        Boolean threw = false;
        try {
            RLM_RampScheduleFlowAction.execute(inputs);
        } catch (RLM_RampScheduleFlowException e) {
            threw = true;
            System.assert(e.getMessage().length() > 0, 'Exception should carry error message');
        }
        Test.stopTest();
        
        System.assert(threw, 'Execute should throw RLM_RampScheduleFlowException when validation fails so Flow shows Error screen');
    }
    
    /**
     * @description Test bulk execution (multiple inputs)
     */
    @isTest
    static void testBulkExecution() {
        Id quoteId = getTestQuoteId();
        Date startDate = Date.today().addDays(10);
        
        // Create two valid requests
        List<Map<String, Object>> segments1 = new List<Map<String, Object>>();
        Map<String, Object> seg1 = new Map<String, Object>();
        seg1.put('sequence', 1);
        seg1.put('name', 'Year 1');
        seg1.put('segmentType', RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY);
        seg1.put('startDate', String.valueOf(startDate));
        seg1.put('endDate', String.valueOf(startDate.addMonths(12).addDays(-1)));
        seg1.put('discountPercent', 10);
        segments1.add(seg1);
        
        List<Map<String, Object>> segments2 = new List<Map<String, Object>>();
        Map<String, Object> seg2 = new Map<String, Object>();
        seg2.put('sequence', 1);
        seg2.put('name', 'Year 1');
        seg2.put('segmentType', RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY);
        seg2.put('startDate', String.valueOf(startDate.addDays(365)));
        seg2.put('endDate', String.valueOf(startDate.addDays(365).addMonths(12).addDays(-1)));
        seg2.put('discountPercent', 15);
        segments2.add(seg2);
        
        RLM_RampScheduleFlowAction.FlowInput input1 = new RLM_RampScheduleFlowAction.FlowInput();
        input1.quoteId = quoteId;
        input1.scheduleName = 'Test Flow Schedule 1';
        input1.scheduleType = RLM_RampScheduleRequest.SCHEDULE_TYPE_YEARLY;
        input1.segmentsJson = JSON.serialize(segments1);
        input1.action = RLM_RampScheduleRequest.ACTION_CREATE;
        
        RLM_RampScheduleFlowAction.FlowInput input2 = new RLM_RampScheduleFlowAction.FlowInput();
        input2.quoteId = quoteId;
        input2.scheduleName = 'Test Flow Schedule 2';
        input2.scheduleType = RLM_RampScheduleRequest.SCHEDULE_TYPE_YEARLY;
        input2.segmentsJson = JSON.serialize(segments2);
        input2.action = RLM_RampScheduleRequest.ACTION_CREATE;
        
        List<RLM_RampScheduleFlowAction.FlowInput> inputs = new List<RLM_RampScheduleFlowAction.FlowInput>();
        inputs.add(input1);
        inputs.add(input2);
        
        Test.startTest();
        List<RLM_RampScheduleFlowAction.FlowOutput> outputs = RLM_RampScheduleFlowAction.execute(inputs);
        Test.stopTest();
        
        System.assertEquals(2, outputs.size(), 'Should have two outputs');
        System.assertEquals(true, outputs[0].success, 'First should succeed');
        System.assertEquals(true, outputs[1].success, 'Second should succeed');
    }
    
    /**
     * @description Test default action (CREATE when not specified)
     */
    @isTest
    static void testDefaultAction() {
        Id quoteId = getTestQuoteId();
        Date startDate = Date.today().addDays(10);
        
        List<Map<String, Object>> segments = new List<Map<String, Object>>();
        Map<String, Object> seg1 = new Map<String, Object>();
        seg1.put('sequence', 1);
        seg1.put('name', 'Year 1');
        seg1.put('segmentType', RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY);
        seg1.put('startDate', String.valueOf(startDate));
        seg1.put('endDate', String.valueOf(startDate.addMonths(12).addDays(-1)));
        seg1.put('discountPercent', 10);
        segments.add(seg1);
        
        String segmentsJson = JSON.serialize(segments);
        
        RLM_RampScheduleFlowAction.FlowInput input = new RLM_RampScheduleFlowAction.FlowInput();
        input.quoteId = quoteId;
        input.scheduleName = 'Test Flow Schedule';
        input.scheduleType = RLM_RampScheduleRequest.SCHEDULE_TYPE_YEARLY;
        input.segmentsJson = segmentsJson;
        input.action = null; // Not specified, should default to CREATE
        
        List<RLM_RampScheduleFlowAction.FlowInput> inputs = new List<RLM_RampScheduleFlowAction.FlowInput>();
        inputs.add(input);
        
        Test.startTest();
        List<RLM_RampScheduleFlowAction.FlowOutput> outputs = RLM_RampScheduleFlowAction.execute(inputs);
        Test.stopTest();
        
        System.assertEquals(1, outputs.size(), 'Should have one output');
        System.assertEquals(true, outputs[0].success, 'Should succeed');
        System.assertNotEquals(null, outputs[0].rampScheduleGroupId, 'Should have parent group ID');
    }
}