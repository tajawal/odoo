# Copyright 2019 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from contextlib import contextmanager

from odoo import _, api, fields, models

from ..components.backend_adapter import SapXmlApi

try:
    from odoo.addons.server_environment import serv_config
except ImportError:
    logging.getLogger('odoo.module').warning(
        'server_environment not available in addons path.')

_logger = logging.getLogger(__name__)


class SAPBackend(models.Model):
    _name = 'sap.backend'
    _description = 'Hub Backend'
    _inherit = 'connector.backend'

    name = fields.Char(
        string="Backend name",
        default='dev-hub',
    )
    sap_xml_api_url = fields.Char(
        string="SAP XML API URL",
        compute='_compute_server_env',
        store=False,
        readonly=True,
    )

    _sql_constraints = [
        ('unique_hub_backend', 'unique(name)',
         _("A backend-end should always be unique."))
    ]

    @property
    def _server_env_fields(self):
        return (
            'sap_xml_api_url',)

    @api.multi
    def _compute_server_env(self):
        for backend in self:
            for field_name in self._server_env_fields:
                section_name = '{model}.{name}'.format(
                    model=self._name.replace('.', '_'),
                    name=backend.name)
                try:
                    value = serv_config.get(section_name, field_name)
                    backend[field_name] = value
                except Exception:
                    _logger.exception(
                        'error trying to read field %s in section %s',
                        field_name, section_name)

    @contextmanager
    @api.multi
    def work_on(self, model_name, **kwargs):
        # We create a SAP Client API here, so we can create the
        # client once (lazily on the first use) and propagate it
        # through all the sync session, instead of recreating a client
        # in each backend adapter usage.
        self.ensure_one()
        sap_api = SapXmlApi(
            sap_xml_api_url=self.sap_xml_api_url
        )
        _super = super(SAPBackend, self)
        # from the components we'll be able to do: self.work.sap_api
        with _super.work_on(model_name, sap_api=sap_api, **kwargs) as work:
            yield work
