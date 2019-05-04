# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models
from odoo.tools import float_is_zero, float_compare


class OfhPaymentRequest(models.Model):

    _name = 'ofh.payment.request'
    _description = "Ofh Payment Request"
    _rec_name = 'track_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    created_at = fields.Datetime(
        required=True,
        index=True,
        readonly=True,
    )
    updated_at = fields.Datetime(
        required=True,
        index=True,
        readonly=True,
        track_visibility='always',
    )
    order_reference = fields.Char(
        string="Order #",
        readonly=True,
    )
    processed_by = fields.Char(
        string="Processed By",
        readonly=True,
    )
    request_type = fields.Selection(
        required=True,
        selection=[
            ('charge', 'Charge'),
            ('refund', 'Refund'),
            ('void', 'Void')],
        index=True,
        readonly=True,
    )
    # TODO: maybe should be selection field
    request_reason = fields.Char(
        required=True,
        index=True,
        readonly=True,
    )
    # TODO: maybe should be selection field.
    request_status = fields.Char(
        required=True,
        index=True,
        readonly=True,
    )
    is_egypt = fields.Boolean(
        string='Is Egypt?',
        index=True,
        default=False,
        help='True of the Payment request is related to an order created from'
             'Egypt office',
    )
    auth_code = fields.Char(
        readonly=True,
    )
    vendor_id = fields.Char(
        string="Airline",
        readonly=True,
        # TODO: should be reference to comodel_name='ofh.vendor.contract',
    )
    # Amounts field
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    fees = fields.Char(
        readonly=True,
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
    manual_output_vat_amount = fields.Monetary(
        string="Manual Output VAT",
        currency_field='currency_id',
        help="Technical field to ajust VAT when neeeded",
        track_visibility='onchange',
    )
    total_amount = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        readonly=True,
    )
    tax_code = fields.Selection(
        string='Tax code',
        selection=[('ss', 'SS'), ('sz', 'SZ')],
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    estimated_cost = fields.Monetary(
        string="Estimated Cost",
        currency_field='currency_id',
        readonly=True,
        compute='_compute_estimated_cost',
        store=False,
    )
    # End of amount fields
    entity = fields.Selection(
        selection=[
            ('almosafer', 'Almosafer'),
            ('tajawal', 'Tajawal')],
        required=False,  # TODO: Fix it!
        readonly=True,
        index=True,
    )
    payment_mode = fields.Char(
        string="Payment Method",
        readonly=True,
    )
    provider = fields.Char(
        string="Provider",
        readonly=True,
    )
    charge_ids = fields.One2many(
        comodel_name="ofh.payment.charge",
        string="Charge IDs",
        inverse_name='payment_request_id',
        readonly=True,
    )
    track_id = fields.Char(
        required=True,
        readonly=True,
    )
    plan_code = fields.Char(
        readonly=True,
    )
    notes = fields.Text(
        readonly=True,
    )
    # SAP related statuses
    payment_request_status = fields.Selection(
        string="Payment Request Status",
        selection=[
            ('incomplete', 'Incomplete Data'),
            ('ready', 'Ready for matching')],
        compute='_compute_payment_request_status',
        store=True,
        index=True,
        readonly=True,
        track_visibility='always',
    )
    reconciliation_status = fields.Selection(
        string="Supplier Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        default='unmatched',
        required=True,
        index=True,
        readonly=True,
        track_visibility='always',
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
        track_visibility='always',
    )
    hub_bind_ids = fields.One2many(
        comodel_name='hub.payment.request',
        inverse_name='odoo_id',
        string="Hub Bindings",
        readonly=True,
    )
    is_investigated = fields.Boolean(
        string="Is Investigated",
        help="This is a helper flag to mark the records that where "
             "matching needs investigation as investigated or not.",
        default=False,
    )
    # manual fields
    manual_supplier_reference = fields.Char(
        string="Manual Supplier Reference",
        index=True,
    )
    manual_payment_reference = fields.Char(
        string="Manual Payment Reference",
    )
    supplier_reference = fields.Char(
        string="Supplier Reference",
        readonly=True,
        track_visibility='always',
        compute='_compute_supplier_reference',
        store=False,
    )
    payment_reference = fields.Char(
        string="Payment Reference",
        readonly=True,
        track_visibility='always',
        compute='_compute_payment_reference',
        store=False,
    )

    # newly added VAT fields
    change_fee_vat_amount = fields.Monetary(
        string="Change Fee VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    fare_difference_vat_amount = fields.Monetary(
        string="Fare Difference VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    penalty_vat_amount = fields.Monetary(
        string="Penalty VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    adm_vat_amount = fields.Monetary(
        string="ADM VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    booking_fee_vat_amount = fields.Monetary(
        string="Booking Fee VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    deals_vat_amount = fields.Monetary(
        string="Deals VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )
    discount_vat_amount = fields.Monetary(
        string="Discount VAT",
        currency_field='currency_id',
        compute='_compute_fees',
        readonly=True,
        store=False,
    )

    @api.multi
    @api.depends('insurance', 'fare_difference', 'penalty')
    def _compute_estimated_cost(self):
        for rec in self:
            rec.estimated_cost = 0.0
            if rec.request_type not in ('charge', 'refund'):
                continue
            if rec.request_type == 'charge':
                rec.estimated_cost = \
                    rec.fare_difference + rec.insurance + rec.penalty
            else:
                rec.estimated_cost = \
                    rec.fare_difference - rec.insurance - rec.penalty

    # TODO: check how to
    @api.multi
    @api.depends('manual_payment_reference', 'charge_ids')
    def _compute_payment_reference(self):
        for rec in self:
            if rec.manual_payment_reference:
                rec.payment_reference = rec.manual_payment_reference
                continue
            if rec.charge_ids:
                rec.payment_reference = rec.charge_ids[0].charge_id
                continue
            else:
                rec.payment_reference = ""

    @api.multi
    @api.depends('fees', 'manual_output_vat_amount')
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
                rec.tax_code = 'sz'
            rec.fare_difference = fees_dict.get('fareDifference')
            rec.change_fee = fees_dict.get('changeFee')
            rec.penalty = fees_dict.get('penalty')
            rec.booking_fee = fees_dict.get('bookingFee')
            rec.discount = fees_dict.get('discount')
            rec.input_vat_amount = fees_dict.get('inputVat')

            # Sometimes the user correct manual the output vat amount.
            # For this reason we use the manual field instead the one fetched
            # from hub.
            if not float_is_zero(
                    rec.manual_output_vat_amount,
                    precision_rounding=rec.currency_id.rounding):
                rec.output_vat_amount = rec.manual_output_vat_amount
            else:
                rec.output_vat_amount = fees_dict.get('outputVat')

            rec.adm_amount = fees_dict.get('adm')
            rec.loss_type = fees_dict.get('lossType')
            # newly added vat fields
            rec.change_fee_vat_amount = fees_dict.get('changeFeeVat')
            rec.fare_difference_vat_amount = fees_dict.get('fareDifferenceVat')
            rec.penalty_vat_amount = fees_dict.get('penaltyVat')
            rec.adm_vat_amount = fees_dict.get('admVat')
            rec.booking_fee_vat_amount = fees_dict.get('bookingFeeVat')
            rec.deals_vat_amount = fees_dict.get('dealsVat')
            rec.discount_vat_amount = fees_dict.get('discountVat')

            if float_compare(
                    rec.output_vat_amount, 0.0,
                    precision_digits=rec.currency_id.rounding) > 0:
                rec.tax_code = 'ss'
            else:
                rec.tax_code = 'sz'

    @api.multi
    @api.depends('order_reference')
    def _compute_payment_request_status(self):
        for rec in self:
            # TODO: not sure what to use here,
            # either order_id or order reference
            rec.payment_request_status = \
                'ready' if rec.order_reference else 'incomplete'

    @api.multi
    def open_order_in_hub(self):
        """Open the order link to the payment request in hub using URL
        Returns:
            [dict] -- URL action dictionary
        """

        self.ensure_one()
        if not self.order_reference:
            return {}
        hub_backend = self.env['hub.backend'].search([], limit=1)
        if not hub_backend:
            return
        hub_url = "{}admin/order/air/detail/{}".format(
            hub_backend.hub_api_location, self.order_reference)
        return {
            "type": "ir.actions.act_url",
            "url": hub_url,
            "target": "new",
        }

    @api.multi
    def action_supplier_status_not_appilicable(self):
        records = self.filtered(
            lambda r: r.reconciliation_status in ('investigate', 'pending'))
        return records.write({'reconciliation_status': 'not_applicable'})

    @api.multi
    def action_mark_as_investigated(self):
        """Mark Selected Records as investigated, so they will not have the
        red color.
        """

        records = self.filtered(lambda r: r.need_to_investigate)
        if records:
            return records.write({'is_investigated': True})
        return True
