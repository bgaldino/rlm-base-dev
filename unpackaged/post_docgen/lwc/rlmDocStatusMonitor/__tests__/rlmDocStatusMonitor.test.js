// getRecord.emit() is the sfdx-lwc-jest test adapter's API, not a wire call in a component.
/* eslint-disable @lwc/lwc/no-unexpected-wire-adapter-usages */
import { createElement } from 'lwc';
import RlmDocStatusMonitor from 'c/rlmDocStatusMonitor';
import { getRecord, notifyRecordUpdateAvailable } from 'lightning/uiRecordApi';
import { subscribe, unsubscribe } from 'lightning/empApi';
import { FlowAttributeChangeEventName, FlowNavigationNextEventName } from 'lightning/flowSupport';

const PROCESS_ID = '0nnWt0000007slFIAQ';
const POLL_INTERVAL_MS = 2000;
const MAX_WAIT_MS = 300000;

const statusRecord = (status) => ({
    apiName: 'DocumentGenerationProcess',
    fields: { Status: { value: status, displayValue: status } }
});

// Lets resolved promises (the EMP subscribe, notifyRecordUpdateAvailable) run their callbacks.
const flushPromises = async () => {
    for (let i = 0; i < 5; i++) {
        // eslint-disable-next-line no-await-in-loop
        await Promise.resolve();
    }
};

function mount() {
    const el = createElement('c-rlm-doc-status-monitor', { is: RlmDocStatusMonitor });
    el.processId = PROCESS_ID;
    const next = jest.fn();
    el.addEventListener(FlowNavigationNextEventName, next);
    document.body.appendChild(el);
    return { el, next };
}

