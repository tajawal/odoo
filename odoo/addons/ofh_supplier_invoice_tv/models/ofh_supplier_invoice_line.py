# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class OfhSupplierInvoiceLine(models.Model):
    _inherit = 'ofh.supplier.invoice.line'

    invoice_type = fields.Selection(
        selection_add=[('tv', 'Travel Port')],
    )
    supplier_reference = fields.Char(
        string="Supplier Reference",
        readonly=True,
    )
    booked_by_branch = fields.Char(
        string="Booked By Branch",
        readonly=True,
    )
    booked_by_user = fields.Char(
        string="Booked By User",
        readonly=True,
    )

    @api.multi
    def _tv_compute_name(self):
        self.ensure_one()
        self.name = '{}_{}_{}'.format(
            self.invoice_type, self.locator, self.ticket_number)
