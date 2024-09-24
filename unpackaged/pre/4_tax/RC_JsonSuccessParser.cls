global with sharing class RC_JsonSuccessParser
{
  public static void consumeObject(JSONParser parser)
  {
    Integer depth = 0;
    do {
      JSONToken curr = parser.getCurrentToken();
      if (curr == JSONToken.START_OBJECT ||
        curr == JSONToken.START_ARRAY) {
        depth++;
      } else if (curr == JSONToken.END_OBJECT ||
        curr == JSONToken.END_ARRAY) {
        depth--;
      }
    } while (depth > 0 && parser.nextToken() != null);
  }

    public class Addresses {
        public String id {get;set;}
        public String transactionId {get;set;}
        public String boundaryLevel {get;set;}
        public String line1 {get;set;}
        public String city {get;set;}
        public String region {get;set;}
        public String postalCode {get;set;}
        public String country {get;set;}
        public Integer taxRegionId {get;set;}

        public Addresses(JSONParser parser) {
            while (parser.nextToken() != JSONToken.END_OBJECT) {
                if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                    String text = parser.getText();
                    if (parser.nextToken() != JSONToken.VALUE_NULL) {
                        if (text == 'id') {
                            id = parser.getText();
                        } else if (text == 'transactionId') {
                            transactionId = parser.getText();
                        } else if (text == 'boundaryLevel') {
                            boundaryLevel = parser.getText();
                        } else if (text == 'line1') {
                            line1 = parser.getText();
                        } else if (text == 'city') {
                            city = parser.getText();
                        } else if (text == 'region') {
                            region = parser.getText();
                        } else if (text == 'postalCode') {
                            postalCode = parser.getText();
                        } else if (text == 'country') {
                            country = parser.getText();
                        } else if (text == 'taxRegionId') {
                            taxRegionId = parser.getIntegerValue();
                        } else {
                            consumeObject(parser);
                        }
                    }
                }
            }
        }
    }

    public class Details {
        public String id {get;set;}
        public String transactionLineId {get;set;}
        public String transactionId {get;set;}
        public String country {get;set;}
        public String region {get;set;}
        public Integer exemptAmount {get;set;}
        public String jurisCode {get;set;}
        public String jurisName {get;set;}
        public String stateAssignedNo {get;set;}
        public String jurisType {get;set;}
        public Integer nonTaxableAmount {get;set;}
        public Double rate {get;set;}
        public Double tax {get;set;}
        public Integer taxableAmount {get;set;}
        public String taxType {get;set;}
        public String taxName {get;set;}
        public Integer taxAuthorityTypeId {get;set;}
        public Double taxCalculated {get;set;}
        public String rateType {get;set;}

        public Details(JSONParser parser) {
            while (parser.nextToken() != JSONToken.END_OBJECT) {
                if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                    String text = parser.getText();
                    if (parser.nextToken() != JSONToken.VALUE_NULL) {
                        if (text == 'id') {
                            id = parser.getText();
                        } else if (text == 'transactionLineId') {
                            transactionLineId = parser.getText();
                        } else if (text == 'transactionId') {
                            transactionId = parser.getText();
                        } else if (text == 'country') {
                            country = parser.getText();
                        } else if (text == 'region') {
                            region = parser.getText();
                        } else if (text == 'exemptAmount') {
                            exemptAmount = parser.getIntegerValue();
                        } else if (text == 'jurisCode') {
                            jurisCode = parser.getText();
                        } else if (text == 'jurisName') {
                            jurisName = parser.getText();
                        } else if (text == 'stateAssignedNo') {
                            stateAssignedNo = parser.getText();
                        } else if (text == 'jurisType') {
                            jurisType = parser.getText();
                        } else if (text == 'nonTaxableAmount') {
                            nonTaxableAmount = parser.getIntegerValue();
                        } else if (text == 'rate') {
                            rate = parser.getDoubleValue();
                        } else if (text == 'tax') {
                            tax = parser.getDoubleValue();
                        } else if (text == 'taxableAmount') {
                            taxableAmount = parser.getIntegerValue();
                        } else if (text == 'taxType') {
                            taxType = parser.getText();
                        } else if (text == 'taxName') {
                            taxName = parser.getText();
                        } else if (text == 'taxAuthorityTypeId') {
                            taxAuthorityTypeId = parser.getIntegerValue();
                        } else if (text == 'taxCalculated') {
                            taxCalculated = parser.getDoubleValue();
                        } else if (text == 'rateType') {
                            rateType = parser.getText();
                        } else {
                            consumeObject(parser);
                        }
                    }
                }
            }
        }
    }

    public class Messages {
        public String summary {get;set;}
        public String details {get;set;}
        public String refersTo {get;set;}
        public String severity {get;set;}
        public String source {get;set;}

        public Messages(JSONParser parser) {
            while (parser.nextToken() != JSONToken.END_OBJECT) {
                if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                    String text = parser.getText();
                    if (parser.nextToken() != JSONToken.VALUE_NULL) {
                        if (text == 'summary') {
                            summary = parser.getText();
                        } else if (text == 'details') {
                            details = parser.getText();
                        } else if (text == 'refersTo') {
                            refersTo = parser.getText();
                        } else if (text == 'severity') {
                            severity = parser.getText();
                        } else if (text == 'source') {
                            source = parser.getText();
                        } else {
                            consumeObject(parser);
                        }
                    }
                }
            }
        }
    }

    public String id {get;set;}
    public String code {get;set;}
    public String referenceCode {get;set;}
    public Integer companyId {get;set;}
    public String taxDate {get;set;}
    public String transactionDate {get;set;}
    public String status {get;set;}
    public String type_Z {get;set;} // in json: type
    public Boolean reconciled {get;set;}
    public Integer totalAmount {get;set;}
    public Integer totalExempt {get;set;}
    public Double totalTax {get;set;}
    public Integer totalTaxable {get;set;}
    public Double totalTaxCalculated {get;set;}
    public String adjustmentReason {get;set;}
    public Boolean locked {get;set;}
    public Integer version {get;set;}
    public String modifiedDate {get;set;}
    public Integer modifiedUserId {get;set;}
    public List<Lines> lines {get;set;}
    public List<Addresses> addresses {get;set;}
    public List<Summary> summary {get;set;}
    public List<Messages> messages {get;set;}

    public RC_JsonSuccessParser(JSONParser parser) {
        while (parser.nextToken() != JSONToken.END_OBJECT) {
            if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                String text = parser.getText();
                if (parser.nextToken() != JSONToken.VALUE_NULL) {
                    if (text == 'id') {
                        id = parser.getText();
                    } else if (text == 'code') {
                        code = parser.getText();
                    } else if (text == 'referenceCode'){
                        referenceCode = parser.getText();
                    } else if (text == 'companyId') {
                        companyId = parser.getIntegerValue();
                    } else if (text == 'taxDate') {
                        taxDate = parser.getText();
                    } else if (text == 'date') {
                        transactionDate = parser.getText();
                    } else if (text == 'status') {
                        status = parser.getText();
                    } else if (text == 'type') {
                        type_Z = parser.getText();
                    } else if (text == 'reconciled') {
                        reconciled = parser.getBooleanValue();
                    } else if (text == 'totalAmount') {
                        totalAmount = parser.getIntegerValue();
                    } else if (text == 'totalExempt') {
                        totalExempt = parser.getIntegerValue();
                    } else if (text == 'totalTax') {
                        totalTax = parser.getDoubleValue();
                    } else if (text == 'totalTaxable') {
                        totalTaxable = parser.getIntegerValue();
                    } else if (text == 'totalTaxCalculated') {
                        totalTaxCalculated = parser.getDoubleValue();
                    } else if (text == 'adjustmentReason') {
                        adjustmentReason = parser.getText();
                    } else if (text == 'locked') {
                        locked = parser.getBooleanValue();
                    } else if (text == 'version') {
                        version = parser.getIntegerValue();
                    } else if (text == 'modifiedDate') {
                        modifiedDate = parser.getText();
                    } else if (text == 'modifiedUserId') {
                        modifiedUserId = parser.getIntegerValue();
                    } else if (text == 'lines') {
                        lines = new List<Lines>();
                        while (parser.nextToken() != JSONToken.END_ARRAY) {
                            lines.add(new Lines(parser));
                        }
                    } else if (text == 'addresses') {
                        addresses = new List<Addresses>();
                        while (parser.nextToken() != JSONToken.END_ARRAY) {
                            addresses.add(new Addresses(parser));
                        }
                    } else if (text == 'summary') {
                        summary = new List<Summary>();
                        while (parser.nextToken() != JSONToken.END_ARRAY) {
                            summary.add(new Summary(parser));
                        }
                    } else if (text == 'messages') {
                        messages = new List<Messages>();
                        while (parser.nextToken() != JSONToken.END_ARRAY) {
                            messages.add(new Messages(parser));
                        }
                    } else {
                        consumeObject(parser);
                    }
                }
            }
        }
    }

    public class Summary {
        public String country {get;set;}
        public String region {get;set;}
        public String jurisType {get;set;}
        public String jurisCode {get;set;}
        public String jurisName {get;set;}
        public Integer taxAuthorityType {get;set;}
        public String stateAssignedNo {get;set;}
        public String taxType {get;set;}
        public String taxName {get;set;}
        public String taxGroup {get;set;}
        public String rateType {get;set;}
        public Integer taxable {get;set;}
        public Double rate {get;set;}
        public Double tax {get;set;}
        public Double taxCalculated {get;set;}
        public Integer nonTaxable {get;set;}
        public Integer exemption {get;set;}

        public Summary(JSONParser parser) {
            while (parser.nextToken() != JSONToken.END_OBJECT) {
                if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                    String text = parser.getText();
                    if (parser.nextToken() != JSONToken.VALUE_NULL) {
                        if (text == 'country') {
                            country = parser.getText();
                        } else if (text == 'region') {
                            region = parser.getText();
                        } else if (text == 'jurisType') {
                            jurisType = parser.getText();
                        } else if (text == 'jurisCode') {
                            jurisCode = parser.getText();
                        } else if (text == 'jurisName') {
                            jurisName = parser.getText();
                        } else if (text == 'taxAuthorityType') {
                            taxAuthorityType = parser.getIntegerValue();
                        } else if (text == 'stateAssignedNo') {
                            stateAssignedNo = parser.getText();
                        } else if (text == 'taxType') {
                            taxType = parser.getText();
                        } else if (text == 'taxName') {
                            taxName = parser.getText();
                        } else if (text == 'taxGroup') {
                            taxGroup = parser.getText();
                        } else if (text == 'rateType') {
                            rateType = parser.getText();
                        } else if (text == 'taxable') {
                            taxable = parser.getIntegerValue();
                        } else if (text == 'rate') {
                            rate = parser.getDoubleValue();
                        } else if (text == 'tax') {
                            tax = parser.getDoubleValue();
                        } else if (text == 'taxCalculated') {
                            taxCalculated = parser.getDoubleValue();
                        } else if (text == 'nonTaxable') {
                            nonTaxable = parser.getIntegerValue();
                        } else if (text == 'exemption') {
                            exemption = parser.getIntegerValue();
                        } else {
                            consumeObject(parser);
                        }
                    }
                }
            }
        }
    }

    public class Lines {
        public String id {get;set;}
        public String transactionId {get;set;}
        public String lineNumber {get;set;}
        public Integer discountAmount {get;set;}
        public Integer exemptAmount {get;set;}
        public Integer exemptCertId {get;set;}
        public Boolean isItemTaxable {get;set;}
        public Integer lineAmount {get;set;}
        public Double quantity {get;set;}
        public String reportingDate {get;set;}
        public Double tax {get;set;}
        public Integer taxableAmount {get;set;}
        public Double taxCalculated {get;set;}
        public String taxCode {get;set;}
        public String taxDate {get;set;}
        public Boolean taxIncluded {get;set;}
        public List<Details> details {get;set;}
        public String itemCode {get;set;}
        public Lines(JSONParser parser) {
            while (parser.nextToken() != JSONToken.END_OBJECT) {
                if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                    String text = parser.getText();
                    if (parser.nextToken() != JSONToken.VALUE_NULL) {
                        if (text == 'id') {
                            id = parser.getText();
                        } else if (text == 'transactionId') {
                            transactionId = parser.getText();
                        }else if (text == 'itemCode') {
                            itemCode = parser.getText();
                        }else if (text == 'lineNumber') {
                            lineNumber = parser.getText();
                        } else if (text == 'discountAmount') {
                            discountAmount = parser.getIntegerValue();
                        } else if (text == 'exemptAmount') {
                            exemptAmount = parser.getIntegerValue();
                        } else if (text == 'exemptCertId') {
                            exemptCertId = parser.getIntegerValue();
                        } else if (text == 'isItemTaxable') {
                            isItemTaxable = parser.getBooleanValue();
                        } else if (text == 'lineAmount') {
                            lineAmount = parser.getIntegerValue();
                        } else if (text == 'quantity') {
                            quantity = parser.getDoubleValue();
                        } else if (text == 'reportingDate') {
                            reportingDate = parser.getText();
                        } else if (text == 'tax') {
                            tax = parser.getDoubleValue();
                        } else if (text == 'taxableAmount') {
                            taxableAmount = parser.getIntegerValue();
                        } else if (text == 'taxCalculated') {
                            taxCalculated = parser.getDoubleValue();
                        } else if (text == 'taxCode') {
                            taxCode = parser.getText();
                        } else if (text == 'taxDate') {
                            taxDate = parser.getText();
                        } else if (text == 'taxIncluded') {
                            taxIncluded = parser.getBooleanValue();
                        } else if (text == 'details') {
                            details = new List<Details>();
                            while (parser.nextToken() != JSONToken.END_ARRAY) {
                                details.add(new Details(parser));
                            }
                        } else {
                            consumeObject(parser);
                        }
                    }
                }
            }
        }
    }


    public static RC_JsonSuccessParser parse(String json)
    {
        return new RC_JsonSuccessParser(System.JSON.createParser(json));
    }
}