describe('rlmDocStatusMonitor', () => {
    beforeEach(() => {
        jest.useFakeTimers();
        notifyRecordUpdateAvailable.mockClear();
        subscribe.mockReset();
        subscribe.mockResolvedValue({});
        unsubscribe.mockClear();
    });

    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.useRealTimers();
        jest.restoreAllMocks();
    });

    it('re-reads the status right after the EMP subscription is live', async () => {
        subscribe.mockResolvedValue({ channel: '/event/DocGenProcStsChgEvent' });
        mount();
        await flushPromises();

        expect(notifyRecordUpdateAvailable).toHaveBeenCalledWith([{ recordId: PROCESS_ID }]);
    });

    it('advances when a later read shows Success, without any platform event', async () => {
        const { el, next } = mount();
        await flushPromises();
        // The first read happens while the document is still being generated.
        getRecord.emit(statusRecord('InProgress'));
        notifyRecordUpdateAvailable.mockClear();

        jest.advanceTimersByTime(POLL_INTERVAL_MS);
        expect(notifyRecordUpdateAvailable).toHaveBeenCalledWith([{ recordId: PROCESS_ID }]);

        // Lightning Data Service re-reads the record and it is now Success.
        getRecord.emit(statusRecord('Success'));
        jest.advanceTimersByTime(300);

        expect(el.status).toBe('Success');
        expect(next).toHaveBeenCalledTimes(1);
    });

    it('stops polling once the flow has moved on', async () => {
        const { next } = mount();
        await flushPromises();
        getRecord.emit(statusRecord('Failure'));
        jest.advanceTimersByTime(300);
        expect(next).toHaveBeenCalledTimes(1);
        // The poll interval was cleared when the status arrived, not left to stop itself.
        expect(jest.getTimerCount()).toBe(0);
        notifyRecordUpdateAvailable.mockClear();

        jest.advanceTimersByTime(POLL_INTERVAL_MS * 5);

        expect(notifyRecordUpdateAvailable).not.toHaveBeenCalled();
        expect(next).toHaveBeenCalledTimes(1);
    });

    it('reports TimedOut and advances when the process never leaves InProgress', async () => {
        const { el, next } = mount();
        await flushPromises();
        getRecord.emit(statusRecord('InProgress'));

        jest.advanceTimersByTime(MAX_WAIT_MS - POLL_INTERVAL_MS);
        expect(next).not.toHaveBeenCalled();
        expect(el.status).toBe('InProgress');

        jest.advanceTimersByTime(POLL_INTERVAL_MS + 300);

        expect(el.status).toBe('TimedOut');
        expect(next).toHaveBeenCalledTimes(1);
    });

    it('advances on the platform event for its own process only', async () => {
        let deliver;
        subscribe.mockImplementation((channel, replayId, callback) => {
            deliver = callback;
            return Promise.resolve({ channel });
        });
        const { el, next } = mount();
        await flushPromises();

        deliver({ data: { payload: { DocGenProcessIdentifier: '0nnWt0000000000AAA', Status: 'Success' } } });
        jest.advanceTimersByTime(300);
        expect(next).not.toHaveBeenCalled();

        deliver({ data: { payload: { DocGenProcessIdentifier: PROCESS_ID, Status: 'Success' } } });
        jest.advanceTimersByTime(300);
        expect(el.status).toBe('Success');
        expect(next).toHaveBeenCalledTimes(1);
    });

    it('stops polling when it is removed from the page', async () => {
        const { el, next } = mount();
        const attributeChange = jest.fn();
        el.addEventListener(FlowAttributeChangeEventName, attributeChange);
        await flushPromises();
        getRecord.emit(statusRecord('InProgress'));
        jest.advanceTimersByTime(POLL_INTERVAL_MS);
        expect(notifyRecordUpdateAvailable).toHaveBeenCalled();
        notifyRecordUpdateAvailable.mockClear();

        document.body.removeChild(el);

        // No interval or timer is left behind: a leaked poll would report TimedOut after
        // MAX_WAIT_MS and navigate a flow screen that is gone.
        expect(jest.getTimerCount()).toBe(0);
        jest.advanceTimersByTime(MAX_WAIT_MS + 1000);
        expect(notifyRecordUpdateAvailable).not.toHaveBeenCalled();
        expect(attributeChange).not.toHaveBeenCalled();
        expect(next).not.toHaveBeenCalled();
    });

    it('starts polling when processId arrives after it is on the page', async () => {
        const el = createElement('c-rlm-doc-status-monitor', { is: RlmDocStatusMonitor });
        document.body.appendChild(el);
        jest.advanceTimersByTime(POLL_INTERVAL_MS * 2);
        expect(notifyRecordUpdateAvailable).not.toHaveBeenCalled();
        expect(subscribe).not.toHaveBeenCalled();

        el.processId = PROCESS_ID;
        await flushPromises();
        notifyRecordUpdateAvailable.mockClear();
        jest.advanceTimersByTime(POLL_INTERVAL_MS);

        expect(subscribe).toHaveBeenCalledTimes(1);
        expect(notifyRecordUpdateAvailable).toHaveBeenCalledWith([{ recordId: PROCESS_ID }]);
    });

    it('releases a subscription that resolves after it was removed, without reading the status', async () => {
        let resolveSubscribe;
        subscribe.mockImplementation(
            () =>
                new Promise((resolve) => {
                    resolveSubscribe = resolve;
                })
        );
        const { el } = mount();
        document.body.removeChild(el);

        const response = { channel: '/event/DocGenProcStsChgEvent' };
        resolveSubscribe(response);
        await flushPromises();

        expect(unsubscribe).toHaveBeenCalledWith(response, expect.any(Function));
        expect(notifyRecordUpdateAvailable).not.toHaveBeenCalled();
    });

    it('does not navigate after it is removed during the navigation delay', async () => {
        const { el, next } = mount();
        await flushPromises();
        getRecord.emit(statusRecord('Success'));
        document.body.removeChild(el);

        expect(jest.getTimerCount()).toBe(0);
        jest.advanceTimersByTime(1000);

        expect(next).not.toHaveBeenCalled();
    });

    it('subscribes once, even when processId is set before and again after insertion', async () => {
        const el = createElement('c-rlm-doc-status-monitor', { is: RlmDocStatusMonitor });
        el.processId = PROCESS_ID;
        document.body.appendChild(el);
        el.processId = PROCESS_ID;
        await flushPromises();

        expect(subscribe).toHaveBeenCalledTimes(1);
    });

    it('logs a failed status read and keeps waiting', async () => {
        const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
        const { el, next } = mount();
        await flushPromises();

        getRecord.error({ message: 'refused' });
        jest.advanceTimersByTime(300);

        expect(consoleError).toHaveBeenCalledWith('rlmDocStatusMonitor: status read failed', expect.anything());
        expect(el.status).toBe('InProgress');
        expect(next).not.toHaveBeenCalled();
    });
});
