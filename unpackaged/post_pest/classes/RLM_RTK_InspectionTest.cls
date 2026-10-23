@IsTest
private class RLM_RTK_InspectionTest {
    private static RLM_RTK_Finding__c finding(String pest, String evidence, String severity) {
        return new RLM_RTK_Finding__c(Zone__c = 'Garage', Pest__c = pest, Evidence__c = evidence, Severity__c = severity);
    }

    private static Id newInspection() {
        Account acct = new Account(Name = 'Inspection Test');
        insert acct;
        RLM_RTK_Inspection__c insp = new RLM_RTK_Inspection__c(Account__c = acct.Id);
        insert insp;
        return insp.Id;
    }

    private static RLM_RTK_Inspection.FindingInput input(String zone, String pest, String evidence, String severity) {
        RLM_RTK_Inspection.FindingInput f = new RLM_RTK_Inspection.FindingInput();
        f.zone = zone;
        f.pest = pest;
        f.evidence = evidence;
        f.severity = severity;
        f.customerNote = 'Seen near the door';
        return f;
    }

    @IsTest
    static void noFindingsRecommendsEssential() {
        RLM_RTK_Inspection.Recommendation rec = RLM_RTK_Inspection.recommend(new List<RLM_RTK_Finding__c>());
        Assert.areEqual(RLM_RTK_Inspection.ESSENTIAL, rec.planSku);
        Assert.areEqual('Light', rec.severity);
        Assert.isFalse(rec.includeMosquito);
        Assert.isFalse(rec.includeTermite);
        Assert.areEqual(1, rec.reasons.size());
    }

    @IsTest
    static void rodentFindingRecommendsHomeProtection() {
        RLM_RTK_Inspection.Recommendation rec = RLM_RTK_Inspection.recommend(
            new List<RLM_RTK_Finding__c>{ finding('Rodents', 'Droppings', 'Moderate') }
        );
        Assert.areEqual(RLM_RTK_Inspection.HOME_PROT, rec.planSku);
        Assert.areEqual('Moderate', rec.severity);
        Assert.areEqual('Garage: rodents droppings (moderate)', rec.reasons[0].because[0]);
    }

    @IsTest
    static void heavyRodentsRecommendPlus() {
        RLM_RTK_Inspection.Recommendation rec = RLM_RTK_Inspection.recommend(
            new List<RLM_RTK_Finding__c>{ finding('Rodents', 'Entry Point', 'Heavy') }
        );
        Assert.areEqual(RLM_RTK_Inspection.HOME_PROT_PLUS, rec.planSku);
        Assert.areEqual('Heavy', rec.severity);
    }

    @IsTest
    static void heavyGeneralPestRecommendsHomeProtection() {
        RLM_RTK_Inspection.Recommendation rec = RLM_RTK_Inspection.recommend(
            new List<RLM_RTK_Finding__c>{ finding('Ants', 'Live Activity', 'Heavy') }
        );
        Assert.areEqual(RLM_RTK_Inspection.HOME_PROT, rec.planSku);
    }

    @IsTest
    static void termiteAndMosquitoAddOns() {
        RLM_RTK_Inspection.Recommendation rec = RLM_RTK_Inspection.recommend(
            new List<RLM_RTK_Finding__c>{
                finding(null, 'Wood-to-Soil Contact', 'Light'),
                finding('Mosquitoes', 'Standing Water', 'Moderate')
            }
        );
        Assert.areEqual(RLM_RTK_Inspection.ESSENTIAL, rec.planSku);
        Assert.isTrue(rec.includeTermite);
        Assert.isTrue(rec.includeMosquito);
        Assert.areEqual(3, rec.reasons.size());
        Assert.isTrue(rec.summary.contains('Termite Plan'));
    }

    @IsTest
    static void saveEditDeleteAndQuote() {
        Id inspectionId = newInspection();
        Test.startTest();
        RLM_RTK_Inspection.InspectionState state = RLM_RTK_Inspection.saveFinding(
            inspectionId,
            input('Kitchen', 'Rodents', 'Droppings', 'Moderate')
        );
        Assert.areEqual(1, state.findings.size());
        Assert.areEqual(RLM_RTK_Inspection.HOME_PROT, state.recommendation.planSku);

        Id findingId = state.findings[0].id;
        insert new ContentVersion(
            Title = 'photo',
            PathOnClient = 'photo.jpg',
            VersionData = Blob.valueOf('img'),
            FirstPublishLocationId = findingId
        );
        state = RLM_RTK_Inspection.getState(inspectionId);
        Assert.areEqual(1, state.findings[0].photos.size());

        RLM_RTK_Inspection.FindingInput edit = input('Kitchen', 'Rodents', 'Droppings', 'Heavy');
        edit.id = findingId;
        state = RLM_RTK_Inspection.saveFinding(inspectionId, edit);
        Assert.areEqual(RLM_RTK_Inspection.HOME_PROT_PLUS, state.recommendation.planSku);

        RLM_RTK_Inspection__c insp = [
            SELECT Recommended_Plan__c, Overall_Severity__c FROM RLM_RTK_Inspection__c WHERE Id = :inspectionId
        ];
        Assert.areEqual(RLM_RTK_Inspection.HOME_PROT_PLUS, insp.Recommended_Plan__c);
        Assert.areEqual('Heavy', insp.Overall_Severity__c);

        state = RLM_RTK_Inspection.deleteFinding(inspectionId, findingId);
        Assert.areEqual(0, state.findings.size());
        Assert.areEqual(0, [SELECT COUNT() FROM ContentDocument WHERE Title = 'photo']);

        RLM_RTK_Inspection.markQuoted(inspectionId, null, 'Customer asked for the smaller plan');
        Test.stopTest();

        insp = [SELECT Status__c, Override_Reason__c FROM RLM_RTK_Inspection__c WHERE Id = :inspectionId];
        Assert.areEqual('Quoted', insp.Status__c);
        Assert.areEqual('Customer asked for the smaller plan', insp.Override_Reason__c);
    }

