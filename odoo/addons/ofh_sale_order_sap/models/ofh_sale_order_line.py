# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhSaleOrderLine(models.Model):

    _inherit = 'ofh.sale.order.line'

    sale_order_line_ids = fields.One2many(
        string="Sap Sale Order Line Ids",
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
        return {
            'name': self.name,
            'sequence': self.sequence,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'line_type': self.line_type,
            'line_category': self.line_category,
            'state': self.state,
            'is_domestic_ksa': self.is_domestic_ksa,
            'vendor_confirmation_number': self.vendor_confirmation_number,
            'vendor_name': self.vendor_name,
            'vendor_currency_id': self.vendor_currency_id,
            'vendor_cost_amount': self.vendor_cost_amount,
            'vendor_base_fare_amount': self.vendor_base_fare_amount,
            'vendor_input_tax_amount': self.vendor_input_tax_amount,
            'supplier_confirmation_number': self.supplier_confirmation_number,
            'supplier_name': self.supplier_name,
            'supplier_currency_id': self.supplier_currency_id,
            'supplier_cost_amount': self.supplier_cost_amount,
            'supplier_base_fare_amount': self.supplier_base_fare_amount,
            'supplier_input_tax_amount': self.supplier_input_tax_amount,
            'exchange_rate': self.exchange_rate,
            'traveller': self.traveller,
            'traveller_type': self.traveller_type,
            'office_id': self.office_id,
            'ticketing_office_id': self.ticketing_office_id,
            'tour_code_office_id': self.tour_code_office_id,
            'line_reference': self.line_reference,
            'tickets': self.tickets,
            'passengers_count': self.passengers_count,
            'last_leg_flying_date': self.last_leg_flying_date,
            'segment_count': self.segment_count,
            'booking_class': self.booking_class,
            'destination_city': self.destination_city,
            'departure_date': self.departure_date,
            'route': self.route,
            'origin_city': self.origin_city,
            'ahs_group_name': self.ahs_group_name,
            'contract': self.contract,
            'hotel_id': self.hotel_id,
            'hotel_city': self.hotel_city,
            'hotel_country': self.hotel_country,
            'hotel_supplier_id': self.hotel_supplier_id,
            'tax_code': self.tax_code,
            'currency_id': self.currency_id,
            'sale_price': self.sale_price,
            'service_fee_amount': self.service_fee_amount,
            'discount_amount': self.discount_amount,
            'tax_amount': self.tax_amount,
            'subtotal_amount': self.subtotal_amount,
            'total_amount': self.total_amount,
        }
