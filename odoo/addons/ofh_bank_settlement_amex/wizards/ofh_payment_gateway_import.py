
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OfhBankSettlementImport(models.TransientModel):

    _inherit = 'ofh.bank.settlement.import'

    file_type = fields.Selection(
        selection_add=[('amex', 'Amex')],
    )

    @api.multi
    def _amex_import_report(self):

        backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')
        import_type = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_type')

        return backend._import_report(
            import_type=import_type,
            file_name=self.file_name,
            data=self.upload_file)
