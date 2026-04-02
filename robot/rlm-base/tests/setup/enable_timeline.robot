*** Settings ***
Documentation     Enable the Timeline feature toggle at Setup → Feature Settings → Timeline.
...               Required before billing_ui flexipages that reference industries_common:timeline
...               can be deployed. Once enabled, this toggle cannot be disabled.
...
...               Sequence:
...               1. Navigate to /lightning/setup/Timeline/home
...               2. If .voiceSliderCheckBox is absent the feature is already enabled — skip.
...               3. Click label.uiLabel inside .toggle to trigger the Aura change event.
...               4. Confirm the "Turn on Timeline?" modal by clicking "Turn On".
...               5. Verify the "Timeline was enabled." toast.
Resource          ../../resources/SetupToggles.robot
Suite Setup       Open Browser For Setup
Suite Teardown    Close Browser After Setup

*** Variables ***
${ORG_ALIAS}      ${EMPTY}

*** Test Cases ***
Enable Timeline Feature
    [Documentation]    Navigate to /lightning/setup/Timeline/home and enable the
    ...                Timeline Configuration toggle if not already enabled.
    Open Setup Page    /lightning/setup/Timeline/home
    Enable Timeline Toggle
    Log    Timeline feature enabled successfully.

*** Keywords ***
Enable Timeline Toggle
    [Documentation]    Enable the Timeline Configuration toggle. The toggle is an Aura
    ...                uiInputCheckbox inside .voiceSliderCheckBox — not a lightning-input.
    ...                Clicking the label triggers a "Turn on Timeline?" confirmation modal;
    ...                we click "Turn On" to confirm. If the toggle is already gone from the
    ...                page, Timeline is already enabled and we skip.
    # If the toggle section is absent, Timeline is already enabled — nothing to do.
    ${already_on}=    Run Keyword And Return Status    Wait Until Page Contains    Configure Timelines    timeout=5s
    ${has_toggle}=    Run Keyword And Return Status    Page Should Contain Element    css:.voiceSliderCheckBox
    IF    ${already_on} and not ${has_toggle}
        Log    Timeline is already enabled (toggle not present, Configure Timelines section visible). Skipping.
        Capture Page Screenshot
        RETURN
    END
    # Wait for the toggle section to appear
    Wait Until Page Contains    Timeline Configuration    timeout=15s
    Wait Until Page Contains Element    css:.voiceSliderCheckBox .toggle label.uiLabel    timeout=10s
    # Check current state via JS — if already checked, skip
    ${result}=    Execute JavaScript
    ...    return (function() {
    ...        var inp = document.querySelector('.voiceSliderCheckBox .toggle input[type="checkbox"]');
    ...        if (!inp) return 'input_not_found';
    ...        if (inp.checked) return 'already_enabled';
    ...        var label = document.querySelector('.voiceSliderCheckBox .toggle label.uiLabel');
    ...        if (!label) return 'label_not_found';
    ...        label.click();
    ...        return 'clicked';
    ...    })()
    Log    Timeline toggle JS result: ${result}
    IF    "${result}" == "already_enabled"
        Log    Timeline toggle checkbox is already checked. Skipping.
        Capture Page Screenshot
        RETURN
    ELSE IF    "${result}" == "clicked"
        # Confirm the "Turn on Timeline?" modal
        Wait Until Page Contains    Turn on Timeline?    timeout=10s
        ${turn_on_btn}=    Execute JavaScript
        ...    return (function() {
        ...        var btns = Array.from(document.querySelectorAll('button'));
        ...        var btn = btns.find(function(b) { return b.textContent.trim() === 'Turn On'; });
        ...        if (btn) { btn.click(); return 'clicked'; }
        ...        return 'not_found';
        ...    })()
        IF    "${turn_on_btn}" != "clicked"
            Capture Page Screenshot
            Fail    msg="Turn On" button not found in the Timeline confirmation modal.
        END
        Sleep    3s    reason=Allow save to complete
        Wait Until Page Contains    Timeline was enabled.    timeout=15s
        Capture Page Screenshot
        Log    Timeline enabled and confirmed via toast.
    ELSE
        Capture Page Screenshot
        Fail    msg=Timeline toggle JS returned unexpected result: ${result}. Check the page manually.
    END
