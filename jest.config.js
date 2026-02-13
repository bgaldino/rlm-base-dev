const { jestConfig } = require('@salesforce/sfdx-lwc-jest/config');

module.exports = {
    ...jestConfig,
    modulePathIgnorePatterns: ['<rootDir>/.localdevserver'],
    testPathIgnorePatterns: ['/__mocks__/'],
    moduleNameMapper: {
        ...jestConfig.moduleNameMapper,
        '^c/quotePricingChart$': '<rootDir>/unpackaged/post_fsl/lwc/quotePricingChart/quotePricingChart',
        '^c/appointmentSelector$': '<rootDir>/unpackaged/post_fsl/lwc/appointmentSelector/appointmentSelector',
        '^c/embedFlowOnCDC$': '<rootDir>/unpackaged/post_fsl/lwc/embedFlowOnCDC/embedFlowOnCDC',
        '^c/revenueCloudConfigurationWithStyling$': '<rootDir>/unpackaged/post_visualization/lwc/revenueCloudConfigurationWithStyling/revenueCloudConfigurationWithStyling',
        '^rdrawconfig/revenueCloudConfiguration$': '<rootDir>/unpackaged/post_visualization/lwc/revenueCloudConfigurationWithStyling/__tests__/__mocks__/rdrawconfig/revenueCloudConfiguration'
    }
};
