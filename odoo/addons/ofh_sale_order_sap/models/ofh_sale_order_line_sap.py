# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import json


class OfhSaleOrderLineSap(models.Model):
    _name = 'ofh.sale.order.line.sap'
    _description = 'Ofh Sale Order Line SAP'

    send_date = fields.Datetime(
        string="Send to Sap At",
        required=True,
        readonly=True,
        index=True,
    )
    sale_order_line_id = fields.Many2one(
        string="Sale Order Line",
        comodel_name='ofh.sale.order.line',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    sap_sale_order_id = fields.Many2one(
        comodel_name='ofh.sale.order.sap',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    line_detail = fields.Text(
        string="Line Detail",
        readonly=True,
    )
    sap_line_detail = fields.Text(
        string="SAP Line Detail",
        readonly=True,
    )
    # SAP Line Item Fields (Item General)
    booking_line_item_flag = fields.Char(  # sap_details
        string="Booking Line Item Flag",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    booking_line_item_number = fields.Char(  # sap_details
        string="Booking Line Item Number",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    line_item_billing_block = fields.Char(
        string="Line Item Billing Block",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    segment = fields.Char(
        string="Segment",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    service_item = fields.Char(
        string="Service Item",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    qty = fields.Char(
        string="Qty",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    billing_date = fields.Char(
        string="Billing Date",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    plant = fields.Char(
        string="Plant",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    vat_tax_code = fields.Char(
        string="VAT Tax Code",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    airline_code = fields.Char(
        string="Airline Code",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    iata_number = fields.Char(
        string="IATA Number",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    domestic_international = fields.Char(
        string="Domestic International",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    vendor = fields.Char(
        string="Vendor",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    vendor2 = fields.Char(
        string="Vendor2",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    travel_order_number = fields.Char(
        string="Travel Order Number",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    ticket_number = fields.Char(
        string="Ticket Number",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    pnr = fields.Char(
        string="PNR",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    gds_code = fields.Char(
        string="GDSCode",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    lcc_ind = fields.Char(
        string="LCCIND",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    vendor_confirmation = fields.Char(
        string="Vendor Confirmation",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    segment_count = fields.Char(
        string="Segment Count",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    custom1 = fields.Char(
        string="Custom1",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    pax_name = fields.Char(
        string="Pax Name",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    # SAP Sale Order Line Item fields (Item Characteristics)
    z_airline_code = fields.Char(
        string="Z_AIRLINECODE",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_fare_class = fields.Char(
        string="Z_FARE_CLASS",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_booking_type = fields.Char(
        string="Z_BOOKING_TYPE",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_booking_class = fields.Char(
        string="Z_BOOKING_CLASS",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_last_leg_flying_date = fields.Char(
        string="Z_LASTLEGFLYINGDATE",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_paxname = fields.Char(
        string="Z_PAXNAME",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_vendor = fields.Char(
        string="Z_VENDOR",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_destination_city = fields.Char(
        string="Z_DESTINATIONCITY",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_locator = fields.Char(
        string="Z_LOCATER",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_tkt_status = fields.Char(
        string="Z_TKTSTATUS",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_owner_id = fields.Char(
        string="Z_OWNEROID",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_departure_date = fields.Char(
        string="Z_DEPARTUREDATE",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_route = fields.Char(
        string="Z_ROUTE",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_iata = fields.Char(
        string="Z_IATA",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    z_number_of_pax = fields.Char(
        string="Z_NUMBEROFPAX",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    # SAP Sale Order Line Item fields (Item Conditions)
    zsel = fields.Char(
        string="ZSEL",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    zvd1 = fields.Char(
        string="ZVD1",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    zvnr = fields.Char(
        string="ZVNR",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    zvt1 = fields.Char(
        string="ZVT1",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    zgds = fields.Char(
        string="ZGDS",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    zdis = fields.Char(
        string="ZDIS",
        readonly=True,
        compute="_compute_sap_line_fields"
    )
    # Sale Order Line Fields
    name = fields.Char(
        string="Product",
        compute="_compute_line_fields"
    )
    sequence = fields.Char(
        string="Sequence",
        readonly=True,
        compute="_compute_line_fields"
    )
    created_at = fields.Datetime(
        string="Created At",
        readonly=True,
        compute="_compute_line_fields"
    )
    updated_at = fields.Datetime(
        string="Updated At",
        readonly=True,
        compute="_compute_line_fields"
    )
    line_type = fields.Char(
        string="type",
        readonly=True,
        compute="_compute_line_fields"
    )
    line_category = fields.Char(
        string="Category",
        readonly=True,
        compute="_compute_line_fields"
    )
    state = fields.Char(
        string="Status",
        readonly=True,
        compute="_compute_line_fields"
    )
    is_domestic_ksa = fields.Boolean(
        string="Is Domestic KSA",
        readonly=True,
        default=False,
        help="True if the order is a domestic KSA, else False",
        compute="_compute_line_fields"
    )
    vendor_confirmation_number = fields.Char(
        string="Vendor Confirmation Number",
        readonly=True,
        compute="_compute_line_fields"
    )
    vendor_name = fields.Char(
        string="Vendor Name",
        readonly=True,
        compute="_compute_line_fields"
    )
    vendor_currency_id = fields.Many2one(
        string="Vendor Currency",
        comodel_name='res.currency',
        readonly=True,
        compute="_compute_line_fields"
    )
    vendor_cost_amount = fields.Monetary(
        string="Vendor Cost",
        currency_field='vendor_currency_id',
        readonly=True,
        compute="_compute_line_fields"
    )
    vendor_base_fare_amount = fields.Monetary(
        string="Vendor Base Fare",
        currency_field='vendor_currency_id',
        readonly=True,
        compute="_compute_line_fields"
    )
    vendor_input_tax_amount = fields.Monetary(
        string="Vendor Input Tax",
        currency_field='vendor_currency_id',
        readonly=True,
        compute="_compute_line_fields"
    )
    # Supplier data
    supplier_confirmation_number = fields.Char(
        string="Supplier Confirmation Number",
        readonly=True,
        compute="_compute_line_fields"
    )
    supplier_name = fields.Char(
        string="Supplier Name",
        readonly=True,
        compute="_compute_line_fields"
    )
    supplier_currency_id = fields.Many2one(
        string="Supplier Currency",
        comodel_name='res.currency',
        readonly=True,
        compute="_compute_line_fields"
    )
    supplier_cost_amount = fields.Monetary(
        string="Supplier Cost",
        currency_field='supplier_currency_id',
        readonly=True,
        compute="_compute_line_fields"
    )
    supplier_base_fare_amount = fields.Monetary(
        string="Supplier Base Fare",
        currency_field='supplier_currency_id',
        readonly=True,
        compute="_compute_line_fields"
    )
    supplier_input_tax_amount = fields.Monetary(
        string="Supplier Input Tax",
        currency_field='supplier_currency_id',
        readonly=True,
        compute="_compute_line_fields"
    )
    exchange_rate = fields.Float(
        readonly=True,
        compute="_compute_line_fields"
    )
    # traveller details
    traveller = fields.Char(
        readonly=True,
        compute="_compute_line_fields"
    )
    traveller_type = fields.Char(
        string="Traveller type",
        readonly=True,
        compute="_compute_line_fields"
    )
    office_id = fields.Char(
        string="Office ID",
        readonly=True,
        compute="_compute_line_fields"
    )
    ticketing_office_id = fields.Char(
        string="Ticketing Office ID",
        readonly=True,
        compute="_compute_line_fields"
    )
    tour_code_office_id = fields.Char(
        string="Tour Code",
        readonly=True,
        compute="_compute_line_fields"
    )
    line_reference = fields.Char(
        string="Ticket/Segment",
        readonly=True,
        compute="_compute_line_fields"
    )
    tickets = fields.Char(
        string="Tickets",
        readonly=True,
        compute="_compute_line_fields"
    )
    passengers_count = fields.Integer(
        string="Number of passengers",
        readonly=True,
        compute="_compute_line_fields"
    )
    last_leg_flying_date = fields.Char(
        string="Last LEG Flying date",
        readonly=True,
        compute="_compute_line_fields"
    )
    segment_count = fields.Integer(
        string="Number of Segments",
        readonly=True,
        compute="_compute_line_fields"
    )
    booking_class = fields.Char(
        string="Booking Class",
        readonly=True,
        compute="_compute_line_fields"
    )
    destination_city = fields.Char(
        string="Destination City",
        readonly=True,
        compute="_compute_line_fields"
    )
    departure_date = fields.Char(
        string="Departure Date",
        readonly=True,
        compute="_compute_line_fields"
    )
    route = fields.Char(
        string="Route",
        readonly=True,
        compute="_compute_line_fields"
    )
    origin_city = fields.Char(
        string="Origin City",
        readonly=True,
        compute="_compute_line_fields"
    )
    ahs_group_name = fields.Char(
        string="AHS Group Name",
        readonly=True,
        compute="_compute_line_fields"
    )
    # Segment details
    contract = fields.Char(
        string="Contract",
        readonly=True,
        compute="_compute_line_fields"
    )
    hotel_id = fields.Char(
        string="Hotel ID",
        readonly=True,
        compute="_compute_line_fields"
    )
    hotel_city = fields.Char(
        string="Hotel City",
        readonly=True,
        compute="_compute_line_fields"
    )
    hotel_country = fields.Char(
        string="Hotel Country",
        readonly=True,
        compute="_compute_line_fields"
    )
    hotel_supplier_id = fields.Char(
        string="Hotel Supplier ID",
        readonly=True,
        compute="_compute_line_fields"
    )

    # Sale price data
    tax_code = fields.Selection(
        string="Tax Code",
        selection=[('ss', 'SS'), ('sz', 'SZ')],
        readonly=True,
        default='sz',
        compute="_compute_line_fields"
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name='res.currency',
        readonly=True,
        compute="_compute_line_fields"
    )
    sale_price = fields.Monetary(
        string="Sale Price",
        currency_field='currency_id',
        readonly=True,
        help="Sale price = vendor cost + service fee.",
        compute="_compute_line_fields"
    )
    service_fee_amount = fields.Monetary(
        string="Service Fee",
        currency_field='currency_id',
        readonly=True,
        help="Prorated service fee",
        compute="_compute_line_fields"
    )
    discount_amount = fields.Monetary(
        string="Discount",
        currency_field='currency_id',
        readonly=True,
        help="Prorated discount amount",
        compute="_compute_line_fields"
    )
    tax_amount = fields.Monetary(
        string="Tax",
        currency_field='currency_id',
        readonly=True,
        help="Prorated tax amount",
        compute="_compute_line_fields"
    )
    subtotal_amount = fields.Monetary(
        string="Subtotal",
        currency_field='currency_id',
        readonly=True,
        help="Sale Price amount - discount amount",
        compute="_compute_line_fields"
    )
    total_amount = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        readonly=True,
        help="Total Amount = Sale Price amount + discount",
        compute="_compute_line_fields"
    )

    @api.multi
    @api.depends('line_detail')
    def _compute_line_fields(self):
        for rec in self:
            line_detail = json.loads(rec.line_detail)

            rec.name = line_detail.get('name')
            rec.sequence = line_detail.get('sequence')
            rec.created_at = line_detail.get('created_at')
            rec.updated_at = line_detail.get('updated_at')
            rec.line_type = line_detail.get('line_type')
            rec.line_category = line_detail.get('line_category')
            rec.state = line_detail.get('state')
            rec.is_domestic_ksa = line_detail.get('is_domestic_ksa')
            rec.vendor_confirmation_number = line_detail.get('vendor_confirmation_number')
            rec.vendor_name = line_detail.get('vendor_name')
            rec.vendor_currency_id = line_detail.get('vendor_currency_id')
            rec.vendor_cost_amount = line_detail.get('vendor_cost_amount')
            rec.vendor_base_fare_amount = line_detail.get('vendor_base_fare_amount')
            rec.vendor_input_tax_amount = line_detail.get('vendor_input_tax_amount')
            rec.supplier_confirmation_number = line_detail.get('supplier_confirmation_number')
            rec.supplier_name = line_detail.get('supplier_name')
            rec.supplier_currency_id = line_detail.get('supplier_currency_id')
            rec.supplier_cost_amount = line_detail.get('supplier_cost_amount')
            rec.supplier_base_fare_amount = line_detail.get('supplier_base_fare_amount')
            rec.supplier_input_tax_amount = line_detail.get('supplier_input_tax_amount')
            rec.exchange_rate = line_detail.get('exchange_rate')
            rec.traveller = line_detail.get('traveller')
            rec.traveller_type = line_detail.get('traveller_type')
            rec.office_id = line_detail.get('office_id')
            rec.ticketing_office_id = line_detail.get('ticketing_office_id')
            rec.tour_code_office_id = line_detail.get('tour_code_office_id')
            rec.line_reference = line_detail.get('line_reference')
            rec.tickets = line_detail.get('tickets')
            rec.passengers_count = line_detail.get('passengers_count')
            rec.last_leg_flying_date = line_detail.get('last_leg_flying_date')
            rec.segment_count = line_detail.get('segment_count')
            rec.booking_class = line_detail.get('booking_class')
            rec.destination_city = line_detail.get('destination_city')
            rec.departure_date = line_detail.get('departure_date')
            rec.route = line_detail.get('route')
            rec.origin_city = line_detail.get('origin_city')
            rec.ahs_group_name = line_detail.get('ahs_group_name')
            rec.contract = line_detail.get('contract')
            rec.hotel_id = line_detail.get('hotel_id')
            rec.hotel_city = line_detail.get('hotel_city')
            rec.hotel_country = line_detail.get('hotel_country')
            rec.hotel_supplier_id = line_detail.get('hotel_supplier_id')
            rec.tax_code = line_detail.get('tax_code')
            rec.currency_id = line_detail.get('currency_id')
            rec.sale_price = line_detail.get('sale_price')
            rec.service_fee_amount = line_detail.get('service_fee_amount')
            rec.discount_amount = line_detail.get('discount_amount')
            rec.tax_amount = line_detail.get('tax_amount')
            rec.subtotal_amount = line_detail.get('subtotal_amount')
            rec.total_amount = line_detail.get('total_amount')

    @api.multi
    @api.depends('sap_line_detail')
    def _compute_sap_line_fields(self):
        for rec in self:
            sap_line_detail = json.loads(rec.sap_line_detail)

            rec.booking_line_item_flag = sap_line_detail.get('booking_line_item_flag')
            rec.booking_line_item_number = sap_line_detail.get('booking_line_item_number')
            rec.line_item_billing_block = sap_line_detail.get('line_item_billing_block')
            rec.segment = sap_line_detail.get('segment')
            rec.service_item = sap_line_detail.get('service_item')
            rec.qty = sap_line_detail.get('qty')
            rec.billing_date = sap_line_detail.get('billing_date')
            rec.plant = sap_line_detail.get('plant')
            rec.vat_tax_code = sap_line_detail.get('vat_tax_code')
            rec.airline_code = sap_line_detail.get('airline_code')
            rec.iata_number = sap_line_detail.get('iata_number')
            rec.domestic_international = sap_line_detail.get('domestic_international')
            rec.vendor = sap_line_detail.get('vendor')
            rec.vendor2 = sap_line_detail.get('vendor2')
            rec.travel_order_number = sap_line_detail.get('travel_order_number')
            rec.ticket_number = sap_line_detail.get('ticket_number')
            rec.pnr = sap_line_detail.get('pnr')
            rec.gds_code = sap_line_detail.get('gds_code')
            rec.lcc_ind = sap_line_detail.get('lcc_ind')
            rec.vendor_confirmation = sap_line_detail.get('vendor_confirmation')
            rec.segment_count = sap_line_detail.get('segment_count')
            rec.custom1 = sap_line_detail.get('custom1')
            rec.pax_name = sap_line_detail.get('pax_name')
            rec.z_airline_code = sap_line_detail.get('z_airline_code')
            rec.z_fare_class = sap_line_detail.get('z_fare_class')
            rec.z_booking_type = sap_line_detail.get('z_booking_type')
            rec.z_booking_class = sap_line_detail.get('z_booking_class')
            rec.z_last_leg_flying_date = sap_line_detail.get('z_last_leg_flying_date')
            rec.z_paxname = sap_line_detail.get('z_paxname')
            rec.z_vendor = sap_line_detail.get('z_vendor')
            rec.z_destination_city = sap_line_detail.get('z_destination_city')
            rec.z_locator = sap_line_detail.get('z_locator')
            rec.z_tkt_status = sap_line_detail.get('z_tkt_status')
            rec.z_owner_id = sap_line_detail.get('z_owner_id')
            rec.z_departure_date = sap_line_detail.get('z_departure_date')
            rec.z_route = sap_line_detail.get('z_route')
            rec.z_iata = sap_line_detail.get('z_iata')
            rec.z_number_of_pax = sap_line_detail.get('z_number_of_pax')
            rec.zsel = sap_line_detail.get('zsel')
            rec.zvd1 = sap_line_detail.get('zvd1')
            rec.zvnr = sap_line_detail.get('zvnr')
            rec.zvt1 = sap_line_detail.get('zvt1')
            rec.zgds = sap_line_detail.get('zgds')
            rec.zdis = sap_line_detail.get('zdis')
