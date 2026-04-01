public with sharing class RLM_CreateOpportunityService {

    public class Request {
        @InvocableVariable(required=true label='Account ID')
        public String accountId;

        @InvocableVariable(required=false label='Account Name' description='Account name for display in confirmation dialog (optional)')
        public String accountName;

        @InvocableVariable(required=false label='Opportunity Name')
        public String opportunityName;

        @InvocableVariable(required=false label='Stage Name')
        public String stageName;

        @InvocableVariable(required=false label='Close Date')
        public String closeDate;
    }

    public class Response {
        @InvocableVariable
        public Boolean success;

        @InvocableVariable
        public String message;

        @InvocableVariable
        public String opportunityId;
    }

    @InvocableMethod(label='Create Opportunity' description='Creates a new Opportunity for the given account. Returns the new Opportunity ID for use in quote creation.')
    public static List<Response> createOpportunity(List<Request> requests) {
        List<Response> responses = new List<Response>();

        for (Request req : requests) {
            Response resp = new Response();

            try {
                // Validate account exists
                List<Account> accounts = [
                    SELECT Id, Name
                    FROM Account
                    WHERE Id = :req.accountId
                    LIMIT 1
                ];

                if (accounts.isEmpty()) {
                    resp.success = false;
                    resp.message = 'Account not found with ID: ' + req.accountId;
                } else {
                    Account acct = accounts[0];

                    // Build the Opportunity
                    Opportunity opp = new Opportunity();
                    opp.AccountId = acct.Id;

                    // Name: use provided or generate default
                    if (String.isNotBlank(req.opportunityName)) {
                        opp.Name = req.opportunityName;
                    } else {
                        opp.Name = 'Whitespace Opportunity - ' + acct.Name;
                    }

                    // Stage: use provided or default to Prospecting
                    if (String.isNotBlank(req.stageName)) {
                        opp.StageName = req.stageName;
                    } else {
                        opp.StageName = 'Prospecting';
                    }

                    // Close Date: use provided or default to 30 days from now
                    if (String.isNotBlank(req.closeDate)) {
                        try {
                            opp.CloseDate = Date.valueOf(req.closeDate);
                        } catch (Exception dateEx) {
                            opp.CloseDate = Date.today().addDays(30);
                        }
                    } else {
                        opp.CloseDate = Date.today().addDays(30);
                    }

                    // Set the standard pricebook
                    List<Pricebook2> pricebooks = [
                        SELECT Id FROM Pricebook2
                        WHERE IsStandard = true AND IsActive = true
                        LIMIT 1
                    ];
                    if (!pricebooks.isEmpty()) {
                        opp.Pricebook2Id = pricebooks[0].Id;
                    }

                    insert opp;

                    resp.success = true;
                    resp.opportunityId = opp.Id;
                    resp.message = 'Created new opportunity "' + opp.Name + '" for ' + acct.Name + ' (Stage: ' + opp.StageName + ', Close Date: ' + String.valueOf(opp.CloseDate) + '). You can now create a quote on this opportunity.';
                }
            } catch (Exception e) {
                resp.success = false;
                resp.message = 'Error creating opportunity: ' + e.getMessage();
            }

            responses.add(resp);
        }

        return responses;
    }
}
