# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ofhVendorContract(models.Model):

    _name = 'ofh.vendor.contract'
    _description = 'Vendor Contract'

    name = fields.Char(
        string="Supplier Name",
        required=True,
    )
    supplier_type = fields.Selection(
        string="Type",
        required=True,
        selection=[('flight', 'Flight'), ('hotel', 'Hotel')],
    )
    supplier_id = fields.Char(
        string="Supplier ID",
        required=True,
    )
    contract_id = fields.Char(
        string="Contract ID",
    )
    sap_vendor_code = fields.Char(
        string="SAP vendor code",
    )
    sap_legal_entity_code = fields.Char()

    vendor_ids = fields.One2many(
        string="Vendors",
        comodel_name='ofh.vendor',
        inverse_name='contract_id',
    )
    enett = fields.Boolean(
        default=False,
    )
    active = fields.Boolean(
        default=True,
    )

    @api.multi
    @api.constrains(
        'contract_id', 'sap_vendor_code',
        'sap_legal_entity_code', 'vendor_ids')
    def _check_sap_mapping(self):
        for rec in self:
            if rec.contract_id or rec.vendor_ids:
                continue
            if not rec.sap_vendor_code:
                raise ValidationError(
                    _("Please provide sap vendor code."))
            if not rec.sap_legal_entity_code:
                raise ValidationError(
                    _("Please provide Sap legal entity code."))
