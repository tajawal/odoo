# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from odoo import api, fields, models, _
from odoo.exceptions import MissingError


class OfhSaleOrderLine(models.Model):
    _inherit = 'ofh.sale.order.line'

    sap_line_ids = fields.One2many(
        string="SAP Lines",
        comodel_name="ofh.sale.order.line.sap",
        inverse_name='sale_order_line_id',
        readonly=True,
    )

    @api.multi
    def _get_sale_line_dict(self) -> dict:
        return {
            "entity": self.order_id.entity,
            "order_number": self.order_id.name,
            "item_type": self.line_type,
            "order_status": self.state,
            "office_id": self.ticketing_office_id,
            "billing_date": self.created_at,
            "vat_tax_code": self.tax_code,
            "airline_code": self.supplier_name,
            "segment_count": self.segment_count,
            "custom1": self.order_id.paid_at,
            "payment_status": self.order_id.payment_status,
            "booking_method": self.order_id.booking_method,
            "vendor_name": self.vendor_name,
            "supplier_name": self.supplier_name,
            "item_currency": self.currency_id.name,
            "is_domestic_ksa": self.is_domestic_ksa,
            "ahs_group_name": self.ahs_group_name,
            "number_of_pax": self.passengers_count,
            "pax_name": self.traveller,
            "booking_class": self.booking_class,
            "last_leg_flying_date": self.last_leg_flying_date,
            "destination_city": self.destination_city,
            "departure_date": self.departure_date,
            "route": self.route,
            "segments": json.loads(self.segments),
            "last_leg": self.destination_city,
            "sale_price": abs(round(self.total_amount, 2)),
            "output_vat": abs(round(self.tax_amount, 2)),
            "discount": abs(round(self.discount_amount, 2)),
        }

    @api.multi
    def to_dict(self) -> list:
        """Return dict of Sap Sale Order Line
        Returns:
            [dict] -- Sap Sale Order Line dictionary
        """
        self.ensure_one()

        if self.matching_status in ('unmatched', 'not_applicable'):
            sale_line_dict = self._get_sale_line_dict()
            sale_line_dict['pnr'] = \
                self.vendor_confirmation_number if self.vendor_name == 'amd' \
                else self.supplier_confirmation_number
            sale_line_dict['cost_price'] = abs(round(
                self.supplier_cost_amount, 2))
            sale_line_dict['cost_currency'] = self.supplier_currency_id.name
            sale_line_dict['ticket_number'] = self.line_reference
            return [sale_line_dict]

        invoice_type = self.invoice_line_ids.mapped('invoice_type')[0]
        compute_function = f'_get_{invoice_type}_sale_line_dict'
        if hasattr(self, compute_function):
            return getattr(self, compute_function)()
        else:
            raise MissingError(_("Method not implemented."))
