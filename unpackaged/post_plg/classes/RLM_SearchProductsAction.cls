public with sharing class RLM_SearchProductsAction {

    public class Request {
        @InvocableVariable(label='Search Keyword' required=true)
        public String keyword;
    }

    public class Result {
        @InvocableVariable(label='Products JSON')
        public String productsJson;
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess;
        @InvocableVariable(label='Error Message')
        public String errorMessage;
    }

    @InvocableMethod(
        label='Search Products (RLM)'
        description='GET /connect/cpq/products/search — Searches the Revenue Cloud product catalog'
        category='Revenue Cloud'
    )
    public static List<Result> execute(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            Result res = new Result();
            try {
                Map<String, Object> response = RLM_RevenueCloudService.searchProducts(req.keyword);
                res.productsJson = JSON.serialize(response);
                res.isSuccess = true;
            } catch (Exception e) {
                res.isSuccess = false;
                res.errorMessage = e.getMessage();
            }
            results.add(res);
        }
        return results;
    }
}