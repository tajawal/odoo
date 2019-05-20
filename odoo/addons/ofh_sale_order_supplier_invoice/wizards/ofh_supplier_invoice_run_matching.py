# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.exceptions import ValidationError


class OfhSupplierInvoiceRunMatching(models.TransientModel):
    _name = 'ofh.supplier.invoice.run.matching'

    date_from = fields.Date(
        string="Date From",
        required=True,
    )
    date_to = fields.Date(
        string="Date To",
        required=True,
    )
    invoice_type = fields.Selection(
        string="Invoice Type",
        required=True,
        selection=[
            ('gds', 'Gds'),
            ('nile', 'Nile'),
            ('aig', 'Aig'),
            ('itl', 'ITL'),
            ('enett', 'Enett'),
            ('galileo', 'Galileo'),
            ('tf', 'Travel Fusion'),
            ('tv', 'Travel Port')
        ],
    )

    @api.constrains('data_from', 'date_to')
    @api.multi
    def _check_dates(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError(
                    '`Date To` cannot be greater than `Date From`')

    @api.multi
    def match_supplier_invoice_lines(self):
        self.ensure_one()
        return self.env['ofh.supplier.invoice.line'].with_delay(). \
            match_supplier_invoice_lines(
                self.date_from, self.date_to, self.invoice_type)
