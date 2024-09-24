global class RLM_PlaceOrderModel {
    global string pricingPref;
    global string configurationInput;
    global Map<String, Boolean> configurationOptions;
    global OrderGraphModel graph;

    global class OrderGraphModel{
        global string graphId;
        global List<ObjectRecordModel> records;

    }

    global class ObjectRecordModel{
        global string referenceId;
        global Map<String, Object> record;
    }
    
}