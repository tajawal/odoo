# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
        required=True,
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    reconciliation_tag = fields.Char(
        string="Reconciliation Tag",
        readonly=True,
    )
    reconciliation_amount = fields.Monetary(
        string="Deal/Loss Amount",
        compute='_compute_reconciliation_amount',
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
    def _compute_reconciliation_amount(self):
        for rec in self:
            pass

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
