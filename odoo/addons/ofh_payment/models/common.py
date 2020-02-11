# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


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

    @job(default_channel='root.hub')
    @api.model
    def import_record(self, backend, external_id, payment_type, force=False):
        """ Import a Hub record """
        with backend.work_on('hub.payment') as work:
            importer = work.component(usage='record.importer')
            importer.run(external_id, payment_type=payment_type, force=force)


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
        payments = hub_api.get_payment_by_track_id(external_id, attributes.get('payment_type'))
        if payments:
            return payments[0]
        return []


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
