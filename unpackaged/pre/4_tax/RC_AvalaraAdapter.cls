global virtual class RC_AvalaraAdapter implements commercetax.TaxEngineAdapter {

    global commercetax.TaxEngineResponse processRequest(commercetax.TaxEngineContext taxEngineContext) {
        commercetax.RequestType requestType = taxEngineContext.getRequestType();
        if(requestType == commercetax.RequestType.CalculateTax){
            return RC_CalculateTaxService.getTax(taxEngineContext);
        }
        else 
        	return null;
    }
}