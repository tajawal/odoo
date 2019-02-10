# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime


class OfhPaymentRequestSapLine(models.Model):

    _name = 'ofh.payment.request.sap.line'
    _description = 'Ofh Payment Request Line'

    payment_request_id = fields.Many2one(
        string="Payment Request",
        comodel_name='ofh.payment.request',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    supplier_invoice_line = fields.Many2one(
        string="Invoice line",
        comodel_name='ofh.supplier.invoice.line',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    currency_id = fields.Many2one(
        string="Sale Currency",
        comodel_name='res.currency',
        related='payment_request_id.currency_id',
        required=True,
        readonly=True,
        store=False,
    )
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        related="supplier_invoice_line.currency_id",
        required=True,
        readonly=True,
        store=False,
    )
    sap_zsel = fields.Monetary(
        string="ZSEL",
        currency_field='currency_id',
        compute='_compute_sap_conditions',
        readonly=True,
        store=False,
    )
    sap_zvd1 = fields.Monetary(
        string="ZVD1",
        currency_field='supplier_currency_id',
        compute='_compute_sap_conditions',
        readonly=True,
        store=False,
    )
    sap_zdis = fields.Monetary(
        string="ZDIS",
        currency_field='currency_id',
        compute='_compute_sap_conditions',
        readonly=True,
        store=False,
    )
    sap_zvt1 = fields.Monetary(
        string="ZVT1",
        currency_field='currency_id',
        compute='_compute_sap_conditions',
        readonly=True,
        store=False,
    )
    sap_tax_code = fields.Selection(
        string="VAT Tax Code",
        currency_field='currency_id',
        related="payment_request_id.tax_code",
        readonly=True,
        store=False,
    )
    sap_pnr = fields.Char(
        string="PNR",
        related="supplier_invoice_line.locator",
        readonly=True,
        store=False,
    )
    sap_ticket_number = fields.Char(
        string="Ticket Number",
        related="supplier_invoice_line.ticket_number",
        readonly=True,
        store=False,
    )
    sap_billing_date = fields.Datetime(
        string="Billing Date",
        related="payment_request_id.created_at",
        readonly=True,
        store=False,
    )
    sap_pax_name = fields.Char(
        string="Pax Name",
        related="supplier_invoice_line.passenger",
        readonly=True,
        store=False,
    )
    sap_owner_id = fields.Char(
        string="OWNERID",
        related="supplier_invoice_line.office_id",
        readonly=True,
        store=False,
    )

    @api.multi
    @api.depends(
        'payment_request_id.sap_zsel', 'supplier_currency_id',
        'payment_request_id.sap_zdis', 'payment_request_id.sap_zvt1',
        'payment_request_id.supplier_total_amount',
        'payment_request_id.supplier_shamel_total_amount',
        'supplier_invoice_line.gds_net_amount', 'supplier_invoice_line.total')
    def _compute_sap_conditions(self):
        for rec in self:
            rec.sap_zsel = rec.sap_zvd1 = rec.sap_dis = rec.sap_zvt1 = 0

            if rec.supplier_invoice_line.invoice_type == 'gds':
                rec.sap_zvd1 = rec.supplier_invoice_line.gds_net_amount
            else:
                rec.sap_zvd1 = rec.supplier_invoice_line.total

            if rec.supplier_currency_id == self.env.ref('base.KWD'):
                supplier_cost = \
                    rec.payment_request_id.supplier_shamel_total_amount
            else:
                supplier_cost = rec.payment_request_id.supplier_total_amount

            rec.sap_zsel = \
                rec.payment_request_id.sap_zsel * rec.sap_zvd1 / supplier_cost

            rec.sap_zdis = \
                rec.payment_request_id.sap_zdis * rec.sap_zvd1 / supplier_cost

            rec.sap_zvt1 = \
                rec.payment_request_id.sap_zvt1 * rec.sap_zvd1 / supplier_cost

    @api.multi
    def to_dict(self):
        self.ensure_one()
        booking_date = datetime.strftime(
            fields.Datetime.from_string(
                self.sap_billing_date), '%Y%m%d')
        return {
            "item_general": {
                "BillingDate": booking_date,
                "VATTaxCode": self.sap_tax_code.upper(),
                "PNR": self.sap_pnr,
                "TicketNumber": self.sap_ticket_number,
                "Pax_Name": self.sap_pax_name,
            },
            "item_charecteristic": {
                "Z_PAXNAME": self.sap_pax_name,
                "Z_OWNEROID": self.sap_owner_id,
            },
            "item_condition": {
                'ZVD1': self.sap_zvd1,
                'ZVD1_CURRENCY': self.supplier_currency_id.name if
                self.supplier_currency_id else self.currency_id.name,
                'ZSEL': self.sap_zsel,
                'ZSEL_CURRENCY': self.currency_id.name,
                'ZVT1': self.sap_zvt1,
                'ZVT1_CURRENCY': self.currency_id.name,
                'ZDIS': self.sap_zdis,
                'ZDIS_CURRENCY': self.currency_id.name,
            }
        }
