---
article_id: ind.sf_contracts_unlock_section.htm
title: Unlock Sections in a Document
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_unlock_section.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_section_management.htm
fetched_at: 2026-10-13
---

# Unlock Sections in a Document

Template designers and contract authors can unlock locked sections when they create templates and author contracts, respectively. However, if a template designer locks a section, contract authors, internal reviewers, and external reviewers can't unlock, edit, or delete that section. You can't unlock sections during internal or external reviews.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To unlock a section while designing a document template:	

Microsoft 365 Word Designer

AND

DocGen Designer

AND

Clause User OR Clause Designer


To unlock a section while authoring a contract document:	

Microsoft 365 Word Designer

AND

CLM Admin OR CLM Runtime User

AND

DocGen Designer

AND

Clause User OR Clause Designer

Unlocking is based on section ownership:

Sections locked by a contract author can only be unlocked by the same contract author.

Sections locked by a template designer can be unlocked by the same designer or other designers with the required permissions. For example, DocGen Designer 2 can unlock the section created by DocGen Designer 1 provided that the document template file is shared with the Microsoft 365 user ID linked to DocGen Designer 2.

Open a contract document or document template in the Microsoft 365 editor.
From the Home tab, open the Salesforce Contracts for Word add-in.
Click and then click Edit. Click Edit.
To unlock a section, you can also click , and then click Edit Properties. Deselect Lock Section for Editiing and save your changes.
