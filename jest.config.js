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
