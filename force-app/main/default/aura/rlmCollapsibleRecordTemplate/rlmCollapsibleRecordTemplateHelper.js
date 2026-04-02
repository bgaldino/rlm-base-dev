({
    toggleSidebar: function(component) {
        var href = (window.location && window.location.href) ? window.location.href.toLowerCase() : "";
        var isDesignTimeContext = href.indexOf("flexipageeditor") !== -1 || href.indexOf("/setup/") !== -1;
        var nextValue = !component.get("v.isSidebarCollapsed");
        var recordId = component.get("v.recordId") || "default";
        var storageKey = "rlmCollapsibleRecordTemplate:" + window.location.pathname + ":" + recordId;

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