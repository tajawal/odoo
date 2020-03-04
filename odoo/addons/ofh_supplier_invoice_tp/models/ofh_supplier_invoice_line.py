# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from hashlib import blake2b

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    invoice_type = fields.Selection(
        selection_add=[('tp', 'TravelPort')],
    )

    @api.multi
    def _tp_compute_name(self):
        self.ensure_one()
        self.ensure_one()
        self.name = '{}_{}{}'.format(
            self.invoice_type, self.ticket_number, self.invoice_status)
