/**
 * Handles self-service signup: creates Account (all form data), Contact (first/last only),
 * Opportunity, and OpportunityLineItems. Uses Standard Price Book.
 */
public with sharing class RLM_HomeServices_CustomerSignupCtrl {

    public class SignupRequest {
        @AuraEnabled public String firstName;
        @AuraEnabled public String lastName;
        @AuraEnabled public String street;
        @AuraEnabled public String city;
        @AuraEnabled public String state;
        @AuraEnabled public String postalCode;
        @AuraEnabled public String country;
        @AuraEnabled public String phone;
        @AuraEnabled public String email;
        @AuraEnabled public List<String> pricebookEntryIds; // from carousel selection
    }

    public class SignupResult {
        @AuraEnabled public Boolean success;
        @AuraEnabled public String accountId;
        @AuraEnabled public String contactId;
        @AuraEnabled public String opportunityId;
        @AuraEnabled public String errorMessage;
    }

    /** Entry point for LWC: single JSON string to avoid wire adapter param binding issues in Experience Cloud. */
    @AuraEnabled
    public static SignupResult submitSignup(String requestJson) {
        SignupRequest req = null;
        if (String.isNotBlank(requestJson)) {
            try {
                req = (SignupRequest) JSON.deserialize(requestJson, SignupRequest.class);
            } catch (Exception e) {
                SignupResult err = new SignupResult();
                err.success = false;
                err.errorMessage = 'Invalid request: ' + e.getMessage();
                return err;
            }
        }
        return submitSignupImpl(req);
    }

    private static SignupResult submitSignupImpl(SignupRequest req) {
        SignupResult result = new SignupResult();
        result.success = false;
        if (req == null || req.pricebookEntryIds == null || req.pricebookEntryIds.isEmpty()) {
            result.errorMessage = 'Please select at least one product.';
            return result;
        }
        if (String.isBlank(req.firstName) || String.isBlank(req.lastName)) {
            result.errorMessage = 'First name and last name are required.';
            return result;
        }
        Savepoint sp = Database.setSavepoint();
        try {
            Id standardPricebookId = getStandardPricebookId();
            if (standardPricebookId == null) {
                result.errorMessage = 'Standard Price Book is not available.';
                return result;
            }

            // 1. Account (all form data; RLM_HomeServices_Account record type)
            Account acc = new Account();
            acc.RecordTypeId = getHomeServicesRecordTypeId('Account');
            acc.Name = (req.firstName + ' ' + req.lastName).trim();
            acc.RLM_HomeServices_FirstName__c = req.firstName;
            acc.RLM_HomeServices_LastName__c = req.lastName;
            acc.BillingStreet = req.street;
            acc.BillingCity = req.city;
            acc.BillingState = req.state;
            acc.BillingPostalCode = req.postalCode;
            acc.BillingCountry = req.country;
            acc.Phone = req.phone;
            acc.RLM_HomeServices_Email__c = req.email;
            insert acc;
            result.accountId = acc.Id;

            // 2. Contact (FirstName, LastName only)
            Contact con = new Contact();
            con.AccountId = acc.Id;
            con.FirstName = req.firstName;
            con.LastName = req.lastName;
            insert con;
            result.contactId = con.Id;

            // 3. Opportunity
            Opportunity opp = new Opportunity();
            opp.RecordTypeId = getHomeServicesRecordTypeId('Opportunity');
            opp.AccountId = acc.Id;
            opp.Name = acc.Name + ' - Self Service';
            opp.StageName = 'New Inquiry';
            opp.CloseDate = Date.today().addDays(30);
            opp.Pricebook2Id = standardPricebookId;
            insert opp;

            // 4. OpportunityLineItems
            List<OpportunityLineItem> oppLines = new List<OpportunityLineItem>();
            List<PricebookEntry> entries = [
                SELECT Id, UnitPrice, Product2Id
                FROM PricebookEntry
                WHERE Id IN :req.pricebookEntryIds
                  AND Pricebook2Id = :standardPricebookId
                  AND IsActive = true
            ];
            for (PricebookEntry pbe : entries) {
                oppLines.add(new OpportunityLineItem(
                    OpportunityId = opp.Id,
                    PricebookEntryId = pbe.Id,
                    Quantity = 1,
                    UnitPrice = pbe.UnitPrice != null ? pbe.UnitPrice : 0
                ));
            }
            insert oppLines;
            result.opportunityId = opp.Id;

            result.success = true;
        } catch (DmlException e) {
            Database.rollback(sp);
            result.errorMessage = e.getDmlMessage(0);
        } catch (Exception e) {
            Database.rollback(sp);
            result.errorMessage = e.getMessage();
        }
        return result;
    }

    /** Legacy entry: single SignupRequest (can deserialize as null in some contexts). */
    @AuraEnabled(cacheable=false)
    public static SignupResult submitSignupWithRequest(SignupRequest req) {
        return submitSignupImpl(req);
    }

    private static Id getStandardPricebookId() {
        List<Pricebook2> pb = [SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1];
        return pb.isEmpty() ? null : pb[0].Id;
    }

    private static Id getHomeServicesRecordTypeId(String sObjectType) {
        String developerName = 'RLM_HomeServices_' + sObjectType;
        List<RecordType> rts = [
            SELECT Id FROM RecordType
            WHERE SObjectType = :sObjectType
              AND DeveloperName = :developerName
            LIMIT 1
        ];
        return rts.isEmpty() ? null : rts[0].Id;
    }
}