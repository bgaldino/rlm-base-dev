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
- Text dumps match `h1`-`h3`, buttons, links, labels, table cells, spans, paragraphs and
  `lightning-formatted-text`. [Measured:
  2026-11-26, 264 (USA796), ent-sb0 harness build] A rich-text component's text was
  missing from the dump but visible in the screenshot, so use the screenshot for it.

[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, Chrome for Testing 157]
`shot` reached the Home page and printed its navigation text.

## Log in as a test user

For role-specific checks (a rep, a billing user) the sf user is the wrong identity.

1. Create the user with a Standard (or other) profile: `sf data create record -s User -v "..."`
   with `Username`, `LastName`, `Email`, `Alias`, `ProfileId`, `TimeZoneSidKey`,
   `LocaleSidKey`, `EmailEncodingKey` and `LanguageLocaleKey`. Test users are not
   org-authenticated. [Open: an earlier batch reported `sf org generate password` has no
   auth for such users; not re-measured here.]
2. Set a password through the REST password resource, which is what `set-password`
   does: `POST /services/data/v68.0/sobjects/User/<id>/password` with
   `{"NewPassword": ...}`. The password comes from an environment variable you set
   (`--password-env`); it is never taken from the command line and never printed.
3. Log in and screenshot:

```bash
# Each agent Bash call is a fresh shell: export and use the passwords in one call.
export UI_CHECK_PASSWORD="$(python3 -c 'import secrets;print(secrets.token_urlsafe(12)+"aA1!")')"
python scripts/ui_check/ui_check.py set-password --org <o> --username <u> --password-env UI_CHECK_PASSWORD
python scripts/ui_check/ui_check.py user-shot --org <o> --username <u> \
    --password-env UI_CHECK_PASSWORD \
    --path /lightning/page/home --out user.png --text
```

`user-shot` opens the org's my-domain login page, enters the username, continues to
the password step if the page is identity-first, signs in, then opens `--path`. It stops
with "login did not complete" if the final page is the login or change-password page. `--app-path /lightning/app/c__<AppDeveloperName>`
opens an app first (record pages render under the last-used app).

[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build] A Standard User created
over the API and given a REST password signed in and landed on the forced
change-password page (`/_ui/system/security/ChangePassword`) after every
`set-password`. The session was already signed in: navigating on to a Lightning path
skipped the page without changing the password, and the user's own app menu showed
(not the sf user's). Submitting the change form did not leave the page in the helper's
runs, so the helper does not use it.

[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build] `shot` (with `--text`),
`set-password`, `user-shot` and `--app-path` all ran live. So did the identity-first
step (the password field is absent until the first Login click) and the
"login did not complete" guard, which fired on the change-password page. The guard's
pass path ran on the final successful runs.

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
       <content>UiCheck_Account_Page</content>
       <formFactor>Large</formFactor>
       <skipRecordTypeSelect>false</skipRecordTypeSelect>
       <type>Flexipage</type>
       <pageOrSobjectType>Account</pageOrSobjectType>
   </actionOverrides>
   ```

   The CustomApplication also needs `<navType>Standard</navType>`,
   `<uiType>Lightning</uiType>`, `<formFactors>Large</formFactors>`, a label and a
   `<tabs>` entry. Do not put `<mode>Replace</mode>` on a region with no parent (see the
   measured note below).
2. Make the app visible to the permission set with a `SetupEntityAccess` row:
   `ParentId` = the PermissionSet Id, `SetupEntityId` = the CustomApplication Id
   (Tooling `CustomApplication`, or `AppMenuItem.ApplicationId`).
3. Assign the permission set to the test user (`PermissionSetAssignment`).
4. Open the app, then the record: `user-shot --app-path /lightning/app/c__<DeveloperName>
   --path /lightning/r/Account/<id>/view`.

[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build] The test user saw the
test page (the marker text) only inside the test app. The same record opened in the
user's default app, and as the sf user, showed the normal record page. The app URL
`/lightning/app/c__<DeveloperName>` switched apps; `/lightning/app/<CustomApplication
Id>` did not. A deploy with `<mode>Replace</mode>` on a parentless region failed with
"specifies mode 'REPLACE' but a parent region enabling that mode doesn't exist".

The app, page, permission set and assignment are test metadata: remove them with the
test records once the check is done.
