# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhSaleOrderLine(models.Model):

    _name = 'ofh.sale.order.line'
    _description = 'Ofh Sale Order Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'line_reference'

    @api.model
    def _get_order_status_selection(self):
        return self.env['ofh.sale.order']._get_order_status_selection()

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
        track_visibility='onchange',
    )
    updated_at = fields.Datetime(
        string="Updated At",
        required=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
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
    state = fields.Selection(
        string="Status",
        selection=_get_order_status_selection,
        required=True,
        readonly=True,
        track_visibility='onchange',
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
        track_visibility='onchange',
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
        track_visibility='onchange',
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
        track_visibility='onchange',
    )
    tour_code_office_id = fields.Char(
        string="Tour Code",
        readonly=True,
        index=True,
    )
    line_reference = fields.Char(
        string="Ticket/Segment",
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    tickets = fields.Char(
        string="Tickets",
        compute='_compute_tickets',
        readonly=True,
        store=False,
    )
    passengers_count = fields.Integer(
        string="Number of passengers",
        readonly=True,
    )
    last_leg_flying_date = fields.Char(
        string="Last LEG Flying date",
        readonly=True,
    )
    segment_count = fields.Integer(
        string="Number of Segments",
        readonly=True,
    )
    booking_class = fields.Char(
        string="Booking Class",
        readonly=True,
    )
    destination_city = fields.Char(
        string="Destination City",
        readonly=True,
    )
    departure_date = fields.Char(
        string="Departure Date",
        readonly=True,
    )
    route = fields.Char(
        string="Route",
        readonly=True,
    )
    # Segment details
    contract = fields.Char(
        string="Contract",
        readonly=True,
        track_visibility='onchange',
    )
    hotel_id = fields.Char(
        string="Hotel ID",
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    hotel_city = fields.Char(
        string="Hotel City",
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    hotel_country = fields.Char(
        string="Hotel Country",
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    hotel_supplier_id = fields.Char(
        string="Hotel Supplier ID",
        readonly=True,
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
    matching_status = fields.Selection(
        string="Matching Status",
        selection=[
            ('unmatched', 'Unmatched'),
            ('matched', 'Matched'),
            ('not_applicable', 'Not Applicable')],
        default='unmatched',
        required=True,
        index=True,
        readonly=True,
        track_visibility='onchange',
    )
    not_applicable_flag = fields.Selection(
        string="Not applicable flag",
        selection=[
            ('none', 'N/A'),
            ('low_fare', 'Low Fare'),
            ('tajawal_fee', 'Tajawal Fee')],
        index=True,
        default='none',
        required=True,
        readonly=True,
        track_visibility='onchange',
    )

    @api.multi
    @api.depends('line_reference')
    def _compute_tickets(self):
        for rec in self:
            pass
