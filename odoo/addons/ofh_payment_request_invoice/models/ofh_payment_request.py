# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhPaymentRequest(models.Model):

    _inherit = 'ofh.payment.request'

    supplier_invoice_ids = fields.One2many(
        string="Supplier costs",
        comodel_name='ofh.supplier.invoice.line',
        inverse_name='payment_request_id',
    )

    # SAP related statuses
    reconciliation_status = fields.Selection(
        string="Reconciliation Status",
        selection=[
            ('pending', 'pending'),
            ('matched', 'Matched'),
            ('investigate', 'Investigate')],
        default='pending',
        required=True,
        index=True,
    )
