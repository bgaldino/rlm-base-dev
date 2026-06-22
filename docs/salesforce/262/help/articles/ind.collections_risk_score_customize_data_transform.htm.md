---
article_id: ind.collections_risk_score_customize_data_transform.htm
title: Customize the Training and Scoring Data Transforms Used for Collections Risk Score Predictions
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_risk_score_customize_data_transform.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_risk_scores.htm
fetched_at: 2026-06-21
---

# Customize the Training and Scoring Data Transforms Used for Collections Risk Score Predictions

Customize the assets of the Tableau Next app that are created for predicting Collections risk scores according to your business requirements.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To customize the Tableau Next app assets:	Data Cloud Admin

Customize the training data transform according to your business requirements, and then run the predictive AI model. Use training metrics to evaluate the model’s performance, and determine whether it’s ready to activate. Training metrics provide information about how effectively the model understands patterns and relationships within the training data, and indicate its predictive efficacy. Do this iteratively until you achieve the required results. Customize the scoring batch data transform according to the changes that you have made to the training batch data transform. Run the scoring data transform to predict risk scores for the new collection plans.

View and edit the training batch data transform, which is included in the Tableau Next app that is installed and configured for consolidating training data. The name of the training batch data transform is in the format, <App name> Training BDT. For example, if your app name Collections, the training batch data transform name is, Collections Training BDT.
Run the training batch data transform that you customized earlier.
Check batch data transform status.
Retrain the model in Einstein Studio by using the modified training data.
Evaluate the model’s quality and determine whether it’s ready to activate by using the training metrics.
Edit the model if required.
Repeat steps 1 through 6 until you achieve the required results.
Model quality is a critical success factor in predictive AI solutions. Einstein Studio supports continuous, iterative improvement for predictive models.
Activate the model.
View and edit the scoring batch data transform, which is included in the Tableau Next app that is installed and configured for predicting risk scores. The name of the scoring batch data transform is in the format, <App name> Scoring BDT. For example, if your app name Collections, the scoring batch data transform name is, Collections Scoring BDT.
Run the scoring batch data transform that you customized earlier.
Check batch data transform status.
To make sure that any recent updates to collection plans are accounted for, and the most up-to-date risk score data is available for collection plans, schedule the scoring batch data transform according to your business requirements.
To make sure that the training data is periodically calibrated, schedule the training batch data transform to run a few times a year, according to your business requirements.
SEE ALSO
Batch Data Transforms
Einstein Predictive AI
Create, Connect, and Activate Models
