# Copyright 2019 Seera Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.addons.connector_importer.log import logger
from odoo.addons.connector_importer.models.job_mixin import JobRelatedMixin
from odoo.addons.queue_job.job import job


class ImportRecordset(models.Model, JobRelatedMixin):
    _inherit = 'import.recordset'

    @api.multi
    @job(default_channel='root.import.report')
    def set_report(self, values, reset=False):
        return super(ImportRecordset, self).set_report(values, reset)

    @api.multi
    def _run_import(self, channel=''):
        job_method = self.with_delay().import_recordset

        if channel:
            job_method = self.with_delay(channel=channel).import_recordset

        if self.debug_mode():
            logger.warn('### DEBUG MODE ACTIVE: WILL NOT USE QUEUE ###')
            job_method = self.import_recordset

        for item in self:
            result = job_method()
            if self.debug_mode():
                # debug mode, no job here: reset it!
                item.write({'job_id': False})
            else:
                # link the job
                item.write({'job_id': result.db_record().id})
        if self.debug_mode():
            pass

    @api.multi
    def run_import(self):
        return self._run_import()
