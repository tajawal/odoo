# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import json


class OfhSaleOrderSap(models.Model):
    _name = 'ofh.sale.order.sap'
    _description = 'Ofh Sale Order SAP'

    order_detail = fields.Text(
        string="Order Details",
        readonly=True,
    )
    sap_header_detail = fields.Text(
        string="SAP Header Details",
        readonly=True,
    )
    send_date = fields.Datetime(
        string="Send to Sap At",
        required=True,
        readonly=True,
        index=True,
    )
    sap_status = fields.Selection(
        string='SAP status',
        selection=[
            ('pending', 'Pending'),
            ('not_in_sap', "Not In SAP"),
            ('in_sap', "Sale & Payment In SAP"),
            ('payment_in_sap', "Payment in SAP"),
            ('sale_in_sap', 'Sale in SAP')],
        default='pending',
        required=True,
        index=True,
        readonly=True,
        track_visibility='always',
    )
    integration_status = fields.Selection(
        string="Integration Status",
        selection=[
            ('not_sent', 'Not sent'),
            ('payment_sent', 'Payment sent'),
            ('sale_sent', 'Sale sent'),
            ('sale_payment_sent', 'Sale & Payment sent')],
        readonly=True,
        required=True,
        default='not_sent',
        index=True,
        track_visibility='always',
    )
    update = fields.Char(
        string="Update Reason if any",
        readonly=True,
    )
    sale_order_id = fields.Many2one(
        string="Sale Order",
        comodel_name='ofh.sale.order',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    sap_sale_order_line_ids = fields.One2many(
        string="Sap Sale Order Line Ids",
        comodel_name="ofh.sale.order.line.sap",
        inverse_name='sap_sale_order_id',
        readonly=True,
    )
    sap_payment_ids = fields.One2many(
        string="Sap Payment Ids",
        comodel_name="ofh.payment.sap",
        inverse_name='sap_sale_order_id',
        readonly=True,
    )
    # SAP Header Fields
    system_id = fields.Char(
        string="System ID",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    sales_type = fields.Char(
        string="Sales Type",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    collection_mode = fields.Char(
        string="Collection Mode",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    booking_entity = fields.Char(
        string="Booking Entity",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    booking_number = fields.Char(
        string="Booking Number",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    sales_office = fields.Char(
        string="Sales Office",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    channel = fields.Char(
        string="Channel",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    customer = fields.Char(
        string="Customer",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    file_id = fields.Char(
        string="File ID",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    booking_date = fields.Char(
        string="Booking Date",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    fe_indicator = fields.Char(
        string="FE Indicator",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    invoice_currency = fields.Char(
        string="Invoice Currency",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    tapro_invoice_number = fields.Char(
        string="Tapro Invoice Number",
        readonly=True,
        compute="_compute_sap_header_detail"
    )
    # Sale Order Header Fields
    name = fields.Char(
        string="Order ID",
        readonly=True,
        compute="_compute_order_detail"
    )
    track_id = fields.Char(
        string="Track ID",
        readonly=True,
        compute="_compute_order_detail"
    )
    order_type = fields.Selection(
        string="Order Type",
        selection=[
            ('hotel', 'Hotel'),
            ('flight', 'Flight'),
            ('package', 'Package')],
        readonly=True,
        compute="_compute_order_detail"
    )
    entity = fields.Selection(
        selection=[
            ('almosafer', 'Almosafer'),
            ('tajawal', 'Tajawal')],
        readonly=True,
        compute="_compute_order_detail"
    )
    order_status = fields.Char(
        string="Order Status",
        readonly=True,
        compute="_compute_order_detail"
    )
    point_of_sale = fields.Char(
        string="Point Of Sale",
        readonly=True,
        compute="_compute_order_detail"
    )
    payment_status = fields.Char(
        string="payment Status",
        readonly=True,
        compute="_compute_order_detail"
    )
    paid_at = fields.Datetime(
        string="Paid At",
        readonly=True,
        compute="_compute_order_detail"
    )
    store_id = fields.Char(
        string="Store ID",
        readonly=True,
        compute="_compute_order_detail"
    )
    group_id = fields.Char(
        string="Group ID",
        readonly=True,
        compute="_compute_order_detail"
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name='res.currency',
        required=True,
        readonly=True,
        index=True,
        compute="_compute_order_detail"
    )
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        readonly=True,
        compute="_compute_order_detail"
    )
    total_supplier_cost = fields.Monetary(
        string="Total Supplier Cost",
        currency_field='supplier_currency_id',
        readonly=True
    )
    vendor_reference = fields.Char(
        string='Vendor Reference',
        readonly=True,
        compute="_compute_order_detail"
    )
    supplier_reference = fields.Char(
        string="Supplier Reference",
        readonly=True,
        compute="_compute_order_detail"
    )

    @api.multi
    @api.depends('order_detail')
    def _compute_order_detail(self):
        for rec in self:
            order_detail = json.loads(rec.order_detail)

            rec.name = order_detail.get('name')
            rec.track_id = order_detail.get('track_id')
            rec.order_type = order_detail.get('order_type')
            rec.entity = order_detail.get('entity')
            rec.order_status = order_detail.get('order_status')
            rec.point_of_sale = order_detail.get('point_of_sale')
            rec.payment_status = order_detail.get('payment_status')
            rec.paid_at = order_detail.get('paid_at')
            rec.store_id = order_detail.get('store_id')
            rec.group_id = order_detail.get('group_id')
            rec.currency_id = order_detail.get('currency_id')
            rec.supplier_currency_id = order_detail.get('supplier_currency_id')
            rec.total_supplier_cost = order_detail.get('total_supplier_cost')
            rec.vendor_reference = order_detail.get('vendor_reference')
            rec.supplier_reference = order_detail.get('supplier_reference')

    @api.multi
    @api.depends('sap_header_detail')
    def _compute_sap_header_detail(self):
        for rec in self:
            sap_header_detail = json.loads(rec.sap_header_detail)

            rec.system_id = sap_header_detail.get("system_id")
            rec.sales_type = sap_header_detail.get("sales_type")
            rec.collection_mode = sap_header_detail.get("collection_mode")
            rec.booking_entity = sap_header_detail.get("booking_entity")
            rec.booking_number = sap_header_detail.get("booking_number")
            rec.sales_office = sap_header_detail.get("sales_office")
            rec.channel = sap_header_detail.get("channel")
            rec.customer = sap_header_detail.get("customer")
            rec.file_id = sap_header_detail.get("file_id")
            rec.booking_date = sap_header_detail.get("booking_date")
            rec.fe_indicator = sap_header_detail.get("fe_indicator")
            rec.invoice_currency = sap_header_detail.get("invoice_currency")
            rec.tapro_invoice_number = sap_header_detail.get("tapro_invoice_number")
