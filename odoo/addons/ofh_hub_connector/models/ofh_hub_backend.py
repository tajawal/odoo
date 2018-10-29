# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from contextlib import contextmanager
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.addons.ofh_hub_connector.components.backend_adapter import HubAPI

_logger = logging.getLogger(__name__)

IMPORT_DELTA_BUFFER = 600   # seconds


class HubBackend(models.Model):

    _name = 'hub.backend'
    _description = 'Hub Backend'
    _inherit = 'connector.backend'

    hub_api_location = fields.Char(
        string='HUB API URL',
        required=True,
    )
    token = fields.Text(
        required=True,
    )
    username = fields.Char(
        required=True,
    )
    password = fields.Char(
        required=True,
    )
    import_payment_request_from_date = fields.Datetime(
        string="Import payment request from date",
    )
    import_sale_order_from_date = fields.Datetime(
        string="Import Sale order from date",
    )

    _sql_constraints = [
        ('unique_hub_api_locaiton', 'unique(hub_api_location)',
         _("A backend-end should always be unique."))
    ]

    @contextmanager
    @api.multi
    def work_on(self, model_name, **kwargs):
        # We create a Hub Client API here, so we can create the
        # client once (lazily on the first use) and propagate it
        # through all the sync session, instead of recreating a client
        # in each backend adapter usage.
        #
        hub_api = HubAPI(
            url=self.hub_api_location,
            token=self.token,
            username=self.username,
            password=self.password)
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
