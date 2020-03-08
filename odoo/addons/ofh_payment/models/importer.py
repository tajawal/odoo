# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime
from odoo import fields, _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import IDMissingInBackend

_logger = logging.getLogger(__name__)


class HubPaymentImportMapper(Component):
    _name = 'hub.payment.import.mapper'
    _inherit = 'hub.import.mapper'
    _apply_on = 'hub.payment'

    direct = [
        ('track_id', 'track_id'),
        ('auth_code', 'auth_code'),
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
        ('reference_id', 'reference_id'),
        ('is_apple_pay', 'is_apple_pay'),
        ('is_mada', 'is_mada'),
        ('is_3d_secure', 'is_3d_secure'),
        ('is_mada', 'is_mada'),
        ('is_apple_pay', 'is_apple_pay'),
        ('is_installment', 'is_installment'),
        ('id', 'external_id'),
        ('file_id', 'file_id'),
        ('file_reference', 'file_reference'),
        ('payment_category', 'payment_category'),
        ('rrn_no', 'rrn_no'),
        ('iban', 'iban'),
        ('cashier_id', 'cashier_id'),
        ('successfactors_id', 'successfactors_id'),
        ('ahs_group_name', 'ahs_group_name'),
        ('store_id', 'store_id'),
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

    def _get_binding(self):
        """Override the binding method to take in consideration the constraint
        based on the group_id and the product_id for case of unify.
        """
        binding = self.env[self._apply_on[0]].search([
            ('backend_id', '=', self.backend_record.id),
            ('external_id', '=', self.hub_record.get('id'))],
            limit=1)
        if not binding:
            binding = self.binder.to_internal(self.external_id)

        return binding

    def _is_uptodate(self, binding) -> bool:
        if not binding:
            return False  # The record has never been synchronised.

        assert self.hub_record

        sync_date = fields.Datetime.from_string(binding.sync_date)
        hub_date = fields.Datetime.from_string(
            self.hub_record.get('updated_at'))

        return hub_date < sync_date

    def run(self, external_id, payment_type='amendment', force=False):
        """[summary]

        Arguments:
            external_id {[type]} -- [description]

        Keyword Arguments:
            force {bool} -- [description] (default: {False})
        """
        self.external_id = external_id
        lock_name = 'import({}, {}, {}, {})'.format(
            self.backend_record._name,
            self.backend_record.id,
            self.work.model_name,
            external_id,
        )
        try:
            self.hub_record = self._get_hub_data(payment_type)
        except IDMissingInBackend:
            return _('Record does no longer exist in HUB.')

        if not self.hub_record:
            return True

        skip = self._must_skip()
        if skip:
            return skip
        binding = self._get_binding()

        if not force and self._is_uptodate(binding):
            return _('Already up-to-date.')

        # Important hack to make sure everytime the external
        # ID is the ID of the payment and not the track ID.
        self.external_id = self.hub_record.get('id')

        block = self._must_block(binding)
        if block:
            return block

        # Keep a lock on this import until the transaction is committed
        # The lock is kept since we have detected that the informations
        # will be updated into Odoo
        self.advisory_lock_or_retry(lock_name)
        self._before_import()

        # import the missing linked resources
        self._import_dependencies()
        map_record = self._map_data()

        if binding:
            record = self._update_data(map_record)
            self._update(binding, record)
        else:
            record = self._create_data(map_record)
            binding = self._create(record)

        self.binder.bind(self.external_id, binding)

        self._after_import(binding)

    def _get_hub_data(self, payment_type='amendment'):
        """ Return the raw hub data for ``self.external_id `` """
        return self.backend_adapter.read(
            self.external_id, {'payment_type': payment_type})
