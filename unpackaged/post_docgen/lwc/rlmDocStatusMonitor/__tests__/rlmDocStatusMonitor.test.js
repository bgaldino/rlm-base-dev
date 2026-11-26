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

    it('re-reads the status right after the EMP subscription is live, not before', async () => {
        let resolveSubscribe;
        subscribe.mockImplementation(
            () =>
                new Promise((resolve) => {
                    resolveSubscribe = resolve;
                })
        );
        mount();
        await flushPromises();
        // A read before the subscription is live could miss a status that lands in between.
        expect(notifyRecordUpdateAvailable).not.toHaveBeenCalled();

        resolveSubscribe({ channel: '/event/DocGenProcStsChgEvent' });
        await flushPromises();

        expect(notifyRecordUpdateAvailable).toHaveBeenCalledTimes(1);
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

        // The same status can arrive again, by event and by read: the flow moves on only once.
        deliver({ data: { payload: { DocGenProcessIdentifier: PROCESS_ID, Status: 'Failure' } } });
        getRecord.emit(statusRecord('Success'));
        jest.advanceTimersByTime(1000);
        expect(el.status).toBe('Success');
        expect(next).toHaveBeenCalledTimes(1);
    });

    it('does not read the status when the subscription goes live after the flow moved on', async () => {
        let resolveSubscribe;
        subscribe.mockImplementation(
            () =>
                new Promise((resolve) => {
                    resolveSubscribe = resolve;
                })
        );
        const { next } = mount();
        getRecord.emit(statusRecord('Success'));
        jest.advanceTimersByTime(300);
        expect(next).toHaveBeenCalledTimes(1);

        resolveSubscribe({ channel: '/event/DocGenProcStsChgEvent' });
        await flushPromises();

        expect(notifyRecordUpdateAvailable).not.toHaveBeenCalled();
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
        const next = jest.fn();
        el.addEventListener(FlowNavigationNextEventName, next);
        document.body.appendChild(el);
        // Without a processId it waits: no timer, no subscription, no outcome.
        expect(jest.getTimerCount()).toBe(0);
        jest.advanceTimersByTime(POLL_INTERVAL_MS * 2);
        expect(notifyRecordUpdateAvailable).not.toHaveBeenCalled();
        expect(subscribe).not.toHaveBeenCalled();
        expect(next).not.toHaveBeenCalled();
        expect(el.status).toBe('InProgress');

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

    it('ignores a platform event or a status read that arrives after it was removed', async () => {
        let deliver;
        subscribe.mockImplementation((channel, replayId, callback) => {
            deliver = callback;
            return Promise.resolve({ channel });
        });
        const { el, next } = mount();
        const attributeChange = jest.fn();
        el.addEventListener(FlowAttributeChangeEventName, attributeChange);
        await flushPromises();
        document.body.removeChild(el);

        // unsubscribe() is asynchronous, so an event can still arrive after removal.
        deliver({ data: { payload: { DocGenProcessIdentifier: PROCESS_ID, Status: 'Success' } } });
        getRecord.emit(statusRecord('Success'));
        jest.advanceTimersByTime(1000);

        expect(attributeChange).not.toHaveBeenCalled();
        expect(next).not.toHaveBeenCalled();
        expect(jest.getTimerCount()).toBe(0);
    });

    it('starts no new polling when processId is set again after the flow moved on', async () => {
        const { el, next } = mount();
        await flushPromises();
        getRecord.emit(statusRecord('Success'));
        jest.advanceTimersByTime(300);
        expect(next).toHaveBeenCalledTimes(1);

        el.processId = PROCESS_ID;

        expect(jest.getTimerCount()).toBe(0);
    });

    it('unsubscribes from the platform event when it is removed', async () => {
        const live = { channel: '/event/DocGenProcStsChgEvent' };
        subscribe.mockResolvedValue(live);
        const { el } = mount();
        await flushPromises();

        document.body.removeChild(el);

        expect(unsubscribe).toHaveBeenCalledWith(live, expect.any(Function));
    });

    it('subscribes again when it is put back on the page after a failed subscription', async () => {
        jest.spyOn(console, 'error').mockImplementation(() => {});
        subscribe.mockRejectedValueOnce(new Error('handshake refused'));
        const { el } = mount();
        await flushPromises();
        expect(subscribe).toHaveBeenCalledTimes(1);

        document.body.removeChild(el);
        document.body.appendChild(el);
        await flushPromises();

        expect(subscribe).toHaveBeenCalledTimes(2);
    });

    it('moves the flow on once when it is put back after removal during the navigation delay', async () => {
        const { el, next } = mount();
        await flushPromises();
        getRecord.emit(statusRecord('Success'));
        document.body.removeChild(el);
        subscribe.mockClear();

        // No status is pushed after reinsertion: it reuses the final status it already read.
        document.body.appendChild(el);
        await flushPromises();
        jest.advanceTimersByTime(1000);

        expect(next).toHaveBeenCalledTimes(1);
        expect(el.status).toBe('Success');
        expect(subscribe).not.toHaveBeenCalled();
    });

    it('moves the flow on again with the status it read when it is put back after it already did', async () => {
        const { el, next } = mount();
        await flushPromises();
        getRecord.emit(statusRecord('Failure'));
        jest.advanceTimersByTime(300);
        expect(next).toHaveBeenCalledTimes(1);
        document.body.removeChild(el);

        document.body.appendChild(el);
        jest.advanceTimersByTime(300);

        expect(el.status).toBe('Failure');
        expect(next).toHaveBeenCalledTimes(2);
    });

    it('shows the waiting state and reads the status again when it is put back after timing out', async () => {
        const { el, next } = mount();
        await flushPromises();
        jest.advanceTimersByTime(MAX_WAIT_MS + 300);
        expect(el.status).toBe('TimedOut');
        expect(next).toHaveBeenCalledTimes(1);
        document.body.removeChild(el);
        subscribe.mockClear();
        notifyRecordUpdateAvailable.mockClear();

        document.body.appendChild(el);
        await flushPromises();

        // TimedOut is not a status the process had, so it starts a fresh wait and reads the status.
        expect(el.status).toBe('InProgress');
        expect(el.shadowRoot.querySelector('lightning-spinner')).not.toBeNull();
        expect(subscribe).toHaveBeenCalledTimes(1);
        expect(notifyRecordUpdateAvailable).toHaveBeenCalledWith([{ recordId: PROCESS_ID }]);
        expect(jest.getTimerCount()).toBe(1);
        getRecord.emit(statusRecord('Success'));
        jest.advanceTimersByTime(300);
        expect(next).toHaveBeenCalledTimes(2);
    });

    it.each(['Waiting', 'Blocked', 'InProgress'])(
        'keeps waiting on a %s status from the platform event or the record read',
        async (pending) => {
            let deliver;
            subscribe.mockImplementation((channel, replayId, callback) => {
                deliver = callback;
                return Promise.resolve({ channel });
            });
            const { el, next } = mount();
            const attributeChange = jest.fn();
            el.addEventListener(FlowAttributeChangeEventName, attributeChange);
            await flushPromises();

            deliver({ data: { payload: { DocGenProcessIdentifier: PROCESS_ID, Status: pending } } });
            getRecord.emit(statusRecord(pending));
            jest.advanceTimersByTime(POLL_INTERVAL_MS + 300);

            expect(el.status).toBe('InProgress');
            expect(attributeChange).not.toHaveBeenCalled();
            expect(next).not.toHaveBeenCalled();
            expect(jest.getTimerCount()).toBe(1);

            // The real outcome still moves the flow on.
            deliver({ data: { payload: { DocGenProcessIdentifier: PROCESS_ID, Status: 'Success' } } });
            jest.advanceTimersByTime(300);
            expect(el.status).toBe('Success');
            expect(next).toHaveBeenCalledTimes(1);
        }
    );

    it('keeps exactly one poll timer when processId is set again', async () => {
        const { el } = mount();
        await flushPromises();
        expect(jest.getTimerCount()).toBe(1);

        el.processId = PROCESS_ID;
        expect(jest.getTimerCount()).toBe(1);

        el.processId = '0nnWt0000007zzzAAA';
        await flushPromises();
        expect(jest.getTimerCount()).toBe(1);
        notifyRecordUpdateAvailable.mockClear();
        jest.advanceTimersByTime(POLL_INTERVAL_MS);
        expect(notifyRecordUpdateAvailable).toHaveBeenCalledTimes(1);
        expect(notifyRecordUpdateAvailable).toHaveBeenCalledWith([{ recordId: '0nnWt0000007zzzAAA' }]);
    });

    it('starts nothing on an element that was never put on the page', () => {
        const el = createElement('c-rlm-doc-status-monitor', { is: RlmDocStatusMonitor });
        el.processId = PROCESS_ID;

        expect(jest.getTimerCount()).toBe(0);
        expect(subscribe).not.toHaveBeenCalled();
    });

    it('unsubscribes each live subscription exactly once across removals', async () => {
        const first = { channel: '/event/DocGenProcStsChgEvent', id: 1 };
        subscribe.mockResolvedValueOnce(first);
        const { el } = mount();
        await flushPromises();
        document.body.removeChild(el);
        expect(unsubscribe).toHaveBeenCalledTimes(1);
        expect(unsubscribe).toHaveBeenLastCalledWith(first, expect.any(Function));

        let resolveSecond;
        subscribe.mockImplementationOnce(
            () =>
                new Promise((resolve) => {
                    resolveSecond = resolve;
                })
        );
        document.body.appendChild(el);
        document.body.removeChild(el);
        // The first subscription is not released twice.
        expect(unsubscribe).toHaveBeenCalledTimes(1);

        const second = { channel: '/event/DocGenProcStsChgEvent', id: 2 };
        resolveSecond(second);
        await flushPromises();
        expect(unsubscribe).toHaveBeenCalledTimes(2);
        expect(unsubscribe).toHaveBeenLastCalledWith(second, expect.any(Function));
    });
});
