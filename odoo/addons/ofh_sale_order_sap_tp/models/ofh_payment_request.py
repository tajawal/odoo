# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class OfhPaymentRequest(models.Model):

    _inherit = 'ofh.payment.request'

    @api.multi
    def _get_tp_payment_request_dict(self) -> list:
        self.ensure_one()
        sap_zsel = abs(self.sap_zsel) - abs(self.sap_zdis)
        total_cost = self.supplier_total_amount
        lines = []
        for line in self.supplier_invoice_ids:
            line_dict = self.order_id.line_ids[0]._get_sale_line_dict()

            if self.request_type != 'charge':
                line_dict['is_refund'] = True

            line_dict['pnr'] = line.locator
            line_dict['ticket_number'] = line.ticket_number[-10:]
            line_dict['office_id'] = line.office_id
            line_dict['pax_name'] = line.passenger
            line_dict['billing_date'] = self.updated_at
            line_dict['custom1'] = self.updated_at
            line_dict["vat_tax_code"] = self.tax_code
            line_dict["item_currency"] = self.currency_id.name

            line_dict['cost_price'] = abs(line.currency_id.round(
                line.gds_net_amount))

            prorated_sale = \
                (line.gds_net_amount * sap_zsel) / total_cost

            line_dict['sale_price'] = abs(
                line.currency_id.round(prorated_sale))

            prorated_discount = \
                (line.gds_net_amount * self.sap_zdis) / total_cost
            line_dict['discount'] = abs(
                line.currency_id.round(prorated_discount))

            prorated_tax = \
                (line.gds_net_amount * self.sap_zvt1) / total_cost
            line_dict['output_vat'] = abs(line.currency_id.round(prorated_tax))

            line_dict['cost_currency'] = line.currency_id.name
            lines.append(line_dict)

        return lines
