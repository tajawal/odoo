# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class OfhPaymentGateway(models.Model):
    _inherit = 'ofh.payment.gateway'

    hub_payment_id = fields.Many2one(
        string="Hub Payment Id",
        comodel_name='ofh.payment',
        required=False,
        ondelete='cascade'
    )
    hub_payment_request_id = fields.Many2one(
        string="Hub Payment Request Id",
        comodel_name='ofh.payment.request',
        required=False,
        ondelete='cascade'
    )
    hub_matching_status = fields.Selection(
        string="Hub Matching Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        default='unmatched',
        required=True,
        index=True,
        readonly=True,
        track_visibility='always',
    )
    settlement_matching_status = fields.Selection(
        string="Settlement Matching Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        default='unmatched',
        required=True,
        index=True,
        readonly=True,
        track_visibility='always',
    )
    bank_settlement_id = fields.Many2one(
        string="Bank Settlement",
        comodel_name='ofh.bank.settlement',
        required=False,
        track_visibility='onchange',
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
        store=False,
        track_visibility='onchange',
    )
    reconciliation_tag = fields.Char(
        string="Reconciliation Tag",
        track_visibility='onchange',
    )
    reconciliation_amount = fields.Monetary(
        string="Reconciliation Amount",
        compute='_compute_reconciliation_amount',
        currency_field='currency_id',
        readonly=True,
        store=False,
    )

    @api.multi
    @api.depends(
        'total', 'settlement_matching_status',
        'bank_settlement_id.gross_amount', 'reconciliation_tag')
    def _compute_reconciliation_amount(self):
        for rec in self:
            rec.reconciliation_amount = 0

            if rec.settlement_matching_status == 'unmatched':
                rec.reconciliation_status = 'unreconciled'
                continue

            if rec.settlement_matching_status == 'not_applicable':
                rec.reconciliation_status = 'not_applicable'
                continue

            rec.reconciliation_amount = \
                abs(rec.total - rec.bank_settlement_id.gross_amount)

            if rec.reconciliation_tag:
                rec.reconciliation_status = 'reconciled'
                continue

            if rec.reconciliation_amount <= 1:
                rec.reconciliation_status = 'reconciled'
            else:
                rec.reconciliation_status = 'unreconciled'

    @api.multi
    def match_with_payment(self):
        """Match a payment gateway object with a Payment or Payment Request."""
        self.ensure_one()
        if self.hub_matching_status not in ('matched', 'not_applicable'):
            self._match_with_payment()
            self._match_with_payment_request()

    @api.multi
    def _match_with_payment(self):
        self.ensure_one()
        # Matching with Payment Logic
        payment_id = self.env['ofh.payment'].search(
            self._get_payment_domain(), limit=1)

        if payment_id:
            self.write({
                "hub_payment_id": payment_id.id,
                "hub_matching_status": 'matched'
            })
            # Updating the relation
            payment_id.write({
                'payment_gateway_id': self.id,
                'pg_matching_status': 'matched',
            })

    # TODO: Need to remove this when done with Payments Object change
    @api.multi
    def _match_with_payment_request(self):
        self.ensure_one()
        # Matching with Payment Request Logic
        payment_request_id = self.env['ofh.payment.request'].search(
            self._get_payment_domain(), limit=1)

        if len(payment_request_id):
            self.write({
                "hub_payment_request_id": payment_request_id.id,
                "hub_matching_status": 'matched'
            })
            # Updating the relation
            payment_request_id.write({
                'payment_gateway_id': self.id,
            })

    @api.multi
    def _get_payment_domain(self):
        return [
            ('track_id', '=', self.track_id)]
