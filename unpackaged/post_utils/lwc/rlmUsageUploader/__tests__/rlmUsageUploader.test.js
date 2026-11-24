import { createElement } from 'lwc'
import RlmUsageUploader from 'c/rlmUsageUploader'
import { createApexTestWireAdapter } from '@salesforce/sfdx-lwc-jest'
import getUsageResourcesForAsset from '@salesforce/apex/RLM_UsageUploaderController.getUsageResourcesForAsset'
import validateUsageEntries from '@salesforce/apex/RLM_UsageUploaderController.validateUsageEntries'
import bulkUploadUsage from '@salesforce/apex/RLM_UsageUploaderController.bulkUploadUsage'

jest.mock(
    '@salesforce/apex/RLM_UsageUploaderController.getAssetsForAccount',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest')
        return { default: createApexTestWireAdapter(jest.fn()) }
    },
    { virtual: true }
)
jest.mock(
    '@salesforce/apex/RLM_UsageUploaderController.getUsageResourcesForAsset',
    () => {
        const { createApexTestWireAdapter } = require('@salesforce/sfdx-lwc-jest')
        return { default: createApexTestWireAdapter(jest.fn()) }
    },
    { virtual: true }
)
jest.mock('@salesforce/apex/RLM_UsageUploaderController.uploadUsage', () => ({ default: jest.fn() }), {
    virtual: true
})
jest.mock('@salesforce/apex/RLM_UsageUploaderController.validateUsageEntries', () => ({ default: jest.fn() }), {
    virtual: true
})
jest.mock('@salesforce/apex/RLM_UsageUploaderController.bulkUploadUsage', () => ({ default: jest.fn() }), {
    virtual: true
})

const ASSET_ID = '02i000000000001AAA'
const RESOURCE = {
    resourceId: '0Tz000000000001AAA',
    resourceName: 'Data Storage',
    unitOfMeasureId: '0hE000000000001AAA',
    unitOfMeasureName: 'Gigabyte',
    unitOfMeasureCode: 'GB',
    availableUoms: []
}

// FileReader and the Apex mocks resolve on the task and microtask queues; a few turns settle both.
const settle = async () => {
    for (let i = 0; i < 5; i++) {
        await new Promise((resolve) => setTimeout(resolve, 0))
    }
}

async function mountWithParsedCsv() {
    const element = createElement('c-rlm-usage-uploader', { is: RlmUsageUploader })
    element.recordId = ASSET_ID
    document.body.appendChild(element)
    getUsageResourcesForAsset.emit([RESOURCE])
    await settle()

    validateUsageEntries.mockResolvedValue([
        { isValid: true, errorMessage: null },
        { isValid: true, errorMessage: null }
    ])
    const input = element.shadowRoot.querySelector('[data-id="csv-file-input"]')
    const csv = 'Usage Resource,Quantity,Transaction Date\nData Storage,1,2026-01-01\nData Storage,2,2026-01-02\n'
    Object.defineProperty(input, 'files', { value: [new File([csv], 'usage.csv', { type: 'text/csv' })] })
    input.dispatchEvent(new CustomEvent('change'))
    await settle()
    return element
}

function uploadButton(element) {
    return [...element.shadowRoot.querySelectorAll('lightning-button')].find((b) => b.label === 'Confirm Upload')
}

describe('c-rlm-usage-uploader bulk upload', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild)
        }
        jest.clearAllMocks()
    })

    it('toasts an error when no row was saved', async () => {
        const element = await mountWithParsedCsv()
        bulkUploadUsage.mockResolvedValue({
            successCount: 0,
            errorCount: 2,
            journalIds: [],
            errors: ['Row 1: A fixed sentence.', 'Row 2: A fixed sentence.']
        })
        const toasts = jest.fn()
        element.addEventListener('lightning__showtoast', toasts)
        const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {})

        const button = uploadButton(element)
        expect(button).toBeTruthy()
        button.click()
        await settle()

        expect(bulkUploadUsage).toHaveBeenCalledTimes(1)
        expect(toasts).toHaveBeenCalledTimes(1)
        const detail = toasts.mock.calls[0][0].detail
        expect(detail.variant).toBe('error')
        expect(detail.message).toBe('No usage records were created. 2 row(s) had errors.')
        consoleError.mockRestore()
    })

    it('shows the server sentence without a prefix when the upload throws', async () => {
        const element = await mountWithParsedCsv()
        bulkUploadUsage.mockRejectedValue({ body: { message: 'The usage records could not be uploaded. Try again, or contact your administrator.' } })
        const toasts = jest.fn()
        element.addEventListener('lightning__showtoast', toasts)

        uploadButton(element).click()
        await settle()

        expect(toasts).toHaveBeenCalledTimes(1)
        expect(toasts.mock.calls[0][0].detail.message).toBe(
            'The usage records could not be uploaded. Try again, or contact your administrator.'
        )
    })
})
