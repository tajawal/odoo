# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    payment_request_id = fields.Many2one(
        string="Payment request",
        comodel_name='ofh.payment.request',
    )
