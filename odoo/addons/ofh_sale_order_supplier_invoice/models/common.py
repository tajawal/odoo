# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class SupplierInvoiceLineHandler(Component):

    _inherit = 'supplier.invoice.line.handler'

    def odoo_post_create(self, odoo_record, values, orig_values):
        """
        Match a new created record with existing
        sale order and sale order line.
        """
        odoo_record.match_with_sale_order()
