global class RLM_PlaceQuoteModel {
    global string pricingPref;
    global string configurationInput;
    global Map<String, Boolean> configurationOptions;
    global QuoteGraphModel graph;

    global class QuoteGraphModel{
        global string graphId;
        global List<ObjectRecordModel> records;

    }

    global class ObjectRecordModel{
        global string referenceId;
        global Map<String, Object> record;
    }
    
}