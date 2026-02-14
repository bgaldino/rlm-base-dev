*** Variables ***
# Revenue Settings setup page URL. Override via command line: robot -v REVENUE_SETTINGS_URL:https://your-org.scratch.my.salesforce-setup.com/lightning/setup/RevenueSettings/home ...
# Example scratch org (river-playground-9279):
${REVENUE_SETTINGS_URL}    https://river-playground-9279.scratch.my.salesforce-setup.com/lightning/setup/RevenueSettings/home
# If the page shows login, wait this long (e.g. 90s) for you to log in manually, then reload.
${MANUAL_LOGIN_WAIT}    90s
# Toggle label as shown on the Revenue Settings page (Doc Gen / Document Builder):
${DOCUMENT_BUILDER_TOGGLE_LABEL}    Document Builder
