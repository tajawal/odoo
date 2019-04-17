# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from hashlib import blake2b

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    invoice_type = fields.Selection(
        selection_add=[('tf', 'TravelFusion')],
    )

    @api.constrains('invoice_type', 'index')
    @api.multi
    def _check_tf_index(self):
        for rec in self:
            if rec.invoice_type != 'tf':
                continue
            if not rec.index:
                raise ValidationError(
                    _("The index is required for TravelFusion invoice line."))

    @api.multi
    def _tf_compute_name(self):
        self.ensure_one
        uniq_ref = \
            f"{self.locator}{self.passenger}{self.invoice_date}" \
            f"{self.total}{self.index}"
        # blake2b accepts only 64 bytes
        if len(uniq_ref) >= 64:
            uniq_ref = uniq_ref[:64]
        uniq_ref = blake2b(key=str.encode(uniq_ref), digest_size=9).hexdigest()
        self.name = 'tf_{}'.format(uniq_ref)
