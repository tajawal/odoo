# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import json


class OfhSaleOrder(models.Model):
    _inherit = 'ofh.sale.order'

    sale_order_ids = fields.One2many(
        string="Sap Sale Order Ids",
        comodel_name="ofh.sale.order.sap",
        inverse_name='sale_order_id',
        readonly=True,
    )

    @api.multi
    def send_orders_to_sap(self):
        for rec in self:
            rec.with_delay().send_order_to_sap()

    @api.multi
    def send_order_to_sap(self):
        self.ensure_one()
        values = {
            'send_date': fields.Datetime.now(),
            'update': 'Dummy for now',  # TODO: Update
            'sale_order_id': self.id,
            'sap_status': 'in_sap',  # TODO: Update
            'integration_status': 'sale_sent',  # TODO: Update
            'order_detail': json.dumps(self.to_dict()),
        }

        self.env['ofh.sale.order.sap'].create(values)

    @api.multi
    def to_dict(self) -> dict:
        """Return dict of Sap Sale Order
        Returns:
            [dict] -- Sap Sale Order dictionary
        """
        self.ensure_one()
        return {
            'name': self.name,
            'track_id': self.track_id,
            'order_type': self.order_type,
            'entity': self.entity,
            'order_status': self.order_status,
            'point_of_sale': self.point_of_sale,
            'payment_status': self.payment_status,
            'paid_at': self.paid_at,
            'store_id': self.store_id,
            'group_id': self.group_id,
            'currency_id': self.currency_id,
            'supplier_currency_id': self.supplier_currency_id,
            'total_supplier_cost': self.total_supplier_cost,
            'vendor_reference': self.vendor_reference,
            'supplier_reference': self.supplier_reference,
        }
