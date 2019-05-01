# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class OfhSupplierInvoiceRunMatching(models.TransientModel):

    _name = 'ofh.supplier.invoice.run.matching'

    @api.multi
    def match_supplier_invoice_lines(self):
        self.ensure_one()
        return self.env['ofh.supplier.invoice.line'].with_delay().\
            match_supplier_invoice_lines()
