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

    @api.model
    def _get_default_current_payment_request_id(self):
        active_model = self.env.context.get('active_model')
        if active_model != 'ofh.supplier.invoice.line':
            raise ValidationError(
                _("The active model is not the one expected."))
        active_id = self.env.context.get('active_id')
        line = self.env[active_model].browse(active_id)
        if line:
            return line.payment_request_id
        else:
            return self.env['ofh.payment.request'].browse()

    new_payment_request_id = fields.Many2one(
        string="New Payment Request",
        comodel_name='ofh.payment.request',
        domain="[('id', '!=', current_payment_request_id),"
               "('order_type', '=', 'flight'),"
               "('payment_request_status', '=', 'ready')]",
        required=True,
    )
    current_payment_request_id = fields.Many2one(
        string="Current Payment Request",
        comodel_name='ofh.payment.request',
        readonly=True,
        default=_get_default_current_payment_request_id,
    )
    line_id = fields.Many2one(
        string="Invoice Line",
        comodel_name='ofh.supplier.invoice.line',
        required=True,
        readonly=True,
        default=_get_default_line_id,
    )

    @api.multi
    @api.constrains('line_id', 'new_payment_request_id')
    def _check_new_payment_request_id(self):
        for rec in self:
            if rec.line_id.invoice_status == 'TKTT' and \
                    rec.new_payment_request_id.request_type != 'charge':
                raise ValidationError(
                    _("A 'TKTT' line can only match with a 'Charge' "
                      "payment request."))
            if rec.line_id.invoice_status == 'RFND' and \
                    rec.new_payment_request_id.request_type == 'charge':
                raise ValidationError(
                    _("A 'RFND' line can't match with a 'Charge' "
                      "payment request."))
            if rec.new_payment_request_id.order_type == 'hotel':
                raise ValidationError(
                    _("You are not allowed to match with a 'Hotel' "
                      "payment request."))

    @api.multi
    def force_match(self):
        self.ensure_one()
        if self.new_payment_request_id:
            return self.line_id._update_payment_request(
                self.new_payment_request_id)
