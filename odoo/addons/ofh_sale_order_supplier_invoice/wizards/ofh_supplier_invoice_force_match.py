# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OfhSupplierInvoiceForceMatch(models.TransientModel):
    _name = 'ofh.supplier.invoice.force.match'

    @api.model
    def _get_default_line_id(self):
        active_model = self.env.context.get('active_model')
        if active_model != 'ofh.supplier.invoice.line':
            raise ValidationError(
                _("The active model is not the one expected."))
        active_id = self.env.context.get('active_id')
        return self.env[active_model].browse(active_id)

    line_id = fields.Many2one(
        string="Invoice Line",
        comodel_name='ofh.supplier.invoice.line',
        required=True,
        readonly=True,
        default=_get_default_line_id,
    )
    current_order_id = fields.Many2one(
        string="Current Sale Order",
        comodel_name='ofh.sale.order',
        readonly=True,
        related='line_id.order_id',
    )
    current_payment_request_id = fields.Many2one(
        string="Current Payment Request",
        comodel_name='ofh.payment.request',
        readonly=True,
        related='line_id.payment_request_id',
    )
    current_order_line_id = fields.Many2one(
        string="Current Order Line",
        comodel_name='ofh.sale.order.line',
        readonly=True,
        related='line_id.order_line_id',
    )
    new_order_id = fields.Many2one(
        string="New Order",
        comodel_name='ofh.sale.order',
        domain="[('id', '!=', current_order_id)]",
    )
    new_payment_request_id = fields.Many2one(
        string="New Payment Request",
        comodel_name='ofh.payment.request',
        domain="[('id', '!=', current_payment_request_id),"
               "('order_type', '=', 'flight'),"
               "('payment_request_status', '=', 'ready'),"
               "'|', ('order_id', '=', new_order_id),"
               "('order_id', '=', current_order_id)]",
    )
    new_order_line_id = fields.Many2one(
        string="New Order Line",
        comodel_name='ofh.sale.order.line',
        domain="[('id', '!=', current_order_line_id),"
               "'|', ('order_id', '=', new_order_id),"
               "('order_id', '=', current_order_id)]",
    )

    @api.multi
    @api.constrains('line_id', 'new_order_id', 'new_payment_request_id')
    def _check_new_payment_request_id(self):
        for rec in self:
            if not rec.new_payment_request_id:
                continue
            if rec.new_order_id:
                if rec.new_payment_request_id not in \
                        rec.new_order_id.payment_request_ids:
                    raise ValidationError(
                        f"The new selected PR "
                        f"{rec.new_payment_request_id.name} "
                        f"must belong to new selected Sale: "
                        f"{rec.new_order_id}.")
            else:
                if rec.new_payment_request_id not in \
                        rec.current_order_id.payment_request_ids:
                    raise ValidationError(
                        f"The new selected PR: "
                        f"{rec.new_payment_request_id.name} "
                        f"must belong to currently selected Sale: "
                        f"{rec.current_order_id.name}.")

            if rec.new_payment_request_id.order_type == 'hotel':
                raise ValidationError(
                    _("You are not allowed to match with a 'Hotel' "
                      "payment request."))

    @api.multi
    @api.constrains('line_id', 'new_order_id', 'new_order_line_id')
    def _check_new_order_line_id(self):
        for rec in self:
            if not rec.new_order_line_id:
                continue
            if rec.new_order_id:
                if rec.new_order_line_id not in rec.new_order_id.line_ids:
                    raise ValidationError(
                        f"The selected order line: "
                        f"{rec.new_order_line_id.name} "
                        f"must belong to new selected Sale: "
                        f"{rec.new_order_id.name}.")
            else:
                if rec.new_order_line_id not in rec.current_order_id.line_ids:
                    raise ValidationError(
                        f"The new selected order line: "
                        f"{rec.new_order_line_id.name} "
                        f" must belong to currently selected Sale: "
                        f"{rec.current_order_id.name}.")

                if rec.line_id.invoice_status == 'RFND':
                    raise ValidationError(
                        "A sale order line can't match with a refund line.")

    @api.multi
    @api.constrains('new_order_line_id', 'new_payment_request_id')
    def _check_set_data(self):
        for rec in self:
            if rec.new_order_line_id and rec.new_payment_request_id:
                raise ValidationError(
                    "An Invoice line can only match with a initial booking "
                    "or a payment request, not both.")

    @api.onchange('new_order_line_id')
    def _onchange_new_order_line_id(self):
        if self.new_order_line_id:
            self.new_payment_request_id = False

    @api.onchange('new_payment_request_id')
    def _onchange_new_payment_request_id(self):
        if self.new_payment_request_id:
            self.new_order_line_id = False

    @api.multi
    def force_match(self):
        self.ensure_one()
        return self.line_id._force_match_invoice_line(
            order_id=self.new_order_id,
            pr_id=self.new_payment_request_id,
            line_id=self.new_order_line_id)
