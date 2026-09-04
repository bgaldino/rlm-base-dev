---
article_id: ind.billing_payment_reconciliation_setup_data_connection.htm
title: Establish Data Connection with Data 360
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup_data_connection.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation_setup.htm
fetched_at: 2026-09-04
---

# Establish Data Connection with Data 360

Billing uses unstructured Data 360 connectors to ingest unstructured data in payment documents such as payment advice documents and payment proof documents.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To set up payment reconciliation and deploy data kits:	

Billing Admin permission set

AND

Data Cloud Architect permission set

Turn on Data 360.
Set up a Salesforce CRM connection.
Connect to a Salesforce org by setting up a CRM Salesforce org connection.
Create and deploy data streams for the Account and Invoice objects. On the Invoice object, select all fields except the Corporate Currency Converted Total Amount With Tax and Functional Currency Converted Total Amount With Tax standard fields.
Set up a data connection with Data 360.
In Data Cloud Setup, go to Feature Manager and enable Connectors. For a list of supported connectors, see Unstructured Data Connectors.
Integrate your preferred data connector to enable the flow of unstructured data in Data 360.

For example, to ingest unstructured data in payment advice and payment proofs, you can use unstructured data connectors such as Confluence, GitHub, or Google Drive. Follow the connector-specific instructions in the Data 360 Connectors and Integrations section of Data 360 Integration Guide.

Enable access to the folder, drive, or repository that contains your payment advice and payment proof documents. We recommend that you store or access the payment advice and proof documents from separate locations.
For example, if you’ve set up the unstructured Google connector, access the payment advice and payment proof docs from separate folders on Google Drive.
To ingest data from the source into Data 360, create two unstructured data lake objects (UDLO), and map the payment advice and payment proof UDLOs to corresponding payment advice and payment proof unstructured data model objects (UDMO).
The connector begins to ingest the unstructured data from the payment advice and payment proof documents into Data 360. The data ingestion process can take several minutes depending on the size and nature of your data. You can monitor the ingestion status by using the Data Streams tab or Query Editor in Data 360.
