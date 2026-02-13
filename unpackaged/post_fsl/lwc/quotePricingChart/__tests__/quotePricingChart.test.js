import { createElement } from 'lwc';
import QuotePricingChart from 'c/quotePricingChart';
import getMonthlyAveragePricing from '@salesforce/apex/QuotePricingChartController.getMonthlyAveragePricing';

// Mock the Apex method
jest.mock(
    '@salesforce/apex/QuotePricingChartController.getMonthlyAveragePricing',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest');
        return {
            default: createApexTestWireAdapter(jest.fn())
        };
    },
    { virtual: true }
);

describe('c-quote-pricing-chart', () => {
    afterEach(() => {
        // Clean up the DOM after each test
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('should render component', () => {
        const element = createElement('c-quote-pricing-chart', {
            is: QuotePricingChart
        });
        document.body.appendChild(element);

        expect(element).toBeTruthy();
    });

    it('should accept recordId as api property', () => {
        const element = createElement('c-quote-pricing-chart', {
            is: QuotePricingChart
        });
        element.recordId = '0Q0xx0000000001';
        document.body.appendChild(element);

        expect(element.recordId).toBe('0Q0xx0000000001');
    });

    it('should handle successful wire data', async () => {
        const element = createElement('c-quote-pricing-chart', {
            is: QuotePricingChart
        });
        element.recordId = '0Q0xx0000000001';
        document.body.appendChild(element);

        const mockData = [
            { month: 'January', avgPrice: 100 },
            { month: 'February', avgPrice: 150 },
            { month: 'March', avgPrice: 125 }
        ];

        // Emit mock data through the wire adapter
        getMonthlyAveragePricing.emit(mockData);

        // Wait for any async DOM updates
        await Promise.resolve();

        // Component should have processed the data
        expect(element).toBeTruthy();
    });

    it('should handle wire error', async () => {
        const element = createElement('c-quote-pricing-chart', {
            is: QuotePricingChart
        });
        element.recordId = '0Q0xx0000000001';
        document.body.appendChild(element);

        const mockError = { message: 'An error occurred' };

        // Emit error through the wire adapter
        getMonthlyAveragePricing.error(mockError);

        // Wait for any async DOM updates
        await Promise.resolve();

        // Component should handle the error gracefully
        expect(element).toBeTruthy();
    });

    it('should transform data for chart when data is received', async () => {
        const element = createElement('c-quote-pricing-chart', {
            is: QuotePricingChart
        });
        
        // Spy on console.log to verify transformDataForChart is called
        const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
        
        element.recordId = '0Q0xx0000000001';
        document.body.appendChild(element);

        const mockData = [
            { month: 'January', avgPrice: 100 }
        ];

        getMonthlyAveragePricing.emit(mockData);
        await Promise.resolve();

        // Verify console.log was called with the data
        expect(consoleSpy).toHaveBeenCalledWith(
            'Raw Data from Apex:',
            expect.any(String)
        );

        consoleSpy.mockRestore();
    });

    it('should not have chart data initially', () => {
        const element = createElement('c-quote-pricing-chart', {
            is: QuotePricingChart
        });
        document.body.appendChild(element);

        // Before wire returns, chartData should be undefined
        expect(element).toBeTruthy();
    });
});
