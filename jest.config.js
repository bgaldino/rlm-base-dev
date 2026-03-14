const { jestConfig } = require('@salesforce/sfdx-lwc-jest/config');

module.exports = {
    ...jestConfig,
    modulePathIgnorePatterns: ['<rootDir>/.localdevserver'],
    testPathIgnorePatterns: ['/__mocks__/'],
    moduleNameMapper: {
        ...jestConfig.moduleNameMapper
    }
};
