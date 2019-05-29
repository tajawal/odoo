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
        ('value', 'total'),
        ('provider', 'provider'),
        ('source', 'source'),
        ('payment_mode', 'payment_mode'),
        ('card_type', 'card_type'),
        ('mid', 'mid'),
        ('last_four', 'last_four'),
        ('card_bin', 'card_bin'),
        ('charge_id', 'external_id'),
        ('payment_method', 'payment_method'),
        ('reference_id', 'reference_id'),
        ('bank_name', 'bank_name'),
        ('card_owner', 'card_owner'),
        ('is_3d_secure', 'is_3d_secure'),
        ('is_installment', 'is_installment'),
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


class HubPaymentChargeImportMapChild(Component):
    _name = 'map.child.hub.payment.charge.import'
    _inherit = 'base.map.child.import'
    _apply_on = 'hub.payment.charge'

    def format_items(self, items_values):
        """
        Format the values of the items mapped from the child Mappers.

        It can be overridden for instance to add the Odoo
        relationships commands ``(6, 0, [IDs])``, ...

        As instance, it can be modified to handle update of existing
        items: check if an 'id' has been defined by
        :py:meth:`get_item_values` then use the ``(1, ID, {values}``)
        command

        :param items_values: list of values for the items to create
        :type items_values: list

        """
        items = []
        for values in items_values:
            if 'external_id' not in values:
                continue
            binding = self.model.search(
                [('external_id', '=', values.get('external_id'))])
            if binding:
                items.append((1, binding.id, values))
                continue
            else:
                items.append((0, 0, values))

        return items
