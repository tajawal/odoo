
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhSupplierInvoiceImport(models.TransientModel):

    _inherit = 'ofh.supplier.invoice.import'

    file_type = fields.Selection(
        selection_add=[('tp', 'TravelPort')],
    )

    @api.multi
    def _tp_import_report(self):
        backend = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_backend')
        import_type = self.env.ref(
            'ofh_supplier_invoice_tp.tp_import_type')

        return backend._import_report(
            import_type=import_type,
            file_name=self.file_name,
            data=self.upload_file)
