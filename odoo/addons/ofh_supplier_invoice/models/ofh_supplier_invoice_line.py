
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import json


class OfhSupplierInvoiceLine(models.Model):

    _name = 'ofh.supplier.invoice.line'
    _description = 'Supplier Invoice lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_default_currency_id(self):
        return self.env.ref('base.AED')

    name = fields.Char(
        string="Unique ID",
        compute='_compute_name',
        readonly=True,
        store=True,
    )
    invoice_type = fields.Selection(
        string="Invoice from",
        selection=[],
        required=True,
        index=True,
        readonly=True,
    )
    invoice_date = fields.Date(
        string="Invoice Date",
        required=True,
        readonly=True,
    )
    ticket_number = fields.Char(
        string="Ticket",
        readonly=True,
    )
    invoice_status = fields.Selection(
        string="Supplier Status",
        selection=[('none', 'Not applicable'),
                   ('TKTT', 'Ticket'),
                   ('RFND', 'Refund')],
        required=True,
        default='none',
        readonly=True,
    )
    locator = fields.Char(
        required=True,
        readonly=True,
    )
    office_id = fields.Char(
        string="Office ID",
        index=True,
        readonly=True,
    )
    passenger = fields.Char(
        string="Passenger's name",
        readonly=True,
    )
    vendor_id = fields.Char(
        string="Vendor Name",
        # TODO: comodel_name='ofh.vendor',
        required=True,
        readonly=True,
    )
    fees = fields.Char(
        required=True,
        default='{}',
        readonly=True,
    )
    total = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        required=True,
        comodel_name='res.currency',
        default=_get_default_currency_id,
        readonly=True,
    )
    state = fields.Selection(
        string="Matching Status",
        selection=[
            ('ready', 'Pending'),
            ('suggested', 'Suggested Matching'),
            ('not_matched', 'Not Matched'),
            ('matched', 'Matched')],
        required=True,
        default='ready',
        readonly=True,
    )

    _sql_constraints = [
        ('unique_invoice_line', 'unique(name)',
         _("This line has been uploaded"))
    ]

    @api.multi
    @api.depends('ticket_number', 'invoice_status', 'passenger',
                 'locator', 'invoice_date', 'vendor_id')
    def _compute_name(self):
        for rec in self:
            compute_function = '_{}_compute_name'.format(rec.invoice_type)
            if hasattr(rec, compute_function):
                getattr(rec, compute_function)()
            else:
                rec.name = '{}{}'.format(rec.invoice_type, rec.ticket_number)

    @api.multi
    @api.depends('fees', 'invoice_type')
    def _compute_fees(self):
        for rec in self:
            compute_function = '_{}_compute_fees'.format(rec.invoice_type)
            if rec.fees:
                fees = json.loads(rec.fees)
            else:
                fees = {}
            if hasattr(rec, compute_function):
                getattr(rec, compute_function)(fees)
