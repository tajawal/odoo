# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class PaymentGatewayLineHandler(Component):
    _inherit = 'payment.gateway.line.handler'

    def odoo_post_create(self, odoo_record, values, orig_values):
        """
        Match a new created record with existing
        payment.
        """
        odoo_record.payment_gateway_id.match_with_payment()


class BankSettlementHandler(Component):
    _inherit = 'bank.settlement.handler'

    def odoo_post_create(self, odoo_record, values, orig_values):
        """
        Match a new created record with existing
        payment.
        """
        bank_name = odoo_record.bank_name

        odoo_record.match_with_payment_gateway()



