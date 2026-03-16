import lwc from "@salesforce/eslint-config-lwc/recommended";

export default [
    ...lwc,
    {
        files: ["force-app/**/lwc/**/*.js", "unpackaged/**/lwc/**/*.js"],
    },
];
