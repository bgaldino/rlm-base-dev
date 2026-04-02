({
    initializeSidebarState: function(component) {
        var href = (window.location && window.location.href) ? window.location.href.toLowerCase() : "";
        var isDesignTimeContext = href.indexOf("flexipageeditor") !== -1 || href.indexOf("/setup/") !== -1;
        if (isDesignTimeContext) {
            component.set("v.isSidebarCollapsed", false);
            return;
        }

        var defaultState = component.get("v.defaultSidebarCollapsed") === true;
        var storageKey = "rlmCollapsibleRecordTemplate:" + window.location.pathname;
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

    toggleSidebar: function(component) {
        var href = (window.location && window.location.href) ? window.location.href.toLowerCase() : "";
        var isDesignTimeContext = href.indexOf("flexipageeditor") !== -1 || href.indexOf("/setup/") !== -1;
        var nextValue = !component.get("v.isSidebarCollapsed");
        var storageKey = "rlmCollapsibleRecordTemplate:" + window.location.pathname;

        component.set("v.isSidebarCollapsed", nextValue);

        if (isDesignTimeContext) {
            return;
        }

        try {
            window.localStorage.setItem(storageKey, nextValue ? "true" : "false");
        } catch (e) {
            // Ignore storage access issues; toggle still works for current page session.
        }
    }
})
