# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class OfhPaymentRequest(models.Model):

    _inherit = 'ofh.payment.request'

    order_id = fields.Many2one(
        comodel_name="ofh.sale.order",
        string="Order ID",
        readonly=True,
        ondelete="cascade",
        auto_join=True,
    )
    order_reference = fields.Char(
        related="order_id.name",
    )
    order_created_at = fields.Datetime(
        string="Order Created At",
        related='order_id.created_at',
        readonly=True,
        store=True,
    )
    order_updated_at = fields.Datetime(
        string="Order Updated At",
        related='order_id.updated_at',
        readonly=True,
        store=True,
    )
    order_type = fields.Selection(
        selection=[
            ('hotel', 'Hotel'),
            ('flight', 'Flight'),
            ('package', 'Package')],
        related='order_id.order_type',
        readonly=True,
    )
    order_track_id = fields.Char(
        readonly=True,
        related='order_id.track_id',
    )
    ticketing_office_id = fields.Char(
        string="Ticketing Office ID",
        related='order_id.ticketing_office_id',
        search='_search_ticketing_office_id',
        store=False,
        readonly=True,
    )
    order_amount = fields.Monetary(
        currency_field='order_currency_id',
        related='order_id.total_amount',
        readonly=True,
    )
    order_discount = fields.Monetary(
        currency_field='order_currency_id',
        related='order_id.total_discount',
        readonly=True,
    )
    order_currency_id = fields.Many2one(
        string="Order Currency",
        related='order_id.currency_id',
        readonly=True,
    )
    order_supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        compute='_compute_estimated_cost',
        comodel_name='res.currency',
    )
    order_supplier_cost = fields.Monetary(
        currency_field='order_supplier_currency_id',
        related='order_id.total_supplier_cost',
        readonly=True,
    )
    is_egypt = fields.Boolean(
        string='Is Egypt?',
        related='order_id.is_egypt',
        readonly=True,
        store=True,
        default=False,
        index=True,
    )
    entity = fields.Selection(
        related='order_id.entity',
        store=True,
    )
    vendor_reference = fields.Char(
        string="Vendor Reference",
        readonly=True,
        track_visibility='always',
        related='order_id.vendor_reference',
        search='_search_vendor_reference',
        store=False,
    )
    supplier_reference = fields.Char(
        string="Supplier Reference",
        readonly=True,
        track_visibility='always',
        related='order_id.supplier_reference',
        search='_search_supplier_reference',
        store=False,
    )
    payment_request_status = fields.Selection(
        compute='_compute_payment_request_status',
        store=True,
    )
    vendor_id = fields.Char(
        compute='_compute_vendor_id',
        store=True,
    )
    provider = fields.Char(
        compute='_compute_provider',
        store=True,
    )
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
    estimated_cost_in_supplier_currency = fields.Monetary(
        string="Estimated Cost in Supplier Currency",
        currency_field='order_supplier_currency_id',
        readonly=True,
        compute='_compute_estimated_cost',
        store=False,
    )
    is_full_refund = fields.Boolean(
        string='Is Full Refund?',
        compute='_compute_is_full_refund',
        store=True,
        readonly=True,
    )
    is_voided = fields.Boolean(
        string='Is Voided?',
        compute='_compute_is_voided',
        store=True,
        readonly=True,
    )

    @api.multi
    @api.depends(
        'insurance', 'fare_difference', 'penalty',
        'order_id.supplier_currency_id', 'order_id.vendor_currency_id',
        'currency_id')
    def _compute_estimated_cost(self):
        res = super(OfhPaymentRequest, self)._compute_estimated_cost()
        for rec in self:
            rec.estimated_cost_in_supplier_currency = 0.0
            if not rec.order_id:
                continue
            if rec.order_id.supplier_currency_id:
                rec.order_supplier_currency_id = \
                    rec.order_id.supplier_currency_id
            else:
                rec.order_supplier_currency_id = \
                    rec.order_id.vendor_currency_id
            if not rec.order_supplier_currency_id:
                continue
            rec.estimated_cost_in_supplier_currency = \
                rec.currency_id.compute(
                    rec.estimated_cost, rec.order_supplier_currency_id)
        return res

    @api.multi
    @api.depends('order_id')
    def _compute_payment_request_status(self):
        for rec in self:
            rec.payment_request_status = \
                'ready' if rec.order_id else 'incomplete'

    @api.multi
    @api.depends('order_id.line_ids')
    def _compute_vendor_id(self):
        for rec in self:
            rec.vendor_id = ''
            if rec.order_id:
                rec.vendor_id = ', '.join(set([
                    l.supplier_name for l in rec.order_id.line_ids]))

    @api.multi
    @api.depends('payment_ids.provider')
    def _compute_provider(self):
        for rec in self:
            rec.provider = ''
            if rec.payment_ids:
                rec.provider = ', '.join(
                    set([c.provider for c in rec.payment_ids]))

    @api.multi
    @api.depends('order_id.payment_request_ids')
    def _compute_is_full_refund(self):
        for rec in self:
            rec.is_full_refund = False
            if len(rec.order_id.payment_request_ids) != 1:
                continue
            if rec.request_type != 'refund':
                continue
            rec.is_full_refund = float_compare(
                rec.order_amount, rec.total_amount,
                precision_rounding=rec.currency_id.rounding) == 0

    @api.multi
    @api.depends('order_id.payment_request_ids')
    def _compute_is_voided(self):
        for rec in self:
            rec.is_voided = False
            if len(rec.order_id.payment_request_ids) != 1:
                continue
            if rec.request_type != 'void':
                continue
            rec.is_voided = True

    @api.multi
    def _search_ticketing_office_id(self, operator, value):
        return [('order_id.ticketing_office_id', operator, value)]

    @api.multi
    def _search_supplier_reference(self, operator, value):
        return [('order_id.supplier_reference', operator, value)]

    @api.multi
    def _search_vendor_reference(self, operator, value):
        return [('order_id.vendor_reference', operator, value)]
