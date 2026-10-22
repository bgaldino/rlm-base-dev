/**
 * Posts invoices for the billing schedules of Field Service driven orders once they are
 * ReadyForInvoicing. Billing schedules are released asynchronously (after a milestone is
 * accomplished or an order activates), so the job retries a few times before giving up.
 */
public with sharing class RLM_FSL_InvoiceOrder {
    @TestVisible
    private static final Integer MAX_ATTEMPTS = 5;
    private static final Integer RETRY_DELAY_MINUTES = 1;

    @InvocableMethod(label='Invoice Ready Billing Schedules' category='Field Service'
        description='Posts an invoice for the order billing schedules that are ready for invoicing.')
    public static void invoiceOrders(List<Id> orderIds) {
        enqueue(new Set<Id>(orderIds));
    }

    public static void enqueue(Set<Id> orderIds) {
        System.enqueueJob(new InvoiceJob(orderIds, 1), RETRY_DELAY_MINUTES);
    }

    public class InvoiceJob implements Queueable {
        private final Set<Id> orderIds;
        private final Integer attempt;

        public InvoiceJob(Set<Id> orderIds, Integer attempt) {
            this.orderIds = orderIds;
            this.attempt = attempt;
        }

        public void execute(QueueableContext context) {
            List<String> scheduleIds = readyScheduleIds(orderIds);
            if (scheduleIds.isEmpty()) {
                if (attempt < MAX_ATTEMPTS && !Test.isRunningTest()) {
                    System.enqueueJob(new InvoiceJob(orderIds, attempt + 1), RETRY_DELAY_MINUTES);
                }
                return;
            }
            ConnectApi.RevenueAsyncRepresentation result = ConnectApi.Billing.generateInvoices(buildRequest(scheduleIds));
            if (result.success != true) {
                System.debug(LoggingLevel.ERROR, 'Invoice generation failed for ' + orderIds + ': ' + JSON.serialize(result.errors));
            }
        }
    }

    @TestVisible
    private static List<String> readyScheduleIdsOverride;

    private static List<String> readyScheduleIds(Set<Id> orderIds) {
        if (readyScheduleIdsOverride != null) {
            return readyScheduleIdsOverride;
        }
        List<String> scheduleIds = new List<String>();
        for (BillingSchedule schedule : [SELECT Id FROM BillingSchedule
                WHERE ReferenceEntityId IN :orderIds AND Status = 'ReadyForInvoicing' LIMIT 200]) {
            scheduleIds.add(schedule.Id);
        }
        return scheduleIds;
    }

    @TestVisible
    private static ConnectApi.InvoiceInputRepresentation buildRequest(List<String> scheduleIds) {
        String today = String.valueOf(Date.today());
        ConnectApi.InvoiceInputRepresentation input = new ConnectApi.InvoiceInputRepresentation();
        input.action = ConnectApi.InvoiceAction.Posted;
        input.billingScheduleIds = scheduleIds;
        input.invoiceDate = today;
        input.targetDate = today;
        return input;
    }
}
