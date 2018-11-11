# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ofhVendor(models.Model):

    _name = 'ofh.vendor'
    _description = 'ofh Vendors'

    name = fields.Char(
        required=True,
    )
    vendor_name = fields.Char(
        string="Vendor/Supplier Name",
        required=True,
    )
    b2b_hotel_id = fields.Char(
        string="B2B Hotel ID",
    )
    tv_hotel_id = fields.Char(
        string="TV Hotel ID",
    )
    sap_id = fields.Char(
        string="SAP Vendor Code",
    )
    sap_legal_entity_id = fields.Char(
        string="SAP vendor legal entity ID",
    )
    contract_id = fields.Many2one(
        string="Contract",
        comodel_name='ofh.vendor.contract',
        required=True,
    )
    active = fields.Boolean(
        default=True,
    )
