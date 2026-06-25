---
article_id: ind.collections_setup_calculate_risk_scores.htm
title: Install and Configure the Tableau Next App for Collections Risk Score Predictions
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_setup_calculate_risk_scores.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_risk_scores.htm
fetched_at: 2026-06-21
---

# Install and Configure the Tableau Next App for Collections Risk Score Predictions

Use the prebuilt Scoring Framework configuration template type, Collections Risk Score to install and configure a Tableau Next app. This app creates and trains the Einstein Predictive AI model, which can predict risk scores for collections.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To create and configure Tableau Next app:	

AI Accelerator User

AND

Einstein for Financial Services

Enable Scoring Framework, and assign users the necessary permission sets and object access.
From Setup, in the Quick Find box, enter Industries Cloud Einstein, and then select Scoring Framework.
Click New Template Configuration.
Select Collections Risk Scoring as the template configuration type.
Enter a label for the Tableau Next App to be created.
Make sure that the label length doesn't exceed 20 characters.
Select Train and deploy.
Enter a description, and click Save and Continue.
To select a data space:
Click Set Up.
Select the custom data space that you created earlier for Collections data, and click Save & Continue.
To select a Data Model Object for training and scoring:
Click Set Up.
Select Collection Plan (STANDARD), and click Save & Continue.
To consider financial account, financial account balance, and related data in Data 360, include financial accounts assets.
Click Set Up.
Select Yes, and click Save & Continue.
To consider party financial assets data in Data 360, include party financial assets.
Click Set Up.
Select Yes, and click Save & Continue.
To set the training filter duration, specify a time period in months. The predictive AI model is trained using historical data from the present back to that specified time period. For example, if you set the time period as 12 months, the predictive AI model is trained by using the past year's data.
Click Set Up.
Select the time period in months, and click Save & Continue.
To set the threshold for collection recovery, specify a time period in days. The collection plans that are still in progress are considered as not recoverable, if their corresponding days past due is more than this threshold value.
Click Set Up.
Select the time period in days, and click Save & Continue.
Set the threshold for days past due. Only records with a minimum of this specified days past due are considered for training the model. This applies only to collection plans that are currently in progress.
Click Set Up.
Select the threshold in days, and click Save & Continue.
To define conditions to filter training and scoring data:
Click Set Up.
If you plan to specify different filtering conditions for training and scoring data, turn on Configure Different Training and Scoring Conditions.
Specify the filter conditions, and click Save & Continue.
To select the input features that are used for training the predictive AI model:
Click Set Up.
Select input features from a predefined set of fields or a set of Collection Plan DMO fields, or both, and click Save & Continue.
To select features that best fit your business requirements, review the set of input features.
To set up debug configuration, click Set Up.
If you enable Save Assets, any successfully installed assets are saved even if the overall installation fails. Otherwise, a failed installation is reverted completely.
Review the template configuration summary, and activate it.
The Tableau Next app is created, and you can see the newly created app on the Scoring Framework page. If the app is installed successfully, the status of the app is shown as Active. To view the predictive AI model, open the app that is created. If the app installation fails, go to App Install History in Setup, and review the failure.
Overview of Features and Assets of Tableau Next App for Collections
Review these input features and assets that are used when installing and configuring the Tableau Next app for Collections by using the Scoring Framework configuration template type, Collections Risk Score.
SEE ALSO
Scoring Framework
