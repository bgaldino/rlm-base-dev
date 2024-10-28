public class ProductRulesRequestWrapper {
    //private attribute
    private Map<String, Object> criteriaAttributes; 

    public ProductRulesRequestWrapper(){
        
    }
    
    public void setWrapperAttributes(Map<String, Object> criteriaAttributes){
        this.criteriaAttributes = criteriaAttributes;
    }
    
    public Map<String, Object> getWrapperAttributes(){
        return criteriaAttributes;
    }
}