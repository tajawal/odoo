# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class HubPaymentChargeImportMapper(Component):
    _name = 'hub.payment.charge.import.mapper'
    _inherit = 'hub.import.mapper'
    _apply_on = 'hub.payment.charge'

    direct = [
        ('charge_id', 'charge_id'),
        ('track_id', 'track_id'),
        ('auth_code', 'auth_code'),
        ('status', 'status'),
        ('currency', 'currency'),
        ('value', 'total'),
        ('provider', 'provider'),
        ('payment_mode', 'payment_mode'),
        ('card_type', 'card_type'),
        ('mid', 'mid'),
        ('last_four', 'last_four'),
        ('card_bin', 'card_bin'),
    ]

    @mapping
    def created_at(self, record) -> dict:
        dt = datetime.strptime(record['created_at'], "%Y-%m-%d %H:%M:%S")
        return {'created_at': dt}

    @mapping
    def updated_at(self, record) -> dict:
        dt = datetime.strptime(record['updated_at'], "%Y-%m-%d %H:%M:%S")

        return {'updated_at': dt}

    @mapping
    def currency_id(self, record) -> dict:
        if 'currency' in record:
            currency = self.env['res.currency'].search(
                [('name', '=', record['currency'])], limit=1)
            if currency:
                return {'currency_id': currency.id}
        return {'currency_id': self.env.ref('base.AED').id}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}
