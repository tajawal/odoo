# Copyright LLC Tajawal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhPaymentRequestSapImport(models.TransientModel):

    _name = 'ofh.payment.request.sap.import'

    report_type = fields.Selection(
        string="Report Type",
        selection=[('va05', 'VA05'), ('fbl5n', 'FBL5N')],
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
        """
        Run the matching of the uploaded file against payment
        """
        self.ensure_one()
        if self.report_type == 'va05':
            import_type = self.env.ref(
                'ofh_payment_request_sap.sap_sale_import_type')
            backend = self.env.ref(
                'ofh_payment_request_sap.sap_sale_import_backend')
        else:
            import_type = self.env.ref(
                'ofh_payment_request_sap.sap_payment_import_type')
            backend = self.env.ref(
                'ofh_payment_request_sap.sap_payment_import_backend')

        return backend._import_report(
            import_type=import_type,
            file_name=self.upload_file,
            data=self.file_name)
