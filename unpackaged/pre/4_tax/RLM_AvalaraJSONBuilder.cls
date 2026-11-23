public with sharing class RLM_AvalaraJSONBuilder 
{
    private static RLM_AvalaraJSONBuilder avalaraJSONBuilderInstance;
    
    public static RLM_AvalaraJSONBuilder getInstance() 
    {
        if (NULL == avalaraJSONBuilderInstance) 
        {
            avalaraJSONBuilderInstance = new RLM_AvalaraJSONBuilder();
        }
        return avalaraJSONBuilderInstance;
    }
    
    public String frameJsonForGetTaxOrderItem(commercetax.CalculateTaxRequest calculateTaxRequest) 
    {
        try
        {
            Id accountid  = null;
            if(calculateTaxRequest.CustomerDetails.AccountId != null &&  calculateTaxRequest.CustomerDetails.AccountId != '')
               accountid = Id.valueof(calculateTaxRequest.CustomerDetails.AccountId);
            JSONGenerator jsonGeneratorInstance = JSON.createGenerator(true);
            jsonGeneratorInstance.writeStartObject();
            String type = null;
            if(calculateTaxRequest.taxtype == commercetax.CalculateTaxType.Actual)
                type ='SalesInvoice';
                else type = 'SalesOrder';
            jsonGeneratorInstance.writeStringField('type', type);
            if(calculateTaxRequest.SellerDetails != null)
                jsonGeneratorInstance.writeStringField('companyCode', calculateTaxRequest.SellerDetails.code);
            else 
                jsonGeneratorInstance.writeStringField('companyCode', 'billing2');
            if(calculateTaxRequest.isCommit != null) {
                jsonGeneratorInstance.writeBooleanField('commit', calculateTaxRequest.isCommit);
            }
            if(calculateTaxRequest.documentcode != null){
                jsonGeneratorInstance.writeStringField('code', calculateTaxRequest.documentcode);
            }else if(calculateTaxRequest.referenceEntityId != null) {
                jsonGeneratorInstance.writeStringField('code', calculateTaxRequest.referenceEntityId);
            }
            if(calculateTaxRequest.CustomerDetails.code == null && accountid !=null) {
                Account acc = [select id, name from account where id=:accountid];
                jsonGeneratorInstance.writeStringField('customerCode', acc.name);
            } else {
                jsonGeneratorInstance.writeStringField('customerCode', calculateTaxRequest.CustomerDetails.code);
            }
            if(calculateTaxRequest.EffectiveDate == null)
                jsonGeneratorInstance.writeDateField('date', system.today());
            else         
                jsonGeneratorInstance.writeDateTimeField('date', calculateTaxRequest.EffectiveDate);
            
            jsonGeneratorInstance.writeFieldName('lines');
            jsonGeneratorInstance.writeStartArray();
            for(integer i=0;i<1;i++){
                for(Commercetax.TaxLineItemRequest lineItem : calculateTaxRequest.LineItems)
                {
                    jsonGeneratorInstance.writeStartObject();
                    if(lineItem.linenumber != null){
                        jsonGeneratorInstance.writeStringField('number', lineItem.linenumber);
                    }
                    jsonGeneratorInstance.writeNumberField('quantity', lineItem.Quantity);
                    jsonGeneratorInstance.writeNumberField('amount', (lineItem.Amount));
                    jsonGeneratorInstance.writeStringField('taxCode',lineItem.taxCode);
                    
                    jsonGeneratorInstance.writeFieldName('addresses');
                    jsonGeneratorInstance.writeStartObject();  
                    jsonGeneratorInstance.writeFieldName('ShipFrom');
                    jsonGeneratorInstance.writeStartObject();
                    jsonGeneratorInstance.writeStringField('line1', lineItem.addresses.shipfrom.street);
                    jsonGeneratorInstance.writeStringField('city', lineItem.addresses.shipfrom.city);
                    jsonGeneratorInstance.writeStringField('region', lineItem.addresses.shipfrom.state);
                    jsonGeneratorInstance.writeStringField('country', lineItem.addresses.shipfrom.country);
                    jsonGeneratorInstance.writeStringField('postalCode',lineItem.addresses.shipfrom.postalcode);              
                    jsonGeneratorInstance.writeEndObject();               

                    jsonGeneratorInstance.writeFieldName('ShipTo');
                    jsonGeneratorInstance.writeStartObject();
                    jsonGeneratorInstance.writeStringField('line1', lineItem.addresses.shipto.street);
                    jsonGeneratorInstance.writeStringField('city', lineItem.addresses.shipto.city);
                    jsonGeneratorInstance.writeStringField('region', lineItem.addresses.shipto.state);
                    jsonGeneratorInstance.writeStringField('country', lineItem.addresses.shipto.country);
                    jsonGeneratorInstance.writeStringField('postalCode',lineItem.addresses.shipto.postalcode); 
                    jsonGeneratorInstance.writeEndObject();               

                    jsonGeneratorInstance.writeFieldName('pointOfOrderOrigin');
                    jsonGeneratorInstance.writeStartObject();
                    jsonGeneratorInstance.writeStringField('line1', lineItem.addresses.soldto.street);
                    jsonGeneratorInstance.writeStringField('city', lineItem.addresses.soldto.city);
                    jsonGeneratorInstance.writeStringField('region', lineItem.addresses.soldto.state);
                    jsonGeneratorInstance.writeStringField('country', lineItem.addresses.soldto.country);
                    jsonGeneratorInstance.writeStringField('postalCode',lineItem.addresses.soldto.postalcode); 
                    jsonGeneratorInstance.writeEndObject(); 
                    // close "addresses"; taxOverride belongs to the line, not to the addresses
                    jsonGeneratorInstance.writeEndObject(); 

                    if(lineItem.effectiveDate != null)    
                    {
                        // Avalara's line-level TaxOverride requires a type and a reason.
                        jsonGeneratorInstance.writeFieldName('taxOverride');
                        jsonGeneratorInstance.writeStartObject();
                        jsonGeneratorInstance.writeStringField('type', 'TaxDate');
                        jsonGeneratorInstance.writeStringField('reason', 'Tax date from the line effective date');
                        jsonGeneratorInstance.writeDateTimeField('taxDate', lineItem.effectiveDate);             
                        jsonGeneratorInstance.writeEndObject();               
                    }
                    jsonGeneratorInstance.writeEndObject(); 
                }
            }
                jsonGeneratorInstance.writeEndArray();             
            jsonGeneratorInstance.writeEndObject();
            return jsonGeneratorInstance.getAsString();
        }
        catch (Exception e) 
        { 
             throw e;
        } 
    }
}