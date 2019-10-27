# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhPaymentGateway(models.Model):
    _inherit = 'ofh.payment.gateway'

    hub_payment_id = fields.Many2one(
        string="Hub Payment",
        comodel_name='ofh.payment',
        required=False,
        ondelete="set null",
        readonly=True,
        track_visibility='onchange',
    )
    hub_payment_request_id = fields.Many2one(
        string="Hub Payment Request",
        comodel_name='ofh.payment.request',
        required=False,
        ondelete="set null",
        readonly=True,
        track_visibility='onchange',
    )
    hub_matching_status = fields.Selection(
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        default='unmatched',
        required=True,
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    settlement_matching_status = fields.Selection(
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        default='unmatched',
        required=True,
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    bank_settlement_id = fields.Many2one(
        string="Bank Settlement",
        comodel_name='ofh.bank.settlement',
        required=False,
        track_visibility='onchange',
        readonly=True,
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
            rec.reconciliation_status = 'unreconciled'

            if rec.settlement_matching_status == 'unmatched':
                rec.reconciliation_status = 'unreconciled'
                continue

            if rec.settlement_matching_status == 'not_applicable':
                rec.reconciliation_status = 'not_applicable'
                continue

            if rec.reconciliation_tag:
                rec.reconciliation_status = 'reconciled'
                continue

            rec.reconciliation_amount = \
                abs(rec.total - rec.bank_settlement_id.gross_amount)

            if rec.reconciliation_amount <= 1:
                rec.reconciliation_status = 'reconciled'
                continue

    @api.multi
    def match_with_payment(self):
        """Match a payment gateway object with a Payment or Payment Request."""
        self.ensure_one()
        if self.hub_matching_status in ('matched', 'not_applicable'):
            return
        self._match_with_payment()
        if not self.hub_payment_id:
            self._match_with_payment_request()
        return

    @api.multi
    def _match_with_payment(self):
        self.ensure_one()

        # Only Match with Auth and Captured
        if self.payment_status not in ('auth', 'capture'):
            return False

        # Matching with Payment Logic
        payment_id = self.env['ofh.payment'].search(
            self._get_payment_domain())

        if not payment_id:
            return False

        # In case of more than two matches, match with amounts as well
        if len(payment_id) > 1:
            for payment in payment_id:
                if payment.total_amount == self.total:
                    payment_id = payment
                    break

        self.write({
            "hub_payment_id": payment_id.id,
            "hub_matching_status": 'matched'
        })

        # Updating the relation
        payment_id.write({
            'payment_gateway_id': self.id,
            'pg_matching_status': 'matched',
        })
        return True

    # TODO: Need to remove this when done with Payments Object change
    @api.multi
    def _match_with_payment_request(self):
        # TODO: needs better implementation
        self.ensure_one()

        # Only Match with Void, Charge and Refund
        if self.payment_status not in ('void', 'refund'):
            domain = self._get_payment_request_domain_charge()
        else:
            domain = self._get_payment_request_domain_refund()

        # Matching with Payment Request Logic
        payment_request_id = self.env['ofh.payment.request'].search(
            domain)

        if not payment_request_id:
            return False

        # In case of more than two matches, match with amounts as well
        if len(payment_request_id) > 1:
            for payment_request in payment_request_id:
                if payment_request.total_amount == self.total:
                    payment_request_id = payment_request
                    break

        self.write({
            "hub_payment_request_id": payment_request_id.id,
            "hub_matching_status": 'matched'
        })
        # Updating the relation
        payment_request_id.write({
            'payment_gateway_id': self.id,
            'pg_matching_status': 'matched',
        })
        return True

    @api.multi
    def _get_payment_domain(self):
        self.ensure_one()
        # TODO: the search should by provider.
        return [
            ('track_id', '=', self.track_id),
            ('provider', '!=', 'loyalty')]

    @api.multi
    def _get_payment_request_domain_charge(self):
        self.ensure_one()
        return [
            ('track_id', '=', self.track_id),
            ('request_type', '=', 'charge')]

    @api.multi
    def _get_payment_request_domain_refund(self):
        self.ensure_one()
        return [
            ('parent_track_id', '=', self.track_id),
            ('request_type', 'in', ('void', 'refund'))]

    def _force_match_payment(
            self, hub_payment_id=False, hub_payment_request_id=False):

        self.ensure_one()
        if not hub_payment_id and not hub_payment_request_id:
            return False

        # Remove the current link in the invoice line.
        if self.hub_payment_id or self.hub_payment_request_id:
            self._unlink_payment()

        if hub_payment_id:
            # Link the payment gateway with the new payment.
            hub_payment_id.write({
                'payment_gateway_id': self.id,
                'pg_matching_status': 'matched',
            })
            self.write({
                'hub_payment_id': hub_payment_id.id,
                'hub_matching_status': 'matched',
            })
            return True
        else:
            hub_payment_request_id.write({
                'payment_gateway_id': self.id,
                'pg_matching_status': 'matched',
            })
            self.write({
                'hub_payment_request_id': hub_payment_request_id.id,
                'hub_matching_status': 'matched',
            })
            return True

    @api.multi
    def _unlink_payment(self):
        self.ensure_one()
        if self.hub_payment_id:
            self.hub_payment_id.write({
                'payment_gateway_id': False,
                'pg_matching_status': 'unmatched',
            })

        if self.hub_payment_request_id:
            self.hub_payment_request_id.write({
                'payment_gateway_id': False,
                'pg_matching_status': 'unmatched',
            })
        self.write({
            'hub_payment_id': False,
            'hub_payment_request_id': False,
            'hub_matching_status': 'unmatched',
        })

    @api.multi
    def action_unlink_payment(self):
        for rec in self:
            rec._unlink_payment()

    @api.multi
    def action_update_reconciliation_tag(self, reconciliation_tag):
        return self.write({
            'reconciliation_tag': reconciliation_tag,
            'reconciliation_status': 'reconciled',
        })
