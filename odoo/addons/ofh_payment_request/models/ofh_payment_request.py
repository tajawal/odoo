# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models


class OfhPaymentRequest(models.Model):

    _name = 'ofh.payment.request'
    _description = "Ofh Payment Request"
    _rec_name = 'order_reference'

    created_at = fields.Datetime(
        required=True,
        index=True,
    )
    updated_at = fields.Datetime(
        required=True,
        index=True,
    )
    order_reference = fields.Char(
        string="Order #",
    )
    request_type = fields.Selection(
        required=True,
        selection=[
            ('charge', 'Charge'),
            ('refund', 'Refund'),
            ('void', 'Void')],
        index=True,
    )
    # TODO: maybe should be selection field
    request_reason = fields.Char(
        required=True,
        index=True,
    )
    # TODO: maybe should be selection field.
    request_status = fields.Char(
        required=True,
    )
    auth_code = fields.Char()
    office_id = fields.Char()
    vendor_id = fields.Char(
        string="Airline",
        # TODO: should be reference to comodel_name='ofh.vendor.contract',
    )
    # Amounts field
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True,
    )
    fees = fields.Char(
        # TODO: required=True,
    )
    fare_difference = fields.Monetary(
        string="Fare Difference",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    change_fee = fields.Monetary(
        string="Change Fee",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    booking_fee = fields.Monetary(
        string="Booking Fee",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    insurance = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    discount = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    penality = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    adm_amount = fields.Monetary(
        string="ADM",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    loss_amount = fields.Monetary(
        string="Losses",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    loss_type = fields.Char(
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    input_vat_amount = fields.Monetary(
        string="Input VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    output_vat_amount = fields.Monetary(
        string="Output VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    total_amount = fields.Monetary(
        string="Total",
        currency_field='currency_id',
    )
    tax_code = fields.Selection(
        string='Tax code',
        selection=[('ss', 'SS'), ('sz', 'SZ')],
        required=True,
        default='sz',
    )
    # End of amount fields
    entity = fields.Selection(
        selection=[
            ('almosafer', 'Almosafer'),
            ('tajawal', 'Tajawal')],
        required=True,
        readonly=True,
        index=True,
    )

    # Technical fields
    order_id = fields.Char(
        string="Order ID",
    )
    charge_id = fields.Char(
        required=True,
    )
    track_id = fields.Char(
        required=True,
    )
    # End of technical fields.

    pnr = fields.Char(
        # TODO: required=True,
        string="PNR",
    )
    record_locator = fields.Char(
        # TODO: required=True,
    )
    insurance_ref = fields.Char()
    plan_code = fields.Char()
    notes = fields.Text()
    # SAP related statuses
    sap_status = fields.Selection(
        string='SAP status',
        selection=[('pending', 'Pending'),
                   ('done', 'Loaded in SAP'),
                   ('sl_loader_ready', 'Sale loader ready'),
                   ('ar_loader_ready', 'A/R loader ready'),
                   ('need_loader', 'Need Loader')],
        default='pending',
        required=True,
        index=True,
    )
    flag = fields.Selection(
        string='Payment request flag',
        selection=[('not_matched', 'Not Matched'),
                   ('void', 'Voided'),
                   ('amemdment', 'Amendment'),
                   ('full_refund', 'Full Refund'),
                   ('partial_refund', 'Partial Refund')],
        default='not_matched',
        required=True,
        index=True,
    )
    hub_bind_ids = fields.One2many(
        comodel_name='hub.payment.request',
        inverse_name='odoo_id',
        string="Hub Bindings",
    )

    @api.multi
    @api.depends('fees')
    def _compute_fees(self):
        for rec in self:
            if not rec.fees:
                continue
            fees_dict = json.loads(rec.fees)
            rec.fare_difference = fees_dict.get('fareDifference')
            rec.change_fee = fees_dict.get('changeFee')
            rec.penality = fees_dict.get('penalty')
            rec.booking_fee = fees_dict.get('bookingFee')
            rec.discount = fees_dict.get('discount')
            rec.input_vat_amount = fees_dict.get('inputVat')
            rec.output_vat_amount = fees_dict.get('outputVat')
            rec.adm_amount = fees_dict.get('adm')
            rec.loss_type = fees_dict.get('lossType')
