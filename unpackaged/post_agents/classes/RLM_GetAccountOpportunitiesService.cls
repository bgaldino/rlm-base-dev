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
        public String opportunities;

        @InvocableVariable
        public Integer opportunityCount;

        @InvocableVariable
        public Integer openOpportunityCount;

        @InvocableVariable
        public String accountName;
    }

    @InvocableMethod(label='Get Account Opportunities' description='Retrieves open and recent opportunities for an account to support whitespace analysis and quoting')
    public static List<Response> getOpportunities(List<Request> requests) {
        List<Response> responses = new List<Response>();

        for (Request req : requests) {
            Response resp = new Response();
            resp.opportunityCount = 0;
            resp.openOpportunityCount = 0;

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
                    resp.accountName = accounts[0].Name;

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
                        resp.message = 'No opportunities found for account "' + accounts[0].Name + '". A new opportunity can be created to add recommended products.';
                        resp.opportunities = 'None';
                    } else {
                        Integer openCount = 0;
                        List<String> oppDescriptions = new List<String>();

                        for (Opportunity opp : opps) {
                            if (!opp.IsClosed) {
                                openCount++;
                            }

                            String oppLine = opp.Name + ' | Stage: ' + opp.StageName;
                            if (opp.Amount != null) {
                                oppLine = oppLine + ' | Amount: $' + opp.Amount.format();
                            }
                            if (opp.CloseDate != null) {
                                oppLine = oppLine + ' | Close: ' + String.valueOf(opp.CloseDate);
                            }
                            if (opp.IsClosed) {
                                oppLine = oppLine + ' | Status: ' + (opp.IsWon ? 'Won' : 'Lost');
                            } else {
                                oppLine = oppLine + ' | Status: Open';
                            }
                            if (opp.Pricebook2 != null) {
                                oppLine = oppLine + ' | Pricebook: ' + opp.Pricebook2.Name;
                            }

                            if (opp.OpportunityLineItems != null && !opp.OpportunityLineItems.isEmpty()) {
                                List<String> lineItems = new List<String>();
                                for (OpportunityLineItem li : opp.OpportunityLineItems) {
                                    lineItems.add(li.Product2.Name + ' (Qty: ' + li.Quantity + ', $' + li.UnitPrice.format() + ')');
                                }
                                oppLine = oppLine + ' | Products: ' + String.join(lineItems, ', ');
                            }

                            oppDescriptions.add(oppLine);
                        }

                        resp.opportunities = String.join(oppDescriptions, '; ');
                        resp.opportunityCount = opps.size();
                        resp.openOpportunityCount = openCount;
                        resp.success = true;

                        if (openCount > 0) {
                            resp.message = 'Found ' + opps.size() + ' opportunity(ies) for "' + accounts[0].Name + '", of which ' + openCount + ' are open. Products from whitespace analysis can be added to an existing open opportunity or a new one.';
                        } else {
                            resp.message = 'Found ' + opps.size() + ' opportunity(ies) for "' + accounts[0].Name + '", but none are currently open. A new opportunity would need to be created to add recommended products.';
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
