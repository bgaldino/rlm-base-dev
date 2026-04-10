({
    initializeSidebarState: function(component) {
        var href = (window.location && window.location.href) ? window.location.href.toLowerCase() : "";
        var isDesignTimeContext = href.indexOf("flexipageeditor") !== -1 || href.indexOf("/setup/") !== -1;
        if (isDesignTimeContext) {
            component.set("v.isSidebarCollapsed", false);
            return;
        }

        var defaultState = component.get("v.defaultSidebarCollapsed") === true;
        var recordId = component.get("v.recordId") || "default";
        var storageKey = "rlmCollapsibleRecordTemplateWithCalculation:" + window.location.pathname + ":" + recordId;
        var collapsed = defaultState;

        try {
            var stored = window.localStorage.getItem(storageKey);
            if (stored === "true" || stored === "false") {
                collapsed = stored === "true";
            }
        } catch (e) {
            // Ignore storage access issues and use configured default.
        }

        component.set("v.isSidebarCollapsed", collapsed);
    },

    toggleSidebar: function(component, event, helper) {
        helper.toggleSidebar(component);
    },

    handleKeydown: function(component, event, helper) {
        // Check for Ctrl+\ or Cmd+\ (backslash key)
        var key = event.keyCode || event.which;
        var isModifierKey = event.ctrlKey || event.metaKey;

        // KeyCode 220 is backslash
        if (isModifierKey && key === 220) {
            event.preventDefault();
            helper.toggleSidebar(component);
        }
    }
})
