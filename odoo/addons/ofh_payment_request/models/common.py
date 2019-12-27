# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


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
    product_id = fields.Char(
        string="Product Id",
        readonly=True,
    )
    group_id = fields.Char(
        string="Group Id",
        readonly=True,
        required=True,
    )
    hub_payment_ids = fields.One2many(
        comodel_name='hub.payment',
        inverse_name='hub_payment_request_id',
        string="Hub Payments",
    )
    hub_charge_ids = fields.One2many(
        comodel_name='hub.payment.charge',
        inverse_name='hub_payment_request_id',
        string="Hub Payment Charges",
    )

    _sql_constraints = [
        ('hub_payment_request_uniq', 'unique(backend_id, group_id, product_id)',
         _("A binding already exists with the same Hub ID.")),
    ]

    @job(default_channel='root.hub')
    @api.model
    def import_record(self, backend, external_id, force=False):
        """ Import a Hub record """
        with backend.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            self._run_refund_payment(track_id=external_id, backend=backend)
            return importer.run(external_id, force=force)

    @job(default_channel='root.hub')
    def _run_online_charge_payment_request(self, order_id, track_id, backend):
        if order_id:
            with backend.work_on('hub.sale.order') as work:
                importer = work.component(usage='record.importer')
                importer.run(track_id, force=False)
        else:
            with backend.work_on('hub.payment') as work:
                importer = work.component(usage='record.importer')
                importer.run(track_id, payment_type='initial', force=False)

    @job(default_channel='root.hub')
    def _run_unify_charge_payment_request(self, track_id, backend):
        with backend.work_on('hub.payment') as work:
            importer = work.component(usage='record.importer')
            importer.run(track_id, payment_type='amendment', force=False)

    @job(default_channel='root.hub')
    def _run_refund_payment(self, track_id, backend):
        with backend.work_on('hub.payment') as work:
            importer = work.component(usage='record.importer')
            importer.run(track_id, payment_type='refund', force=False)


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
        return hub_api.get_list_payment_request(
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


class HubPayment(models.Model):
    _inherit = 'hub.payment'

    hub_payment_request_id = fields.Many2one(
        string="HUB Payment",
        comodel_name='hub.payment.request',
        ondelete='cascade',
        index=True,
    )

    @api.model
    def create(self, vals):
        if 'hub_payment_request_id' in vals:
            hub_payment_request_id = vals['hub_payment_request_id']
            binding = self.env['hub.payment.request'].browse(
                hub_payment_request_id)
            vals['payment_request_id'] = binding.odoo_id.id

        binding = super(HubPayment, self).create(vals)
        return binding


class HubPaymentCharge(models.Model):
    _inherit = 'hub.payment.charge'

    hub_payment_request_id = fields.Many2one(
        string="HUB Payment Charge",
        comodel_name='hub.payment.request',
        required=False,
        ondelete='cascade',
        index=True,
    )

    @api.model
    def create(self, vals):
        if 'hub_payment_request_id' in vals:
            hub_payment_request_id = vals['hub_payment_request_id']
            binding = self.env['hub.payment.request'].browse(
                hub_payment_request_id)
            vals['payment_request_id'] = binding.odoo_id.id
        binding = super(HubPaymentCharge, self).create(vals)
        return binding
