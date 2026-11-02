import lwc from "@salesforce/eslint-config-lwc/recommended.js";
import globals from "globals";

export default [
    {
        ignores: [
            "node_modules/**",
            "unpackaged/post_ux/**",
            ".agents/artifacts/**",
            ".harness/**",
        ],
    },
    ...lwc,
    {
        files: ["force-app/**/lwc/**/*.js", "unpackaged/**/lwc/**/*.js"],
    },
    // Jest suites run under jsdom, not in the platform: they need the Jest globals, and they
    // drive timers and promises the component rules forbid in shipped code.
    {
        files: ["**/lwc/**/__tests__/**/*.js"],
        languageOptions: { globals: globals.jest },
        rules: { "@lwc/lwc/no-async-operation": "off" },
    },
];
