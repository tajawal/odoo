# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from odoo import api, fields, models


class OfhSaleOrderLine(models.Model):
    _inherit = 'ofh.sale.order.line'

    sap_line_ids = fields.One2many(
        string="SAP Lines",
        comodel_name="ofh.sale.order.line.sap",
        inverse_name='sale_order_line_id',
        readonly=True,
    )

    @api.multi
    def to_dict(self) -> dict:
        """Return dict of Sap Sale Order Line
        Returns:
            [dict] -- Sap Sale Order Line dictionary
        """
        self.ensure_one()
        sale_line_dict = {
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
            "sale_price": self.total_amount,
            "output_vat": self.tax_amount,
            "discount": self.discount_amount,
        }

        if self.matching_status == 'not_applicable':
            pnr = self.vendor_confirmation_number if self.vendor_name == 'amd'\
                else self.supplier_confirmation_number
            sale_line_dict['pnr'] = pnr
            sale_line_dict['cost_price'] = self.supplier_cost_amount
            sale_line_dict['cost_currency'] = self.supplier_currency_id.name
            sale_line_dict['ticket_number'] = self.line_reference
            return [sale_line_dict]

        lines = []
        for line in self.invoice_line_ids:
            line_dict = sale_line_dict
            cost_amount = line.total
            if line.invoice_type == 'gds':
                cost_amount = line.gds_net_amount
            line_dict.update({
                'pnr': line.locator,
                'cost_price': cost_amount,
                'cost_currency': line.currency_id.name,
                'ticket_number': line.ticket_number,
            })
            lines.append(line_dict)

        return lines
