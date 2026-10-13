---
article_id: ind.sf_contracts_known_limitations_for_microsoft_365_integration.htm
title: Integration Limitations with Microsoft 365
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_known_limitations_for_microsoft_365_integration.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_authoring.htm
fetched_at: 2026-10-13
---

# Integration Limitations with Microsoft 365

Keep these issues and workarounds in mind when you integrate Salesforce Contracts with Microsoft 365.

KNOWN LIMITATION	DESCRIPTION	RESOLUTION
Clause alignment behavior	When a clause is inserted with left alignment, the content of the new clause is also left-aligned.	Manually adjust the clause alignment . Modifying the alignment doesn’t affect the clause reference.
Image insertion issue	When attempting to insert a document clause with a cropped image into a Microsoft 365 document, the image isn't added because there is no image source (src) in the formatted content.	To move an image from a document clause to a Microsoft 365 document, copy and paste it directly into the document.
Metadata processing issue	

Attempting to save more than 200 records in a single API call results in a metadata failure with the error message

ExternalDocumentException

.

	Submit fewer than 200 records in an API call.
Download for External Review button issue	The presence of shapes or text boxes in the contract document results in the Download for External Review button failing to load.	Omit shapes and text boxes from the contract document.
Microsoft Word and Microsoft 365 editor feature parity issue	
If the template is created in Microsoft Word, you can't edit tokens in the document template footer in Microsoft 365 editor.
If the document template or contract document includes images from nonpublic domains—that is, copyrighted images—then you can't edit the files.
If you attempt to loop over anchor boxes within the Microsoft 365 editor, it isn't supported.
If you insert richtext tokens into the document footer, Microsoft 365 editor converts them into images during document generation, making them uneditable and incompatible.
	Create the document template in the Microsoft 365 editor.
Tab key usage causes content to lock in Microsoft 365 editor	

When you press the tab key to add extra spacing within sections or clauses, it causes the Microsoft 365 editor to lock those areas. This results in two key issues:

Static text becomes uneditable unless Track Changes is enabled.
Clauses can't be inserted into locked sections during document editing.

This behavior is due to how the editor handles tab characters within content controls.

	To prevent this issue, avoid using the Tab key inside sections or clauses. To maintain spacing or indentation, press the space-bar multiple times instead of using the Tab key. This ensures content remains editable and clauses can be inserted without enabling Track Changes.
Section name formatting not applied when locked	When a section is inserted into a document, the section name is enclosed within a locked content control to prevent manual changes. However, in the Microsoft 365 editor, you can still modify font styles and formatting inside these locked controls. This leads to inconsistencies in how section headers appear across documents.	To prevent this issue, avoid making formatting changes to section names when using the Microsoft 365 editor.
Document view and PDF output don’t match	When editing documents by using Microsoft 365 editor, the formatting may differ from the final PDF output. This is noticeable when the “Don’t add spaces between paragraphs of the same style” paragraph setting is enabled. Microsoft 365 editor and Microsoft Word render this setting differently, and the PDF reflects the Microsoft Word formatting.	To prevent this issue, don’t enable the Don’t add spaces between paragraphs of the same style option while editing in the Microsoft 365 editor. This ensures consistent formatting between the editor and the generated PDF.
Microsoft 365 Word editor document source compatibility	Microsoft 365 Word editor only supports documents that are created using Microsoft 365 or Microsoft Word. Documents created by using other tools, such as Google Docs, might not be fully compatible and can result in editing or rendering issues within the Microsoft 365 editor.	Create all document templates and contract documents by using Microsoft 365 Word or Microsoft Word.
