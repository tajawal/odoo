# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from contextlib import contextmanager
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from ..components.backend_adapter import HubAPI

try:
    from odoo.addons.server_environment import serv_config
except ImportError:
    logging.getLogger('odoo.module').warning(
        'server_environment not available in addons path. '
        'server_env_connector_magento will not be usable')

_logger = logging.getLogger(__name__)

IMPORT_DELTA_BUFFER = 600   # seconds


class HubBackend(models.Model):

    _name = 'hub.backend'
    _description = 'Hub Backend'
    _inherit = 'connector.backend'

    name = fields.Char(
        string="Backend name",
        default='dev-hub',
    )
    hub_api_location = fields.Char(
        string='HUB API URL',
        compute='_compute_server_env',
        store=False,
        readonly=True,
    )
    hub_api_username = fields.Char(
        string="HUB username",
        compute='_compute_server_env',
        store=False,
        readonly=True,
    )
    hub_api_password = fields.Char(
        string="Hub password",
        compute='_compute_server_env',
        store=False,
        readonly=True,
    )
    config_api_url = fields.Char(
        string="Config API URL",
        compute='_compute_server_env',
        store=False,
        readonly=True,
    )
    config_api_username = fields.Char(
        string="Config API Username",
        compute='_compute_server_env',
        store=False,
        readonly=True,
    )
    config_api_password = fields.Char(
        string="Config API Password",
        compute='_compute_server_env',
        store=False,
        readonly=True,
    )
    import_payment_request_from_date = fields.Datetime(
        string="Import payment request from date",
        readonly=True,
    )
    import_sale_order_from_date = fields.Datetime(
        string="Import Sale order from date",
        readonly=True,
    )

    _sql_constraints = [
        ('unique_hub_backend', 'unique(name)',
         _("A backend-end should always be unique."))
    ]

    @property
    def _server_env_fields(self):
        return (
            'hub_api_location',
            'hub_api_username',
            'hub_api_password',
            'config_api_url',
            'config_api_username',
            'config_api_password')

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
        # We create a Hub Client API here, so we can create the
        # client once (lazily on the first use) and propagate it
        # through all the sync session, instead of recreating a client
        # in each backend adapter usage.
        #
        hub_api = HubAPI(
            hub_url=self.hub_api_location,
            hub_username=self.hub_api_username,
            hub_password=self.hub_api_password,
            config_url=self.config_api_url,
            config_username=self.config_api_username,
            config_password=self.config_api_password)
        _super = super(HubBackend, self)
        # from the components we'll be able to do: self.work.hub_api
        with _super.work_on(model_name, hub_api=hub_api, **kwargs) as work:
            yield work

    @api.multi
    def _import_from_date(self, model, from_date_field):
        import_start_time = datetime.now()
        for backend in self:
            from_date = backend[from_date_field]
            if from_date:
                from_date = fields.Datetime.from_string(from_date)
            else:
                from_date = None
            self.env[model].with_delay().import_batch(
                backend,
                filters={'from': from_date,
                         'to': import_start_time}
            )
        # TODO: update this comment
        # Records from Hub are imported based on their `created_at`
        # date.  This date is set on Hub at the beginning of a
        # transaction, so if the import is run between the beginning and
        # the end of a transaction, the import of a record may be
        # missed.  That's why we add a small buffer back in time where
        # the eventually missed records will be retrieved.  This also
        # means that we'll have jobs that import twice the same records,
        # but this is not a big deal because they will be skipped when
        # the last `sync_date` is the same.
        next_time = import_start_time - timedelta(seconds=IMPORT_DELTA_BUFFER)
        next_time = fields.Datetime.to_string(next_time)
        self.write({from_date_field: next_time})

    @api.multi
    def import_payment_requests(self):
        self._import_from_date(
            'hub.payment.request', 'import_payment_request_from_date')
        return True
