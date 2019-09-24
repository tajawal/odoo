from odoo import fields, models, api


class OfhPayment(models.Model):
    _inherit = 'ofh.payment'

    payment_gateway_ids = fields.One2many(
        string="Payment Gateway ID",
        comodel_name='ofh.payment.gateway',
        inverse_name='hub_payment_id',
    )
    bank_settlement_ids = fields.One2many(
        string="Bank Settlements",
        related="payment_gateway_ids.bank_settlement_ids",
        readonly=True,
        store=False,
    )
    settlement_date = fields.Date(
        string="Bank Settlement Date",
        related="bank_settlement_ids.settlement_date",
    )
    response_description = fields.Char(
        related="payment_gateway_ids.response_description",
    )
    arn = fields.Char(
        related="payment_gateway_ids.arn",
    )
    is_apple_pay = fields.Boolean(
        related="payment_gateway_ids.is_apple_pay",
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

    @api.multi
    @api.depends(
        'payment_gateway_ids', 'bank_settlement_ids')
    def _compute_matching_status(self):
        for rec in self:
            rec.matching_status = "unmatched"
            if rec.payment_gateway_ids and rec.bank_settlement_ids:
                rec.matching_status = 'matched'
                continue

            if rec.payment_gateway_ids or rec.bank_settlement_ids:
                rec.matching_status = 'partial_matched'
                continue

    @api.multi
    @api.depends('bank_settlement_ids')
    def _compute_reconciliation_status(self):
        for rec in self:
            rec.reconciliation_status = 'unreconciled'
            if rec.bank_settlement_ids and rec.bank_settlement_ids.reconciliation_status == "reconciled":
                rec.reconciliation_status = 'reconciled'
                continue


