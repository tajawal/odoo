# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from hashlib import blake2b

from odoo import api, fields, models


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    invoice_type = fields.Selection(
        selection_add=[('tf', 'TravelFusion')],
    )

    @api.multi
    def _tf_compute_name(self):
        self.ensure_one
        uniq_ref = \
            f"{self.locator}{self.passenger}{self.invoice_date}{self.total}"
        uniq_ref = blake2b(key=str.encode(uniq_ref), digest_size=9).hexdigest()
        self.name = 'tf_{}'.format(uniq_ref)
