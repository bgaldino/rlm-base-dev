global with sharing class RLM_JsonSuccessParser
{
  // Field names are matched case-sensitively (equals, not ==, which ignores case in Apex), like the
  // untyped map the caller checks first, so both read the same fields.
  //
  // A body of the wrong shape (a number where an array or object belongs, an array of numbers) is
  // refused with a JSONException, which the caller reports as an unreadable response. Without these
  // checks such a body sent a read loop past the end of the input, where nextToken() keeps returning
  // null, until the CPU limit ended the transaction (measured on a 264 org). The messages name the
  // token, never a value from the body.
  @TestVisible
  private static JSONToken advance(JSONParser parser) {
    JSONToken token = parser.nextToken();
    if (token == null) {
      throw new JSONException('The response ended before its object or array closed.');
    }
    return token;
  }

  @TestVisible
  private static void requireToken(JSONParser parser, JSONToken expected) {
    if (parser.getCurrentToken() != expected) {
      throw new JSONException('Expected ' + expected + ' but found ' + parser.getCurrentToken() + '.');
    }
  }

  // Called on the array's opening token or on the end of the element just read: moves to the next
  // element and returns true when it is an object, false on the closing token of the array.
  @TestVisible
  private static Boolean nextElement(JSONParser parser) {
    JSONToken current = parser.getCurrentToken();
    if (current != JSONToken.START_ARRAY && current != JSONToken.END_OBJECT) {
      throw new JSONException('Expected an array of objects but found ' + current + '.');
    }
    if (advance(parser) == JSONToken.END_ARRAY) {
      return false;
    }
    requireToken(parser, JSONToken.START_OBJECT);
    return true;
  }

  // A text field holding an object or an array is refused: getText would return its opening token
  // and the read would go on inside it as if its fields were the parent's.
  @TestVisible
  private static String text(JSONParser parser) {
    JSONToken current = parser.getCurrentToken();
    if (current == JSONToken.START_OBJECT || current == JSONToken.START_ARRAY) {
      throw new JSONException('Expected a value but found ' + current + '.');
    }
    return parser.getText();
  }

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
            requireToken(parser, JSONToken.START_OBJECT);
            while (advance(parser) != JSONToken.END_OBJECT) {
                if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                    String text = parser.getText();
                    if (advance(parser) != JSONToken.VALUE_NULL) {
                        if (text.equals('id')) {
                            id = text(parser);
                        } else if (text.equals('transactionId')) {
                            transactionId = text(parser);
                        } else if (text.equals('boundaryLevel')) {
                            boundaryLevel = text(parser);
                        } else if (text.equals('line1')) {
                            line1 = text(parser);
                        } else if (text.equals('city')) {
                            city = text(parser);
                        } else if (text.equals('region')) {
                            region = text(parser);
                        } else if (text.equals('postalCode')) {
                            postalCode = text(parser);
                        } else if (text.equals('country')) {
                            country = text(parser);
                        } else if (text.equals('taxRegionId')) {
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
        public Decimal exemptAmount {get;set;}
        public String jurisCode {get;set;}
        public String jurisName {get;set;}
        public String stateAssignedNo {get;set;}
        public String jurisType {get;set;}
        public Decimal nonTaxableAmount {get;set;}
        public Double rate {get;set;}
        public Double tax {get;set;}
        public Decimal taxableAmount {get;set;}
        public String taxType {get;set;}
        public String taxName {get;set;}
        public Integer taxAuthorityTypeId {get;set;}
        public Double taxCalculated {get;set;}
        public String rateType {get;set;}

        public Details(JSONParser parser) {
            requireToken(parser, JSONToken.START_OBJECT);
            while (advance(parser) != JSONToken.END_OBJECT) {
                if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                    String text = parser.getText();
                    if (advance(parser) != JSONToken.VALUE_NULL) {
                        if (text.equals('id')) {
                            id = text(parser);
                        } else if (text.equals('transactionLineId')) {
                            transactionLineId = text(parser);
                        } else if (text.equals('transactionId')) {
                            transactionId = text(parser);
                        } else if (text.equals('country')) {
                            country = text(parser);
                        } else if (text.equals('region')) {
                            region = text(parser);
                        } else if (text.equals('exemptAmount')) {
                            exemptAmount = parser.getDecimalValue();
                        } else if (text.equals('jurisCode')) {
                            jurisCode = text(parser);
                        } else if (text.equals('jurisName')) {
                            jurisName = text(parser);
                        } else if (text.equals('stateAssignedNo')) {
                            stateAssignedNo = text(parser);
                        } else if (text.equals('jurisType')) {
                            jurisType = text(parser);
                        } else if (text.equals('nonTaxableAmount')) {
                            nonTaxableAmount = parser.getDecimalValue();
                        } else if (text.equals('rate')) {
                            rate = parser.getDoubleValue();
                        } else if (text.equals('tax')) {
                            tax = parser.getDoubleValue();
                        } else if (text.equals('taxableAmount')) {
                            taxableAmount = parser.getDecimalValue();
                        } else if (text.equals('taxType')) {
                            taxType = text(parser);
                        } else if (text.equals('taxName')) {
                            taxName = text(parser);
                        } else if (text.equals('taxAuthorityTypeId')) {
                            taxAuthorityTypeId = parser.getIntegerValue();
                        } else if (text.equals('taxCalculated')) {
                            taxCalculated = parser.getDoubleValue();
                        } else if (text.equals('rateType')) {
                            rateType = text(parser);
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
            requireToken(parser, JSONToken.START_OBJECT);
            while (advance(parser) != JSONToken.END_OBJECT) {
                if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                    String text = parser.getText();
                    if (advance(parser) != JSONToken.VALUE_NULL) {
                        if (text.equals('summary')) {
                            summary = text(parser);
                        } else if (text.equals('details')) {
                            details = text(parser);
                        } else if (text.equals('refersTo')) {
                            refersTo = text(parser);
                        } else if (text.equals('severity')) {
                            severity = text(parser);
                        } else if (text.equals('source')) {
                            source = text(parser);
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
    public Decimal totalAmount {get;set;}
    public Decimal totalExempt {get;set;}
    public Double totalTax {get;set;}
    public Decimal totalTaxable {get;set;}
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

    public RLM_JsonSuccessParser(JSONParser parser) {
        advance(parser);
        requireToken(parser, JSONToken.START_OBJECT);
        while (advance(parser) != JSONToken.END_OBJECT) {
            if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                String text = parser.getText();
                if (advance(parser) != JSONToken.VALUE_NULL) {
                    if (text.equals('id')) {
                        id = text(parser);
                    } else if (text.equals('code')) {
                        code = text(parser);
                    } else if (text.equals('referenceCode')){
                        referenceCode = text(parser);
                    } else if (text.equals('companyId')) {
                        companyId = parser.getIntegerValue();
                    } else if (text.equals('taxDate')) {
                        taxDate = text(parser);
                    } else if (text.equals('date')) {
                        transactionDate = text(parser);
                    } else if (text.equals('status')) {
                        status = text(parser);
                    } else if (text.equals('type')) {
                        type_Z = text(parser);
                    } else if (text.equals('reconciled')) {
                        reconciled = parser.getBooleanValue();
                    } else if (text.equals('totalAmount')) {
                        totalAmount = parser.getDecimalValue();
                    } else if (text.equals('totalExempt')) {
                        totalExempt = parser.getDecimalValue();
                    } else if (text.equals('totalTax')) {
                        totalTax = parser.getDoubleValue();
                    } else if (text.equals('totalTaxable')) {
                        totalTaxable = parser.getDecimalValue();
                    } else if (text.equals('totalTaxCalculated')) {
                        totalTaxCalculated = parser.getDoubleValue();
                    } else if (text.equals('adjustmentReason')) {
                        adjustmentReason = text(parser);
                    } else if (text.equals('locked')) {
                        locked = parser.getBooleanValue();
                    } else if (text.equals('version')) {
                        version = parser.getIntegerValue();
                    } else if (text.equals('modifiedDate')) {
                        modifiedDate = text(parser);
                    } else if (text.equals('modifiedUserId')) {
                        modifiedUserId = parser.getIntegerValue();
                    } else if (text.equals('lines')) {
                        lines = new List<Lines>();
                        while (nextElement(parser)) {
                            lines.add(new Lines(parser));
                        }
                    } else if (text.equals('addresses')) {
                        addresses = new List<Addresses>();
                        while (nextElement(parser)) {
                            addresses.add(new Addresses(parser));
                        }
                    } else if (text.equals('summary')) {
                        summary = new List<Summary>();
                        while (nextElement(parser)) {
                            summary.add(new Summary(parser));
                        }
                    } else if (text.equals('messages')) {
                        messages = new List<Messages>();
                        while (nextElement(parser)) {
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
        public Decimal taxable {get;set;}
        public Double rate {get;set;}
        public Double tax {get;set;}
        public Double taxCalculated {get;set;}
        public Decimal nonTaxable {get;set;}
        public Decimal exemption {get;set;}

        public Summary(JSONParser parser) {
            requireToken(parser, JSONToken.START_OBJECT);
            while (advance(parser) != JSONToken.END_OBJECT) {
                if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                    String text = parser.getText();
                    if (advance(parser) != JSONToken.VALUE_NULL) {
                        if (text.equals('country')) {
                            country = text(parser);
                        } else if (text.equals('region')) {
                            region = text(parser);
                        } else if (text.equals('jurisType')) {
                            jurisType = text(parser);
                        } else if (text.equals('jurisCode')) {
                            jurisCode = text(parser);
                        } else if (text.equals('jurisName')) {
                            jurisName = text(parser);
                        } else if (text.equals('taxAuthorityType')) {
                            taxAuthorityType = parser.getIntegerValue();
                        } else if (text.equals('stateAssignedNo')) {
                            stateAssignedNo = text(parser);
                        } else if (text.equals('taxType')) {
                            taxType = text(parser);
                        } else if (text.equals('taxName')) {
                            taxName = text(parser);
                        } else if (text.equals('taxGroup')) {
                            taxGroup = text(parser);
                        } else if (text.equals('rateType')) {
                            rateType = text(parser);
                        } else if (text.equals('taxable')) {
                            taxable = parser.getDecimalValue();
                        } else if (text.equals('rate')) {
                            rate = parser.getDoubleValue();
                        } else if (text.equals('tax')) {
                            tax = parser.getDoubleValue();
                        } else if (text.equals('taxCalculated')) {
                            taxCalculated = parser.getDoubleValue();
                        } else if (text.equals('nonTaxable')) {
                            nonTaxable = parser.getDecimalValue();
                        } else if (text.equals('exemption')) {
                            exemption = parser.getDecimalValue();
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
        public Decimal discountAmount {get;set;}
        public Decimal exemptAmount {get;set;}
        public Integer exemptCertId {get;set;}
        public Boolean isItemTaxable {get;set;}
        public Decimal lineAmount {get;set;}
        public Double quantity {get;set;}
        public String reportingDate {get;set;}
        public Double tax {get;set;}
        public Decimal taxableAmount {get;set;}
        public Double taxCalculated {get;set;}
        public String taxCode {get;set;}
        public String taxDate {get;set;}
        public Boolean taxIncluded {get;set;}
        public List<Details> details {get;set;}
        public String itemCode {get;set;}
        public Lines(JSONParser parser) {
            requireToken(parser, JSONToken.START_OBJECT);
            while (advance(parser) != JSONToken.END_OBJECT) {
                if (parser.getCurrentToken() == JSONToken.FIELD_NAME) {
                    String text = parser.getText();
                    if (advance(parser) != JSONToken.VALUE_NULL) {
                        if (text.equals('id')) {
                            id = text(parser);
                        } else if (text.equals('transactionId')) {
                            transactionId = text(parser);
                        }else if (text.equals('itemCode')) {
                            itemCode = text(parser);
                        }else if (text.equals('lineNumber')) {
                            lineNumber = text(parser);
                        } else if (text.equals('discountAmount')) {
                            discountAmount = parser.getDecimalValue();
                        } else if (text.equals('exemptAmount')) {
                            exemptAmount = parser.getDecimalValue();
                        } else if (text.equals('exemptCertId')) {
                            exemptCertId = parser.getIntegerValue();
                        } else if (text.equals('isItemTaxable')) {
                            isItemTaxable = parser.getBooleanValue();
                        } else if (text.equals('lineAmount')) {
                            lineAmount = parser.getDecimalValue();
                        } else if (text.equals('quantity')) {
                            quantity = parser.getDoubleValue();
                        } else if (text.equals('reportingDate')) {
                            reportingDate = text(parser);
                        } else if (text.equals('tax')) {
                            tax = parser.getDoubleValue();
                        } else if (text.equals('taxableAmount')) {
                            taxableAmount = parser.getDecimalValue();
                        } else if (text.equals('taxCalculated')) {
                            taxCalculated = parser.getDoubleValue();
                        } else if (text.equals('taxCode')) {
                            taxCode = text(parser);
                        } else if (text.equals('taxDate')) {
                            taxDate = text(parser);
                        } else if (text.equals('taxIncluded')) {
                            taxIncluded = parser.getBooleanValue();
                        } else if (text.equals('details')) {
                            details = new List<Details>();
                            while (nextElement(parser)) {
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


    public static RLM_JsonSuccessParser parse(String json)
    {
        return new RLM_JsonSuccessParser(System.JSON.createParser(json));
    }
}