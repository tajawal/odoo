# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class OfhSaleOrderLine(models.Model):

    _inherit = 'ofh.sale.order.line'

    invoice_line_ids = fields.One2many(
        string="Invoice lines",
        comodel_name='ofh.supplier.invoice.line',
        inverse_name='order_line_id',
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
        ],
        default='unreconciled',
        required=True,
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    reconciliation_tag = fields.Selection(
        string="Deal/Loss",
        selection=[
            ('deal', 'DEAL'),
            ('loss', 'LOSS'),
            ('none', 'N/A')],
        compute='_compute_reconciliation_tag',
        default='none',
        readonly=True,
        store=False,
    )
    reconciliation_amount = fields.Monetary(
        string="Deal/Loss Amount",
        compute='_compute_reconciliation_tag',
        currency_field='supplier_currency_id',
        readonly=True,
        store=False,
    )

    @api.depends('supplier_currency_id', 'segment_count')
    @api.multi
    def _compute_air_india_commission(self):
        commissions = {'AED': 30, 'SAR': 30, 'KWD': 2.5}
        for rec in self:
            rec.air_india_commission = 0
            if not rec.supplier_currency_id or \
               rec.ticketing_office_id != 'TRAVEL FUSION':
                continue
            rec.air_india_commission = \
                rec.segment_count * commissions.get(
                    rec.supplier_currency_id.name)

    @api.multi
    def _compute_reconciliation_tag(self):
        for rec in self:
            pass
