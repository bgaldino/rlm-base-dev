public with sharing class RLM_HomeServices_FieldTechController {

    /**
     * Called by the LWC to run the service completion flow and trigger invoice generation.
     * Runs the autolaunched flow synchronously, then enqueues an async job to invoke
     * the Generate Invoices (BillNow) action for the account.
     */
    @AuraEnabled
    public static void invokeServiceCompletion(
        String accountId,
        Integer serviceMonth,
        String techNotes,
        String serviceDate
    ) {
        if (String.isBlank(accountId)) {
            throw new AuraHandledException('Account ID is required.');
        }
        if (serviceMonth == null || serviceMonth < 1 || serviceMonth > 12) {
            throw new AuraHandledException('Service month must be between 1 and 12.');
        }
        if (String.isBlank(serviceDate)) {
            throw new AuraHandledException('Service date is required.');
        }
        Date parsedServiceDate = Date.valueOf(serviceDate);

        Map<String, Object> inputs = new Map<String, Object>{
            'accountId'    => accountId,
            'serviceMonth' => serviceMonth,
            'serviceDate'  => parsedServiceDate
        };

        try {
            Flow.Interview interview = Flow.Interview.createInterview(
                'RLM_HomeServices_FieldTechMonthlyService',
                inputs
            );
            interview.start();

            // AutoLaunched flows use an output variable to surface errors
            // since customErrors is not supported in that process type
            String flowError = (String) interview.getVariableValue('errorMessage');
            if (String.isNotBlank(flowError)) {
                throw new AuraHandledException(flowError);
            }
        } catch (AuraHandledException ahe) {
            throw ahe;
        } catch (Exception e) {
            throw new AuraHandledException(
                'Service completion failed: ' + e.getMessage()
            );
        }

        // Enqueue async job to invoke the Generate Invoices (BillNow) action.
        // BillNow is a UI-standard button with no direct REST equivalent; the
        // queueable attempts the platform action and logs the outcome.
        if (!Test.isRunningTest()) {
            System.enqueueJob(new GenerateInvoicesQueueable(accountId));
        }
    }

    /**
     * Queueable job that invokes the Generate Invoices platform action for an Account.
     * Uses the current session credentials to call the Salesforce UI API.
     */
    public class GenerateInvoicesQueueable implements Queueable, Database.AllowsCallouts {
        private final String accountId;

        public GenerateInvoicesQueueable(String accountId) {
            this.accountId = accountId;
        }

        public void execute(QueueableContext ctx) {
            triggerGenerateInvoices(this.accountId);
        }
    }

    /**
     * Performs the HTTP callout to invoke the Generate Invoices (BillNow) action
     * on the Account record via the Salesforce REST API.
     */
    private static void triggerGenerateInvoices(String accountId) {
        try {
            String sessionId   = UserInfo.getSessionId();
            String instanceUrl = System.Url.getOrgDomainUrl().toExternalForm();
            String endpoint    = instanceUrl
                + '/services/data/v66.0/sobjects/Account/'
                + accountId
                + '/BillNow';

            HttpRequest req = new HttpRequest();
            req.setEndpoint(endpoint);
            req.setMethod('POST');
            req.setHeader('Authorization', 'Bearer ' + sessionId);
            req.setHeader('Content-Type', 'application/json');
            req.setBody('{}');
            req.setTimeout(10000);

            HttpResponse res = new Http().send(req);

            if (res.getStatusCode() >= 200 && res.getStatusCode() < 300) {
                System.debug(LoggingLevel.INFO,
                    'Generate Invoices triggered successfully for account ' + accountId);
            } else {
                System.debug(LoggingLevel.WARN,
                    'Generate Invoices returned ' + res.getStatusCode()
                    + ' for account ' + accountId
                    + '. Manual BillNow click may be required.');
            }
        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR,
                'Generate Invoices callout failed: ' + e.getMessage());
        }
    }
}