/**
 * @description Test class for RLM_RampScheduleValidator
 * Tests all validation scenarios including field-level, structural, and business rule validations
 */
@isTest
private class RLM_RampScheduleValidatorTest {
    
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
     * @description Test valid request passes validation
     */
    @isTest
    static void testValidRequest() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertEquals(0, errors.size(), 'Valid request should have no errors');
    }
    
    /**
     * @description Test invalid action
     */
    @isTest
    static void testInvalidAction() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.action = 'INVALID';
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_ACTION, errors[0].code);
    }
    
    /**
     * @description Test blank action
     */
    @isTest
    static void testBlankAction() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.action = null;
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_ACTION, errors[0].code);
    }
    
    /**
     * @description Test invalid quote ID
     */
    @isTest
    static void testInvalidQuoteId() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.quoteId = '001000000000000AAA'; // Invalid Quote ID format
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_QUOTE_ID, errors[0].code);
    }
    
    /**
     * @description Test blank quote ID
     */
    @isTest
    static void testBlankQuoteId() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.quoteId = null;
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_QUOTE_ID, errors[0].code);
    }
    
    /**
     * @description Test non-existent quote ID
     */
    @isTest
    static void testNonExistentQuoteId() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.quoteId = '0Q000000000000AAA'; // Valid format but non-existent
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_QUOTE_ID, errors[0].code);
    }
    
    /**
     * @description Test empty segments
     */
    @isTest
    static void testEmptySegments() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.segments = new List<RLM_RampScheduleRequest.SegmentDefinition>();
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_EMPTY_SCHEDULE, errors[0].code);
    }
    
    /**
     * @description Test null segments
     */
    @isTest
    static void testNullSegments() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.segments = null;
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_EMPTY_SCHEDULE, errors[0].code);
    }
    
    /**
     * @description Test missing start date
     */
    @isTest
    static void testMissingStartDate() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.segments[0].startDate = null;
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_DATE, errors[0].code);
    }
    
    /**
     * @description Test missing end date
     */
    @isTest
    static void testMissingEndDate() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.segments[0].endDate = null;
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_DATE, errors[0].code);
    }
    
    /**
     * @description Test invalid date range (end before start)
     */
    @isTest
    static void testInvalidDateRange() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.segments[0].endDate = request.segments[0].startDate.addDays(-1);
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_DATE_RANGE, errors[0].code);
    }
    
    /**
     * @description Test invalid discount percent (negative)
     */
    @isTest
    static void testInvalidDiscountNegative() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.segments[0].discountPercent = -1;
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_DISCOUNT, errors[0].code);
    }
    
    /**
     * @description Test invalid discount percent (over 100)
     */
    @isTest
    static void testInvalidDiscountOver100() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.segments[0].discountPercent = 101;
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_DISCOUNT, errors[0].code);
    }
    
    /**
     * @description Test invalid uplift percent (negative)
     */
    @isTest
    static void testInvalidUpliftNegative() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.segments[0].upliftPercent = -1;
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_UPLIFT, errors[0].code);
    }
    
    /**
     * @description Test invalid uplift percent (over 100)
     */
    @isTest
    static void testInvalidUpliftOver100() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        request.segments[0].upliftPercent = 101;
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_UPLIFT, errors[0].code);
    }
    
    /**
     * @description Test segment gap
     */
    @isTest
    static void testSegmentGap() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        // Create a gap between segments
        request.segments[1].startDate = request.segments[0].endDate.addDays(5);
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_SEGMENT_DISCONTINUITY, errors[0].code);
    }
    
    /**
     * @description Test segment overlap
     */
    @isTest
    static void testSegmentOverlap() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        // Create an overlap
        request.segments[1].startDate = request.segments[0].endDate.addDays(-5);
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_SEGMENT_DISCONTINUITY, errors[0].code);
    }
    
    /**
     * @description Test multiple trial segments (should fail)
     */
    @isTest
    static void testMultipleTrialSegments() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        
        // Add a trial segment
        RLM_RampScheduleRequest.SegmentDefinition trialSeg = new RLM_RampScheduleRequest.SegmentDefinition();
        trialSeg.sequence = 0;
        trialSeg.name = 'Trial';
        trialSeg.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_TRIAL;
        Date trialStart = request.segments[0].startDate.addDays(-30);
        trialSeg.startDate = trialStart;
        trialSeg.endDate = trialStart.addDays(29);
        request.segments.add(trialSeg);
        
        // Add another trial segment
        RLM_RampScheduleRequest.SegmentDefinition trialSeg2 = new RLM_RampScheduleRequest.SegmentDefinition();
        trialSeg2.sequence = 3;
        trialSeg2.name = 'Trial 2';
        trialSeg2.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_TRIAL;
        trialSeg2.startDate = request.segments[1].endDate.addDays(1);
        trialSeg2.endDate = trialSeg2.startDate.addDays(29);
        request.segments.add(trialSeg2);
        
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_TRIAL_CONFIG, errors[0].code);
    }
    
    /**
     * @description Test trial segment not first (should fail)
     */
    @isTest
    static void testTrialNotFirst() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        
        // Add a trial segment with sequence 2 (not first) but properly aligned dates
        RLM_RampScheduleRequest.SegmentDefinition trialSeg = new RLM_RampScheduleRequest.SegmentDefinition();
        trialSeg.sequence = 2;
        trialSeg.name = 'Trial';
        trialSeg.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_TRIAL;
        // Position it between segments 1 and 2, maintaining continuity
        Date trialStart = request.segments[0].endDate.addDays(1);
        trialSeg.startDate = trialStart;
        trialSeg.endDate = trialStart.addDays(29);
        // Adjust segment 2 to start after trial
        request.segments[1].startDate = trialSeg.endDate.addDays(1);
        request.segments[1].endDate = request.segments[1].startDate.addMonths(12).addDays(-1);
        request.segments.add(trialSeg);
        
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        // Check if ERROR_INVALID_TRIAL_CONFIG exists in the errors list
        Boolean foundTrialError = false;
        for (RLM_RampScheduleResponse.ApiError err : errors) {
            if (err.code == RLM_RampScheduleResponse.ERROR_INVALID_TRIAL_CONFIG) {
                foundTrialError = true;
                break;
            }
        }
        System.assertEquals(true, foundTrialError, 'Should have INVALID_TRIAL_CONFIG error');
    }
    
    /**
     * @description Test valid trial segment (first segment)
     */
    @isTest
    static void testValidTrialSegment() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        
        // Add a trial segment as first segment (sequence 1, but before yearly segments)
        RLM_RampScheduleRequest.SegmentDefinition trialSeg = new RLM_RampScheduleRequest.SegmentDefinition();
        trialSeg.sequence = 1; // Set as first sequence
        trialSeg.name = 'Trial';
        trialSeg.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_TRIAL;
        Date trialStart = request.segments[0].startDate.addDays(-30);
        trialSeg.startDate = trialStart;
        trialSeg.endDate = trialStart.addDays(29);
        
        // Adjust yearly segments to start after trial and update their sequences
        request.segments[0].sequence = 2;
        request.segments[0].startDate = trialSeg.endDate.addDays(1);
        request.segments[0].endDate = request.segments[0].startDate.addMonths(12).addDays(-1);
        request.segments[1].sequence = 3;
        request.segments[1].startDate = request.segments[0].endDate.addDays(1);
        request.segments[1].endDate = request.segments[1].startDate.addMonths(12).addDays(-1);
        
        // Insert trial as first element
        request.segments.add(0, trialSeg);
        
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertEquals(0, errors.size(), 'Valid trial segment should pass validation');
    }
    
    /**
     * @description Test multiple pro-rata segments (should fail)
     */
    @isTest
    static void testMultipleProRataSegments() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        
        // Add pro-rata as first non-trial
        RLM_RampScheduleRequest.SegmentDefinition proRata1 = new RLM_RampScheduleRequest.SegmentDefinition();
        proRata1.sequence = 0;
        proRata1.name = 'Pro-Rata 1';
        proRata1.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_PRORATA;
        Date prStart = request.segments[0].startDate.addDays(-10);
        proRata1.startDate = prStart;
        proRata1.endDate = prStart.addDays(9);
        request.segments.add(proRata1);
        
        // Add another pro-rata as last
        RLM_RampScheduleRequest.SegmentDefinition proRata2 = new RLM_RampScheduleRequest.SegmentDefinition();
        proRata2.sequence = 3;
        proRata2.name = 'Pro-Rata 2';
        proRata2.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_PRORATA;
        proRata2.startDate = request.segments[1].endDate.addDays(1);
        proRata2.endDate = proRata2.startDate.addDays(9);
        request.segments.add(proRata2);
        
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INVALID_PRORATA_POSITION, errors[0].code);
    }
    
    /**
     * @description Test pro-rata segment in wrong position (should fail)
     */
    @isTest
    static void testProRataWrongPosition() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        
        // Add pro-rata in the middle (not first non-trial, not last) but maintain continuity
        RLM_RampScheduleRequest.SegmentDefinition proRata = new RLM_RampScheduleRequest.SegmentDefinition();
        proRata.sequence = 2;
        proRata.name = 'Pro-Rata';
        proRata.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_PRORATA;
        proRata.startDate = request.segments[0].endDate.addDays(1);
        proRata.endDate = proRata.startDate.addDays(9);
        // Adjust segment 2 to start after pro-rata
        request.segments[1].startDate = proRata.endDate.addDays(1);
        request.segments[1].endDate = request.segments[1].startDate.addMonths(12).addDays(-1);
        request.segments.add(proRata);
        
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        // Check if ERROR_INVALID_PRORATA_POSITION exists in the errors list
        Boolean foundProRataError = false;
        for (RLM_RampScheduleResponse.ApiError err : errors) {
            if (err.code == RLM_RampScheduleResponse.ERROR_INVALID_PRORATA_POSITION) {
                foundProRataError = true;
                break;
            }
        }
        System.assertEquals(true, foundProRataError, 'Should have INVALID_PRORATA_POSITION error');
    }
    
    /**
     * @description Test valid pro-rata segment (as last)
     */
    @isTest
    static void testValidProRataAsLast() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        
        // Add pro-rata as last segment
        RLM_RampScheduleRequest.SegmentDefinition proRata = new RLM_RampScheduleRequest.SegmentDefinition();
        proRata.sequence = 3;
        proRata.name = 'Pro-Rata';
        proRata.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_PRORATA;
        proRata.startDate = request.segments[1].endDate.addDays(1);
        proRata.endDate = proRata.startDate.addDays(9);
        request.segments.add(proRata);
        
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertEquals(0, errors.size(), 'Valid pro-rata segment should pass validation');
    }
    
    /**
     * @description Test mixing yearly and custom segments (should fail)
     */
    @isTest
    static void testMixingYearlyAndCustom() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        
        // Change second segment to custom
        request.segments[1].segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_CUSTOM;
        
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        System.assertEquals(RLM_RampScheduleResponse.ERROR_INCOMPATIBLE_SEGMENT_TYPES, errors[0].code);
    }
    
    /**
     * @description Test invalid yearly duration (not exactly 12 months)
     */
    @isTest
    static void testInvalidYearlyDuration() {
        RLM_RampScheduleRequest request = createValidYearlyRequest();
        
        // Make yearly segment 11 months instead of 12, but maintain continuity with next segment
        request.segments[0].endDate = request.segments[0].startDate.addMonths(11).addDays(-1);
        // Adjust segment 2 to start after segment 1 (maintain continuity)
        request.segments[1].startDate = request.segments[0].endDate.addDays(1);
        request.segments[1].endDate = request.segments[1].startDate.addMonths(12).addDays(-1);
        
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertNotEquals(0, errors.size(), 'Should have validation errors');
        // Check if ERROR_INVALID_YEARLY_DURATION exists in the errors list
        Boolean foundYearlyDurationError = false;
        for (RLM_RampScheduleResponse.ApiError err : errors) {
            if (err.code == RLM_RampScheduleResponse.ERROR_INVALID_YEARLY_DURATION) {
                foundYearlyDurationError = true;
                break;
            }
        }
        System.assertEquals(true, foundYearlyDurationError, 'Should have INVALID_YEARLY_DURATION error');
    }
    
    /**
     * @description Test valid custom schedule
     */
    @isTest
    static void testValidCustomSchedule() {
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
        
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertEquals(0, errors.size(), 'Valid custom schedule should pass validation');
    }
    
    /**
     * @description Staggered Ramp: overlapping segments and co-term yearly end dates should pass (continuity and yearly duration checks skipped)
     */
    @isTest
    static void testStaggeredRampPassesWithCoTermSegments() {
        Id quoteId = getTestQuoteId();
        Date startDate = Date.today().addDays(10);
        Date coTermEnd = startDate.addMonths(48).addDays(-1);
        
        RLM_RampScheduleRequest request = new RLM_RampScheduleRequest();
        request.quoteId = quoteId;
        request.action = RLM_RampScheduleRequest.ACTION_CREATE;
        
        request.scheduleHeader = new RLM_RampScheduleRequest.ScheduleHeader();
        request.scheduleHeader.scheduleName = 'Staggered Ramp Schedule';
        request.scheduleHeader.scheduleType = RLM_RampScheduleRequest.SCHEDULE_TYPE_YEARLY;
        request.scheduleHeader.rampMode = 'Staggered Ramp';
        
        request.segments = new List<RLM_RampScheduleRequest.SegmentDefinition>();
        
        // Year 1: staggered start, co-term end (would fail yearly duration in Standard Ramp)
        RLM_RampScheduleRequest.SegmentDefinition seg1 = new RLM_RampScheduleRequest.SegmentDefinition();
        seg1.sequence = 1;
        seg1.name = 'Year 1';
        seg1.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY;
        seg1.startDate = startDate;
        seg1.endDate = coTermEnd;
        seg1.discountPercent = 0;
        request.segments.add(seg1);
        
        // Year 2: starts after Year 1 start (overlap with Year 1), same co-term end (would fail continuity in Standard Ramp)
        RLM_RampScheduleRequest.SegmentDefinition seg2 = new RLM_RampScheduleRequest.SegmentDefinition();
        seg2.sequence = 2;
        seg2.name = 'Year 2';
        seg2.segmentType = RLM_RampScheduleRequest.SEGMENT_TYPE_YEARLY;
        seg2.startDate = startDate.addMonths(12);
        seg2.endDate = coTermEnd;
        seg2.discountPercent = 0;
        request.segments.add(seg2);
        
        RLM_RampScheduleValidator validator = new RLM_RampScheduleValidator();
        
        Test.startTest();
        List<RLM_RampScheduleResponse.ApiError> errors = validator.validate(request);
        Test.stopTest();
        
        System.assertEquals(0, errors.size(), 'Staggered Ramp with co-term segments should pass (continuity and yearly duration skipped)');
    }
}