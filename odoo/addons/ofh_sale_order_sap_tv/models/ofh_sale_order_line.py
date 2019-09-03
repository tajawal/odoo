# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_is_zero


class OfhSaleOrderLine(models.Model):

    _inherit = 'ofh.sale.order.line'

    @api.multi
    def _get_tv_sale_line_dict(self):
        self.ensure_one()

        sale_line_dict = self._get_sale_line_dict()

        # Hotel may be paid later and at the time of the payment is where
        # we will send the whole order to SAP.
        sale_line_dict['billing_date'] = self.order_id.paid_at
        sale_line_dict['pnr'] = \
            f"{self.vendor_confirmation_number}.{self.line_reference}"
        sale_line_dict['supplier_ref'] = \
            self.supplier_confirmation_number

        sale_line_dict['cost_currency'] = self.supplier_currency_id.name

        if self.invoice_line_ids:
            sale_line_dict['cost_price'] = sum([
                l.total for l in self.invoice_line_ids])
            sale_line_dict['cost_currency'] = \
                self.invoice_line_ids[0].currency_id.name

        # Not Applicable matching status cost should be 0.
        elif self.matching_status == 'unmatched':
            sale_line_dict['cost_price'] = abs(round(
                self.supplier_cost_amount, 2))
        else:
            sale_line_dict['cost_price'] = 0.00

        # Normal Case: the line item sale amount is not 0.
        if not float_is_zero(
                self.total_amount,
                precision_rounding=self.currency_id.rounding):

            return [sale_line_dict]

        # if the number of order lines is 1 (i.e only the current line)
        # and the amount of the line is zero and the order is paid then
        # take the amount from the sale order and return one line.
        # else return empty line.
        if len(self.order_id.line_ids) == 1:
            if self.order_id.payment_ids:
                sale_line_dict['sale_price'] = \
                    abs(round(self.order_id.total_amount, 2))
                sale_line_dict['total_discount'] = \
                    abs(round(self.order_id.total_discount, 2))
                sale_line_dict['output_vat'] = \
                    abs(round(self.order_id.total_tax, 2))
                return [sale_line_dict]
            else:
                return []

        return []
