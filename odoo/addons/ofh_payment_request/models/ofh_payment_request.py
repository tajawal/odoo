# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models


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
    auth_code = fields.Char(
        readonly=True,
    )
    office_id = fields.Char(
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
    total_amount = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        readonly=True,
    )
    tax_code = fields.Selection(
        string='Tax code',
        selection=[('ss', 'SS'), ('sz', 'SZ')],
        required=True,
        default='sz',
        readonly=True,
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
        readonly=True,
    )
    charge_id = fields.Char(
        string="Payment reference",
        required=True,
        readonly=True,
    )
    track_id = fields.Char(
        required=True,
        readonly=True,
    )
    # End of technical fields.
    hub_supplier_reference = fields.Char(
        string="Supplier Reference",
        readonly=True,
        index=True,
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
            ('pending', 'Pending'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable'),
            ('investigate', 'Investigate')],
        default='pending',
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
    # order details
    order_type = fields.Selection(
        selection=[
            ('hotel', 'Hotel'),
            ('flight', 'Flight'),
            ('package', 'Package')],
        readonly=True,
    )
    order_amount = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    order_supplier_cost = fields.Monetary(
        currency_field='order_supplier_currency',
        readonly=True,
    )
    order_supplier_currency = fields.Many2one(
        comodel_name='res.currency',
        readonly=True,
    )
    order_discount = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    order_created_at = fields.Datetime(
        string="Order Created At",
        readonly=True,
    )
    order_updated_at = fields.Datetime(
        string="Order Updated At",
        readonly=True,
    )
    need_to_investigate = fields.Boolean(
        string="Matching needs investigation",
        compute='_compute_need_to_investigate',
        search='_search_need_to_investigate',
        readonly=True,
        store=False,
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

    @api.multi
    @api.depends('reconciliation_status', 'order_created_at', 'created_at',
                 'is_investigated', 'request_type')
    def _compute_need_to_investigate(self):
        from_str = fields.Date.from_string
        for rec in self:
            rec.need_to_investigate = False
            if rec.reconciliation_status != 'matched':
                continue
            if not rec.order_created_at:
                continue
            if rec.request_type != 'charge':
                continue
            if rec.is_investigated:
                continue
            diff = abs((
                from_str(rec.order_created_at) -
                from_str(rec.created_at)).days)
            rec.need_to_investigate = diff <= 2

    def _search_need_to_investigate(self, operator, operand):
        self.env.cr.execute(
            """
            SELECT id
            FROM ofh_payment_request as pr
            WHERE
                is_investigated = False AND
                pr.created_at - pr.order_created_at  <= interval '48 hours' AND
                reconciliation_status = 'matched' AND request_type = 'charge'
            """)
        ids = self.env.cr.fetchall()
        if (operator == '=' and operand) or (operator == '!=' and not operand):
            return [('id', 'in', ids)]
        else:
            return [('id', 'not in', ids)]

    @api.multi
    @api.depends('hub_supplier_reference', 'manual_supplier_reference')
    def _compute_supplier_reference(self):
        for rec in self:
            if rec.manual_supplier_reference:
                rec.supplier_reference = rec.manual_supplier_reference
            else:
                rec.supplier_reference = rec.hub_supplier_reference

    @api.multi
    @api.depends('manual_payment_reference', 'charge_id')
    def _compute_payment_reference(self):
        for rec in self:
            if rec.manual_payment_reference:
                rec.payment_reference = rec.manual_payment_reference
            else:
                rec.payment_reference = rec.charge_id

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
