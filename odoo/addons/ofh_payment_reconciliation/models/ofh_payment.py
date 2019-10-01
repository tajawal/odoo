from odoo import fields, models, api


class OfhPayment(models.Model):
    _inherit = 'ofh.payment'

    payment_gateway_id = fields.Many2one(
        string="Payment Gateway",
        comodel_name='ofh.payment.gateway',
    )
    bank_settlement_id = fields.Many2one(
        string="Bank Settlement Id",
        comodel_name='ofh.bank.settlement',
        store=True,
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
        string="Payment Gateway Payment Status",
        related="payment_gateway_id.payment_status",
    )
    bank_name = fields.Selection(
        related="bank_settlement_id.bank_name",
    )
    entity = fields.Selection(
        related="payment_gateway_id.entity",
    )
    pg_provider = fields.Selection(
        string="Payment Gateway Provider",
        related="payment_gateway_id.provider",
    )
    is_mada = fields.Boolean(
        related="bank_settlement_id.is_mada",
    )
    gross_amount = fields.Monetary(
        related="bank_settlement_id.gross_amount",
    )
    total = fields.Monetary(
        string="PG Total",
        related="payment_gateway_id.total",
    )
    pg_matching_status = fields.Selection(
        related="payment_gateway_id.matching_status",
    )
    ticketing_office_id = fields.Char(
        related="order_id.ticketing_office_id",
    )
    matching_status = fields.Selection(
        string="Matching Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('partial_matched', 'Partial Matched')],
        default='unmatched',
        required=True,
        index=True,
        readonly=True,
        store=False,
        compute='_compute_matching_status',
    )
    reconciliation_status = fields.Selection(
        string="Reconciliation Status",
        selection=[
            ('reconciled', 'Reconciled'),
            ('unreconciled', 'Unreconciled'),
        ],
        default='unreconciled',
        compute='_compute_reconciliation_status',
        store=False,
        index=True,
        readonly=True,
    )
    reconciliation_tag = fields.Char(
        string="Reconciliation Tag",
        track_visibility='onchange',
    )
    is_applicable = fields.Boolean(
        string="Is Applicable?",
        default=True,
        readonly=True,
        index=True,
    )

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
    @api.depends(
        'payment_gateway_id', 'bank_settlement_id')
    def _compute_matching_status(self):
        for rec in self:
            rec.matching_status = "unmatched"
            if rec.payment_gateway_id and rec.bank_settlement_id:
                rec.matching_status = 'matched'
                continue

            if rec.payment_gateway_id or rec.bank_settlement_id:
                rec.matching_status = 'partial_matched'
                continue

    @api.multi
    @api.depends('bank_settlement_id')
    def _compute_reconciliation_status(self):
        for rec in self:
            rec.reconciliation_status = 'unreconciled'
            if rec.reconciliation_tag:
                rec.reconciliation_status = 'reconciled'
                continue

            if rec.bank_settlement_id and rec.bank_settlement_id.reconciliation_status == "reconciled":
                rec.reconciliation_status = 'reconciled'
                continue

    @api.multi
    def action_update_reconciliation_tag(self, reconciliation_tag):
        return self.write({
            'reconciliation_tag': reconciliation_tag,
            'reconciliation_status': 'reconciled',
        })
