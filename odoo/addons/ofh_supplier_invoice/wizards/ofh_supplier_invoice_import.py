# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import MissingError
# from odoo.addons.ofh_supplier_invoice_line.OfhSupplierInvoiceLine import \
#     _get_invoice_type_selection


class OfhSupplierInvoiceImport(models.TransientModel):

    _name = 'ofh.supplier.invoice.import'

    file_type = fields.Selection(
        string="Report type",
        selection=[],
        required=True,
    )
    upload_file = fields.Binary(
        string="Upload File",
    )
    file_name = fields.Char(
        string="File Name",
    )

    @api.multi
    def import_report(self):
        self.ensure_one()
        compute_function = '_{}_import_report'.format(self.file_type)
        if hasattr(self, compute_function):
            getattr(self, compute_function)()
        else:
            raise MissingError(_("Method not implemented."))
