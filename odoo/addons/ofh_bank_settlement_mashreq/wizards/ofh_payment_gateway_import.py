
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhBankSettlementImport(models.TransientModel):

    _inherit = 'ofh.bank.settlement.import'

    file_type = fields.Selection(
        selection_add=[('mashreq', 'Mashreq')],
    )

    @api.multi
    def _mashreq_import_report(self):

        backend = self.env.ref(
            'ofh_bank_settlement_mashreq.mashreq_bank_settlement_import_backend')
        import_type = self.env.ref(
            'ofh_bank_settlement_mashreq.mashreq_bank_settlement_import_type')

        return backend._import_report(
            import_type=import_type,
            file_name=self.file_name,
            data=self.upload_file)
