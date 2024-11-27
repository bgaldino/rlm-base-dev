public with sharing class ConsumptionRateServiceRequest {
    public Id businessObjectId {get; private set;} 
    public ConsumptionBusinessObject ConsumptionRateRequest = new ConsumptionBusinessObject();

    public ConsumptionRateServiceRequest setConsumptionRateRecords(List<ConsumptionRateProducts> consumptionRateRecords) {
        this.ConsumptionRateRequest.ConsumptionRateProductsList = consumptionRateRecords;
        return this;
    }

    public ConsumptionRateServiceRequest setConsumptionRateRequest(ConsumptionBusinessObject ConsumptionRateRequest) {
        this.ConsumptionRateRequest = ConsumptionRateRequest;
        return this;
    }

    public ConsumptionRateServiceRequest createRequest(ConsumptionBusinessObject ConsumptionRateRequest, List<ConsumptionRateProducts> consumptionRateRecords) {
        return new ConsumptionRateServiceRequest().setConsumptionRateRequest(ConsumptionRateRequest).setConsumptionRateRecords(consumptionRateRecords);
    }

    public class ConsumptionBusinessObject {
        public Id id;
        public Date startDate;
        public Date endDate;
        public String currencyIsoCode;
        public Id priceBook2Id;
        public String quoteBypass;
        public Decimal term;
        public List<ConsumptionRateProducts> ConsumptionRateProductsList = new List<ConsumptionRateProducts>();
    }

    public class ConsumptionRateProducts {
        public Id id;
        public Id productId;
        public Decimal quantity;
        public Id tenantId;
        public Date startDate;
        public Date endDate;
        public String currencyIsoCode;
        public Decimal subscriptionTerm; 
        public Decimal discount;
        public Id priceBook2Id;
        public Id sourceSystemExternalId;
        public Decimal unitPrice;
        public string sellingModelType;
        public Id contractId;
    }
}
