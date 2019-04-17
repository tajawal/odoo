# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhSaleOrder(models.Model):

    _name = 'ofh.sale.order'
    _description = 'Ofh Sale Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_order_status_selection(self):
        return [
            ("10", "New"), ("15", "Tour Code in Progress"),
            ("18", "Booking in Progress"), ("25", "PNR in Progress"),
            ("30", "TST Error"), ("35", "TST in Progress"),
            ("39", "TST Created"), ("40", "New TF Booking"),
            ("41", "Incomplete TF booking"), ("42", "Unconfirmed TF Booking"),
            ("43", "Contact TF Support"), ("44", "Pending"),
            ("50", "Confirm Decision"), ("51", "Manually Ordered"),
            ("52", "Manual Confirm Queue"), ("53", "Manually Confirmed"),
            ("54", "Auto Confirm Started"), ("55", "Auto Confirm Queue"),
            ("56", "Auto Confirm in Progress"),
            ("57", "Auto Confirmed Partial Booking"),
            ("58", "Auto Confirmed"), ("60", "Auto Confirm Failed"),
            ("61", "Auto Confirm Cancelled"), ("62", "Auto Confirm Deleted"),
            ("64", "Manual Payment"), ("65", "Reprice Confirm Queue"),
            ("89", "Unprocessed"), ("91", "Failed"), ("94", "Cancelled"),
            ("95", "Refunded"), ("96", "Manually Cancelled"),
            ("100", "Duplicate"), ("101", "Cancellation under process"),
            ("102", "Cancellation cannot be processed"),
            ("200", "Reorder"), ("201", "Smart booking cancelled"),
            ("1000", "Mixed")
        ]

    @api.model
    def _get_payment_status_selection(self):
        return [
            ("79", 'Authorized - Risk flagged'), ("70", 'Error'),
            ("71", 'Pending'), ("72", 'Progress'), ("73", 'Timeout'),
            ("74", 'Empty'), ("77", 'Partial Paid'),
            ("76", 'Full Refund'), ("75", 'Partial Refund'),
            ("78", 'Authorized'), ("80", 'Captured'),
            ("83", 'Manually Captured'),
            ("81", 'Voided'), ("64", 'Manual Payment'), ("1000", 'Mixed')]

    name = fields.Char(
        string="Order ID",
        readonly=True,
        required=True,
    )
    created_at = fields.Datetime(
        string="Created At",
        required=True,
        readonly=True,
        index=True,
    )
    updated_at = fields.Datetime(
        string="Updated At",
        required=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    track_id = fields.Char(
        string="Track ID",
        required=True,
        readonly=True,
        index=True,
    )
    order_type = fields.Selection(
        string="Order Type",
        selection=[
            ('hotel', 'Hotel'),
            ('flight', 'Flight'),
            ('package', 'Package')],
        required=True,
        readonly=True,
        index=True,
    )
    entity = fields.Selection(
        selection=[
            ('almosafer', 'Almosafer'),
            ('tajawal', 'Tajawal')],
        required=True,
        readonly=True,
        index=True,
    )
    order_status = fields.Selection(
        string="Order Status",
        selection=_get_order_status_selection,
        required=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    is_egypt = fields.Boolean(
        string="Is Egypt?",
        readonly=True,
        default=False,
        index=True,
    )
    payment_status = fields.Selection(
        string="payment Status",
        selection=_get_payment_status_selection,
        required=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    paid_at = fields.Datetime(
        string="Paid At",
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    store_id = fields.Char(
        string="Store ID",
        required=True,
        readonly=True,
        index=True,
    )
    group_id = fields.Char(
        string="Group ID",
        required=True,
        readonly=True,
        index=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name='res.currency',
        required=True,
        readonly=True,
        index=True,
    )
    vendor_currency_id = fields.Many2one(
        string="Vendor Currency",
        comodel_name='res.currency',
        readonly=True,
        index=True,
    )
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        readonly=True,
    )
    total_vendor_cost = fields.Monetary(
        string="Total Vendor Cost",
        currency_field='vendor_currency_id',
        readonly=True
    )
    total_supplier_cost = fields.Monetary(
        string="Total Supplier Cost",
        currency_field='supplier_currency_id',
        readonly=True
    )
    total_amount = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    total_discount = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    total_tax = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    total_service_fee = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    total_insurance_amount = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    line_ids = fields.One2many(
        string="Lines",
        comodel_name='ofh.sale.order.line',
        inverse_name='order_id',
        readonly=True,
    )
    vendor_reference = fields.Char(
        string='Vendor Reference',
        compute='_compute_vendor_reference',
        readonly=True,
        # Storing this value to be able to search a search on it
        store=True,
        index=True,
        track_visibility='onchange',
    )
    supplier_reference = fields.Char(
        string="Supplier Reference",
        compute='_compute_supplier_reference',
        readonly=True,
        # Storing the value to be able to run a search on it
        store=True,
        index=True,
        track_visibility='onchange',
    )
    office_id = fields.Char(
        string="Office ID",
        compute='_compute_office_id',
        readonly=True,
        store=False,
        index=True,
    )
    ticketing_office_id = fields.Char(
        string="Ticketing Office ID",
        compute='_compute_ticketing_office_id',
        readonly=True,
        store=True,
        index=True,
        track_visibility='onchange',
    )
    hub_bind_ids = fields.One2many(
        comodel_name='hub.sale.order',
        inverse_name='odoo_id',
        string="Hub Bindings",
        readonly=True,
    )
    # Computed totals from lines
    lines_total_vendor_cost = fields.Monetary(
        string="Total computed vendor cost",
        compute='_compute_total_amounts',
        currency_field='vendor_currency_id',
        readonly=True,
        store=False,
    )
    lines_total_service_fee = fields.Monetary(
        string="Total computed service fee",
        compute='_compute_total_amounts',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )
    lines_total_sale_price = fields.Monetary(
        string="Total computed sale price",
        compute='_compute_total_amounts',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )
    lines_total_discount = fields.Monetary(
        string="Total computed discount",
        compute='_compute_total_amounts',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )
    lines_total_tax = fields.Monetary(
        string="Total computed tax",
        compute='_compute_total_amounts',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )
    lines_total_amount = fields.Monetary(
        string="Computed total Amount",
        compute='_compute_total_amounts',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )
    order_matching_status = fields.Selection(
        string="Matching Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        default='unmatched',
        compute='_compute_order_matching_status',
        store=False,
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    payment_ids = fields.One2many(
        string="Payments",
        comodel_name='ofh.payment',
        inverse_name='order_id',
        readonly=True
    )

    @api.multi
    @api.depends('line_ids.vendor_confirmation_number')
    def _compute_vendor_reference(self):
        for rec in self:
            rec.vendor_reference = ', '.join(
                set([r.vendor_confirmation_number for r in rec.line_ids]))

    @api.multi
    @api.depends('line_ids.supplier_confirmation_number')
    def _compute_supplier_reference(self):
        for rec in self:
            rec.supplier_reference = ', '.join(
                set([r.supplier_confirmation_number for r in rec.line_ids]))

    @api.multi
    @api.depends('line_ids.office_id')
    def _compute_office_id(self):
        for rec in self:
            rec.office_id = ', '.join(
                set([r.office_id for r in rec.line_ids if r.office_id]))

    @api.multi
    @api.depends('line_ids.ticketing_office_id')
    def _compute_ticketing_office_id(self):
        for rec in self:
            rec.ticketing_office_id = ', '.join(
                set([r.ticketing_office_id for r in rec.line_ids
                     if r.ticketing_office_id]))

    @api.multi
    @api.depends('line_ids')
    def _compute_total_amounts(self):
        for rec in self:
            rec.lines_total_vendor_cost = rec.lines_total_service_fee = \
                rec.lines_total_sale_price = rec.lines_total_discount = \
                rec.lines_total_tax = rec.lines_total_amount = 0.0
            for line in rec.line_ids:
                rec.lines_total_vendor_cost += line.vendor_cost_amount
                rec.lines_total_service_fee += line.service_fee_amount
                rec.lines_total_sale_price += line.sale_price
                rec.lines_total_discount += line.discount_amount
                rec.lines_total_tax += line.tax_amount
                rec.lines_total_amount += line.total_amount

    @api.multi
    @api.depends('line_ids.matching_status')
    def _compute_order_matching_status(self):
        for rec in self:
            if all([l.matching_status == 'not_applicable'
                    for l in rec.line_ids]):
                rec.order_matching_status = 'not_applicable'
                continue
            if all([l.matching_status in ('matched', 'not_applicable')
                    for l in rec.line_ids]):
                rec.order_matching_status = 'matched'
                continue
            rec.order_matching_status = 'unmatched'

    @api.multi
    def open_order_in_hub(self):
        """Open the order link to the payment request in hub using URL
        Returns:
            [dict] -- URL action dictionary
        """

        self.ensure_one()
        hub_backend = self.env['hub.backend'].search([], limit=1)
        if not hub_backend:
            return
        hub_url = "{}admin/order/air/detail/{}".format(
            hub_backend.hub_api_location, self.name)
        return {
            "type": "ir.actions.act_url",
            "url": hub_url,
            "target": "new",
        }
