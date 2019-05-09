# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import json


class OfhPaymentSap(models.Model):
    _name = 'ofh.payment.sap'
    _description = 'Ofh Payment SAP'

    sap_payment_detail = fields.Text(
        string="SAP Payment Details",
        readonly=True,
    )
    payment_detail = fields.Text(
        string="Payment Details",
        readonly=True,
    )
    send_date = fields.Datetime(
        string="Send to Sap At",
        required=True,
        readonly=True,
        index=True,
    )
    sap_sale_order_id = fields.Many2one(
        comodel_name='ofh.sale.order.sap',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    provider = fields.Char(
        string="Provider",
        readonly=True,
        compute="_compute_payment_detail"
    )
    # SAP Payment Fields
    system = fields.Char(
        string="System",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    transaction = fields.Char(
        string="Transaction",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    company_code = fields.Char(
        string="Company Code",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    document_date = fields.Char(
        string="DocumentDate",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    header_text = fields.Char(
        string="HeaderText",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    reference = fields.Char(
        string="Reference",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    currency = fields.Char(
        string="Currency",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    account1 = fields.Char(
        string="Account1",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    account2 = fields.Char(
        string="Account2",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    amount1 = fields.Char(
        string="Amount1",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    amount2 = fields.Char(
        string="Amount2",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    bank_charge = fields.Char(
        string="Bank Charge",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    splgl = fields.Char(
        string="SPLGL",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    sales_office = fields.Char(
        string="Sales Office",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    material = fields.Char(
        string="Material",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    reference_key1 = fields.Char(
        string="Reference Key 1",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    reference_key2 = fields.Char(
        string="Reference Key 2",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    reference_key3 = fields.Char(
        string="Reference Key 3",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    assignment = fields.Char(
        string="Assignment",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )
    line_item_text = fields.Char(
        string="Line Item Text",
        readonly=True,
        compute="_compute_sap_payment_detail"
    )

    @api.multi
    @api.depends('sap_payment_detail')
    def _compute_sap_payment_detail(self):
        for rec in self:
            payment_detail = json.loads(rec.sap_payment_detail)

            rec.system = payment_detail.get('system')
            rec.transaction = payment_detail.get('transaction')
            rec.company_code = payment_detail.get('company_code')
            rec.document_date = payment_detail.get('document_date')
            rec.header_text = payment_detail.get('header_text')
            rec.reference = payment_detail.get('reference')
            rec.currency = payment_detail.get('currency')
            rec.account1 = payment_detail.get('account1')
            rec.account2 = payment_detail.get('account2')
            rec.amount1 = payment_detail.get('amount1')
            rec.amount2 = payment_detail.get('amount2')
            rec.bank_charge = payment_detail.get('bank_charge')
            rec.splgl = payment_detail.get('splgl')
            rec.sales_office = payment_detail.get('sales_office')
            rec.material = payment_detail.get('material')
            rec.reference_key1 = payment_detail.get('reference_key1')
            rec.reference_key2 = payment_detail.get('reference_key2')
            rec.reference_key3 = payment_detail.get('reference_key3')
            rec.assignment = payment_detail.get('assignment')
            rec.line_item_text = payment_detail.get('line_item_text')

    @api.multi
    @api.depends('payment_detail')
    def _compute_payment_detail(self):
        for rec in self:
            payment_detail = json.loads(rec.payment_detail)

            rec.provider = payment_detail.get('provider')
