public with sharing class DPPValidationRunner {
    private static Boolean RUN_DPP_VALIDATIONS = true;
    private IQuoteLineItemDPPValidationService quoteLineItemDPPValidations;
    private IQuoteLineDAO quoteLineDAO;

    public DPPValidationRunner() {
        this.quoteLineItemDPPValidations = (IQuoteLineItemDPPValidationService) ServiceRegistry.getInstance('IQuoteLineItemDPPValidationService');
        this.quoteLineDAO =  (IQuoteLineDAO) ServiceRegistry.getInstance('IQuoteLineDAO');
    }

    public void invokeDPPValidationForQuoteLineItems(List<QuoteLineItem> quoteLineItems) {
        if (!RUN_DPP_VALIDATIONS) {
            return;
        }
        RUN_DPP_VALIDATIONS = false;

        Set<ID> initialQuoteIDs = new Set<ID>();

        for(QuoteLineItem quoteLineItem :quoteLineItems) {
            initialQuoteIDs.add(quoteLineItem.QuoteId);
        }

        List<QuoteLineItem> quoteLineItemsByQuoteId = QuoteLineDAO.getQuoteLinesByQuoteIds(initialQuoteIDs);
        quoteLineItemDPPValidations.validateQuoteLineItems(quoteLineItemsByQuoteId);
    }
}