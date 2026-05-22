---
article_id: ind.pricing_use_the_procedure_plan_framework.htm
title: Use the Procedure Plan Framework
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_use_the_procedure_plan_framework.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Use the Procedure Plan Framework

To ensure your procedures run in the correct order and pricing is applied consistently to a quote, create a new procedure plan.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create and update procedure plan definitions:	

Procedure Plan Access

AND

Salesforce Pricing Design Time User


To create, update, and delete pricing procedures:	

Procedure Plan Access

OR

Salesforce Pricing Design Time User


To use pricing procedures:	Salesforce Pricing Run Time User
To define, edit, delete, set security, and set version settings for Apex classes:	Author Apex

Imagine that you work at an airline and assist business travelers. Now, let’s book a flight! We want our pricing to reflect real-time market conditions and show prices in the customer's local currency.

Before calculating the price, we’ll automatically fetch a dynamic base fare from an external system to ensure competitive pricing. We'll also apply the booking platform’s discounts and add a convenience fee.

Once we build our procedure plan, we’ll create a quote. Then, based on the user's location (for example, India), we’ll convert the total price from USD to INR.

Before you begin, ensure that you:

Have enabled Salesforce Pricing.
Have permissions to create procedures, procedure plans, products, and quotes.
Understand how to create pricing procedures. To learn more about pricing procedures, see Build Your Pricing Procedures Using Salesforce Pricing.
Understand and know how to use Context Definitions. To learn more about context definitions, see Context Definitions.
Use the same context definition across your pricing procedures and procedure plans.

Procedure plan definitions can be complex, especially when they involve Apex classes and different pricing procedures. Follow these steps to create a quote and learn how to make your pricing dynamic and accurate without complicating the procedure itself.

Turn on Procedure Plan Orchestration for Pricing
From Setup, in the Quick Find box, enter Revenue Settings, then select Revenue Settings.
Find and enable Procedure Plan Orchestration for Pricing.
Find and enable Exclude Default and Sales Transaction Type Pricing Procedures.
Create a Commercial Product
From the App Launcher, find and select Products.
Create a commercial product called Delhi - New York.
To learn how to create a product, see Create Simple Products and ensure that the Product Record Type is set as Commercial.
Add your product to the catalog and create a price book entry for it.
From Setup, in the Quick Find box, search for and select Salesforce Pricing Setup.
In the Sync Pricing Data section, click Sync.
Build Your Pricing Procedure
Create a pricing procedure and name it Flight Booking Pricing Procedure.
To create a pricing procedure, follow the first 5 steps in Configure Your Pricing Procedure.
Create constants. These constants will serve as placeholders for fixed values in your pricing procedure.
CONSTANT NAME	DATA TYPE	DEFAULT VALUE
AdjType	TEXT	Percentage
AdjValue	NUMBER	5
Override	TEXT	Override
ConvFeeAdjType	TEXT	Amount
ConvFeeAdjValue	NUMBER	-250
Add the following elements.
Pricing Setting
List Price. Use the Price Book Entries V2 decision table.
Manual Discounts. You’ll need to add three manual discount elements.
The first Manual Discount element is added to calculate the dynamic base fare of the flight. Map these variables.
Input Variables
Adjustment Type: Override
Adjustment Value: PartnerUnitPrice
Quantity: LineItemQuantity
Input Unit Price: ListPrice
Output Variable
Net Unit Price: NetUnitPrice
The second Manual Discount element is added to calculate the platform discount for the flight booking. Map these variables.
Input Variables
Adjustment Type: AdjType
Adjustment Value: AdjValue
Quantity: LineItemQuantity
Input Unit Price: PartnerUnitPrice
Output Variable
Net Unit Price: NetUnitPrice
And the last Manual Discount element is added to calculate the convenience fee to charge your customer for the flight booking.
Input Variables
Adjustment Type: ConvFeeAdjType
Adjustment Value: ConvFeeAdjValue
Quantity: LineItemQuantity
Input Unit Price: NetUnitPrice
Output Variable
Net Unit Price: NetUnitPrice
Set your preferences to view pricing information, profile access, and rank information.
Save your procedure.
Activate your procedure.

Your procedure should look like this. For the sake of clarity, we’ve renamed each Manual Discount element to show the pricing calculation it will perform. To rename an element, click and enter your desired name.

Define Classes for Apex Hooks
From Setup, in the Quick Find box, enter Apex, then select Apex Classes.
Click New.
The first Apex class is a prehook that fetches all Sales Transaction Items from the Pricing context and overrides their PartnerUnitPrice tag with a dynamic random base fare between 990 and 1200 before pricing execution from an external database.
public class DynamicFlightBasePriceApex implements RevSignaling.SignalingApexProcessor {

    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing PREHOOK');
        String contextId = request.ctxInstanceId;
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();
        
