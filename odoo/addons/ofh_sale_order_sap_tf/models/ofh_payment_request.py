# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class OfhPaymentRequest(models.Model):

    _inherit = 'ofh.payment.request'

    @api.multi
    def _get_tf_payment_request_dict(self) -> list:
        self.ensure_one()
        sap_zsel = abs(self.sap_zsel) - abs(self.sap_zdis)
        line_dict = self.order_id.line_ids[0]._get_sale_line_dict()

        line = self.supplier_invoice_ids[0]

        if self.request_type != 'charge':
            line_dict['is_refund'] = True

        line_dict['pnr'] = line.locator
        line_dict['billing_date'] = self.updated_at
        line_dict["vat_tax_code"] = self.tax_code
        line_dict["item_currency"] = self.currency_id.name

        line_dict['cost_price'] = abs(line.currency_id.round(self.sap_zvd1))

        line_dict['sale_price'] = abs(line.currency_id.round(sap_zsel))

        line_dict['discount'] = abs(line.currency_id.round(self.sap_zdis))

        line_dict['output_vat'] = abs(line.currency_id.round(self.sap_zvt1))

        line_dict['cost_currency'] = line.currency_id.name

        return [line_dict]
