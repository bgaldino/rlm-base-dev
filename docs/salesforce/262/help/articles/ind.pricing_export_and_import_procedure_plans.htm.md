---
article_id: ind.pricing_export_and_import_procedure_plans.htm
title: Export and Import Procedure Plans
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_export_and_import_procedure_plans.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Export and Import Procedure Plans

Package procedure plans to export and import them across Salesforce orgs.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer editions of Agentforce Revenue Management where Salesforce Pricing is enabled.
USER PERMISSIONS NEEDED
To deploy and use a procedure plan package:	

Procedure Plan Access

AND

Salesforce Pricing Design Time

Key considerations before exporting a procedure plan:

You can't deploy a packaged procedure plan by using an installation URL.
When packaging a Procedure Plan or Pricing Procedure, include only the specific plan or procedure in the package.xml file. Remove all other dependencies from the file to ensure a successful import to the target org.
Second-Generation Packaging isn't supported.
The state of the source Salesforce org takes precedence over the target org.
Before importing the procedure plan, make sure you package, export, and import all dependencies in this order: Context definitions > Decision tables > Pricing procedure.
The minimum API version required is 66.0.
Package a Procedure Plan
From Setup, in the Quick Find box, find and select Package Manager.
Click New.
In the Create a Package window, specify a package name, and, if needed, a description.
Save your changes.
In the Package Detail window, on the Components tab, click Add.
Select the component type as Procedure Plan Definition.
Click Add to Package.
Make a note of the package name.
Retrieve the Packaged Procedure Plan
Open Salesforce Bench Press and connect it to your source org.
Under Metadata, go to Retrieve, and then paste the package name.
Click Retrieve.
When the retrieval succeeds, first click Fetch, and then click Download.
Unzip the downloaded package.
Open the package.xml file, and remove all dependencies except the procedure plan.
Save the package.xml file.
Compress the package folder.
Import the Packaged Procedure Plan
Log in to the target Salesforce org.
Go back to Workbench and connect it to your target org.
Select the Deploy tab.
Upload the packaged procedure plan.
Check Single Package.
Select Deploy.

From Setup, in the Quick Find box, enter Procedure Plan Definitions, and then select Procedure Plan Definitions. Verify if the procedure plan was imported successfully.
