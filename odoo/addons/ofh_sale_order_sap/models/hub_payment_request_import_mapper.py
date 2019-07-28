# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class HubPaymentRequestImportMapper(Component):
    _inherit = 'hub.payment.request.import.mapper'

    @mapping
    def is_sale_applicable(self, record):
        order_id = record.get('order_id')
        if not order_id:
            return {'is_sale_applicable': False}
        else:
            return {'is_sale_applicable': True}

    @mapping
    def is_payment_applicable(self, record):
        order_id = record.get('order_id')
        if not order_id:
            return {'is_payment_applicable': False}
        else:
            return {'is_payment_applicable': True}

