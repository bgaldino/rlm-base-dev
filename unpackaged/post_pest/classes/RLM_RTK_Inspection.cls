/**
 * Field inspection for Rentokil residential pest. Stores findings (with photos as Files on each
 * finding) and turns them into a recommended plan, add-ons, and severity for RLM_RTK_FieldQuote.
 */
public with sharing class RLM_RTK_Inspection {
    public static final String ESSENTIAL = 'RTK-ESSENTIAL';
    public static final String HOME_PROT = 'RTK-HOME-PROT';
    public static final String HOME_PROT_PLUS = 'RTK-HOME-PROT-PLUS';
    public static final String MOSQUITO = 'RTK-MOSQUITO';
    public static final String TERMITE = 'RTK-TERMITE';

    private static final Map<String, String> PRODUCT_NAMES = new Map<String, String>{
        ESSENTIAL => 'Essential Pest Plan',
        HOME_PROT => 'Home Protection Plan',
        HOME_PROT_PLUS => 'Home Protection Plus',
        MOSQUITO => 'Seasonal Mosquito Plan',
        TERMITE => 'Termite Plan'
    };
    private static final Map<String, Integer> SEVERITY_RANK = new Map<String, Integer>{
        'Light' => 1, 'Moderate' => 2, 'Heavy' => 3
    };

    public class PhotoView {
        @AuraEnabled public Id versionId;
        @AuraEnabled public Id documentId;
        @AuraEnabled public String title;
        @AuraEnabled public String stage;
    }

    public class FindingView {
        @AuraEnabled public Id id;
        @AuraEnabled public String name;
        @AuraEnabled public String zone;
        @AuraEnabled public String pest;
        @AuraEnabled public String evidence;
        @AuraEnabled public String severity;
        @AuraEnabled public String customerNote;
        @AuraEnabled public String internalNote;
        @AuraEnabled public String recommendedProduct;
        @AuraEnabled public String recommendedProductName;
        @AuraEnabled public List<PhotoView> photos = new List<PhotoView>();
        @AuraEnabled public List<PhotoView> afterPhotos = new List<PhotoView>();
        @AuraEnabled public String treatmentStatus;
        @AuraEnabled public String treatmentNote;
        @AuraEnabled public Datetime treatedOn;
    }

    public class Reason {
        @AuraEnabled public String sku;
        @AuraEnabled public String productName;
        @AuraEnabled public List<String> because = new List<String>();
    }

    public class Recommendation {
        @AuraEnabled public String planSku;
        @AuraEnabled public String severity;
        @AuraEnabled public Boolean includeMosquito = false;
        @AuraEnabled public Boolean includeTermite = false;
        @AuraEnabled public List<Reason> reasons = new List<Reason>();
        @AuraEnabled public String summary;
    }

    public class InspectionState {
        @AuraEnabled public Id inspectionId;
        @AuraEnabled public String inspectionName;
        @AuraEnabled public Id workOrderId;
        @AuraEnabled public Integer treatedCount = 0;
        @AuraEnabled public List<FindingView> findings = new List<FindingView>();
        @AuraEnabled public Recommendation recommendation;
    }

    public class FindingInput {
        @AuraEnabled public Id id { get; set; }
        @AuraEnabled public String zone { get; set; }
        @AuraEnabled public String pest { get; set; }
        @AuraEnabled public String evidence { get; set; }
        @AuraEnabled public String severity { get; set; }
        @AuraEnabled public String customerNote { get; set; }
        @AuraEnabled public String internalNote { get; set; }
    }

    @AuraEnabled
    public static InspectionState getState(Id inspectionId) {
        return refresh(inspectionId);
    }

    /** Customer-facing view of the inspection behind a quote (no internal notes). Null when the quote has none. */
    @AuraEnabled(cacheable=true)
    public static InspectionState getQuoteFindings(Id quoteId) {
        if (quoteId == null) {
            return null;
        }
        List<RLM_RTK_Inspection__c> inspections = [
            SELECT Id, Name FROM RLM_RTK_Inspection__c WHERE Quote__c = :quoteId ORDER BY CreatedDate DESC LIMIT 1
        ];
        if (inspections.isEmpty()) {
            return null;
        }
        List<RLM_RTK_Finding__c> findings = queryFindings(inspections[0].Id);
        InspectionState state = buildState(inspections[0].Id, findings, recommend(findings));
        state.inspectionName = inspections[0].Name;
        Set<String> quotedSkus = new Set<String>();
        for (QuoteLineItem line : [SELECT Product2.StockKeepingUnit FROM QuoteLineItem WHERE QuoteId = :quoteId]) {
            quotedSkus.add(line.Product2.StockKeepingUnit);
        }
        for (FindingView v : state.findings) {
            v.internalNote = null;
            v.afterPhotos = new List<PhotoView>();
            if (!quotedSkus.contains(v.recommendedProduct)) {
                v.recommendedProductName = null;
            }
        }
        return state;
    }

    /** Technician view of the inspection a work order treats, including internal notes and after photos. */
    @AuraEnabled
    public static InspectionState getWorkOrderFindings(Id workOrderId) {
        Id inspectionId = inspectionFor(workOrderId);
        if (inspectionId == null) {
            return null;
        }
        List<RLM_RTK_Finding__c> findings = queryFindings(inspectionId);
        InspectionState state = buildState(inspectionId, findings, recommend(findings));
        state.workOrderId = workOrderId;
        state.inspectionName = [SELECT Name FROM RLM_RTK_Inspection__c WHERE Id = :inspectionId].Name;
        for (FindingView v : state.findings) {
            if (v.treatmentStatus == 'Treated') {
                state.treatedCount++;
            }
        }
        return state;
    }

    @AuraEnabled
    public static InspectionState saveTreatment(Id workOrderId, Id findingId, String status, String note) {
        try {
            requireFindingOnWorkOrder(workOrderId, findingId);
            update new RLM_RTK_Finding__c(
                Id = findingId,
                Treatment_Status__c = String.isBlank(status) ? 'Open' : status,
                Treatment_Note__c = note,
                Treated_On__c = Datetime.now()
            );
            return getWorkOrderFindings(workOrderId);
        } catch (Exception e) {
            throw auraError(e);
        }
    }

    /** Marks files just uploaded to a finding from the work order as After photos. */
    @AuraEnabled
    public static InspectionState tagAfterPhotos(Id workOrderId, Id findingId, List<Id> documentIds) {
        try {
            requireFindingOnWorkOrder(workOrderId, findingId);
            Set<Id> onFinding = new Set<Id>();
            for (ContentDocumentLink link : [
                SELECT ContentDocumentId FROM ContentDocumentLink
                WHERE LinkedEntityId = :findingId AND ContentDocumentId IN :documentIds
            ]) {
                onFinding.add(link.ContentDocumentId);
            }
            List<ContentVersion> versions = [
                SELECT Id FROM ContentVersion WHERE ContentDocumentId IN :onFinding AND IsLatest = true
            ];
            for (ContentVersion v : versions) {
                v.RLM_RTK_Photo_Stage__c = 'After';
            }
            update versions;
            return getWorkOrderFindings(workOrderId);
        } catch (Exception e) {
            throw auraError(e);
        }
    }

    private static Id inspectionFor(Id workOrderId) {
        if (workOrderId == null) {
            return null;
        }
        List<WorkOrder> orders = [
            SELECT RLM_RTK_Inspection__c, RLM_Order__r.QuoteId FROM WorkOrder WHERE Id = :workOrderId
        ];
        if (orders.isEmpty()) {
            return null;
        }
        if (orders[0].RLM_RTK_Inspection__c != null) {
            return orders[0].RLM_RTK_Inspection__c;
        }
        Id quoteId = orders[0].RLM_Order__r?.QuoteId;
        if (quoteId == null) {
            return null;
        }
        List<RLM_RTK_Inspection__c> inspections = [
            SELECT Id FROM RLM_RTK_Inspection__c WHERE Quote__c = :quoteId ORDER BY CreatedDate DESC LIMIT 1
        ];
        return inspections.isEmpty() ? null : inspections[0].Id;
    }

    private static void requireFindingOnWorkOrder(Id workOrderId, Id findingId) {
        Id inspectionId = inspectionFor(workOrderId);
        if (inspectionId == null
            || [SELECT COUNT() FROM RLM_RTK_Finding__c WHERE Id = :findingId AND Inspection__c = :inspectionId] == 0) {
            throw new InspectionException('That finding is not part of this work order\'s inspection.');
        }
    }

    private class InspectionException extends Exception {}

    private static AuraHandledException auraError(Exception e) {
        AuraHandledException error = new AuraHandledException(e.getMessage());
        error.setMessage(e.getMessage());
        return error;
    }

    @AuraEnabled
    public static InspectionState saveFinding(Id inspectionId, FindingInput finding) {
        try {
            RLM_RTK_Finding__c record = new RLM_RTK_Finding__c(
                Zone__c = finding.zone,
                Pest__c = finding.pest,
                Evidence__c = finding.evidence,
                Severity__c = String.isBlank(finding.severity) ? 'Light' : finding.severity,
                Customer_Note__c = finding.customerNote,
                Internal_Note__c = finding.internalNote
            );
            if (finding.id != null) {
                record.Id = finding.id;
                update record;
            } else {
                record.Inspection__c = inspectionId;
                insert record;
            }
            return refresh(inspectionId);
        } catch (Exception e) {
            throw auraError(e);
        }
    }

    @AuraEnabled
    public static InspectionState deleteFinding(Id inspectionId, Id findingId) {
        try {
            List<ContentDocumentLink> links = [
                SELECT ContentDocumentId FROM ContentDocumentLink WHERE LinkedEntityId = :findingId
            ];
            Set<Id> docIds = new Set<Id>();
            for (ContentDocumentLink link : links) {
                docIds.add(link.ContentDocumentId);
            }
            delete new RLM_RTK_Finding__c(Id = findingId);
            if (!docIds.isEmpty()) {
                delete [SELECT Id FROM ContentDocument WHERE Id IN :docIds];
            }
            return refresh(inspectionId);
        } catch (Exception e) {
            throw auraError(e);
        }
    }

    /** Recomputes the recommendation, stamps it on the inspection and findings, and returns the full state. */
    public static InspectionState refresh(Id inspectionId) {
        List<RLM_RTK_Finding__c> findings = queryFindings(inspectionId);
        Recommendation rec = recommend(findings);

        List<RLM_RTK_Finding__c> changed = new List<RLM_RTK_Finding__c>();
        for (RLM_RTK_Finding__c f : findings) {
            String sku = productFor(f, rec.planSku);
            if (f.Recommended_Product__c != sku) {
                f.Recommended_Product__c = sku;
                changed.add(f);
            }
        }
        update changed;
        update new RLM_RTK_Inspection__c(
            Id = inspectionId,
            Overall_Severity__c = rec.severity,
            Recommended_Plan__c = rec.planSku,
            Recommended_Mosquito__c = rec.includeMosquito,
            Recommended_Termite__c = rec.includeTermite,
            Recommendation_Summary__c = rec.summary
        );
        return buildState(inspectionId, findings, rec);
    }

    private static List<RLM_RTK_Finding__c> queryFindings(Id inspectionId) {
        return [
            SELECT Id, Name, Zone__c, Pest__c, Evidence__c, Severity__c, Customer_Note__c, Internal_Note__c,
                Recommended_Product__c, Treatment_Status__c, Treatment_Note__c, Treated_On__c
            FROM RLM_RTK_Finding__c
            WHERE Inspection__c = :inspectionId
            ORDER BY CreatedDate ASC
        ];
    }

    private static InspectionState buildState(Id inspectionId, List<RLM_RTK_Finding__c> findings, Recommendation rec) {
        InspectionState state = new InspectionState();
        state.inspectionId = inspectionId;
        state.recommendation = rec;
        Map<Id, FindingView> views = new Map<Id, FindingView>();
        for (RLM_RTK_Finding__c f : findings) {
            FindingView v = new FindingView();
            v.id = f.Id;
            v.name = f.Name;
            v.zone = f.Zone__c;
            v.pest = f.Pest__c;
            v.evidence = f.Evidence__c;
            v.severity = f.Severity__c;
            v.customerNote = f.Customer_Note__c;
            v.internalNote = f.Internal_Note__c;
            v.recommendedProduct = productFor(f, rec.planSku);
            v.recommendedProductName = PRODUCT_NAMES.get(v.recommendedProduct);
            v.treatmentStatus = String.isBlank(f.Treatment_Status__c) ? 'Open' : f.Treatment_Status__c;
            v.treatmentNote = f.Treatment_Note__c;
            v.treatedOn = f.Treated_On__c;
            views.put(f.Id, v);
            state.findings.add(v);
        }
        if (!views.isEmpty()) {
            for (ContentDocumentLink link : [
                SELECT LinkedEntityId, ContentDocumentId, ContentDocument.Title,
                    ContentDocument.LatestPublishedVersionId,
                    ContentDocument.LatestPublishedVersion.RLM_RTK_Photo_Stage__c
                FROM ContentDocumentLink
                WHERE LinkedEntityId IN :views.keySet()
                ORDER BY ContentDocument.CreatedDate ASC
            ]) {
                PhotoView p = new PhotoView();
                p.documentId = link.ContentDocumentId;
                p.versionId = link.ContentDocument.LatestPublishedVersionId;
                p.title = link.ContentDocument.Title;
                p.stage = link.ContentDocument.LatestPublishedVersion.RLM_RTK_Photo_Stage__c == 'After' ? 'After' : 'Before';
                FindingView v = views.get(link.LinkedEntityId);
                if (p.stage == 'After') {
                    v.afterPhotos.add(p);
                } else {
                    v.photos.add(p);
                }
            }
        }
        return state;
    }

    @TestVisible
    private static Recommendation recommend(List<RLM_RTK_Finding__c> findings) {
        Recommendation rec = new Recommendation();
        Integer maxRank = 1;
        Integer rodentFindings = 0;
        Boolean heavyGeneral = false;
        for (RLM_RTK_Finding__c f : findings) {
            Integer rank = SEVERITY_RANK.containsKey(f.Severity__c) ? SEVERITY_RANK.get(f.Severity__c) : 1;
            maxRank = Math.max(maxRank, rank);
            if (isTermite(f)) {
                rec.includeTermite = true;
            } else if (isMosquito(f)) {
                rec.includeMosquito = true;
            } else if (isRodent(f)) {
                rodentFindings++;
            } else if (rank == 3) {
                heavyGeneral = true;
            }
        }
        rec.severity = maxRank == 3 ? 'Heavy' : (maxRank == 2 ? 'Moderate' : 'Light');

        if (rodentFindings > 0 && (rec.severity == 'Heavy' || rodentFindings >= 3)) {
            rec.planSku = HOME_PROT_PLUS;
        } else if (rodentFindings > 0 || heavyGeneral) {
            rec.planSku = HOME_PROT;
        } else {
            rec.planSku = ESSENTIAL;
        }

        Map<String, Reason> bySku = new Map<String, Reason>();
        for (String sku : new List<String>{ rec.planSku, TERMITE, MOSQUITO }) {
            Reason r = new Reason();
            r.sku = sku;
            r.productName = PRODUCT_NAMES.get(sku);
            bySku.put(sku, r);
        }
        for (RLM_RTK_Finding__c f : findings) {
            bySku.get(productFor(f, rec.planSku)).because.add(describe(f));
        }
        if (bySku.get(rec.planSku).because.isEmpty()) {
            bySku.get(rec.planSku).because.add('No active activity found; preventive general pest coverage');
        }

        List<String> lines = new List<String>();
        for (String sku : new List<String>{ rec.planSku, TERMITE, MOSQUITO }) {
            Reason r = bySku.get(sku);
            if (!r.because.isEmpty()) {
                rec.reasons.add(r);
                lines.add(r.productName + ': ' + String.join(r.because, '; '));
            }
        }
        rec.summary = String.join(lines, '\n');
        return rec;
    }

    private static String productFor(RLM_RTK_Finding__c f, String planSku) {
        if (isTermite(f)) {
            return TERMITE;
        }
        if (isMosquito(f)) {
            return MOSQUITO;
        }
        return planSku;
    }

    private static Boolean isTermite(RLM_RTK_Finding__c f) {
        return f.Pest__c == 'Termites' || f.Evidence__c == 'Wood-to-Soil Contact';
    }

    private static Boolean isMosquito(RLM_RTK_Finding__c f) {
        return f.Pest__c == 'Mosquitoes' || f.Evidence__c == 'Standing Water';
    }

    private static Boolean isRodent(RLM_RTK_Finding__c f) {
        return f.Pest__c == 'Rodents' || f.Evidence__c == 'Entry Point';
    }

    private static String describe(RLM_RTK_Finding__c f) {
        List<String> what = new List<String>();
        if (String.isNotBlank(f.Pest__c)) {
            what.add(f.Pest__c.toLowerCase());
        }
        if (String.isNotBlank(f.Evidence__c)) {
            what.add(f.Evidence__c.toLowerCase());
        }
        String text = (String.isBlank(f.Zone__c) ? 'Property' : f.Zone__c) + ': ' + String.join(what, ' ');
        if (String.isNotBlank(f.Severity__c)) {
            text += ' (' + f.Severity__c.toLowerCase() + ')';
        }
        return text;
    }

    /** Links the inspection to the Quote created from it. */
    public static void markQuoted(Id inspectionId, Id quoteId, String overrideReason) {
        update new RLM_RTK_Inspection__c(
            Id = inspectionId,
            Quote__c = quoteId,
            Status__c = 'Quoted',
            Override_Reason__c = overrideReason
        );
    }
}
