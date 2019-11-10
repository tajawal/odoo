# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OfhBankSettlementForceMatch(models.TransientModel):
    _name = 'ofh.bank.settlement.force.match'

    @api.model
    def _get_default_payment_id(self):
        active_model = self.env.context.get('active_model')
        if active_model != 'ofh.bank.settlement':
            raise ValidationError(
                _("The active model is not the one expected."))
        active_id = self.env.context.get('active_id')
        return self.env[active_model].browse(active_id)

    bank_settlement_id = fields.Many2one(
        string="Bank Settlement Id",
        comodel_name='ofh.bank.settlement',
        required=True,
        readonly=True,
        default=_get_default_payment_id,
        ondelete="cascade"
    )
    current_payment_gateway_id = fields.Many2one(
        string="Current Payment Gateway",
        comodel_name='ofh.payment.gateway',
        readonly=True,
        related='bank_settlement_id.payment_gateway_id',
    )
    new_payment_gateway_id = fields.Many2one(
        string="New Payment Gateway",
        comodel_name='ofh.payment.gateway',
        domain="[('id', '!=', current_payment_gateway_id)]",
    )

    @api.multi
    def force_match(self):
        self.ensure_one()
        return self.bank_settlement_id._force_match_payment_gateway(
            payment_gateway_id=self.new_payment_gateway_id)