        //Query SalesTransactionItem nodes
        Map<String, Object> inputQueryItem = new Map<String, Object>{
            'contextId' => contextId,
                'tags' => new List<String>{ 'SalesTransactionItem' }
        };
        Map<String, Object> itemQueryOutput = industriesContext.queryTags(inputQueryItem);
        Map<String, Object> itemQueryResult = (Map<String, Object>)itemQueryOutput.get('queryResult');
        List<Object> itemData = (List<Object>) itemQueryResult.get('SalesTransactionItem');
        System.debug('QLI itemData=' + itemData);

        // Generate random price between 990 and 1200
        Decimal minPrice = 990;
        Decimal maxPrice = 1200;
        Decimal range = maxPrice - minPrice;

        // Use Crypto.getRandomInteger() to generate a secure random number
        Integer randomInt = Math.abs(Crypto.getRandomInteger());
        Decimal randomPrice = minPrice + Math.mod(randomInt, range.intValue() + 1);

        System.debug('Generated Random Price: ' + randomPrice);
        
        // STEP 3 - Build update list
        List<Map<String, Object>> itemNodeUpdates = new List<Map<String, Object>>();
        for (Object itemObj : itemData) {
            Map<String, Object> itemNode = (Map<String, Object>) itemObj;
            List<Object> dataPath = (List<Object>) itemNode.get('dataPath');
            System.debug('Full item dataPath: ' + JSON.serialize(dataPath));
			dataPath.remove(0); // Remove contextId
			itemNodeUpdates.add(new Map<String, Object>{
                'nodePath' => new Map<String, Object>{ 'dataPath' => dataPath },
                'attributes' => new List<Object>{
                    new Map<String, Object>{
                        'attributeName' => 'PartnerUnitPrice',
                        'attributeValue' => randomPrice
                   }
                }
            });
        }
               
        // STEP 4 - Submit context update
        if (!itemNodeUpdates.isEmpty()) {
            Map<String, Object> updateInput = new Map<String, Object>{
                'contextId' => contextId,
                'nodePathAndAttributes' => itemNodeUpdates
            };
            System.debug('--- PREHOOK: SUBMITTING CONTEXT UPDATE ---');
            System.debug(JSON.serializePretty(updateInput));
            industriesContext.updateContextAttributes(updateInput);
        }

        // Return the response
        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        response.message = 'Apex executed successfully with Random Price: ' + randomPrice;
        return response;
    }
}

Create another Apex Class.
This Apex class is a posthook that fetches the NetUnitPrice tag after pricing and converts it to the local currency, INR (Indian Rupees) using a simulated dynamic conversion rate between 85–86. It then updates the Sales Transaction Item description with the new INR fare, providing localized pricing visibility for Indian customers.
public class ConvertFareToINRApex implements RevSignaling.SignalingApexProcessor {

