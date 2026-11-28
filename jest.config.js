// Pinned to UTC so a suite gives the same answer on every machine. A suite whose result depends on
// the browser's zone sets it per case (tests/jest/browser-time-zone-environment.js), as the billing
// UI's *.timezones.test.js suites do (todo 510).
process.env.TZ = 'UTC';

const { jestConfig } = require('@salesforce/sfdx-lwc-jest/config');

module.exports = {
    ...jestConfig,
    modulePathIgnorePatterns: ['<rootDir>/.localdevserver'],
    // The preset's node_modules ignore, restored (this list replaces the preset's), plus the
    // nested repos and worktrees whose copies of components would make a local run differ
    // from CI's clean checkout.
    testPathIgnorePatterns: [
        '/__mocks__/',
        '<rootDir>/node_modules/',
        '<rootDir>/.agents/',
        '<rootDir>/.claude/',
        '<rootDir>/.harness/'
    ],
    moduleNameMapper: {
        ...jestConfig.moduleNameMapper
    }
};
