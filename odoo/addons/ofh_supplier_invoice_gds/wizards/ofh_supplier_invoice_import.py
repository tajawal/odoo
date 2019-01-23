
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhSupplierInvoiceImport(models.TransientModel):

    _inherit = 'ofh.supplier.invoice.import'

    file_type = fields.Selection(
        selection_add=[('gds', 'GDS')],
    )

    @api.multi
    def _gds_import_report(self):
        backend = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_backend')
        import_type = self.env.ref(
            'ofh_supplier_invoice_gds.gds_import_type')

        return backend._import_report(
            import_type=import_type,
            file_name=self.upload_file,
            data=self.file_name)