    public RevSignaling.TransactionResponse execute(RevSignaling.TransactionRequest request) {
        System.debug('Executing POSTHOOK');
        String contextId = request.ctxInstanceId;
        Context.IndustriesContext industriesContext = new Context.IndustriesContext();
        
        //Query SalesTransactionItem nodes
        Map<String, Object> inputQueryItem = new Map<String, Object>{
            'contextId' => contextId,
                'tags' => new List<String>{ 'SalesTransactionItem' }
        };
        Map<String, Object> itemQueryOutput = industriesContext.queryTags(inputQueryItem);
        Map<String, Object> itemQueryResult = (Map<String, Object>)itemQueryOutput.get('queryResult');
        List<Object> itemData = (List<Object>) itemQueryResult.get('SalesTransactionItem');
        System.debug('QLI itemData=' + itemData);
        
        //Query NetUnitPrice nodes
        Map<String, Object> inputQueryItem2 = new Map<String, Object>{
            'contextId' => contextId,
                'tags' => new List<String>{ 'NetUnitPrice' }
        };
        Map<String, Object> itemQueryOutput2 = industriesContext.queryTags(inputQueryItem2);
        Map<String, Object> itemQueryResult2 = (Map<String, Object>)itemQueryOutput2.get('queryResult');
        List<Object> itemData2 = (List<Object>) itemQueryResult2.get('NetUnitPrice');
        System.debug('NetUnitPrice itemData=' + itemData2);
        Map<String, Object> netUnitTagData = (Map<String, Object>) itemData2.get(0);
        Decimal netUnitPrice = (Decimal) netUnitTagData.get('tagValue');
        netUnitPrice = netUnitPrice.setScale(2);
        System.debug('NetUnitPrice Tag Value=' + netUnitPrice);

        // Generate random price between 85.00 and 86.00 with decimals
        Decimal minPrice = 85.00;
        Decimal maxPrice = 86.00;
        Decimal range = maxPrice - minPrice; 
        Integer randomInt = Math.abs(Crypto.getRandomInteger());
        Integer randomDecimalInt = Math.mod(randomInt, 100);
        Decimal randomFraction = Decimal.valueOf(randomDecimalInt) / 100;
        Decimal usdToInrRate = minPrice + randomFraction;
        if (usdToInrRate > maxPrice) { 
            usdToInrRate = maxPrice;
        }
        
        // Calculate NetUnitPrice in INR
        Decimal fareInInr = (netUnitPrice * usdToInrRate).setScale(2);
        
        String fareMessage = 'The Flight fare in INR is: ' + fareInInr + 
                     ' (USD ' + netUnitPrice + 
                     ' at rate ' + usdToInrRate + ')';
        System.debug(fareMessage);
        
        // STEP 3 - Build update list
        List<Map<String, Object>> itemNodeUpdates = new List<Map<String, Object>>();
        for (Object itemObj : itemData) {
            Map<String, Object> itemNode = (Map<String, Object>) itemObj;
            List<Object> dataPath = (List<Object>) itemNode.get('dataPath');
            System.debug('Full item dataPath: ' + JSON.serialize(dataPath));
			dataPath.remove(0); // Remove contextId
			itemNodeUpdates.add(new Map<String, Object>{
                'nodePath' => new Map<String, Object>{ 'dataPath' => dataPath },
                'attributes' => new List<Object>{
                    new Map<String, Object>{
                        'attributeName' => 'SalesTrxnItemDescription',
                        'attributeValue' => fareMessage
                   }
                }
            });
        }
            
        
        // STEP 4 - Submit context update
        if (!itemNodeUpdates.isEmpty()) {
            Map<String, Object> updateInput = new Map<String, Object>{
                'contextId' => contextId,
                'nodePathAndAttributes' => itemNodeUpdates
            };
            System.debug('--- PREHOOK: SUBMITTING CONTEXT UPDATE ---');
            System.debug(JSON.serializePretty(updateInput));
            industriesContext.updateContextAttributes(updateInput);
        }

        // Return the response
        RevSignaling.TransactionResponse response = new RevSignaling.TransactionResponse();
        response.status = RevSignaling.TransactionStatus.SUCCESS;
        response.message = 'Apex executed successfully with Price in INR: ' + fareInInr;
        return response;
    }
}

Configure a Custom Procedure Plan Definition
From Setup, in the Quick Find box, search for and select Procedure Plan Definitions.
Click New
Specify these details.
Title: Flight Booking Procedure Plan.
Press Tab to autopopulate the Developer Name.
Process Type: Revenue Cloud.
Primary Object: Quote.
Context Definition: <Context Definition Name>.
You’ll need to choose a context definition that’s been designed for your use case. However, ensure that this is the same context definition you used when you built your pricing procedure.
Save your changes.
Open the newly created procedure plan definition record.
To add the procedures that you want in the Procedure Plan Sections, select Add.
Add the first section to get the dynamic base price of our flight. Specify these details.
Type: Standard.
Name: DynamicBasePriceApex.
Section Type: Apex.
Once the section is added, click  and specify these details.
Phases: Pricing
Resolution Type: Default
Apex: DynamicFlightBasePriceApex
It should look something like this:
Similarly, add another section to perform the pricing calculation and override the base price with the price we generated using the Apex prehook. Specify these values.
Type: Standard.
Name: FlightPriceCalculation.
Section Type: Pricing Procedure .
Click  and specify these details.
Phases: Pricing
Resolution Type: Default
Procedure: Flight_Booking_Pricing_Procedure
Finally, add a section to convert the price from USD to INR (US Dollar to Indian Rupee) by adding this Apex posthook for users whose Billing Country is set to India
Type: Standard.
Name: ConvertFareToINR.
Section Type: Apex.
Click  and specify these details.
Phases: Pricing
Resolution Type: Rule-Based
Condition Requirements: All Conditions Are Met (AND)
Resource: Bill To Country
Operator: Equals
Output Value: India
Apex: ConvertFareToINRApex
Save and then, activate your procedure plan definition.
Verify Your Procedure Plan Execution

To verify if the procedure plan is executed in the order we set and the pricing is accurate, we’ll need to create a quote.

Create a quote.
In the Bill To Country field, enter India.
Save your changes.
Click Browse Catalogs and add the Delhi - New York product to the quote.
Hover on the Net Unit Price value to see the price waterfall details.
You’ll see the application of your procedure plan and the discounts and additions that you configured in your pricing procedure.
To view the converted rate for your quote line item, click in the quote line item row, and select View.
The Line Item Description shows the localized price for your flight.
