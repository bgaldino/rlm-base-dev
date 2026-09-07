---
article_id: ind.approvals_add_an_approval_button_for_sales_reps.htm
title: "Example: Add an Approval Button on a Record Page"
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_add_an_approval_button_for_sales_reps.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_design_advanced_approvals.htm
fetched_at: 2026-09-07
---

# Example: Add an Approval Button on a Record Page

Add a button that users can click to submit a record for approval. Let’s see an example for adding a button on the quote page.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
NOTE In an autolaunched flow triggered by a quick action, $User resolves to the Automated Process User, not to the submitting user. If your flow needs details about the submitting user, use the Visualforce page and Apex controller approach to pass that information into the flow as an input variable. You can’t hard code the User, Group, or Queue ID in a packaged orchestration. See Revenue Cloud Advanced Approvals: Cannot deploy or package Flow Orchestration with User, Group, or Queue assignee type.

To add an approval button, follow the instructions in each of these sections.

Create an Apex Class

Follow these steps to create and use the QuoteApprovalController Apex class, which begins the approval workflows.

From Setup, search for and select Apex Classes.
Click New.
In the class editor, enter the Apex code for the class.
public class QuoteApprovalController {
    private Id quoteId;
    private String userId;
    public String submitterComments { get; set; }
   
    public QuoteApprovalController(ApexPages.StandardController controller) {
        Quote quote = (Quote) controller.getRecord();
        quoteId = quote.Id;
        userId = UserInfo.getUserId();
    }
    
    public void submitQuoteForApproval() {
        String flowApiName = 'Approval_Autolaunched_Flow';
        Map<String, Object> inputs = new Map<String, Object>();
        inputs.put('recordId', quoteId);
        inputs.put('submitter', userId);
        inputs.put('submissionComments', submitterComments);
        Flow.Interview myFlow = Flow.Interview.createInterview(flowApiName, inputs);
        myFlow.start();
    }
}

Save your changes.
Create a Visualforce Page

Follow these steps to create a Visualforce page called QuoteApprovalPage to trigger the Apex class.

From Setup, search for and select Visualforce Pages.
Click New.
Enter QuoteApprovalPage as the label and name.
Select Available for Salesforce mobile apps and Require CSRF protection on GET requests.
In the Visualforce Markup text box, enter Visualforce markup for the page.
<apex:page standardController="Quote" extensions="QuoteApprovalController" showQuickActionVfHeader="false" lightningStylesheets="true">
    <script>
        function closePopupWindow() {
            if (typeof sforce != 'undefined' && sforce && sforce.one) {
                var quoteId = '{!Quote.Id}';
                sforce.one.navigateToSObject(quoteId);
            } else {
                window.close();
            }
        }
    </script>
    <h2 align='center'>
        Submit for Approval
    </h2>
   <apex:form >
        <apex:pageBlock >
            <apex:pageBlockButtons location="bottom">
                <p align='left'>Enter comments for Approver(s):</p>
                <p align='center'><apex:inputTextarea value="{!submitterComments}" cols="100"/></p>          
                <apex:commandButton value="Submit" action="{!submitQuoteForApproval}" oncomplete="closePopupWindow();" /> 
            </apex:pageBlockButtons>
        </apex:pageBlock>
    </apex:form>
</apex:page>

Save your changes.
From Setup, search for and select Visualforce Pages.
Click Security against the QuoteApprovalPage.
Add your sales reps profiles to enable access to the Visualforce pages.
Create a Custom Action

Follow these steps to create a custom action on an object. For example, let’s create this custom action on the Quote object.

From the Object Manager, search for and select Quote.
Select Buttons, Links, and Actions.
Click New Action and specify these details.
Action Type: Custom Visualforce
Visualforce Page: QuoteApprovalPage
Label: Request for Approval
Name: Request_for_Approval
Save your changes.
Modify Page Layout of the Object

Follow these steps to add the newly created action, Submit for Approval to the page layout of the Quote object.

On the Quote object settings page, click Page Layouts.
Select Quote Layout.
In the palette, click Mobile & Lightning Actions.
Drag Submit for Approval to the Salesforce Mobile and Lightning Experience Actions section in the layout.
Save your changes.
