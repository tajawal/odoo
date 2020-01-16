# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime
from odoo import fields, _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import IDMissingInBackend

_logger = logging.getLogger(__name__)

PROVIDER_WALLET = 'wallet'


class HubPaymentImportMapper(Component):
    _inherit = 'hub.payment.import.mapper'

    @mapping
    def pg_matching_status(self, record):
        if record['provider'] == PROVIDER_WALLET:
            return {'pg_matching_status': 'not_applicable'}
        return {'pg_matching_status': 'unmatched'}
