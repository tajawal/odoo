# Copyright 2019 Seera Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.addons.connector_importer.log import logger
from odoo.addons.connector_importer.models.job_mixin import JobRelatedMixin


class ImportRecord(models.Model, JobRelatedMixin):

    _inherit = 'import.record'

    @api.multi
    def _run_import(self, channel=''):
        """ queue a job for importing data stored in to self
        """
        job_method = self.with_delay().import_record
        if channel:
            job_method = self.with_delay(channel=channel).import_record

        if self.debug_mode():
            logger.warn('### DEBUG MODE ACTIVE: WILL NOT USE QUEUE ###')
            job_method = self.import_record
        _result = {}
        for item in self:
            # we create a record and a job for each model name
            # that needs to be imported
            for (model, importer, is_last_importer) in \
                    item.recordset_id.available_models():
                # TODO: grab component from config
                result = job_method(
                    importer, model, is_last_importer=False)
                _result[model] = result
                if self.debug_mode():
                    # debug mode, no job here: reset it!
                    item.write({'job_id': False})
                else:
                    # FIXME: we should have a o2m here otherwise
                    # w/ multiple importers for the same record
                    # we keep the reference on w/ the last job.
                    item.write({'job_id': result.db_record().id})
        return _result

    @api.multi
    def run_import(self):
        return self._run_import()