    @IsTest
    static void quoteFindingsHideInternalNotes() {
        Id inspectionId = newInspection();
        RLM_RTK_Inspection.FindingInput f = input('Yard', 'Mosquitoes', 'Standing Water', 'Light');
        f.internalNote = 'Upsell termite next visit';
        RLM_RTK_Inspection.saveFinding(inspectionId, f);

        Assert.isNull(RLM_RTK_Inspection.getQuoteFindings(null));
        Id accountId = [SELECT Account__c FROM RLM_RTK_Inspection__c WHERE Id = :inspectionId].Account__c;
        Opportunity opp = new Opportunity(
            Name = 'Inspection Quote', AccountId = accountId, StageName = 'Prospecting', CloseDate = Date.today()
        );
        insert opp;
        Quote q = new Quote(Name = 'Inspection Quote', OpportunityId = opp.Id);
        insert q;
        RLM_RTK_Inspection.markQuoted(inspectionId, q.Id, null);

        RLM_RTK_Inspection.InspectionState state = RLM_RTK_Inspection.getQuoteFindings(q.Id);
        Assert.areEqual(1, state.findings.size());
        Assert.isNull(state.findings[0].internalNote);
        Assert.isNull(state.findings[0].recommendedProductName, 'Mosquito plan is not on the quote');
        Assert.isNotNull(state.inspectionName);
        Assert.areEqual(
            'Mosquitoes – Standing Water',
            [SELECT Observation__c FROM RLM_RTK_Finding__c WHERE Inspection__c = :inspectionId].Observation__c
        );
    }

    @IsTest
    static void workOrderTreatmentAndAfterPhotos() {
        Id inspectionId = newInspection();
        RLM_RTK_Inspection.InspectionState walk = RLM_RTK_Inspection.saveFinding(
            inspectionId,
            input('Garage', 'Rodents', 'Droppings', 'Moderate')
        );
        Id findingId = walk.findings[0].id;
        insert new ContentVersion(
            Title = 'before', PathOnClient = 'before.jpg', VersionData = Blob.valueOf('b'),
            FirstPublishLocationId = findingId
        );
        Id accountId = [SELECT Account__c FROM RLM_RTK_Inspection__c WHERE Id = :inspectionId].Account__c;
        WorkOrder wo = new WorkOrder(Subject = 'Initial Pest Treatment', AccountId = accountId, RLM_RTK_Inspection__c = inspectionId);
        insert wo;

        Assert.isNull(RLM_RTK_Inspection.getWorkOrderFindings(null));
        Test.startTest();
        RLM_RTK_Inspection.InspectionState state = RLM_RTK_Inspection.getWorkOrderFindings(wo.Id);
        Assert.areEqual(1, state.findings.size());
        Assert.areEqual('Open', state.findings[0].treatmentStatus);
        Assert.areEqual(0, state.treatedCount);

        state = RLM_RTK_Inspection.saveTreatment(wo.Id, findingId, 'Treated', 'Set 4 stations');
        Assert.areEqual(1, state.treatedCount);
        Assert.areEqual('Set 4 stations', state.findings[0].treatmentNote);
        Assert.isNotNull(state.findings[0].treatedOn);

        ContentVersion after = new ContentVersion(
            Title = 'after', PathOnClient = 'after.jpg', VersionData = Blob.valueOf('a'),
            FirstPublishLocationId = findingId
        );
        insert after;
        Id afterDoc = [SELECT ContentDocumentId FROM ContentVersion WHERE Id = :after.Id].ContentDocumentId;
        state = RLM_RTK_Inspection.tagAfterPhotos(wo.Id, findingId, new List<Id>{ afterDoc });
        Test.stopTest();

        Assert.areEqual(1, state.findings[0].photos.size());
        Assert.areEqual(1, state.findings[0].afterPhotos.size());
        Assert.areEqual('After', state.findings[0].afterPhotos[0].stage);
    }

    @IsTest
    static void treatmentRejectsFindingFromAnotherInspection() {
        Id inspectionId = newInspection();
        Id otherFinding = RLM_RTK_Inspection.saveFinding(newInspection(), input('Yard', 'Ants', null, 'Light'))
            .findings[0].id;
        WorkOrder wo = new WorkOrder(Subject = 'Initial Pest Treatment', RLM_RTK_Inspection__c = inspectionId);
        insert wo;
        try {
            RLM_RTK_Inspection.saveTreatment(wo.Id, otherFinding, 'Treated', null);
            Assert.fail('Expected the finding to be rejected');
        } catch (AuraHandledException e) {
            Assert.isTrue(e.getMessage().contains('not part of this work order'), e.getMessage());
        }
    }

    @IsTest
    static void saveErrorsSurfaceAsAuraException() {
        try {
            RLM_RTK_Inspection.saveFinding(newInspection(), input('Kitchen', 'Not A Pest', null, 'Light'));
            Assert.fail('Expected an exception for a restricted picklist value');
        } catch (AuraHandledException e) {
            Assert.isNotNull(e.getMessage());
        }
    }
}
