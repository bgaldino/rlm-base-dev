public with sharing class ErrorCollector {
    public Map<String, List<String>> lineErrorMap { get; private set; }
    public List<String> genericErrorList { get; private set; }

    public ErrorCollector() {
        this.lineErrorMap = new Map<String, List<String>>();
        this.genericErrorList = new List<String>();
    }

    public void addLineError(String token, String errorCode) {
        if (lineErrorMap.containsKey(token)) {
            List<String> lineErrorList = lineErrorMap.get(token);
            lineErrorList.add(errorCode);
            lineErrorMap.put(token, lineErrorList);
        } else {
            List<String> lineErrorList = new List<String>();
            lineErrorList.add(errorCode);
            lineErrorMap.put(token, lineErrorList);
        }
    }

    public void addError(String errorCode) {
        genericErrorList.add(errorCode);
    }

    public Boolean hasError() {
        return !(lineErrorMap.isEmpty() && genericErrorList.isEmpty());
    }
}
