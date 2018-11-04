# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import json


class OfhSupplierInvoice(models.Model):

    _name = 'ofh.supplier.invoice.line'
    _description = 'Supplier Invoice lines'

    name = fields.Char(
        string="Unique ID",
        required=True,
        compute='',
        store=True,
    )
    invoice_type = fields.Selection(
        string="Invoice from",
        selection=[('gds', 'GDS'),
                   ('tf', 'Travel Fusion'),
                   ('tv', 'Travolutionary'),
                   ('agoda', 'Agoda')],
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
        selection=[('tktt', 'Ticket'),
                   ('amnd', 'Amendment'), 
                   ('rfnd', 'Refund')],
        required=True,
    )
    locator = fields.Char(
        required=True,
    )
    owner_oid = fields.Char(
        string="Owner OID",
        required=True,
        index=True,
    )
    vendor_id = fields.Char(
        string="Vendor Name",
        # TODO: comodel_name='ofh.vendor',
        required=True,
    )
    fees = fields.Char(
        required=True,
    )
    total = fields.Monetary(
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        string="Currency",
        required=True,
        comodel_name='res.currency',
    )
    base_fare_amount = fields.Monetary(
        string="Base Fare",
        compute='_compute_fees',
        currency_field='currency_id',
    )
    tax_amount = fields.Monetary(
        string="Tax",
        compute='_compute_fees',
        currency_field='currency_id',
    )
    net_amount = fields.Monetary(
        string="Net",
        compute='_compute_fees',
        currency_field='currency_id',
    )
    fee_amount = fields.Monetary(
        string="Fee",
        compute='_compute_fees',
        currency_field='currency_id',
    )
    iata_commission_amount = fields.Monetary(
        string="IATA Commission",
        compute='_compute_fees',
        currency_field='currency_id',
    )
    gds_amount = fields.Monetary(
        string="GDS Commission",
        compute='_compute_fees',
        currency_field='currency_id',
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
            rec.name = '{}_{}{}'.format(
                rec.invoice_type, rec.ticket_number, rec.invoice_status)

    @api.multi
    @api.depends('fees')
    def _compute_fees(self):
        for rec in self:
            if not rec.fees:
                rec.base_fare_amount = rec.tax_amount = rec.net_amount = \
                    rec.fee_amount = rec.iata_commission_amount = \
                    rec.gds_amount = 0.0
            else:
                fees_dict = json.loads(rec.fees)
                rec.base_fare_amount = fees_dict.get('BaseFare', 0.0)
                rec.tax_amount = fees_dict.get('Tax')
                rec.net_amount = fees_dict.get('Net')
                rec.fee_amount = fees_dict.get('FEE')
                rec.iata_commission_amount = fees_dict.get('IATA COMM')
                rec.gds_amount = fees_dict.get('GDS $')
