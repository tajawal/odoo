# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
from odoo import api, fields, models


class OfhPayment(models.Model):
    _inherit = 'ofh.payment'

    sap_payment_ids = fields.One2many(
        string="SAP Payments",
        comodel_name="ofh.payment.sap",
        inverse_name='payment_id',
        readonly=True,
    )

    @api.multi
    def _prepare_payment_values(self, visualize=False):
        self.ensure_one()
        dt = fields.Datetime.now()
        backend = self.env['sap.backend'].search([], limit=1)
        values = {
            'send_date': dt,
            'backend_id': backend.id,
            'payment_detail': json.dumps(self.to_dict()),
            'payment_id': self.id
        }
        if visualize:
            values['state'] = 'visualize'

        return values

    @api.multi
    def send_payment_to_sap(self):
        """Create and Send SAP Sale Order Record."""
        self.ensure_one()

        values = self._prepare_payment_values()
        return self.env['ofh.payment.sap'].create(values)

    @api.multi
    def force_send_payment_to_sap(self):
        self.ensure_one()

        values = self._prepare_payment_values()

        return self.env['ofh.payment.sap'].with_context(
            force_send=True).create(values)

    @api.multi
    def visualize_sap_payment(self):
        self.ensure_one()

        values = self._prepare_payment_values(visualize=True)

        return self.env['ofh.payment.sap'].create(values)

    @api.multi
    def to_dict(self) -> dict:
        """Return dict of Sap Sale Order
        Returns:
            [dict] -- Sap Sale Order dictionary
        """
        self.ensure_one()
        validating_carrier = self.order_id.line_ids[0].validating_carrier
        return {
            "id": self.order_id.hub_bind_ids.external_id,
            "name": self.order_id.name,
            "order_type": self.order_id.order_type,
            "order_status": self.order_id.order_status,
            "validating_carrier": validating_carrier,
            "order_owner": self.order_id.order_owner,
            "entity": self.order_id.entity,
            "ahs_group_name": self.order_id.ahs_group_name,
            "country_code": self.order_id.country_code,
            "payment_provider": self.provider,
            "payment_source": self.source,
            "payment_method": self.payment_method,
            "payment_mode": self.payment_mode,
            "payment_status": self.payment_status,
            "reference_id": self.reference_id,
            "currency": self.currency_id.name,
            "amount": self.total_amount,
            "document_date": self.created_at,
            "mid": self.mid,
            "bank_name": self.bank_name,
            "card_type": self.card_type,
            "card_bin": self.card_bin,
            "card_owner": self.card_name,
            "card_last_four": self.last_four,
            "auth_code": self.auth_code,
            "is_installment": self.is_installment,
            "is_3d_secure": self.is_3d_secure,
        }
