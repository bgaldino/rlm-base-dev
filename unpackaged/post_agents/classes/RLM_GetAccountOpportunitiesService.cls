public with sharing class RLM_GetAccountOpportunitiesService {

    public class Request {
        @InvocableVariable(required=true label='Account ID')
        public String accountId;
    }

    public class Response {
        @InvocableVariable
        public Boolean success;

        @InvocableVariable
        public String message;

        @InvocableVariable
        public String opportunityIds;

        @InvocableVariable
        public String openOpportunityIds;
    }

    @InvocableMethod(label='Get Account Opportunities' description='Retrieves open and recent opportunities for an account to support whitespace analysis and quoting')
    public static List<Response> getOpportunities(List<Request> requests) {
        List<Response> responses = new List<Response>();

        for (Request req : requests) {
            Response resp = new Response();

            try {
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
                    String accountName = accounts[0].Name;

                    List<Opportunity> opps = [
                        SELECT Id, Name, StageName, Amount, CloseDate, IsClosed, IsWon,
                               Pricebook2Id, Pricebook2.Name, Type,
                               (SELECT Id, Product2.Name, Quantity, UnitPrice, TotalPrice
                                FROM OpportunityLineItems
                                ORDER BY Product2.Name
                                LIMIT 20)
                        FROM Opportunity
                        WHERE AccountId = :req.accountId
                        ORDER BY IsClosed ASC, CloseDate DESC
                        LIMIT 20
                    ];

                    if (opps.isEmpty()) {
                        resp.success = true;
                        resp.message = 'No opportunities found for account "' + accountName + '". A new opportunity can be created to add recommended products.';
                    } else {
                        List<String> allOppIds = new List<String>();
                        List<String> openOppIds = new List<String>();
                        Integer openCount = 0;

                        for (Opportunity opp : opps) {
                            allOppIds.add(opp.Id);
                            if (!opp.IsClosed) {
                                openOppIds.add(opp.Id);
                                openCount++;
                            }
                        }

                        resp.opportunityIds = String.join(allOppIds, ',');
                        resp.openOpportunityIds = String.join(openOppIds, ',');
                        resp.success = true;

                        if (openCount > 0) {
                            resp.message = accountName + ' has ' + (openCount == 1 ? 'an' : openCount + '') + ' open opportunit' + (openCount == 1 ? 'y' : 'ies') + ' where these products can be added. Would you like to use ' + (openCount == 1 ? 'this opportunity' : 'an existing opportunity') + ' or create a new one?';
                        } else {
                            resp.message = accountName + ' has ' + opps.size() + ' opportunit' + (opps.size() == 1 ? 'y' : 'ies') + ', but none are currently open. A new opportunity would need to be created to add recommended products.';
                        }
                    }
                }
            } catch (Exception e) {
                resp.success = false;
                resp.message = 'Error retrieving opportunities: ' + e.getMessage();
            }

            responses.add(resp);
        }

        return responses;
    }
}
