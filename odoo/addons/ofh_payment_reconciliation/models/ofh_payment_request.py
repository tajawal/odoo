from odoo import fields, models, api


class OfhPaymentRequest(models.Model):
    _inherit = 'ofh.payment.request'

    payment_gateway_id = fields.Many2one(
        string="Payment Gateway",
        comodel_name='ofh.payment.gateway',
    )
    bank_settlement_id = fields.Many2one(
        related="payment_gateway_id.bank_settlement_id",
    )
    settlement_date = fields.Date(
        string="Bank Settlement Date",
        related="bank_settlement_id.settlement_date",
    )
    response_description = fields.Char(
        related="payment_gateway_id.response_description",
    )
    arn = fields.Char(
        related="payment_gateway_id.arn",
    )
    is_apple_pay = fields.Boolean(
        related="payment_gateway_id.is_apple_pay",
    )
    pg_payment_status = fields.Selection(
        string="PG Payment Status",
        related="payment_gateway_id.payment_status",
    )
    bank_name = fields.Selection(
        related="bank_settlement_id.bank_name",
    )
    gross_amount = fields.Monetary(
        related="bank_settlement_id.gross_amount",
    )
    net_transaction_amount = fields.Monetary(
        related="bank_settlement_id.net_transaction_amount",
    )
    pg_matching_status = fields.Selection(
        string="PG Matching Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched')],
        default='unmatched',
        required=True,
        index=True,
        readonly=True,
        store=True,
    )
    is_applicable = fields.Boolean(
        string="Is Applicable?",
        default=True,
        readonly=True,
        index=True,
    )
    pg_reconciliation_status = fields.Selection(
        string="Reconciliation Status",
        selection=[
            ('reconciled', 'Reconciled'),
            ('unreconciled', 'Unreconciled'),
            ('not_applicable', 'Not Applicable'),
        ],
        default='unreconciled',
        compute='_compute_reconciliation_status',
        search='_search_pg_reconciliation_status',
        index=True,
        readonly=True,
    )

    @api.multi
    @api.depends(
        'payment_gateway_id.reconciliation_status')
    def _compute_reconciliation_status(self):
        for rec in self:
            rec.pg_reconciliation_status = rec.payment_gateway_id.reconciliation_status

            if not rec.payment_gateway_id.reconciliation_status:
                rec.pg_reconciliation_status = 'unreconciled'
                continue

    @api.multi
    def action_applicable(self):
        return self.write({
            'is_applicable': True,
        })

    @api.multi
    def action_not_applicable(self):
        return self.write({
            'is_applicable': False,
        })

    @api.multi
    def _search_pg_reconciliation_status(self, operator, value):
        return [('pg_reconciliation_status', operator, value)]