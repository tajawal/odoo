# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import fields, models
from odoo.addons.component.core import Component


class HubPaymentRequest(models.Model):

    _name = 'hub.payment.request'
    _inherit = 'hub.binding'
    _inherits = {'ofh.payment.request': 'odoo_id'}

    odoo_id = fields.Many2one(
        comodel_name='ofh.payment.request',
        string='Payment Request',
        required=True,
        ondelete='cascade'
    )
    created_at = fields.Datetime(
        required=True,
    )
    updated_at = fields.Datetime(
        required=True,
    )


class PaymentRequestAdapter(Component):

    _name = 'ofh.payment.request.adapter'
    _inherit = 'hub.adapter'
    _apply_on = 'hub.payment.request'

    def search(self, filters: dict) -> list:
        try:
            hub_api = getattr(self.work, 'hub_api')
        except AttributeError:
            raise AttributeError(
                'You must provide a hub_api attribute with a '
                'HubAPI instance to be able to use the '
                'Backend Adapter.'
            )
        from_date = filters.pop('from')
        if not from_date:
            from_date = datetime.strptime("2018-09-01", "%Y-%m-%d")
        to_date = filters.pop('to')
        if not to_date:
            to_date = datetime.now()
        return hub_api.getProcessedPaymentRequest(
            from_date=from_date, to_date=to_date)

    def read(self, external_id, attributes={}) -> dict:
        try:
            hub_api = getattr(self.work, 'hub_api')
        except AttributeError:
            raise AttributeError(
                'You must provide a hub_api attribute with a '
                'HubAPI instance to be able to use the '
                'Backend Adapter.'
            )
        return hub_api.get_payment_request_by_track_id(external_id)
