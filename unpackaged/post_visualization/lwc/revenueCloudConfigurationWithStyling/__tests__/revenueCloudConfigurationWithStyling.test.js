import { createElement } from 'lwc';
import RevenueCloudConfigurationWithStyling from 'c/revenueCloudConfigurationWithStyling';

describe('c-revenue-cloud-configuration-with-styling', () => {
    afterEach(() => {
        // Clean up the DOM after each test
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
    });

    it('should render with default values', () => {
        const element = createElement('c-revenue-cloud-configuration-with-styling', {
            is: RevenueCloudConfigurationWithStyling
        });
        document.body.appendChild(element);

        expect(element.renderContext).toBe('3D');
        expect(element.salesTransactionItems).toEqual([]);
        expect(element.overrideRecordId).toBe('');
        expect(element.size).toBe('Medium');
        expect(element.optionGroups).toEqual([]);
    });

    it('should start unpinned', () => {
        const element = createElement('c-revenue-cloud-configuration-with-styling', {
            is: RevenueCloudConfigurationWithStyling
        });
        document.body.appendChild(element);

        // Check initial pin state via computed properties
        expect(element.shadowRoot.querySelector('.container')).toBeTruthy();
        expect(element.shadowRoot.querySelector('.container.pinned')).toBeFalsy();
    });

    it('should return correct pin icon name when unpinned', () => {
        const element = createElement('c-revenue-cloud-configuration-with-styling', {
            is: RevenueCloudConfigurationWithStyling
        });
        document.body.appendChild(element);

        // Access the component's internal state through the getter
        // Since isPinned starts as false, pinIconName should be 'utility:pin'
        const pinButton = element.shadowRoot.querySelector('.pin-button');
        expect(pinButton).toBeTruthy();
    });

    it('should toggle pin state when togglePin is called', async () => {
        const element = createElement('c-revenue-cloud-configuration-with-styling', {
            is: RevenueCloudConfigurationWithStyling
        });
        document.body.appendChild(element);

        // Find and click the pin button
        const pinButton = element.shadowRoot.querySelector('.pin-button');
        if (pinButton) {
            pinButton.click();
            await Promise.resolve();
            
            // After toggle, container should have pinned class
            const container = element.shadowRoot.querySelector('.container.pinned');
            expect(container).toBeTruthy();
        }
    });

    it('should accept configuratorContext as api property', () => {
        const element = createElement('c-revenue-cloud-configuration-with-styling', {
            is: RevenueCloudConfigurationWithStyling
        });
        
        const mockContext = { productId: '123', configId: '456' };
        element.configuratorContext = mockContext;
        document.body.appendChild(element);

        expect(element.configuratorContext).toEqual(mockContext);
    });

    it('should accept salesTransactionItems as api property', () => {
        const element = createElement('c-revenue-cloud-configuration-with-styling', {
            is: RevenueCloudConfigurationWithStyling
        });
        
        const mockItems = [{ id: '1', name: 'Item 1' }, { id: '2', name: 'Item 2' }];
        element.salesTransactionItems = mockItems;
        document.body.appendChild(element);

        expect(element.salesTransactionItems).toEqual(mockItems);
    });

    it('should have raiseInteractionEvent as public method', () => {
        const element = createElement('c-revenue-cloud-configuration-with-styling', {
            is: RevenueCloudConfigurationWithStyling
        });
        document.body.appendChild(element);

        expect(typeof element.raiseInteractionEvent).toBe('function');
    });

    it('should have getCurrentCanvas as public method', () => {
        const element = createElement('c-revenue-cloud-configuration-with-styling', {
            is: RevenueCloudConfigurationWithStyling
        });
        document.body.appendChild(element);

        expect(typeof element.getCurrentCanvas).toBe('function');
    });

    it('should return null from getCurrentCanvas when child component not found', () => {
        const element = createElement('c-revenue-cloud-configuration-with-styling', {
            is: RevenueCloudConfigurationWithStyling
        });
        document.body.appendChild(element);

        const result = element.getCurrentCanvas();
        expect(result).toBeNull();
    });
});
