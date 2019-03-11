# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhSaleOrderLine(models.Model):

    _name = 'ofh.sale.order.line'
    _description = 'Ofh Sale Order Line'

    name = fields.Char(
        string="Product",
        required=True,
        readonly=True,
    )
    sequence = fields.Char(
        string="Sequence",
        readonly=True,
    )
    order_id = fields.Many2one(
        string="Order",
        required=True,
        readonly=True,
        index=True,
        comodel_name='ofh.sale.order',
        ondelete='cascade',
    )
    created_at = fields.Datetime(
        string="Created At",
        required=True,
        readonly=True,
        index=True,
    )
    updated_at = fields.Datetime(
        string="Updated At",
        required=True,
        readonly=True,
        index=True,
    )
    line_type = fields.Char(
        string="type",
        required=True,
        readonly=True,
    )
    line_category = fields.Char(
        string="Category",
        required=True,
        readonly=True,
    )
    state = fields.Char(
        string="Status",
        required=True,
        readonly=True,
    )
    is_domestic_ksa = fields.Boolean(
        string="Is Domestic KSA",
        readonly=True,
        default=False,
        help="True if the order is a domestic KSA, else False",
    )
    # Vendor data
    vendor_confirmation_number = fields.Char(
        string="Vendor Confirmation Number",
        required=True,
        readonly=True,
    )
    vendor_name = fields.Char(
        string="Vendor Name",
        required=True,
        readonly=True,
        index=True,
    )
    vendor_currency_id = fields.Many2one(
        string="Vendor Currency",
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    vendor_cost_amount = fields.Monetary(
        string="Vendor Cost",
        currency_field='vendor_currency_id',
        readonly=True,
    )

    # Supplier data
    supplier_confirmation_number = fields.Char(
        string="Supplier Confirmation Number",
        required=True,
        readonly=True,
    )
    supplier_name = fields.Char(
        string="Supplier Name",
        required=True,
        readonly=True,
        index=True,
    )
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    supplier_cost_amount = fields.Monetary(
        string="Supplier Cost",
        currency_field='supplier_currency_id',
        readonly=True,
    )
    exchange_rate = fields.Float(
        readonly=True,
    )

    # traveller details
    traveller = fields.Char(
        readonly=True,
    )
    traveller_type = fields.Char(
        string="Traveller type",
        readonly=True,
    )
    office_id = fields.Char(
        string="Office ID",
        readonly=True,
        index=True,
    )
    ticketing_office_id = fields.Char(
        string="Ticketing Office ID",
        readonly=True,
        index=True,
    )
    tour_code_office_id = fields.Char(
        string="Tour Code",
        readonly=True,
        index=True,
    )
    ticket_number = fields.Char(
        string="Ticket",
        readonly=True,
        index=True,
    )

    # Segment details
    contract = fields.Char(
        string="Contract",
        readonly=True,
    )
    hotel_id = fields.Char(
        string="Hotel ID",
        readonly=True,
        index=True,
    )
    hotel_city = fields.Char(
        string="Hotel City",
        readonly=True,
        index=True,
    )
    hotel_country = fields.Char(
        string="Hotel Country",
        readonly=True,
        index=True,
    )

    # Sale price data
    tax_code = fields.Selection(
        string="Tax Code",
        selection=[('ss', 'SS'), ('sz', 'SZ')],
        readonly=True,
        default='sz',
        required=True,
        # TODO update the help for the other cases.
        help="SS if the order is domestick KSA and Almsofer, else SZ",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name='res.currency',
        required=True,
        readonly=True,
    )
    sale_price = fields.Monetary(
        string="Sale Price",
        currency_field='currency_id',
        readonly=True,
        help="Sale price = vendor cost + service fee.",
    )
    service_fee_amount = fields.Monetary(
        string="Service Fee",
        currency_field='currency_id',
        readonly=True,
        help="Prorated service fee",
    )
    discount_amount = fields.Monetary(
        string="Discount",
        currency_field='currency_id',
        readonly=True,
        help="Prorated discount amount",
    )
    tax_amount = fields.Monetary(
        string="Tax",
        currency_field='currency_id',
        readonly=True,
        help="Prorated tax amount",
    )
    subtotal_amount = fields.Monetary(
        string="Subtotal",
        currency_field='currency_id',
        readonly=True,
        help="Sale Price amount - discount amount"
    )
    total_amount = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        readonly=True,
        help="Total Amount = Sale Price amount + discount"
    )
    hub_bind_ids = fields.One2many(
        comodel_name='hub.sale.order.line',
        inverse_name='odoo_id',
        string="Hub Bindings",
        readonly=True,
    )
