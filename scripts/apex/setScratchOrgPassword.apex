// Sets a permanent password for the running scratch-org admin user.
//
// Why: some scratch org definitions (notably the TSO / trialforce-derived
// templates such as tfid-cdo-rlm) flag the admin user to "change password at
// next login". When a Robot/Selenium setup step then logs in via
// `sf org open --url-only` (frontdoor), Salesforce redirects to the
// "Change Your Password" screen instead of the requested Setup page, so every
// UI toggle lookup (prepare_docgen, prepare_revenue_settings, etc.) fails on
// the wrong page. Calling System.setPassword installs a permanent password and
// clears the must-reset flag, so frontdoor login lands directly on Setup.
//
// Idempotent: safe to re-run; it simply (re)sets the same password.
String pwd = 'Cumulus1234!';
try {
    System.setPassword(UserInfo.getUserId(), pwd);
    System.debug('Scratch org admin password set; must-reset flag cleared.');
} catch (Exception e) {
    // Don't fail the build if the org doesn't allow setPassword (e.g. a
    // persistent org with a stricter policy) — the step is gated to scratch
    // orgs, but stay defensive.
    System.debug(LoggingLevel.WARN, 'setScratchOrgPassword skipped: ' + e.getMessage());
}
