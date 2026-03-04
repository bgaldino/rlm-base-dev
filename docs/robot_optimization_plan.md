# Robot Framework Document Builder - Optimization Plan

**Status**: Ready for Implementation
**Created**: 2026-03-04
**Estimated Total Time**: 45-60 minutes

## Overview

This document outlines remaining optimization opportunities for the Document Builder toggle fix. Items 1-3 have been completed. This plan covers items 4-8 for future implementation.

---

## Completed Items ✅

- ✅ **Item 1**: Document Chrome 109+ requirement in READMEs
- ✅ **Item 3**: Extract `findInShadows` JavaScript function to eliminate duplication

## Items Not Possible ❌

- ❌ **Item 2**: ~~Add script_timeout to SeleniumLibrary settings~~
  - **Status**: Cannot be implemented - SeleniumLibrary does not support `script_timeout` parameter at library import level
  - **Finding**: SeleniumLibrary only supports: `timeout`, `implicit_wait`, `run_on_failure`, `screenshot_root_directory`
  - **Attempted**: Added `script_timeout=10` which caused error: "Library 'SeleniumLibrary' got unexpected named argument 'script_timeout'"
  - **Alternatives Considered**:
    - Set timeout programmatically via WebDriver capabilities (requires driver initialization refactoring)
    - Use `Execute Async Javascript` keyword (different API, would require refactoring all JS calls)
  - **Mitigation**: Existing `timeout=15` and `implicit_wait=5` provide reasonable protection. JavaScript execution is typically fast (<1s) in these tests.

---

## Outstanding Items

### 🟡 Item 4: Optimize DOM Traversal in findInShadows (15 min)

**Priority**: Medium
**File**: `robot/rlm-base/resources/SetupToggles.robot`
**Lines**: Variable `${FIND_IN_SHADOWS_JS}` (around line 15)

**Current Implementation**:
```javascript
var list = root.querySelectorAll("*");
```

**Problem**:
- Gets ALL elements in the DOM tree
- Inefficient on large pages (though Revenue Settings is typically small)
- Unnecessary processing for elements without shadowRoot

**Recommended Solution**:
```javascript
// Option 1: Iterate only direct descendants recursively
function findInShadows(root) {
    var el = root.querySelector("input[name=documentBuilderEnabled]");
    if (el) return el;

    // Use children instead of querySelectorAll("*")
    var children = root.children || [];
    for (var i = 0; i < children.length; i++) {
        if (children[i].shadowRoot) {
            var r = findInShadows(children[i].shadowRoot);
            if (r) return r;
        }
        // Also check descendants of this child
        var descendant = findInShadows(children[i]);
        if (descendant) return descendant;
    }
    return null;
}

// Option 2: Use TreeWalker (more efficient for deep trees)
function findInShadows(root) {
    var el = root.querySelector("input[name=documentBuilderEnabled]");
    if (el) return el;

    var walker = document.createTreeWalker(
        root,
        NodeFilter.SHOW_ELEMENT,
        {
            acceptNode: function(node) {
                return node.shadowRoot ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
            }
        }
    );

    var node;
    while (node = walker.nextNode()) {
        if (node.shadowRoot) {
            var r = findInShadows(node.shadowRoot);
            if (r) return r;
        }
    }
    return null;
}
```

**Testing**:
1. Run `cci task run enable_document_builder_toggle --org <test-org>`
2. Verify Document Builder toggle still works
3. Check Robot log for timing improvements

**Impact**: Minor performance improvement, better code quality

---

### 🟡 Item 5: Add JavaScript Return Value Validation (10 min)

**Priority**: Medium
**File**: `robot/rlm-base/resources/SetupToggles.robot`
**Keywords**: `_VerifyDocumentBuilderViaShadowDOM`, `_VerifyToggleViaShadowDOM`, `_EnsureShadowDOMToggle`

**Problem**:
- No validation that JavaScript returns expected values
- Could fail silently on unexpected return values
- No clear error message if JS execution fails

**Current Implementation**:
```robot
IF    "${state}" == "on" and ${expected_on}
    Log    Toggle verified ON
ELSE IF    "${state}" == "off" and not ${expected_on}
    Log    Toggle verified OFF
ELSE
    # Falls through to warning/error
END
```

