import LightningDatatable from 'lightning/datatable';
import sellingModelCell from './sellingModelCell.html';
import quantityStepperCell from './quantityStepperCell.html';

/**
 * Datatable extension shared by the Contracted Pricing catalog and the product cart. Adds two custom
 * cell types:
 *   - `sellingModelPicker` — the in-row selling-model selector (c/dlSellingModelPicker), used by the
 *     original catalog.
 *   - `quantityStepper` — the in-row instance-count stepper (c/dlQuantityStepper), used by the cart.
 * Everything else is standard lightning-datatable. Both children dispatch composed events
 * (`modelchange` / `quantitychange`) so they bubble out of this datatable's shadow root to the host
 * component. Purely additive: the original catalog never references `quantityStepper`, so its
 * behavior is unchanged.
 */
export default class DlCatalogDatatable extends LightningDatatable {
    static customTypes = {
        sellingModelPicker: {
            template: sellingModelCell,
            // Standard cell typeAttributes the picker needs from the row.
            typeAttributes: ['rowKey', 'selectedPbeId', 'sellingModels']
        },
        quantityStepper: {
            template: quantityStepperCell,
            typeAttributes: ['rowKey', 'value', 'max']
        }
    };
}
