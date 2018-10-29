# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OfhPaymentRequest(models.Model):

    _name = 'ofh.payment.request'
    _description = "Ofh Payment Request"

    request_type = fields.Selection(
        required=True,
        selection=[('charge', 'Charge'), ('refund', 'Refund')],
    )
    # TODO: maybe should be selection field
    request_reason = fields.Char(
        required=True,
    )
    # TODO: maybe should be selection field.
    request_status = fields.Char(
        required=True,
    )
    charge_id = fields.Char(
        required=True,
    )
    track_id = fields.Char(
        required=True,
    )
    auth_code = fields.Char()
    office_id = fields.Char()
    vendor_id = fields.Many2one(
        string="Airline",
        comodel_name='ofh.vendor.contract',
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True,
    )
    total_amount = fields.Monetary(
        string="Total",
        required=True,
    )
    entity = fields.Char(
        # TODO: required=True,
    )
    order_reference = fields.Char(
        string="Order #",
    )
    order_id = fields.Char(
        string="Order ID",
    )
    pnr = fields.Char(
        # TODO: required=True,
        string="PNR",
    )
    record_locator = fields.Char(
        # TODO: required=True,
    )
    insurance_ref = fields.Char()
    plan_code = fields.Char()
    # SAP related statuses
    sap_status = fields.Selection(
        string='SAP status',
        selection=[('pending', 'Pending'),
                   ('done', 'Loaded in SAP'),
                   ('sl_loader_ready', 'Sale loader ready'),
                   ('ar_loader_ready', 'A/R loader ready'),
                   ('need_loader', 'Need Loader')],
        default='pending',
        required=True,
    )
    flag = fields.Selection(
        string='Payment request flag',
        selection=[('not_matched', 'Not Matched'),
                   ('void', 'Voided'),
                   ('amemdment', 'Amendment'),
                   ('full_refund', 'Full Refund'),
                   ('partial_refund', 'Partial Refund')],
        default='not_matched',
        required=True,
    )
    hub_bind_ids = fields.One2many(
        comodel_name='hub.payment.request',
        inverse_name='odoo_id',
        string="Hub Bindings",
    )