**Recommended Solution**:
```robot
*** Keywords ***
_ValidateToggleState
    [Documentation]    Validates that JavaScript returned an expected toggle state value
    [Arguments]    ${state}    ${label}
    ${valid_states}=    Create List    on    off    not_found    label_not_found    section_not_found
    ${is_valid}=    Evaluate    '${state}' in ${valid_states}
    Run Keyword If    not ${is_valid}    Run Keywords
    ...    Log    ERROR: JavaScript returned unexpected state: ${state} for toggle ${label}    ERROR
    ...    AND    Capture Page Screenshot    filename=js_unexpected_state_${label}.png
    ...    AND    Fail    msg=JavaScript execution error: unexpected state '${state}' for ${label}
    RETURN    ${is_valid}

# Then use in each keyword before processing:
_VerifyDocumentBuilderViaShadowDOM
    [Arguments]    ${label}    ${expected_on}=True
    ${state}=    Execute Javascript    ...
    _ValidateToggleState    ${state}    ${label}
    # Continue with existing logic...
```

**Testing**:
1. Run existing tests - should pass
2. Manually inject invalid return value to verify error handling
3. Check that error message is clear and actionable

**Impact**: Better error diagnostics, fail-fast on unexpected conditions

---

### 🟢 Item 6: Replace Fixed Sleeps with Wait Until Keywords (15 min)

**Priority**: Low (optimization, not correctness)
**File**: `robot/rlm-base/resources/SetupToggles.robot`
**Lines**: 345, 350, 355 (3-second sleeps), 363 (0.5s sleep)

**Problem**:
- Fixed 3-second sleeps slow down execution
- Wastes time if toggle updates faster
- May not be enough if toggle updates slower

**Current Implementation**:
```robot
ELSE IF    "${result}" == "clicked"
    Sleep    3s    reason=Allow toggle state to update after JS click
```

**Recommended Solution**:
```robot
*** Variables ***
${TOGGLE_UPDATE_TIMEOUT}    5s
${TOGGLE_UPDATE_RETRY}      0.5s

*** Keywords ***
_EnsureShadowDOMToggle
    [Arguments]    ${label}    ${toggle_locator}    ${turn_on}=True
    ${result}=    Execute Javascript    ...

    IF    "${result}" == "clicked"
        # Instead of fixed sleep, wait for verification
        Wait Until Keyword Succeeds    ${TOGGLE_UPDATE_TIMEOUT}    ${TOGGLE_UPDATE_RETRY}
        ...    _VerifyToggleStateChanged    ${label}    ${turn_on}
    ELSE IF    "${result}" == "label_not_found"
        Log    WARNING: Label not found, using fallback    WARN
        Capture Page Screenshot
        _ClickToggleElement    ${toggle_locator}
        Wait Until Keyword Succeeds    ${TOGGLE_UPDATE_TIMEOUT}    ${TOGGLE_UPDATE_RETRY}
        ...    _VerifyToggleStateChanged    ${label}    ${turn_on}
    END

_VerifyToggleStateChanged
    [Documentation]    Quick verification keyword for Wait Until - just checks state without full logic
    [Arguments]    ${label}    ${expected_on}
    ${state}=    Execute Javascript    ...    # Fast inline verification
    Run Keyword If    ${expected_on}    Should Be Equal    ${state}    on
    Run Keyword If    not ${expected_on}    Should Be Equal    ${state}    off
```

**Benefits**:
- Faster on average (returns as soon as toggle updates)
- More reliable (retries if toggle is slow)
- Better CI performance

**Testing**:
1. Run on fast network - should complete faster than 3s
2. Run on slow network/org - should still work (with retries)
3. Measure time savings in CI logs

**Impact**: 10-30% faster execution in typical scenarios

---

### 🟢 Item 7: Increase MAX_ANCESTOR_DEPTH (5 min)

**Priority**: Low (preventive maintenance)
**File**: `robot/rlm-base/resources/SetupToggles.robot`
**Lines**: 314 (in `_EnsureShadowDOMToggle`)

**Problem**:
- Hardcoded depth limit of 10 ancestors
- Could fail if Salesforce changes page structure
- No clear indication when depth limit is reached

**Current Implementation**:
```javascript
for (var depth = 0; depth < 10; depth++) {
    section = section.parentElement;
    // ...
}
```

**Recommended Solution**:
```robot
*** Variables ***
${JS_MAX_ANCESTOR_DEPTH}    15    # Increased from 10 for robustness

# Then in JavaScript:
...    for (var depth = 0; depth < 15; depth++) {
```

