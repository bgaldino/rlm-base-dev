import { createElement } from 'lwc'
import RlmAssetRatesGrants from 'c/rlmAssetRatesGrants'
import getRatesForAsset from '@salesforce/apex/RLM_UsageUploaderController.getRatesForAsset'
import getGrantsForAsset from '@salesforce/apex/RLM_UsageUploaderController.getGrantsForAsset'

jest.mock(
    '@salesforce/apex/RLM_UsageUploaderController.getRatesForAsset',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest')
        return { default: createApexTestWireAdapter(jest.fn()) }
    },
    { virtual: true }
)
jest.mock(
    '@salesforce/apex/RLM_UsageUploaderController.getGrantsForAsset',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest')
        return { default: createApexTestWireAdapter(jest.fn()) }
    },
    { virtual: true }
)

const RESOURCE_ID = '0Tz000000000001AAA'

// A grant whose current bucket is the monthly one, mid-period. totalConsumedEntitlement is the
// term-cumulative figure (todo 301) and must never be shown as "Used".
const WITH_BUCKET = {
    entitlementId: '1Ue000000000001AAA',
    usageResourceId: RESOURCE_ID,
    usageResourceName: 'Tokens',
    usageModelType: 'Anchor',
    entitlementQuantity: 10000,
    hasCurrentBucket: true,
    bucketBalance: 7000,
    consumedEntitlement: 3000,
    totalConsumedEntitlement: 9000
}

// A grant with no bucket covering today (a backdated asset past its first period).
const WITHOUT_BUCKET = {
    entitlementId: '1Ue000000000002AAA',
    usageResourceId: RESOURCE_ID,
    usageResourceName: 'Tokens',
    usageModelType: 'Anchor',
    entitlementQuantity: 10000,
    hasCurrentBucket: false
}

async function mount(grants) {
    const element = createElement('c-rlm-asset-rates-grants', { is: RlmAssetRatesGrants })
    element.recordId = '02i000000000001AAA'
    document.body.appendChild(element)
    getRatesForAsset.emit([])
    getGrantsForAsset.emit(grants)
    await Promise.resolve()
    return element
}

function texts(element) {
    return [...element.shadowRoot.querySelectorAll('span, p')].map((n) => n.textContent.trim())
}

describe('c-rlm-asset-rates-grants', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild)
        }
    })

    it('shows the current bucket balance and its own consumption, not the term-cumulative total', async () => {
        const element = await mount([WITH_BUCKET])
        const shown = texts(element)
        expect(shown).toContain('7000 remaining')
        expect(shown).toContain('Used: 3000')
        expect(shown).not.toContain('Used: 9000')
        expect(element.shadowRoot.querySelector('lightning-progress-ring').value).toBe(30)
        expect(element.shadowRoot.querySelector('[data-id="no-current-bucket"]')).toBeNull()
    })

    it('shows an explicit none state, not the entitlement quantity as a balance, when no bucket covers today', async () => {
        const element = await mount([WITHOUT_BUCKET])
        const shown = texts(element)
        expect(element.shadowRoot.querySelector('[data-id="no-current-bucket"]')).not.toBeNull()
        expect(shown).not.toContain('10000 remaining')
        expect(shown.some((t) => t.startsWith('Used:'))).toBe(false)
        expect(element.shadowRoot.querySelector('lightning-progress-ring')).toBeNull()
    })
})
