# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.component.core import Component


class HubPayment(models.Model):
    _name = 'hub.payment'
    _inherit = 'hub.binding'
    _inherits = {'ofh.payment': 'odoo_id'}

    odoo_id = fields.Many2one(
        comodel_name='ofh.payment',
        string='Payment',
        required=True,
        ondelete='cascade'
    )
    hub_charge_ids = fields.One2many(
        comodel_name='hub.payment.charge',
        inverse_name='hub_payment_id',
        string="Hub Charges",
    )


class PaymentAdapter(Component):
    _name = 'ofh.payment.adapter'
    _inherit = 'hub.adapter'
    _apply_on = 'hub.payment'

    def read(self, external_id, attributes={}) -> dict:
        try:
            hub_api = getattr(self.work, 'hub_api')
        except AttributeError:
            raise AttributeError(
                'You must provide a hub_api attribute with a '
                'HubAPI instance to be able to use the '
                'Backend Adapter.'
            )
        result = hub_api.get_payment_by_track_id(external_id)[0]
        return result


class HubPaymentCharge(models.Model):
    _inherit = 'hub.payment.charge'

    hub_payment_id = fields.Many2one(
        string="HUB Payment Charge",
        comodel_name='hub.payment',
        ondelete='cascade',
        index=True,
    )

    @api.model
    def create(self, vals):
        if 'hub_payment_id' in vals:
            hub_payment_id = vals['hub_payment_id']
            binding = self.env['hub.payment'].browse(hub_payment_id)
            vals['payment_id'] = binding.odoo_id.id
        binding = super(HubPaymentCharge, self).create(vals)
        return binding
