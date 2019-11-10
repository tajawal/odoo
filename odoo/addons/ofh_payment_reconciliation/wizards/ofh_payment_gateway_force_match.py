# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OfhPaymentGatewayForceMatch(models.TransientModel):
    _name = 'ofh.payment.gateway.force.match'

    @api.model
    def _get_default_payment_id(self):
        active_model = self.env.context.get('active_model')
        if active_model != 'ofh.payment.gateway':
            raise ValidationError(
                _("The active model is not the one expected."))
        active_id = self.env.context.get('active_id')
        return self.env[active_model].browse(active_id)

    payment_gateway_id = fields.Many2one(
        string="Payment Gateway Id",
        comodel_name='ofh.payment.gateway',
        required=True,
        readonly=True,
        default=_get_default_payment_id,
        ondelete="cascade"
    )
    current_hub_payment_id = fields.Many2one(
        string="Current Hub Payment",
        comodel_name='ofh.payment',
        readonly=True,
        related='payment_gateway_id.hub_payment_id',
    )
    current_hub_payment_request_id = fields.Many2one(
        string="Current Hub Payment Request",
        comodel_name='ofh.payment.request',
        readonly=True,
        related='payment_gateway_id.hub_payment_request_id',
    )
    new_hub_payment_id = fields.Many2one(
        string="New Hub Payment",
        comodel_name='ofh.payment',
        domain="[('id', '!=', current_hub_payment_id)]",
    )
    new_hub_payment_request_id = fields.Many2one(
        string="New Hub Payment request",
        comodel_name='ofh.payment.request',
        domain="[('id', '!=', current_hub_payment_request_id)]",
    )

    @api.multi
    def force_match(self):
        self.ensure_one()
        return self.payment_gateway_id._force_match_payment(
            hub_payment_id=self.new_hub_payment_id,
            hub_payment_request_id=self.new_hub_payment_request_id)
