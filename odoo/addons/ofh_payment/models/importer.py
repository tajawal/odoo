# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime
from odoo import fields

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class HubPaymentImportMapper(Component):
    _name = 'hub.payment.import.mapper'
    _inherit = 'hub.import.mapper'
    _apply_on = 'hub.payment'

    direct = [
        ('track_id', 'track_id'),
        ('auth_code', 'auth_code'),
        ('payment_mode', 'payment_mode'),
        ('amount', 'total_amount'),
        ('payment_status', 'payment_status'),
        ('provider', 'provider'),
        ('source', 'source'),
        ('card_type', 'card_type'),
        ('mid', 'mid'),
        ('card_name', 'card_name'),
        ('card_bin', 'card_bin'),
        ('last_four', 'last_four'),
        ('payment_method', 'payment_method'),
        ('bank_name', 'bank_name'),
        ('source', 'source'),
        ('reference_id', 'reference_id'),
        ('is_3d_secure', 'is_3d_secure'),
        ('is_installment', 'is_installment'),
        ('id', 'external_id'),
    ]

    children = [
        ('charges', 'hub_charge_ids', 'hub.payment.charge')]

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


class HubPaymentImportMapChild(Component):
    _name = 'map.child.hub.payment.import'
    _inherit = 'base.map.child.import'
    _apply_on = 'hub.payment'

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


class HubPaymentImporter(Component):
    _name = 'hub.payment.importer'
    _inherit = 'hub.importer'
    _apply_on = ['hub.payment']

    def _is_uptodate(self, binding) -> bool:
        if not binding:
            return False    # The record has never been synchronised.

        assert self.hub_record

        sync_date = fields.Datetime.from_string(binding.sync_date)
        hub_date = fields.Datetime.from_string(
            self.hub_record.get('updated_at'))

        return hub_date < sync_date
