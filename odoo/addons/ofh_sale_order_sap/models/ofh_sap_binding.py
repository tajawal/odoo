# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job, related_action


class OfhSAPBinding(models.AbstractModel):

    _name = 'sap.binding'
    _inherit = 'external.binding'
    _description = "SAP Binding (Abstract)"

    backend_id = fields.Many2one(
        comodel_name='sap.backend',
        string='SAP Backend',
        required=True,
        ondelete='restrict',
    )
    external_id = fields.Char(
        string="File ID",
    )

    @job(default_channel='root.sap')
    @related_action(action='related_action_unwrap_binding')
    @api.multi
    def export_record(self, force=False, fields=None):
        """ Export a record to SAP."""
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage='record.exporter')
            return exporter.run(self, force=force)
