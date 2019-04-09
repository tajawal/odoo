# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class HubPaymentRequestImportMapper(Component):
    _inherit = 'hub.payment.request.import.mapper'

    @mapping
    def order_id(self, record):
        order_id = record.get('order_id')
        if not order_id:
            return {}

        binder = self.binder_for('hub.sale.order')
        order = binder.to_internal(order_id, unwrap=True)

        return {'order_id': order.id}


class HubPaymentRequestImporter(Component):

    _inherit = 'hub.payment.request.importer'

    def _import_dependencies(self):
        order_id = self.hub_record.get('order_id')
        # TODO Maybe we should add a date check.
        # hub_date = datetime.fromtimestamp(
        #     int(self.hub_record['updatedAt']['$date'].get(
        #         '$numberLong')) / 1000)
        if not order_id:
            return
        self._import_dependency(
            external_id=order_id, binding_model='hub.sale.order')