**Alternative** (better logging):
```javascript
var MAX_DEPTH = 15;
for (var depth = 0; depth < MAX_DEPTH; depth++) {
    section = section.parentElement;
    if (!section || section === document.body) {
        console.log('Reached document boundary at depth ' + depth);
        return 'section_not_found';
    }
    // ... rest of logic
}
console.log('Reached max depth ' + MAX_DEPTH + ' without finding toggle');
return 'section_not_found';
```

**Testing**:
1. Verify on current Revenue Settings page (should work)
2. Add logging to track actual depth used
3. Consider if depth > 15 is ever needed (unlikely)

**Impact**: Prevents future breakage if Salesforce adds nesting

---

### 🟢 Item 8: Add Graceful Import Error Handling (5 min)

**Priority**: Low (developer experience)
**File**: `robot/rlm-base/resources/ChromeOptionsHelper.py`
**Lines**: 8 (import statement)

**Problem**:
- If selenium isn't installed, error message is cryptic
- No guidance on how to fix

**Current Implementation**:
```python
from selenium import webdriver
```

**Recommended Solution**:
```python
try:
    from selenium import webdriver
except ImportError as e:
    raise ImportError(
        "selenium package required for Robot Framework setup tasks. "
        "Install with: pipx inject cumulusci robotframework-seleniumlibrary "
        "or pip install -r robot/requirements.txt"
    ) from e
```

**Testing**:
1. Temporarily rename selenium package
2. Run `robot --version` to trigger import
3. Verify error message is helpful
4. Restore selenium package

**Impact**: Better developer experience, clearer error messages

---

## Implementation Strategy

### Recommended Order

1. **Start with Item 7** (5 min) - Quick win, no testing required
2. **Then Item 8** (5 min) - Another quick win
3. **Then Item 5** (10 min) - Improves error handling for remaining items
4. **Then Item 6** (15 min) - Most impactful optimization
5. **Finally Item 4** (15 min) - Performance optimization, test thoroughly

### Testing Checklist

After each change:
- [ ] Run `cci task run enable_document_builder_toggle --org <test-org>`
- [ ] Verify Document Builder toggle enables successfully
- [ ] Verify Design Document Templates and Export toggles work
- [ ] Check Robot logs for any errors or warnings
- [ ] Run `cci flow run prepare_docgen --org <test-org>` for end-to-end test
- [ ] Test with `HEADLESS=false` to visually verify behavior

### Validation

Create a test script to run before/after optimizations:

```bash
#!/bin/bash
# test_robot_optimizations.sh

echo "Testing Document Builder toggle..."
time cci task run enable_document_builder_toggle --org test-scratch

echo "Checking Robot logs..."
grep -i "error\|fail\|timeout" robot/rlm-base/results/log.html || echo "No errors found"

echo "Testing full docgen flow..."
time cci flow run prepare_docgen --org test-scratch

echo "Complete! Check timings above."
```

---

## Rollback Plan

If any optimization causes issues:

1. **Immediate**: Revert the specific change via `git checkout -- <file>`
2. **Document**: Add note to this plan about why it failed
3. **Continue**: Proceed with other optimizations
4. **Revisit**: Come back to failed item with more investigation

Git workflow:
```bash
# Before starting
git checkout -b robot-optimizations

# After each item
git add -A
git commit -m "Optimize: Item N - <description>"

# If something breaks
git revert HEAD
# or
git reset --hard HEAD~1
```

---

## Success Metrics

- ✅ No test failures introduced
- ✅ Execution time reduced by 10-30% (Items 4, 6)
- ✅ Error messages more actionable (Items 5, 8)
- ✅ Code more maintainable (Items 4, 7)
- ✅ All existing tests pass

---

## Notes

- These optimizations are **optional** - current code is production-ready
- Focus on **Items 4-5** for best ROI (20 min, biggest impact)
- **Item 6** is nice-to-have for CI performance
- **Items 7-8** are preventive maintenance

## Questions / Issues

If you encounter problems during implementation:
1. Check the "Rollback Plan" section above
2. Review the testing checklist
3. Consult the original code review at `/tmp/document_builder_code_review.md`
4. Document any new learnings in this plan

---

**Last Updated**: 2026-03-04
**Next Review**: After implementation or if Salesforce changes Revenue Settings page structure
