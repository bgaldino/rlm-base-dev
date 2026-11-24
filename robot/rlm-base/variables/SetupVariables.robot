*** Variables ***
# Revenue Settings page URL for runs without ORG_ALIAS. Empty by default: with ORG_ALIAS the page is opened through an authenticated session; otherwise pass -v REVENUE_SETTINGS_URL:<plain setup page URL> (never a frontdoor URL).
${REVENUE_SETTINGS_URL}    ${EMPTY}
# If the page shows login, wait this long (e.g. 90s) for you to log in manually, then reload.
${MANUAL_LOGIN_WAIT}    90s
# Toggle label as shown on the Revenue Settings page (Doc Gen / Document Builder):
${DOCUMENT_BUILDER_TOGGLE_LABEL}    Document Builder
