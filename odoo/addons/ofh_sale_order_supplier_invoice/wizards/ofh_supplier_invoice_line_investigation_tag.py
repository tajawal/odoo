# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OfhSupplierInvoiceLineInvestigation_tag(models.TransientModel):

    _name = 'ofh.supplier.invoice.line.investigation.tag'

    @api.model
    def _get_default_invoice_line_ids(self):
        active_model = self.env.context.get('active_model')
        if active_model != 'ofh.supplier.invoice.line':
            raise ValidationError(
                _("The active model is not the one expected."))
        active_ids = self.env.context.get('active_ids', [])
        return self.env[active_model].browse(active_ids)

    invoice_line_ids = fields.Many2many(
        comodel_name='ofh.supplier.invoice.line',
        relation='invoice_line_investigation_rel',
        column1='wizard_id',
        column2='invoice_id',
        default=_get_default_invoice_line_ids,
    )
    investigation_tag = fields.Char(
        string="Investigation Tag",
        required=True,
    )

    @api.multi
    def action_update_investigation_tag(self):
        self.ensure_one()
        self.invoice_line_ids.action_update_investigation_tag(
            investigation_tag=self.investigation_tag)
