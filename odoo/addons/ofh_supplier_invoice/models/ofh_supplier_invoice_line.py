# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import json


class OfhSupplierInvoiceLine(models.Model):

    _name = 'ofh.supplier.invoice.line'
    _description = 'Supplier Invoice lines'

    @api.model
    def _get_invoice_type_selection(self):
        return []

    name = fields.Char(
        string="Unique ID",
        required=True,
        compute='',
        store=True,
    )
    invoice_type = fields.Selection(
        string="Invoice from",
        selection=_get_invoice_type_selection,
        required=True,
        index=True,
    )
    invoice_date = fields.Date(
        string="Invoice Date",
        required=True,
    )
    ticket_number = fields.Char(
        string="Ticket",
        required=True,
    )
    invoice_status = fields.Selection(
        string="Supplier Status",
        selection=[
            ('tktt', 'Ticket'),
            ('amnd', 'Amendment'),
            ('amnd', 'Amendment'),
            ('rfnd', 'Refund')],
        required=True,
    )
    locator = fields.Char(
        required=True,
    )
    office_id = fields.Char(
        string="Office ID",
        required=True,
        index=True,
    )
    passenger = fields.Char(
        string="Passenger's name",
    )
    vendor_id = fields.Char(
        string="Vendor Name",
        # TODO: comodel_name='ofh.vendor',
        required=True,
    )
    fees = fields.Char(
        required=True,
        default='{}',
    )
    total = fields.Monetary(
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        string="Currency",
        required=True,
        comodel_name='res.currency',
    )
    state = fields.Selection(
        string="Flag",
        selection=[('not_matched', 'Not Matched'),
                   ('matched', 'Matched')],
        required=True,
        default='not_matched'
    )
    file_name = fields.Char(
        string="File",
        required=True,
    )

    _sql_constraints = [
        ('unique_invoice_line', 'unique(name)',
         _("This line has been uploaded"))
    ]

    @api.multi
    @api.depends('ticket_number', 'invoice_status', 'invoice_type')
    def _compute_name(self):
        for rec in self:
            compute_function = '_{}_compute_name'.format(rec.invoice_type)
            if hasattr(self, compute_function):
                getattr(self, compute_function)()
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
            if hasattr(self, compute_function):
                getattr(self, compute_function)(fees)
