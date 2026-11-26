# Live UI checks without a Robot suite

Read this to look at a Lightning page once, to check a page as another user, or to
test a FlexiPage in a shared org without touching what other people see. For
behavioral Robot changes, the verification rule in `SKILL.md` still applies; this
file is the lightweight path for investigation and for one-off evidence.

## The helper: `scripts/ui_check/ui_check.py`

Selenium + Chrome for Testing, nothing else. Tests: `python tests/test_ui_check.py`.
Run it with a Python that has selenium (the CumulusCI pipx venv). Environment:
`CHROME_BINARY` and `CHROMEDRIVER_PATH` (Chrome for Testing; see
`toolchain/sandboxed-agents.md` for the paths and for why a sandboxed agent must run
this unsandboxed), `HEADED=1` for a visible window.

```bash
python scripts/ui_check/ui_check.py shot --org <sf alias or username> \
    --path /lightning/r/Account/<id>/view --out shot.png --text
```

- `shot`: logs in as the org's sf user through the frontdoor URL, opens `--path`,
  saves a viewport screenshot and (with `--text`) prints the visible text, including
  text inside shadow roots.
- The frontdoor URL is a live session. The helper reads it from
  `sf org open --url-only --json`, uses it for one `driver.get`, and never prints,
  logs or puts it in an error. Screenshots show no URL bar. Keep it that way in any
  change: no session URL, `sid` or password in a file, a log or a PR.
- Text dumps match headings, buttons, links, labels and table cells. [Measured:
  2026-11-26, 264 (USA796), ent-sb0 harness build] A rich-text component's text was
  missing from the dump but visible in the screenshot, so use the screenshot for it.

[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, Chrome for Testing 157]
`shot` reached the Home page and printed its navigation text.

## Log in as a test user

For role-specific checks (a rep, a billing user) the sf user is the wrong identity.

1. Create the user with a Standard (or other) profile: `sf data create record -s User -v "..."`
   with `Username`, `LastName`, `Email`, `Alias`, `ProfileId`, `TimeZoneSidKey`,
   `LocaleSidKey`, `EmailEncodingKey` and `LanguageLocaleKey`. Test users are not
   org-authenticated, so `sf org generate password` does not apply.
2. Set a password through the REST password resource, which is what `set-password`
   does: `POST /services/data/v68.0/sobjects/User/<id>/password` with
   `{"NewPassword": ...}`. The password comes from an environment variable you set
   (`--password-env`); it is never taken from the command line and never printed.
3. Log in and screenshot:

```bash
export UI_CHECK_PASSWORD='<a password that meets the org policy>'
export UI_CHECK_NEW_PASSWORD='<a different one>'   # used on the forced change-password page
python scripts/ui_check/ui_check.py set-password --org <o> --username <u> --password-env UI_CHECK_PASSWORD
python scripts/ui_check/ui_check.py user-shot --org <o> --username <u> \
    --password-env UI_CHECK_PASSWORD --new-password-env UI_CHECK_NEW_PASSWORD \
    --path /lightning/page/home --out user.png --text
```

`user-shot` opens the org's my-domain login page, enters the username, continues to
the password step if the page is identity-first, signs in, changes the password on the forced change-password page when the org shows it
(to `--new-password-env`; the user then has that password, so later runs pass it as
`--password-env`), then opens `--path`. `--app-path
/lightning/app/c__<AppDeveloperName>` opens an app first (record pages render under
the last-used app).

[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build] A Standard User created
over the API and given a REST password stopped on the forced change-password page
(`/_ui/system/security/ChangePassword`: `newpassword`, `confirmpassword`, a security
`answer` field and the `password-button` submit); after the change it landed on
Lightning Home showing the user's own app menu, not the sf user's. Each `set-password`
brings the page back.

## Test a FlexiPage in a shared org without changing anyone's pages

Activating a record page as the org default changes it for everyone. Instead, give a
**test app** the page override and let only a test user see that app.

1. A FlexiPage (here a record page for Account, one rich-text marker component), a
   CustomApplication whose `actionOverrides` points at it, and an empty PermissionSet.
   Deploy them in one metadata directory (route: `toolchain/sandboxed-agents.md`).
   The app override:

   ```xml
   <actionOverrides>
       <actionName>View</actionName>
       <content>T512_Account_Page</content>
       <formFactor>Large</formFactor>
       <skipRecordTypeSelect>false</skipRecordTypeSelect>
       <type>Flexipage</type>
       <pageOrSobjectType>Account</pageOrSobjectType>
   </actionOverrides>
   ```

   The CustomApplication also needs `<navType>Standard</navType>`,
   `<uiType>Lightning</uiType>`, `<formFactors>Large</formFactors>`, a label and a
   `<tabs>` entry. Do not put `<mode>Replace</mode>` on a region with no parent: the
   deploy fails with "specifies mode 'REPLACE' but a parent region enabling that mode
   doesn't exist".
2. Make the app visible to the permission set with a `SetupEntityAccess` row:
   `ParentId` = the PermissionSet Id, `SetupEntityId` = the CustomApplication Id
   (Tooling `CustomApplication`, or `AppMenuItem.ApplicationId`).
3. Assign the permission set to the test user (`PermissionSetAssignment`).
4. Open the app, then the record: `user-shot --app-path /lightning/app/c__<DeveloperName>
   --path /lightning/r/Account/<id>/view`. The app id form `/lightning/app/<02u id>`
   did not switch apps; the `c__<DeveloperName>` form did.

[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build] The test user saw the
test page (the marker text) only inside the test app. The same record opened in the
user's default app, and as the sf user, showed the normal record page.

The app, page, permission set and assignment are test metadata: remove them with the
test records once the check is done.
