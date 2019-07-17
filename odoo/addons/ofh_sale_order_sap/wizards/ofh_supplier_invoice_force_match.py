# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OfhSupplierInvoiceForceMatch(models.TransientModel):

    _inherit = 'ofh.supplier.invoice.force.match'

    @api.multi
    @api.constrains('line_id', 'new_order_id', 'new_payment_request_id')
    def _check_new_payment_request_id(self):
        """Override the method to block force matching for PR sent to SAP."""
        for rec in self:
            if rec.new_payment_request_id.new_sap_status:
                raise ValidationError(
                    _("The payment request you trying to match with has "
                      "already been sent to SAP."))
        return super(OfhSupplierInvoiceForceMatch, self).\
            _check_new_payment_request_id()

    @api.multi
    @api.constrains('line_id', 'new_order_id', 'new_order_line_id')
    def _check_new_order_line_id(self):
        """Override the method to block force matching for line sent to SAP."""
        for rec in self:
            if rec.new_order_line_id.order_id.sap_status:
                raise ValidationError(
                    _("The Order line you trying to match with has "
                      "already been sent to SAP."))

        return super(OfhSupplierInvoiceForceMatch, self).\
            _check_new_order_line_id()
