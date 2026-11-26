/*
 * Jest environment for LWC suites whose result depends on the browser's time zone.
 *
 * A test cannot change the time zone itself: Jest hands each test file a copy of process.env, so
 * `process.env.TZ = ...` inside a test changes nothing (measured on Node 24). This environment runs
 * outside the test sandbox, in the worker process, where Node does apply a TZ change at once, and
 * gives the test a `setBrowserTimeZone(zone)` global for it. The worker's own zone is put back at
 * teardown, so later test files in the same worker are not affected.
 *
 * Use it with a docblock at the top of the test file:
 *   @jest-environment <rootDir>/tests/jest/browser-time-zone-environment.js
 */
'use strict';

// The jsdom environment sfdx-lwc-jest (the declared dependency) runs its suites in, resolved from it.
const { TestEnvironment } = require(
    require.resolve('jest-environment-jsdom', {
        paths: [require.resolve('@salesforce/sfdx-lwc-jest')]
    })
);

class BrowserTimeZoneEnvironment extends TestEnvironment {
    constructor(config, context) {
        super(config, context);
        this.hadTimeZone = Object.prototype.hasOwnProperty.call(process.env, 'TZ');
        this.originalTimeZone = process.env.TZ;
        this.global.setBrowserTimeZone = (timeZone) => {
            process.env.TZ = timeZone;
        };
    }

    async teardown() {
        if (this.hadTimeZone) {
            process.env.TZ = this.originalTimeZone;
        } else {
            delete process.env.TZ;
        }
        await super.teardown();
    }
}

module.exports = BrowserTimeZoneEnvironment;
