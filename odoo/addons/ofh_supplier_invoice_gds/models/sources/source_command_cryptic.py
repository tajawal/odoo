# Copyright 2019 Tajwal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.ofh_hub_connector.components.backend_adapter import HubAPI


class SourceCommandCryptic(models.Model):
    _name = 'import.source.command_cryptic'
    _inherit = 'import.source'
    _description = 'Command Cryptic import source'
    _source_type = 'command_cryptic'

    office_id = fields.Char(
        string="Office ID",
        required=True,
    )
    report_day = fields.Char(
        string="Report day",
        required=True,
    )

    _sql_constraints = [(
        'source_uniq',
        'unique(office_id, report_day)',
        'Command Cryptic source must be unique!')]

    @api.multi
    def _get_lines(self):
        # Get command cryptic lines
        self.ensure_one()

        backend = self.env['hub.backend'].search([], limit=1)
        if not backend:
            return {}

        hub_api = HubAPI(
            hub_url=backend.hub_api_location,
            hub_username=backend.hub_api_username,
            hub_password=backend.hub_api_password,
            config_url=backend.config_api_url,
            config_username=backend.config_api_username,
            config_password=backend.config_api_password)

        return hub_api.get_gds_daily_report(
            office_id=self.office_id, report_day=self.report_day)
