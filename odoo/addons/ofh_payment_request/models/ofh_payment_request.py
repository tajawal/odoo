# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models


class OfhPaymentRequest(models.Model):

    _name = 'ofh.payment.request'
    _description = "Ofh Payment Request"
    _rec_name = 'order_reference'
    _inherit = ['mail.thread', 'mail.activity.mixin']

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
        index=True,
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
    penalty = fields.Monetary(
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
        string="Airline PNR",
    )
    record_locator = fields.Char(
        # TODO: required=True,
    )
    insurance_ref = fields.Char()
    plan_code = fields.Char()
    notes = fields.Text()
    # SAP related statuses
    payment_request_status = fields.Selection(
        string="Payment Request Status",
        selection=[
            ('incomplete', 'Incomplete Data'),
            ('ready', 'Ready for matching')],
        compute='_compute_payment_request_status',
        store=True,
        index=True,
    )
    sap_status = fields.Selection(
        string='SAP status',
        selection=[
            ('pending', 'Pending'),
            ('not_in_sap', "Not In SAP"),
            ('in_sap', "Sale & Payment In SAP"),
            ('payment_not_in_sap', "Payment not in SAP"),
            ('sale_not_in_sap', 'Sale not in SAP')],
        default='pending',
        required=True,
        index=True,
    )
    state = fields.Selection(
        string='Next Action',
        selection=[
            ('pending', 'Pending'),
            ('sale_loader', 'Need Sale Loader'),
            ('payment_loader', 'Need Payment Loader'),
            ('sl_py_loader', 'Need Sale & Payment Loader'),
            ('no_action', 'No Action')],
        default='pending',
        required=True,
        index=True,
        readonly=True,
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
            fees = rec.fees
            if not fees:
                fees = '{}'

            fees_dict = json.loads(fees)
            if not fees_dict:
                rec.fare_difference = rec.change_fee = rec.penalty = \
                    rec.booking_fee = rec.discount = rec.input_vat_amount = \
                    rec.output_vat_amount = rec.adm_amount = 0.0
                rec.loss_type = ''
            rec.fare_difference = fees_dict.get('fareDifference')
            rec.change_fee = fees_dict.get('changeFee')
            rec.penalty = fees_dict.get('penalty')
            rec.booking_fee = fees_dict.get('bookingFee')
            rec.discount = fees_dict.get('discount')
            rec.input_vat_amount = fees_dict.get('inputVat')
            rec.output_vat_amount = fees_dict.get('outputVat')
            rec.adm_amount = fees_dict.get('adm')
            rec.loss_type = fees_dict.get('lossType')

    @api.multi
    @api.depends('order_reference')
    def _compute_payment_request_status(self):
        for rec in self:
            rec.payment_request_status = \
                'ready' if rec.order_reference else 'incomplete'
