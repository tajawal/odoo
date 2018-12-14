# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    invoice_type = fields.Selection(
        selection_add=[('aig', 'AIG')],
    )

    @api.multi
    def _aig_compute_name(self):
        self.ensure_one
        self.name = '{}_{}{}'.format(
            self.invoice_type, self.locator, self.invoice_status)
