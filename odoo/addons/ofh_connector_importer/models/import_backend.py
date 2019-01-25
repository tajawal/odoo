# Copyright 2019 Tajwal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ImportBackend(models.Model):

    _inherit = 'import.backend'

    @api.multi
    def _import_report(self, import_type, file_name, data):
        """Import a given data to the system.

        :param import_type: import.type record
        :type import_type: import.type object
        :param file_name: The name of the file to be imported.
        :type file_name: str
        :param data: file like object mainly
        :type data: binary
        """

        self.ensure_one()
        source = self.env['import.source.csv'].create({
            'csv_file': data,
            'csv_filename': file_name,
            'csv_delimiter': ','})

        recordset = self.env['import.recordset'].create({
            'backend_id': self.id,
            'import_type_id': import_type.id,
            'source_id': source.id,
            'source_model': 'import.source.csv',
        })
        return recordset.run_import()
