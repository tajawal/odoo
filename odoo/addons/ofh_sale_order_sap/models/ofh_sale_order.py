# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class OfhSaleOrder(models.Model):
    _inherit = 'ofh.sale.order'

    sap_order_ids = fields.One2many(
        string="SAP Orders",
        comodel_name="ofh.sale.order.sap",
        inverse_name='sale_order_id',
        readonly=True,
    )

    @api.multi
    def action_send_order_to_sap(self):
        for rec in self:
            rec.with_delay().send_order_to_sap()

    @api.multi
    def _prepare_sap_lines_values(self):
        self.ensure_one()
        lines = []
        dt = fields.Datetime.now()
        backend = self.env['sap.backend'].search([], limit=1)
        for line in self.line_ids:
            inv_lines = line.to_dict()
            for inv_line in inv_lines:
                lines.append((0, 0, {
                    'send_date': dt,
                    'backend_id': backend.id,
                    'sale_order_line_id': line.id,
                    'line_detail': json.dumps(inv_line)}))
        return lines

    @api.multi
    def _prepare_payment_values(self, visualize=False):
        self.ensure_one()
        payments = []
        dt = fields.Datetime.now()
        backend = self.env['sap.backend'].search([], limit=1)
        for payment in self.payment_ids:
            values = {
                'send_date': dt,
                'backend_id': backend.id,
                'payment_detail': json.dumps(payment.to_dict()),
                'payment_id': payment.id
            }
            if visualize:
                values['state'] = 'visualize'
            payments.append((0, 0, values))
        return payments

    @api.multi
    def _prepare_sap_order_values(self, visualize=False):
        backend = self.env['sap.backend'].search([], limit=1)
        values = {
            'send_date': fields.Datetime.now(),
            'sale_order_id': self.id,
            'backend_id': backend.id,
            'order_detail': json.dumps(self.to_dict()),
            'sap_line_ids': self._prepare_sap_lines_values(),
            'sap_payment_ids': self._prepare_payment_values(visualize)
        }
        if visualize:
            values['state'] = 'visualize'

        return values

    @api.multi
    @job
    def send_order_to_sap(self):
        """Create and Send SAP Sale Order Record."""
        self.ensure_one()

        values = self._prepare_sap_order_values()
        return self.env['ofh.sale.order.sap'].create(values)

    @api.multi
    def force_send_order_to_sap(self):
        self.ensure_one()

        values = self._prepare_sap_order_values()
        # When force sending, for send only the sale part.
        values.pop('sap_payment_ids')

        return self.env['ofh.sale.order.sap'].with_context(
            force_send=True).create(values)

    @api.multi
    def visualize_sap_order(self):
        self.ensure_one()

        values = self._prepare_sap_order_values(visualize=True)

        return self.env['ofh.sale.order.sap'].create(values)

    @api.multi
    def to_dict(self) -> dict:
        """Return dict of Sap Sale Order
        Returns:
            [dict] -- Sap Sale Order dictionary
        """
        self.ensure_one()
        return {
            "name": self.name,
            "id": self.hub_bind_ids.external_id,
            "order_type": self.order_type,
            "created_at": self.created_at,
            "currency": self.currency_id.name,
            "ahs_group_name": self.ahs_group_name,
            "entity": self.entity,
            "country_code": self.country_code,
            "is_egypt": self.is_egypt,
            "payment_provider": self.payment_ids[0].provider,
        }
