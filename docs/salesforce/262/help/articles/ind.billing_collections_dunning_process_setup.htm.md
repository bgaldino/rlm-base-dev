---
article_id: ind.billing_collections_dunning_process_setup.htm
title: Set Up and Send Dunning Emails
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_collections_dunning_process_setup.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Set Up and Send Dunning Emails

Configure automated dunning campaign emails to improve overdue invoice collections. Your collections reps can schedule timely overdue payment email reminders on a recurring basis, helping improve payment recovery rate and reduce collections efforts.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Agentforce Revenue Management
The Collections feature is available with the Agentforce Revenue Management Billing license and the Marketing Cloud Growth edition. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To enable Data Cloud:	Data Cloud Admin permission set
To enable Marketing Cloud:	Marketing Cloud Admin permission set
To create and send dunning emails:	Billing Collections and Recovery Specialist permission set

To segment customer accounts and send personalized communication, complete the prerequisites, integrate your data into Data Cloud, and then create and send dunning emails.

Complete the Prerequisites

Before you configure the dunning process, complete these prerequisites.

Enter your company's address details in the Company Information page.
Verify if Data Cloud is enabled in your Salesforce org. See Build your Data Cloud Connection.
Make sure that your Salesforce org is connected to the Data Cloud org.
Enable Marketing Cloud Next and install the marketing data kit.
If the Sales data kit isn't available in the list of install the marketing data kits, install and deploy it manually.
Import customer consent to receive dunning emails in a CSV file and upload the CSV file to the Marketing Cloud. See Import Consent Data to Marketing Cloud Next.
Integrate Your Data Into Data Cloud

To create dunning emails, integrate and manage your data in Data Cloud by using data streams, mapping fields, employing identity resolution, segmenting data, and creating data graphs.

Ingest the data of accounts, contacts, invoices, collection plans, or collection plan items into the Data Cloud by creating a data stream using Salesforce CRM Starter Bundle.
Data ingested by all data streams is written to data lake objects.
Map the data of the Data Lake Object fields to the Data Model Object fields.
If a standard data model object meets your business needs, view and edit the data model object.
If a standard data model object doesn't meet your business needs, create a custom data model object.
To maintain the relationships between data model objects, map the data of one data model object to another data model object.
This step is required to create data graphs later.
Consolidate data from various sources to integrate information about individuals and accounts into a unified profile by using identity resolution.
See Create identity resolution rulesets and define the identity resolution rulesets to consolidate multiple sources of data into a unified profile.
Create and publish standard, custom, or waterfall segments based on your business needs.
Create and manage data graphs in your Salesforce org.
To use the fields of the datagraph as a placeholder or merge fields when you create a customized email, setup a default data graph in your Salesforce org. See Configure a Data Graph.
Create and Send Dunning Emails

Create campaigns with predefined flows to send dunning emails to the targeted segments. Customize and publish email templates based on your business requirement. Schedule your dunning emails or send them immediately. Track, report, and manage campaigns with the Marketing Calendar to streamline the email communication process.

Create an email campaign and send the dunning emails.
Create and manage SMS messages in Marketing Cloud.
NOTE Instead of segmenting customer accounts and sending dunning emails using the Data Cloud and Marketing Cloud, you can alternatively send emails directly from the Collection Plan record page, See Send Email from a Record in Lightning Experience.
