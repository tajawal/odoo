# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OfhPaymentLoader(models.TransientModel):
    _name = 'ofh.payment.loader'

    entity = fields.Selection(
        selection=[
            ('almosafer', 'Almosafer'),
            ('tajawal', 'Tajawal')],
        default="almosafer",
    )
    bank_name = fields.Selection(
        string="Bank Name",
        selection=[
            ('mashreq', 'Mashreq'),
            ('cib', 'CIB'),
            ('sabb', 'SABB'),
            ('rajhi', 'Rajhi'),
            ('knet', 'Knet'),
            ('amex', 'Amex')],
    )
    provider = fields.Selection(
        string="Provider",
        selection=[
            ('checkout', 'Checkout'),
            ('fort', 'Fort'),
            ('knet', 'Knet'),
        ],
    )
    settlement_date = fields.Date(
        string="Settlement Date",
    )
    is_apple_pay = fields.Boolean(
        string="Apple Pay?",
        default=False,
    )
    currency = fields.Selection(
        string="Currency",
        selection=[
            ('aed', 'AED'),
            ('sar', 'SAR')],
    )
