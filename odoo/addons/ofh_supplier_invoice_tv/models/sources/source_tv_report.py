# Copyright 2019 Tajwal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.ofh_hub_connector.components.backend_adapter import HubAPI


class SourceTvReport(models.Model):
    _name = 'import.source.tv_report'
    _inherit = 'import.source'
    _description = 'TV Api import source'
    _source_type = 'tv_report'
    _reporter_model = 'reporter.tv_report'

    date_from = fields.Datetime(
        string="Date From",
        required=True,
    )
    date_to = fields.Datetime(
        string="Date To",
        required=True,
    )

    _sql_constraints = [(
        'source_uniq',
        'unique(date_from, date_to)',
        'Tv Report source must be unique!')]

    @api.multi
    def _get_lines(self):
        # Get TV Report lines
        self.ensure_one()

        backend = self.env['hub.backend'].search([], limit=1)
        if not backend:
            return {}

        hub_api = HubAPI(
            oms_finance_api_url=backend.oms_finance_api_url
        )

        lines = hub_api.get_tv_daily_report(
            date_from=self.date_from, date_to=self.date_to)

        if not lines:
            return []

        return lines
