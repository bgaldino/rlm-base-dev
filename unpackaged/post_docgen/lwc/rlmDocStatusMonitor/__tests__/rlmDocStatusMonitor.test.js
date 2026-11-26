// getRecord.emit() is the sfdx-lwc-jest test adapter's API, not a wire call in a component.
/* eslint-disable @lwc/lwc/no-unexpected-wire-adapter-usages */
import { createElement } from 'lwc';
import RlmDocStatusMonitor from 'c/rlmDocStatusMonitor';
import { getRecord, notifyRecordUpdateAvailable } from 'lightning/uiRecordApi';
import { subscribe } from 'lightning/empApi';
import { FlowNavigationNextEventName } from 'lightning/flowSupport';

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
        subscribe.mockClear();
        subscribe.mockResolvedValue({});
    });

    afterEach(() => {
        while (document.body.firstChild) document.body.removeChild(document.body.firstChild);
        jest.useRealTimers();
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
});
