---
article_id: ind.product_catalog_example_create_custom_flow_for_browsing_and_adding_products.htm
title: Override Flow for Product Discovery
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_example_create_custom_flow_for_browsing_and_adding_products.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Override Flow for Product Discovery

Use the Discover Products flow to select a catalog and then add products from the catalog to their associated record pages. The Discover Products flow is readily available with Product Discovery, and you can customize the flow beyond the available capabilities to meet your business needs.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS
NEEDED
To open, edit, or create a flow in Flow Builder:	Manage Flow
Create an Apex Class That Creates a Context Data Input Record

The flow uses an Apex class that creates a list of ContextDataInput records that contain the object API name and the record ID. The flow then passes the list that contains additional context data to the Product List Page Container component. The component shows products and uses the additional context data, context definition, qualification rule procedure, and qualification rules to determine product eligibility.

IMPORTANT To use the quote and order fields to determine product eligibility, enable Transaction Management in your org, and also update the qualification rule procedure used for Product Discovery. See Edit a Qualification Rule Procedure and Configure Product Discovery Settings.

Create an Apex class that takes an object’s API name and record ID as input and returns a list of ContextDataInput records as the output.

From Setup, in the Quick Find box, enter Apex Classes and select it.
Click New.
In the editor, customize and paste the code that creates additional context data for your records.
public class DiscoverProductFlowAction {
    
    // Define input parameters
    public class FlowInput {
        @InvocableVariable(required=false)
        public String objectApiName;
        
        @InvocableVariable(required=false)
        public String recordId;
    }
    
    // Define output parameters     
    public class FlowOutput {
        @InvocableVariable
        public runtime_industries_cpq.ContextDataInput[] additionalContextData;
    }

    // This method is invoked from a flow
    @InvocableMethod(label='Process Input' description='Creates the Array of ContextDataInput for additional Context Data')
    public static List<FlowOutput> generateAdditionalContextData(List<FlowInput> inputs) {
        String apiName;
        String recId;
        FlowOutput output = new FlowOutput();
        
        // Capture input from the flow
		for(FlowInput input : inputs ){
            apiName = input.objectApiName;
            recId = input.recordId;
        }

        //Populate the ContextDataInput list to store additional context data
      	List<runtime_industries_cpq.ContextDataInput> listContextData = new List<runtime_industries_cpq.ContextDataInput>();
        runtime_industries_cpq.ContextDataInput cd1 = new runtime_industries_cpq.ContextDataInput();
        cd1.nodeName = 'Quote'; //Where Quote is the name of the node in the context definition.
        cd1.nodeData = new Map<String,Object>();
        cd1.nodeData.put('id',recId);       
        listContextData.add(cd1);
        
        // Return the additional Context Data to a flow
        output.additionalContextData = listContextData;
        return new List<FlowOutput>{output};       
    }
}

Save your changes.
Create a Custom Discover Products Flow

The preconfigured Discover Products flow first identifies the number of catalogs available for the user. If a default catalog is selected on the Product Discovery settings page, then the catalog automatically appears when the user initiates the flow. Next, the flow passes the objectApiName and recordId of the record that the flow is invoked from, to the Apex class to generate additional context data. Then, the flow uses the selected catalog and additional context data in the Product List Page Container component, which shows the products that users can add to quotes and orders.

Use the Product List Page component to add product lists to any object, including quotes and orders, or in custom components. The Product List Page component provides you greater flexibility to customize the display and the action label of the product list according to your specific needs.

NOTE

When you add the Product List Page component onto your custom Lightning Web Component, enable communication between them by subscribing the custom component to the productDiscovery_notification message channel of Lightning Message Service. Then, customize the actions for the events sent from the channel based on your business needs. For more information, see Subscribe and Unsubscribe from a Message Channel.

From Setup, in the Quick Find box, enter Flows and select it.
To open the preconfigured flow, click Discover Products.
Click Save as New Flow on the header of the flow page, and enter a flow label and a flow API name.
Save your changes.

You can now customize the flow.

NOTE

Updating or disabling existing parameters inherited from Discover Products flow leads to undesirable behavior or errors. It’s recommend to create new parameters to customize the Flow for specific use cases

After you create the flow, select it on the Product Discovery Settings page to automatically launch the flow when users click the Browse Catalogs button from quote and order pages. Alternatively, map the flow to its associated action button for your record pages.

SEE ALSO
Product Discovery Component Properties
Include Additional Fields in Your Flow

To show additional standard or custom product fields in your overridden flow, create a collection variable that contains these fields and then select the variable on the properties panel on the product list container component.

From Setup, in the Quick Find box, enter Flows and select it.
Open your overridden flow.
Create a flow collection variable.
You can associate the collection variable with product fields in an Assignment element.
From the toolbox manager, click New Resource.
Select Variable as the resource type.
Enter an API name and a description for the variable.
Select Text as the data type.
To convert the variable into a collection variable that can store multiple values, select Allow multiple values (collection).
Save your changes.
To assign values to the collection variable, add an Assignment element before the Product List Page flow screen component.
Enter a name, an API name, and a description for the Assignment element.
In Variable, enter the API name of the flow collection variable.
Select Add as your operator.
Specify the product field API name as a value for the variable.
For example, to add the Specification Type field of the product object as a value for the collection variable, enter Product2.SpecificationType.
You can include up to 3 additional product fields.
Select the collection variable on the Product List Container flow screen component.
Open the flow screen component.
To access the properties panel, click the Product List Container component on the Edit Screen page.
In the Additional Fields property, enter the API name of the collection variable.
Click Done.
Save your flow.
Discover Products Flow Update for Ramped Segments

If your org uses a custom Discover Products flow and you want to enable upgraded group ramp support, complete these steps.

From Setup, in the Quick Find box, enter Flows and select it.
Open the custom Discover Products flow.
Rearrange the nodes in the Discover Products flow.
In your custom Discover Products flow, move the Ramped Group node so that it appears after the catalog selection node, and before the Product List node.
Configure the Select Ramp Segments node.
Click the Select Ramp Segments node.
Click the node again to open its settings.
In Advanced, set the Discover Products context output variable.
Save the node.
Update the Product List node settings.
Click the Product List node.
In Advanced, locate the Revisited Screen Values field.
Change the value from Use values from when the user last visited this screen to Refresh inputs to incorporate changes elsewhere in the flow.
Save the node.
TIP Refer to the Discovery Products flow to ensure your customized flow is in sync with the latest update
