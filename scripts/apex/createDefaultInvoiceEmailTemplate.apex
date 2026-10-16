// Create the "Default Invoice Email Template" a Billing Settings UI toggle would create.
// Core creates it only from the Setup page's Aura controller (BillingGettingStartedController ->
// DefaultInvoiceEmailTemplateCreationService) when Invoice Email Delivery is switched on, so a
// Metadata API deploy of the setting never does. This reproduces that service: a Lightning
// (SFX) HTML template on Invoice in the org's public folder, with Core's English labels and
// merge fields. Idempotent: skips when a template of that name exists, which is also the check
// Core makes, so a later UI toggle doesn't create a duplicate. deploy_billing_email_template_settings
// then sets it as BillingSettings.defaultEmailTemplate.
String templateName = 'Default Invoice Email Template';
// Also match the developer names, ours or the fallback below: a renamed copy keeps it, and
// inserting a second one fails. deploy_billing_email_template_settings resolves the template
// with the same condition.
List<EmailTemplate> existing = [
    SELECT Id FROM EmailTemplate
    WHERE (Name = :templateName
           OR DeveloperName IN ('Default_Invoice_Email_Template', 'RLM_Default_Invoice_Email_Template'))
      AND RelatedEntityType = 'Invoice'
    LIMIT 1
];
if (!existing.isEmpty()) {
    System.debug('Default Invoice Email Template already exists: ' + existing[0].Id);
    return;
}
String html = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, '
    + 'initial-scale=1.0"><title>Salesforce Invoice Email Template</title></head><body style="margin: 0; padding: 0; '
    + 'box-sizing: border-box; font-family: \'SF Pro\', Arial, sans-serif; background-color: #ffffff;"><table width="10'
    + '0%" border="0" cellpadding="0" cellspacing="0" bgcolor="#ffffff" style="font-family: \'SF Pro\', Arial, sans-ser'
    + 'if;"><tr><td align="center" style="padding: 20px;"><table width="977" border="0" cellpadding="0" cellspacing="'
    + '0" style="width: 977px; background-color: #ffffff; border: 1px solid #dddddd;"><tr><td><div style="height: 6px'
    + '; background: #1a7f5a;"></div><div style="height: 5px; background: #defaf7;"></div><table width="100%" border='
    + '"0" cellpadding="0" cellspacing="0" bgcolor="#defaf7"><tr><td style="padding: 0 35px;"><table width="100%" bor'
    + 'der="0" cellpadding="0" cellspacing="0"><tr><td width="138" valign="middle" style="width: 138px; padding-top: '
    + '30px; padding-bottom: 30px;"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Salesforce.co'
    + 'm_logo.svg/512px-Salesforce.com_logo.svg.png" alt="Salesforce.com logo" width="110" style="width: 110px; displ'
    + 'ay: block;"></td><td valign="middle" align="center" style="padding-top: 30px; padding-bottom: 30px;"><h1 style'
    + '="font-family: \'SF Pro\', Arial, sans-serif; font-size: 28px; font-weight: 600; line-height: 36px; color: #1a36'
    + '5d; text-align: center; margin: 0;">Review and Settle Your Latest Invoice</h1></td><td width="138" style="widt'
    + 'h: 138px;">&nbsp;</td></tr></table></td></tr></table></td></tr><tr><td style="padding: 35px 35px 45px 35px; ba'
    + 'ckground: #ffffff;"><p style="font-family: \'SF Pro\', Arial, sans-serif; font-size: 18px; font-weight: 400; lin'
    + 'e-height: 26px; color: #000000; margin: 0; margin-bottom: 28px;">Hello, {{{Recipient.Name}}},</p><p style="fon'
    + 't-family: \'SF Pro\', Arial, sans-serif; font-size: 18px; font-weight: 400; line-height: 28px; color: #333333; m'
    + 'argin: 0; margin-bottom: 36px;">Thank you for your business with us. Your latest invoice is available for revi'
    + 'ew and payment. Use the Review and Pay button to login and review invoice details, manage payment methods, and'
    + ' pay the outstanding balance of {{{Invoice.Balance}}} by {{{Invoice.DueDate}}}.</p><table width="100%" border='
    + '"0" cellpadding="0" cellspacing="0" style="max-width: 913px; border: 1px solid #defaf7; border-radius: 8px; ba'
    + 'ckground: #defaf7; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0, 158, 219, 0.08);"><tr><td style="padding'
    + ': 24px 25px;"><h3 style="font-family: \'SF Pro\', Arial, sans-serif; font-size: 22px; font-weight: 700; line-hei'
    + 'ght: 28px; color: #1a365d; margin: 0 0 18px 0;">Invoice Details</h3><div style="width: 100%; height: 1px; back'
    + 'ground-color: #1a7f5a; margin-bottom: 18px;"></div><table width="100%" border="0" cellpadding="0" cellspacing='
    + '"0"><tr><td width="170" style="font-family: \'SF Pro\', Arial, sans-serif; font-size: 14px; font-weight: 500; li'
    + 'ne-height: 20px; color: #555555; padding-bottom: 18px;">Document Number</td><td style="font-family: \'SF Pro\', '
    + 'Arial, sans-serif; font-size: 15px; font-weight: 700; line-height: 22px; color: #000000; padding-bottom: 18px;'
    + '">{{{Invoice.DocumentNumber}}}</td></tr><tr><td width="170" style="font-family: \'SF Pro\', Arial, sans-serif; f'
    + 'ont-size: 14px; font-weight: 500; line-height: 20px; color: #555555; padding-bottom: 18px;">Balance</td><td st'
    + 'yle="font-family: \'SF Pro\', Arial, sans-serif; font-size: 15px; font-weight: 700; line-height: 22px; color: #0'
    + '00000; padding-bottom: 18px;">{{{Invoice.Balance}}}</td></tr><tr><td width="170" style="font-family: \'SF Pro\','
    + ' Arial, sans-serif; font-size: 14px; font-weight: 500; line-height: 20px; color: #555555;">Due Date</td><td st'
    + 'yle="font-family: \'SF Pro\', Arial, sans-serif; font-size: 15px; font-weight: 700; line-height: 22px; color: #0'
    + '00000;">{{{Invoice.DueDate}}}</td></tr></table></td></tr></table><div style="margin-bottom: 36px; margin-top: '
    + '-8px;"><span style="font-family: \'SF Pro\', Arial, sans-serif; font-size: 22px; font-weight: 700; color: #1a365'
    + 'd; vertical-align: middle;">{{{Invoice.Balance}}}</span><a href="#" target="_blank" style="display: inline-blo'
    + 'ck; vertical-align: middle; margin-left: 18px; text-align: center; text-decoration: none; background: #1a7f5a;'
    + ' color: #ffffff; border-radius: 26px; height: 44px; padding-left: 24px; padding-right: 24px; font-family: \'SF '
    + 'Pro\', Arial, sans-serif; font-size: 17px; font-weight: 700; line-height: 44px; cursor: pointer; box-shadow: 0 '
    + '3px 12px rgba(26, 127, 90, 0.12);">Review and Pay</a></div><p style="font-family: \'SF Pro\', Arial, sans-serif;'
    + ' font-size: 17px; font-weight: 400; line-height: 26px; color: #333333; margin: 0 0 18px 0;">Contact our suppor'
    + 't team for any billing or payment inquiries.</p><br><p style="font-family: \'SF Pro\', Arial, sans-serif; font-s'
    + 'ize: 17px; font-weight: 400; line-height: 26px; color: #000000; margin: 0;">Thank you,<br><strong>{{{Organizat'
    + 'ion.Name}}}</strong></p></td></tr></table></td></tr></table></body></html>';
