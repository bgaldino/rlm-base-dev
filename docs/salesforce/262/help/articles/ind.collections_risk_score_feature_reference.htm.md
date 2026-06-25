---
article_id: ind.collections_risk_score_feature_reference.htm
title: Overview of Features and Assets of Tableau Next App for Collections
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_risk_score_feature_reference.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_calculate_risk_scores.htm
fetched_at: 2026-06-21
---

# Overview of Features and Assets of Tableau Next App for Collections

Review these input features and assets that are used when installing and configuring the Tableau Next app for Collections by using the Scoring Framework configuration template type, Collections Risk Score.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
Input Features

The Collections Risk Scoring template configuration includes a set of predefined fields that you can select as input features for training and scoring the predictive AI model.

INPUT FEATURE LABEL	DESCRIPTION
Total Charges	The total interest and fees associated with a collection plan.
Due Date Quartile	The week of the year the due date falls on.
Collection Life	The number of days between the due date and the closed date.
Reason Code	A unique code that represents the collection plan reason.
Reason	The reason for initiating the collection process, including non-payment of bills, bankruptcy, outstanding invoices, and deceased account holders.
Recovery Chances	The likelihood of a collection being successfully paid.
Assets

When you install the Tableau Next app for Collections, these assets are installed. You can customize these assets according to your business requirements.

Training Batch Data Transform: This batch data transform is created and run during the Tableau Next app installation. The name of the training batch data transform is in the format, <app name> Training BDT. For example, if the app name is Collections, the training batch transform name is Collections Training BDT. It collects data from multiple relevant Data Model objects based on the configuration and creates the flattened training data in a new transform Data Model Object. The newly created Data Model Object 's name is in the format, <App name> RiskScore. For example, if your app name is Collections, the Data Model Object name is Collections RiskScore. The training batch data transform uses historical Collections data to train the predictive model.
Einstein Predictive AI Model: The model is created during the Tableau Next app installation. Train the model by using the training data. This model's configuration is derived from the predefined template, Collections Risk Scoring template configurations. The predictive AI model's name is Collections Risk Score, and you can view it in Einstein Studio.
Scoring Batch Data Transform: This batch data transform is created and run during the Tableau Next app installation. The name of the scoring batch data transform is in the format, <app name> Scoring BDT. For example, if the app name is Collections, the scoring batch transform name is Collections Scoring BDT. It collects data from multiple relevant Data Model objects based on the configuration, and also collects new and in progress Collection Plan data. Uses the trained Einstein Model to assign the risk scores on them. The consolidated data, along with risk scores is stored in a Transform Data Model object named <App name> Risk Score.
SEE ALSO
Salesforce Help: Predictive Model Monitoring
