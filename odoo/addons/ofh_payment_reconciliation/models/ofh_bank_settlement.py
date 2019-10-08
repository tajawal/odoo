# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from odoo.exceptions import MissingError


class OfhBankSettlement(models.Model):
    _inherit = 'ofh.bank.settlement'

    payment_gateway_id = fields.Many2one(
        string="Payment Gateway Id",
        comodel_name='ofh.payment.gateway',
        required=False,
        ondelete='cascade',
        track_visibility='onchange',
    )
    matching_status = fields.Selection(
        string="Matching Status",
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
    reconciliation_status = fields.Selection(
        string="Reconciliation Status",
        selection=[
            ('reconciled', 'Reconciled'),
            ('unreconciled', 'Unreconciled'),
            ('not_applicable', 'Not Applicable'),
        ],
        default='unreconciled',
        compute='_compute_reconciliation_status',
        search='_search_reconciliation_status',
        index=True,
        readonly=True,
    )

    @api.multi
    @api.depends(
        'payment_gateway_id.reconciliation_status')
    def _compute_reconciliation_status(self):
        for rec in self:
            rec.reconciliation_status = 'unreconciled'

            if rec.payment_gateway_id:
                rec.reconciliation_status = \
                    rec.payment_gateway_id.reconciliation_status
                continue

    @api.multi
    def _search_reconciliation_status(self, operator, value):
        return [('reconciliation_status', operator, value)]

    @api.multi
    def match_with_payment_gateway(self):
        """Match a bank settlement object with a Payment Gateway."""
        self.ensure_one()
        if self.matching_status not in ('matched', 'not_applicable'):
            match_function = f'_match_with_payment_gateway_{self.bank_name}'
            if hasattr(self, match_function):
                getattr(self, match_function)()
            else:
                raise MissingError(_("Method not implemented."))

    @api.multi
    def _match_with_payment_gateway_sabb(self):
        self.ensure_one()
        # Matching with Payment Gateway Checkout and Fort Logic
        payment_gateway_ids = self.env['ofh.payment.gateway'].search(
            self._get_payment_gateway_domain(['checkout', 'fort']), limit=1)

        self._set_payment_gateway_matching(payment_gateway_ids)

    @api.multi
    def _match_with_payment_gateway_rajhi(self):
        self.ensure_one()
        # Matching with Payment Gateway Checkout Logic
        payment_gateway_ids = self.env['ofh.payment.gateway'].search(
            self._get_payment_gateway_domain(['checkout']), limit=1)

        self._set_payment_gateway_matching(payment_gateway_ids)

    @api.multi
    def _match_with_payment_gateway_mashreq(self):
        self.ensure_one()
        # Matching with Payment Gateway Checkout and Fort Logic
        payment_gateway_ids = self.env['ofh.payment.gateway'].search(
            self._get_payment_gateway_domain(['checkout', 'fort']), limit=1)

        self._set_payment_gateway_matching(payment_gateway_ids)

    @api.multi
    def _match_with_payment_gateway_amex(self):
        self.ensure_one()
        # Matching with Payment Gateway Checkout Logic
        payment_gateway_ids = self.env['ofh.payment.gateway'].search(
            self._get_payment_gateway_domain(['checkout']), limit=1)

        self._set_payment_gateway_matching(payment_gateway_ids)

    @api.multi
    def _get_payment_gateway_domain(self, provider):
        return [('provider', 'in', provider),
                ('acquirer_bank', '=', self.bank_name),
                ('auth_code', '=', self.auth_code),
                ('payment_status', '=', self.payment_status)]

    @api.multi
    def _set_payment_gateway_matching(self, payment_gateway_id):
        self.ensure_one()
        if not payment_gateway_id:
            return

        self.write({
            "payment_gateway_id": payment_gateway_id.id,
            "matching_status": 'matched'
        })

        # Updating the relation
        payment_gateway_id.write({
            'bank_settlement_id': self.id,
            'settlement_matching_status': 'matched',
        })
        return

    def _force_match_payment_gateway(
            self, payment_gateway_id=False):

        self.ensure_one()
        if not payment_gateway_id:
            return

        # Remove the current link in the invoice line.
        if self.payment_gateway_id:
            self._unlink_payment_gateway()

        # Link the payment gateway with the new payment gateway.
        payment_gateway_id.write({
            'bank_settlement_id': self.id,
            'settlement_matching_status': 'matched',
        })
        self.write({
            'payment_gateway_id': payment_gateway_id.id,
            'matching_status': 'matched',
        })
        return

    @api.multi
    def _unlink_payment_gateway(self):
        self.ensure_one()
        self.payment_gateway_id.write({
            'bank_settlement_id': False,
            'settlement_matching_status': 'unmatched',
        })
        self.write({
            'payment_gateway_id': False,
            'settlement_matching_status': 'unmatched',
        })
        return

    @api.multi
    def action_unlink_payment_gateway(self):
        for rec in self:
            rec._unlink_payment_gateway()
