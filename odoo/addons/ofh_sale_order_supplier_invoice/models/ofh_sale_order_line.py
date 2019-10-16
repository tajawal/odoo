# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


AIR_INDIA = 'AI'


class OfhSaleOrderLine(models.Model):

    _inherit = 'ofh.sale.order.line'

    invoice_line_ids = fields.One2many(
        string="Invoice lines",
        comodel_name='ofh.supplier.invoice.line',
        inverse_name='order_line_id',
    )
    investigation_tag = fields.Char(
        string="Unmatched Tag",
        index=True,
        track_visibility='onchange',
    )
    air_india_commission = fields.Monetary(
        string="Air India Commission",
        currency_field='supplier_currency_id',
        compute='_compute_air_india_commission',
    )
    reconciliation_status = fields.Selection(
        string="Reconciliation Status",
        selection=[
            ('reconciled', 'Reconciled'),
            ('unreconciled', 'Unreconciled'),
            ('not_applicable', 'Not Applicable'),
        ],
        default='unreconciled',
        compute='_compute_reconciliation_amount',
        index=True,
        readonly=True,
        store=True,
        track_visibility='onchange',
    )
    reconciliation_tag = fields.Char(
        string="Reconciliation Tag",
        track_visibility='onchange',
    )
    reconciliation_amount = fields.Monetary(
        string="Reconciliation Amount",
        compute='_compute_reconciliation_amount',
        currency_field='supplier_currency_id',
        readonly=True,
        store=False,
    )
    total_invoice_amount = fields.Monetary(
        string="Total Invoice Amount",
        compute='_compute_total_invoice_amount',
        currency_field='invoice_currency_id',
        readonly=True,
        store=False,
    )
    invoice_currency_id = fields.Many2one(
        string='Invoice Currency',
        comodel_name='res.currency',
        compute='_compute_total_invoice_amount',
        store=False,
        readonly=True,
    )

    @api.depends(
        'supplier_name', 'supplier_currency_id', 'segment_count')
    @api.multi
    def _compute_air_india_commission(self):
        commissions = {'AED': 30, 'SAR': 30, 'KWD': 2.5}
        for rec in self:
            rec.air_india_commission = 0
            if rec.supplier_name != AIR_INDIA:
                continue
            comm = commissions.get(rec.supplier_currency_id.name)
            if rec.segment_count and comm:
                rec.air_india_commission = rec.segment_count * comm

    @api.multi
    @api.depends(
        'invoice_line_ids.total', 'invoice_line_ids.itl_cost',
        'air_india_commission', 'supplier_cost_amount', 'matching_status',
        'reconciliation_tag')
    def _compute_reconciliation_amount(self):
        for rec in self:
            rec.reconciliation_amount = 0
            if rec.matching_status == 'unmatched':
                rec.reconciliation_status = 'unreconciled'
                continue
            if rec.matching_status == 'not_applicable':
                rec.reconciliation_status = 'not_applicable'
                continue

            total_invoice = sum(
                [l.total - l.itl_cost for l in rec.invoice_line_ids])
            supplier_cost = rec.supplier_cost_amount + rec.air_india_commission
            rec.reconciliation_amount = supplier_cost - total_invoice

            if rec.reconciliation_tag:
                rec.reconciliation_status = 'reconciled'
                continue

            if abs(rec.reconciliation_amount) <= 1:
                rec.reconciliation_status = 'reconciled'
            else:
                rec.reconciliation_status = 'unreconciled'

    @api.multi
    @api.depends('invoice_line_ids.total')
    def _compute_total_invoice_amount(self):
        for rec in self:
            rec.total_invoice_amount = 0
            rec.invoice_currency_id = False
            if rec.invoice_line_ids:
                rec.total_invoice_amount = sum(
                    [l.total - l.itl_cost for l in rec.invoice_line_ids])
                rec.invoice_currency_id = \
                    rec.invoice_line_ids.mapped('currency_id')[0]

    @api.multi
    def action_matching_status_not_applicable(self, not_applicable_flag):
        self.write({
            'matching_status': 'not_applicable',
            'reconciliation_status': 'not_applicable',
            'not_applicable_flag': not_applicable_flag,
        })
        invoice_lines = self.mapped('invoice_line_ids')
        if invoice_lines:
            invoice_lines.write({
                'matching_status': 'unmatched',
                'order_line_id': False,
            })

    @api.multi
    def action_update_investigation_tag(self, investigation_tag):
        return self.write({
            'investigation_tag': investigation_tag})

    @api.multi
    def action_update_reconciliation_tag(self, reconciliation_tag):
        return self.write({
            'reconciliation_tag': reconciliation_tag,
            'reconciliation_status': 'reconciled',
        })
