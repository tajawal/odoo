
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
        source = self.env['import.source.csv'].create({
            'csv_file': self.upload_file,
            'csv_filename': self.file_name,
            'csv_delimiter': ','})
        recordset = self.env['import.recordset'].create({
            'backend_id': self.env.ref(
                'ofh_supplier_invoice_gds.gds_import_backend').id,
            'import_type_id': self.env.ref(
                'ofh_supplier_invoice_gds.gds_import_type').id,
            'source_id': source.id,
            'source_model': 'import.source.csv',
        })
        return recordset.run_import()
