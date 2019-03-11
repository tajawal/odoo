# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhSaleOrder(models.Model):

    _name = 'ofh.sale.order'
    _description = 'Ofh Sale Order'

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
    )
    track_id = fields.Char(
        string="Track ID",
        required=True,
        readonly=True,
    )
    order_status = fields.Char(
        string="Order Status",
        required=True,
        readonly=True,
    )
    payment_status = fields.Char(
        string="payment Status",
        required=True,
        readonly=True,
    )
    store_id = fields.Char(
        string="Store ID",
        required=True,
        readonly=True,
    )
    group_id = fields.Char(
        string="Group ID",
        required=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    vendor_currency_id = fields.Many2one(
        string="Vendor Currency",
        comodel_name='res.currency',
        readonly=True,
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
        store=False,
    )
    supplier_reference = fields.Char(
        string="Supplier Reference",
        compute='_compute_supplier_reference',
        readonly=True,
        store=False,
    )
    office_id = fields.Char(
        string="Office ID",
        compute='_compute_office_id',
        readonly=True,
        store=False,
    )
    ticketing_office_id = fields.Char(
        string="Ticketing Office ID",
        compute='_compute_ticketing_office_id',
        readonly=True,
        store=False,
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
