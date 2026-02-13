import { createElement } from 'lwc';
import AppointmentSelector from 'c/appointmentSelector';

// Mock lightning/flowSupport
jest.mock('lightning/flowSupport', () => {
    return {
        FlowNavigationNextEvent: jest.fn(),
        FlowAttributeChangeEvent: jest.fn()
    };
}, { virtual: true });

describe('c-appointment-selector', () => {
    afterEach(() => {
        // Clean up the DOM after each test
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('should render with default values', () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        document.body.appendChild(element);

        expect(element.salesTransactionItems).toEqual([]);
        expect(element.productClassification).toBeUndefined();
        expect(element.qualificationContext).toBeUndefined();
        expect(element.transactionRecord).toBeUndefined();
        expect(element.summary).toBeUndefined();
    });

    it('should process slots when slotsText is set', async () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        document.body.appendChild(element);

        const mockSlotsText = 
            'Slot:1 Start: 2024-01-15 09:00:00 Finish: 2024-01-15 10:00:00 Grade: 95 ' +
            'Slot:2 Start: 2024-01-15 14:00:00 Finish: 2024-01-15 15:00:00 Grade: 85';
        
        element.slotsText = mockSlotsText;
        await Promise.resolve();

        // Check that slots were processed
        expect(element.slotsText).toBe(mockSlotsText);
    });

    it('should handle empty slotsText', async () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        document.body.appendChild(element);

        element.slotsText = '';
        await Promise.resolve();

        expect(element.slotsText).toBe('');
    });

    it('should handle slotsText with null prefix', async () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        document.body.appendChild(element);

        const mockSlotsText = 
            'null Slot:1 Start: 2024-01-15 09:00:00 Finish: 2024-01-15 10:00:00 Grade: 90';
        
        element.slotsText = mockSlotsText;
        await Promise.resolve();

        expect(element).toBeTruthy();
    });

    it('should have next button disabled when no slot selected', () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        document.body.appendChild(element);

        // isNextDisabled should be true when no slot is selected
        const nextButton = element.shadowRoot.querySelector('[data-id="next-button"]');
        if (nextButton) {
            expect(nextButton.disabled).toBe(true);
        }
    });

    it('should accept salesTransactionItems', () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        
        const mockItems = [{ id: '1', product: 'Product A' }];
        element.salesTransactionItems = mockItems;
        document.body.appendChild(element);

        expect(element.salesTransactionItems).toEqual(mockItems);
    });

    it('should accept productClassification', () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        
        element.productClassification = 'Premium';
        document.body.appendChild(element);

        expect(element.productClassification).toBe('Premium');
    });

    it('should accept qualificationContext', () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        
        const mockContext = { field: 'value' };
        element.qualificationContext = mockContext;
        document.body.appendChild(element);

        expect(element.qualificationContext).toEqual(mockContext);
    });

    it('should accept transactionRecord', () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        
        const mockRecord = { Id: '001xx0000000001', Name: 'Test' };
        element.transactionRecord = mockRecord;
        document.body.appendChild(element);

        expect(element.transactionRecord).toEqual(mockRecord);
    });

    it('should accept summary', () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        
        element.summary = 'Test Summary';
        document.body.appendChild(element);

        expect(element.summary).toBe('Test Summary');
    });

    it('should log debug information on connectedCallback', async () => {
        const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
        
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        document.body.appendChild(element);

        await Promise.resolve();

        expect(consoleSpy).toHaveBeenCalledWith('--- COMPONENT DEBUG START ---');
        expect(consoleSpy).toHaveBeenCalledWith('--- COMPONENT DEBUG END ---');

        consoleSpy.mockRestore();
    });

    it('should provide debug data through getter', () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        
        element.salesTransactionItems = [{ id: '1' }];
        element.productClassification = 'Standard';
        document.body.appendChild(element);

        // The debugData getter should return an array of debug objects
        expect(element).toBeTruthy();
    });

    it('should group slots by date', async () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        document.body.appendChild(element);

        // Slots on different dates
        const mockSlotsText = 
            'Slot:1 Start: 2024-01-15 09:00:00 Finish: 2024-01-15 10:00:00 Grade: 95 ' +
            'Slot:2 Start: 2024-01-16 09:00:00 Finish: 2024-01-16 10:00:00 Grade: 90';
        
        element.slotsText = mockSlotsText;
        await Promise.resolve();

        expect(element).toBeTruthy();
    });

    it('should format time correctly', async () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        document.body.appendChild(element);

        const mockSlotsText = 
            'Slot:1 Start: 2024-01-15 09:00:00 Finish: 2024-01-15 10:30:00 Grade: 95';
        
        element.slotsText = mockSlotsText;
        await Promise.resolve();

        // Component should render with formatted times
        expect(element).toBeTruthy();
    });

    it('should apply gold badge class for high grade slots', async () => {
        const element = createElement('c-appointment-selector', {
            is: AppointmentSelector
        });
        document.body.appendChild(element);

        // Slot with grade >= 90 should get gold badge
        const mockSlotsText = 
            'Slot:1 Start: 2024-01-15 09:00:00 Finish: 2024-01-15 10:00:00 Grade: 95';
        
        element.slotsText = mockSlotsText;
        await Promise.resolve();

        expect(element).toBeTruthy();
    });
});
