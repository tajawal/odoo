# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class OfhPaymentRequest(models.Model):

    _inherit = ['ofh.payment.request']

    order_id = fields.Many2one(
        comodel_name="ofh.sale.order",
        string="Order ID",
        readonly=True,
        ondelete="cascade",
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
    hub_supplier_reference = fields.Char(
        string="Supplier Reference",
        related='order_id.supplier_reference',
        readonly=True,
        store=True,
        index=True,
    )
    hub_vendor_reference = fields.Char(
        string="Vendor Reference",
        related='order_id.vendor_reference',
        readonly=True,
        store=True,
        index=True,
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
    order_supplier_cost = fields.Monetary(
        currency_field='order_supplier_currency',
        related='order_id.total_supplier_cost',
        readonly=True,
    )
    order_supplier_currency = fields.Many2one(
        string="Supplier Currency",
        related='order_id.supplier_currency_id',
        comodel_name='res.currency',
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
    manual_supplier_reference = fields.Char(
        string="Manual Supplier Reference",
        index=True,
    )
    supplier_reference = fields.Char(
        string="Supplier Reference",
        readonly=True,
        track_visibility='always',
        compute='_compute_supplier_reference',
        store=False,
    )
    need_to_investigate = fields.Boolean(
        string="Matching needs investigation",
        compute='_compute_need_to_investigate',
        search='_search_need_to_investigate',
        readonly=True,
        store=False,
    )
    payment_request_status = fields.Selection(
        compute='_compute_payment_request_status',
        store=True,
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

    @api.multi
    @api.depends(
        'hub_supplier_reference', 'manual_supplier_reference')
    def _compute_supplier_reference(self):
        for rec in self:
            if rec.manual_supplier_reference:
                rec.supplier_reference = rec.manual_supplier_reference
            else:
                rec.supplier_reference = rec.hub_supplier_reference

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
    def _search_ticketing_office_id(self, operator, value):
        return [('order_id.ticketing_office_id', operator, value)]
