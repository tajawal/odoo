# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class OfhPaymentGateway(models.Model):
    _inherit = 'ofh.payment.gateway'

    bank_settlement_id = fields.Many2one(
        string="Bank Settlement ID",
        comodel_name='ofh.bank.settlement',
        required=False,
        track_visibility='onchange',
    )

    @api.multi
    def match_with_payment(self):
        """Match a payment gateway object with a Payment or Payment Request."""
        self.ensure_one()
        if self.matching_status not in ('matched', 'not_applicable'):
            self._match_with_payment()
            self._match_with_payment_request()

    @api.multi
    def _match_with_payment(self):
        self.ensure_one()
        # Matching with Payment Logic
        payment_ids = self.env['ofh.payment'].search(
            self._get_payment_domain())

        if len(payment_ids):
            self.hub_payment_id = payment_ids[0].id
            self.matching_status = 'matched'
            # Updating the relation
            payment_ids[0].write({
                'payment_gateway_id': self.id,
            })

    @api.multi
    def _match_with_payment_request(self):
        self.ensure_one()
        # Matching with Payment Request Logic
        payment_request_ids = self.env['ofh.payment.request'].search(
            self._get_payment_domain())

        if len(payment_request_ids):
            self.hub_payment_request_id = payment_request_ids[0].id
            self.matching_status = 'matched'
            # Updating the relation
            payment_request_ids[0].write({
                'payment_gateway_id': self.id,
            })

    @api.multi
    def _get_payment_domain(self):
        return [
            ('track_id', '=', self.track_id)]
