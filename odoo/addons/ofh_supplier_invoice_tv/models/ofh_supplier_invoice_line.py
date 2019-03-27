# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from hashlib import blake2b

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.addons.queue_job.job import job


class OfhSupplierInvoiceLine(models.Model):
    _inherit = 'ofh.supplier.invoice.line'

    invoice_type = fields.Selection(
        selection_add=[('tv', 'Travel Port')],
    )

    invoice_from = fields.Char(
        string="Invoice From",
        readonly=True,
    )

    supplier_currency = fields.Char(
        string="Supplier Currency",
        readonly=True,
    )

    supplier_reference = fields.Char(
        string="Supplier Reference",
        readonly=True,
    )

    index = fields.Char()

    @api.multi
    def _tv_compute_name(self):
        self.ensure_one
        self.name = '{}_{}_{}'.format(
            self.invoice_type, self.index, self.ticket_number)