// The developer name is unique across all templates: if another (non-Invoice) template holds
// it, use a prefixed one, which the lookups above and in deploy_billing_email_template_settings
// also match. Only these two names are matched, so when non-Invoice templates hold both, stop
// with a clear error rather than pick a name a rerun wouldn't find.
List<String> candidates = new List<String>{ 'Default_Invoice_Email_Template', 'RLM_Default_Invoice_Email_Template' };
Set<String> taken = new Set<String>();
for (EmailTemplate t : [SELECT DeveloperName FROM EmailTemplate WHERE DeveloperName IN :candidates]) {
    taken.add(t.DeveloperName);
}
String developerName;
for (String candidate : candidates) {
    if (!taken.contains(candidate)) {
        developerName = candidate;
        break;
    }
}
if (developerName == null) {
    throw new IllegalArgumentException('Can\'t create the Default Invoice Email Template: templates that aren\'t on '
        + 'Invoice already use both developer names (' + String.join(candidates, ', ') + '). Rename one of them, '
        + 'then rerun create_default_invoice_email_template.');
}
EmailTemplate template = new EmailTemplate(
    Name = templateName,
    DeveloperName = developerName,
    Description = 'Email template with a predefined structure and content format to send invoice details. The template includes the invoice number, balance amount, and due date.',
    Subject = 'Your {{{Organization.Name}}} invoice {{{Invoice.DocumentNumber}}} is due {{{Invoice.DueDate}}}',
    HtmlValue = html,
    TemplateType = 'custom',
    UiType = 'SFX',
    RelatedEntityType = 'Invoice',
    FolderId = UserInfo.getOrganizationId(),
    IsActive = true
);
insert template;
System.debug('Created Default Invoice Email Template: ' + template.Id);
