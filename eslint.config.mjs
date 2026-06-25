import lwc from "@salesforce/eslint-config-lwc/recommended.js";

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
];
