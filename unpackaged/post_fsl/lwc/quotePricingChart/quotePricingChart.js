import { LightningElement, api, wire } from 'lwc';
import getMonthlyAveragePricing from '@salesforce/apex/QuotePricingChartController.getMonthlyAveragePricing';

export default class QuotePricingChart extends LightningElement {
    @api recordId; // This will receive the Quote Id automatically when placed on a Quote record page

    chartData;
    error;

    @wire(getMonthlyAveragePricing, { quoteId: '$recordId' })
    wiredPricing({ data, error }) {
        if (data) {
            this.chartData = this.transformDataForChart(data);
            this.error = undefined;
        } else if (error) {
            this.error = error;
            this.chartData = undefined;
        }
    }

    transformDataForChart(data) {
        // Transform the Apex data into a structure your chart library expects
        // For now, just log it
        console.log('Raw Data from Apex:', JSON.stringify(data, null, 2));
        // Return the data as-is or transform if needed
        return data;
    }
}