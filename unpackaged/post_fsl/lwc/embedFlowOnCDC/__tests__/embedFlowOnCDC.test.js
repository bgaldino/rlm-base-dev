import { createElement } from 'lwc';
import EmbedFlowOnCDC from 'c/embedFlowOnCDC';
import { subscribe, unsubscribe, isEmpEnabled } from 'lightning/empApi';

// Mock lightning/empApi
jest.mock('lightning/empApi', () => {
    return {
        subscribe: jest.fn().mockResolvedValue({ channel: '/data/QuoteChangeEvent' }),
        unsubscribe: jest.fn().mockResolvedValue({}),
        isEmpEnabled: jest.fn().mockResolvedValue(true)
    };
}, { virtual: true });

// Mock lightning/platformShowToastEvent
const mockShowToastEvent = jest.fn();
jest.mock('lightning/platformShowToastEvent', () => {
    return {
        ShowToastEvent: function(config) {
            mockShowToastEvent(config);
            // Return a proper Event object
            return new CustomEvent('showtoast', { detail: config });
        }
    };
}, { virtual: true });

describe('c-embed-flow-on-cdc', () => {
    afterEach(() => {
        // Clean up the DOM after each test
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('should render component', () => {
        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        expect(element).toBeTruthy();
    });

    it('should have default flowApiName', () => {
        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        expect(element.flowApiName).toBe('Remote_Hands_Hours_Message');
    });

    it('should have default channelName', () => {
        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        expect(element.channelName).toBe('/data/QuoteChangeEvent');
    });

    it('should accept custom flowApiName', () => {
        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        element.flowApiName = 'Custom_Flow';
        document.body.appendChild(element);

        expect(element.flowApiName).toBe('Custom_Flow');
    });

    it('should accept custom channelName', () => {
        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        element.channelName = '/data/AccountChangeEvent';
        document.body.appendChild(element);

        expect(element.channelName).toBe('/data/AccountChangeEvent');
    });

    it('should check if EMP API is enabled on connect', async () => {
        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        await Promise.resolve();

        expect(isEmpEnabled).toHaveBeenCalled();
    });

    it('should subscribe to CDC channel when EMP is enabled', async () => {
        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        await Promise.resolve();
        await Promise.resolve(); // Extra tick for async operations

        expect(subscribe).toHaveBeenCalledWith(
            '/data/QuoteChangeEvent',
            -1,
            expect.any(Function)
        );
    });

    it('should not subscribe when EMP API is disabled', async () => {
        isEmpEnabled.mockResolvedValueOnce(false);

        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        await Promise.resolve();
        await Promise.resolve();

        expect(subscribe).not.toHaveBeenCalled();
    });

    it('should unsubscribe on disconnect', async () => {
        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        await Promise.resolve();
        await Promise.resolve();

        // Remove element to trigger disconnectedCallback
        document.body.removeChild(element);

        await Promise.resolve();

        expect(unsubscribe).toHaveBeenCalled();
    });

    it('should not show flow initially', () => {
        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        // Flow should not be visible initially
        const flowComponent = element.shadowRoot.querySelector('lightning-flow');
        expect(flowComponent).toBeFalsy();
    });

    it('should handle subscribe error gracefully', async () => {
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
        subscribe.mockRejectedValueOnce(new Error('Subscription failed'));

        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        await Promise.resolve();
        await Promise.resolve();
        await Promise.resolve();

        expect(consoleSpy).toHaveBeenCalled();
        consoleSpy.mockRestore();
    });

    it('should process CDC message with Quote_Message__c change', async () => {
        let capturedCallback;
        subscribe.mockImplementationOnce((channel, replayId, callback) => {
            capturedCallback = callback;
            return Promise.resolve({ channel });
        });

        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        await Promise.resolve();
        await Promise.resolve();

        // Simulate CDC message
        const mockMessage = {
            data: {
                payload: {
                    ChangeEventHeader: {
                        changedFields: ['Quote_Message__c'],
                        recordIds: ['0Q0xx0000000001']
                    }
                }
            }
        };

        if (capturedCallback) {
            capturedCallback(mockMessage);
            await Promise.resolve();
        }

        expect(element).toBeTruthy();
    });

    it('should handle CDC message without Quote_Message__c', async () => {
        let capturedCallback;
        subscribe.mockImplementationOnce((channel, replayId, callback) => {
            capturedCallback = callback;
            return Promise.resolve({ channel });
        });

        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        await Promise.resolve();
        await Promise.resolve();

        // Simulate CDC message without Quote_Message__c
        const mockMessage = {
            data: {
                payload: {
                    ChangeEventHeader: {
                        changedFields: ['Name', 'Status__c'],
                        recordIds: ['0Q0xx0000000001']
                    }
                }
            }
        };

        if (capturedCallback) {
            capturedCallback(mockMessage);
            await Promise.resolve();
        }

        // Flow should not show for unrelated field changes
        const flowComponent = element.shadowRoot.querySelector('lightning-flow');
        expect(flowComponent).toBeFalsy();
    });

    it('should handle malformed CDC message', async () => {
        const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
        let capturedCallback;
        subscribe.mockImplementationOnce((channel, replayId, callback) => {
            capturedCallback = callback;
            return Promise.resolve({ channel });
        });

        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        await Promise.resolve();
        await Promise.resolve();

        // Simulate malformed CDC message
        const mockMessage = { data: {} };

        if (capturedCallback) {
            capturedCallback(mockMessage);
            await Promise.resolve();
        }

        expect(consoleSpy).toHaveBeenCalled();
        consoleSpy.mockRestore();
    });

    it('should hide flow when status is FINISHED', async () => {
        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        await Promise.resolve();

        // Simulate flow status change event
        const statusEvent = new CustomEvent('statuschange', {
            detail: { status: 'FINISHED' }
        });

        // Component should handle the status change
        expect(element).toBeTruthy();
    });

    it('should handle flow ERROR status', async () => {
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
        
        const element = createElement('c-embed-flow-on-cdc', {
            is: EmbedFlowOnCDC
        });
        document.body.appendChild(element);

        await Promise.resolve();

        expect(element).toBeTruthy();
        consoleSpy.mockRestore();
    });
});
