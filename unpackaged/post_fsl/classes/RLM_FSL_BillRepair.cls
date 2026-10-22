/**
 * Bills a completed break/fix Work Order that no entitlement covers: places a priced Revenue
 * Cloud order for the repair service, activates it (which creates its billing schedules), links
 * it to the Work Order and posts the invoice.
 *
 * Orders must be priced by Place Sales Transaction; DML-inserted lines fail activation. Orders
 * placed outside a quote carry no Revenue Lifecycle Management AppUsageAssignment, and without
 * it activation creates no assets or billing schedules, so it is added before activation.
 * Activation also requires a bill-to contact: the Work Order's contact, else the account's first contact.
 * Place Sales Transaction handles one order per call, so the job processes one Work Order and
 * chains itself for the rest.
 */
public with sharing class RLM_FSL_BillRepair {
    public static final String REPAIR_SKU = 'QB-SVC-REPAIR';
    public static final String PEST_RESERVICE_SKU = 'RTK-RESERVICE';

    public interface OrderPlacer {
        Id place(WorkOrder workOrder, PricebookEntry entry);
    }

    @TestVisible
    private static OrderPlacer placer = new SalesTransactionPlacer();

    @InvocableMethod(label='Bill Uncovered Repair' category='Field Service'
        description='Creates, activates and invoices a repair order for completed Work Orders without entitlement coverage.')
    public static void billRepairs(List<Id> workOrderIds) {
        System.enqueueJob(new RepairOrderJob(new List<Id>(new Set<Id>(workOrderIds)), new Set<Id>()));
    }

    public class RepairOrderJob implements Queueable {
        private final List<Id> pending;
        private final Set<Id> orderIds;

        public RepairOrderJob(List<Id> pending, Set<Id> orderIds) {
            this.pending = pending;
            this.orderIds = orderIds;
        }

        public void execute(QueueableContext context) {
            Id workOrderId = pending.remove(0);
            WorkOrder workOrder = [SELECT Id, WorkOrderNumber, AccountId, ContactId, RLM_Billable_Order__c, WorkType.Name,
                    Account.ShippingStreet, Account.ShippingCity, Account.ShippingState, Account.ShippingPostalCode,
                    Account.ShippingCountry, Account.BillingStreet, Account.BillingCity, Account.BillingState,
                    Account.BillingPostalCode, Account.BillingCountry
                FROM WorkOrder WHERE Id = :workOrderId];
            if (workOrder.RLM_Billable_Order__c == null && workOrder.AccountId != null) {
                try {
                    orderIds.add(bill(workOrder));
                } catch (Exception e) {
                    System.debug(LoggingLevel.ERROR, 'Repair billing failed for ' + workOrder.WorkOrderNumber + ': ' + e.getMessage());
                }
            }
            if (!pending.isEmpty()) {
                System.enqueueJob(new RepairOrderJob(pending, orderIds));
            } else if (!orderIds.isEmpty()) {
                RLM_FSL_InvoiceOrder.enqueue(orderIds);
            }
        }
    }

    @TestVisible
    private static String skuFor(WorkOrder workOrder) {
        String workTypeName = workOrder.WorkType != null ? workOrder.WorkType.Name : null;
        if (workTypeName == 'Pest Re-service') {
            return PEST_RESERVICE_SKU;
        }
        return REPAIR_SKU;
    }

    private static Id bill(WorkOrder workOrder) {
        String sku = skuFor(workOrder);
        PricebookEntry entry = [SELECT Id, UnitPrice, Product2Id, Pricebook2Id FROM PricebookEntry
            WHERE Product2.StockKeepingUnit = :sku AND Pricebook2.IsStandard = true
            AND CurrencyIsoCode = 'USD' AND IsActive = true LIMIT 1];
        Id orderId = placer.place(workOrder, entry);
        insert new AppUsageAssignment(RecordId = orderId, AppUsageType = 'RevenueLifecycleManagement');
        update new Order(Id = orderId, Status = 'Activated');
        update new WorkOrder(Id = workOrder.Id, RLM_Billable_Order__c = orderId);
        return orderId;
    }

    public class SalesTransactionPlacer implements OrderPlacer {
        public Id place(WorkOrder workOrder, PricebookEntry entry) {
            String today = String.valueOf(Date.today());
            Account account = workOrder.Account;
            Id billToContactId = workOrder.ContactId;
            if (billToContactId == null) {
                List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :workOrder.AccountId ORDER BY CreatedDate LIMIT 1];
                if (!contacts.isEmpty()) {
                    billToContactId = contacts[0].Id;
                }
            }
            RevSalesTrxn.RecordResource orderRecord = new RevSalesTrxn.RecordResource(Order.SObjectType, 'POST');
            orderRecord.fieldValues = new Map<String, Object>{
                'AccountId' => workOrder.AccountId, 'Pricebook2Id' => entry.Pricebook2Id, 'EffectiveDate' => today,
                'Status' => 'Draft', 'CurrencyIsoCode' => 'USD', 'Name' => 'Break/Fix Repair - WO ' + workOrder.WorkOrderNumber,
                'ShippingStreet' => account.ShippingStreet, 'ShippingCity' => account.ShippingCity,
                'ShippingState' => account.ShippingState, 'ShippingPostalCode' => account.ShippingPostalCode,
                'ShippingCountry' => account.ShippingCountry, 'BillingStreet' => account.BillingStreet,
                'BillingCity' => account.BillingCity, 'BillingState' => account.BillingState,
                'BillingPostalCode' => account.BillingPostalCode, 'BillingCountry' => account.BillingCountry
            };
            if (billToContactId != null) {
                orderRecord.fieldValues.put('BillToContactId', billToContactId);
            }
            RevSalesTrxn.RecordResource actionRecord = new RevSalesTrxn.RecordResource(OrderAction.SObjectType, 'POST');
            actionRecord.fieldValues = new Map<String, Object>{ 'OrderId' => '@{refOrder.id}', 'Type' => 'Add' };
            RevSalesTrxn.RecordResource itemRecord = new RevSalesTrxn.RecordResource(OrderItem.SObjectType, 'POST');
            itemRecord.fieldValues = new Map<String, Object>{
                'OrderId' => '@{refOrder.id}', 'OrderActionId' => '@{refAction.id}', 'Product2Id' => entry.Product2Id,
                'PricebookEntryId' => entry.Id, 'Quantity' => '1', 'UnitPrice' => String.valueOf(entry.UnitPrice),
                'ServiceDate' => today
            };
            RevSalesTrxn.GraphRequest graph = new RevSalesTrxn.GraphRequest('fslRepair', new List<RevSalesTrxn.RecordWithReferenceRequest>{
                new RevSalesTrxn.RecordWithReferenceRequest('refOrder', orderRecord),
                new RevSalesTrxn.RecordWithReferenceRequest('refAction', actionRecord),
                new RevSalesTrxn.RecordWithReferenceRequest('refItem', itemRecord)
            });
            RevSalesTrxn.PlaceSalesTransactionResponse response = RevSalesTrxn.PlaceSalesTransactionExecutor.execute(graph,
                RevSalesTrxn.PricingPreferenceEnum.SYSTEM, RevSalesTrxn.ConfigurationExecutionEnum.SKIP,
                new RevSalesTrxn.ConfigurationOptionsInput(), null, null, RevSalesTrxn.TaxPreferenceEnum.SKIP, null);
            if (response.isSuccess != true || String.isBlank(response.salesTransactionId)) {
                throw new RepairBillingException('Place Sales Transaction failed: ' + JSON.serialize(response.errorResponse));
            }
            return response.salesTransactionId;
        }
    }

    public class RepairBillingException extends Exception {}
}
