# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhPaymentRequest(models.Model):

    _inherit = 'ofh.payment.request'

    reconciliation_status = fields.Selection(
        string="Reconciliation Status",
        selection=[
            ('reconciled', 'Reconciled'),
            ('unreconciled', 'Unreconciled'),
            ('not_applicable', 'Not Applicable'),
        ],
        default='unreconciled',
        compute='_compute_reconciliation_amount',
        store=True,
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    reconciliation_tag = fields.Char(
        string="Reconciliation Tag",
        readonly=True,
        track_visibility='onchange',
    )
    reconciliation_amount = fields.Monetary(
        string="Reconciliation Amount",
        compute='_compute_reconciliation_amount',
        currency_field='supplier_currency_id',
        readonly=True,
        store=False,
    )

    @api.multi
    def action_matching_status_not_applicable(self, not_applicable_flag):
        self.write({
            'matching_status': 'not_applicable',
            'reconciliation_status': 'not_applicable',
            'not_applicable_flag': not_applicable_flag,
        })
        invoice_lines = self.mapped('supplier_invoice_ids')
        if invoice_lines:
            invoice_lines.write({
                'matching_status': 'unmatched',
                'payment_request_id': False,
            })

    @api.multi
    @api.depends(
        'estimated_cost_in_supplier_currency',
        'supplier_total_amount', 'matching_status')
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

            rec.reconciliation_amount = \
                abs(rec.estimated_cost_in_supplier_currency - total_invoice)

            if rec.reconciliation_amount <= 1:
                rec.reconciliation_status = 'reconciled'
            else:
                rec.reconciliation_status = 'unreconciled'
