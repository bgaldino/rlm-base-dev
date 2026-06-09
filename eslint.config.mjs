import lwc from "@salesforce/eslint-config-lwc/recommended.js";

export default [
    ...lwc,
    {
        files: ["force-app/**/lwc/**/*.js", "unpackaged/**/lwc/**/*.js"],
    },
];
