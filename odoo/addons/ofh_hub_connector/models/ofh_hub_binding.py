# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job


class OfhHubBinding(models.AbstractModel):

    _name = 'hub.binding'
    _inherit = 'external.binding'
    _description = "Hub Binding (Abstract)"

    backend_id = fields.Many2one(
        comodel_name='hub.backend',
        string='HUB Backend',
        required=True,
        ondelete='restrict',
    )
    external_id = fields.Char(
        string="ID on HUB",
    )

    _sql_constraints = [
        ('hub_uniq', 'unique(backend_id, external_id)',
         _("A binding already exists with the same Hub ID.")),
    ]

    @job(default_channel='root.hub')
    @api.model
    def import_batch(self, backend, filters=None):
        """ Prepare the import of records modified on Hub """
        if filters is None:
            filters = {}
        with backend.work_on(self._name) as work:
            importer = work.component(usage='batch.importer')
            return importer.run(filters=filters)

    @job(default_channel='root.hub')
    @api.model
    def import_record(self, backend, external_id, force=False):
        """ Import a Hub record """
        with backend.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            return importer.run(external_id, force=force)
