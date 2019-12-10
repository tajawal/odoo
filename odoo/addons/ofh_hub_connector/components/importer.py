# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime

from odoo import _, fields
from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import IDMissingInBackend
from odoo.addons.queue_job.exception import NothingToDoJob

_logger = logging.getLogger(__name__)


class HubImporter(AbstractComponent):
    """ Base Importer for HUB. """

    _name = 'hub.importer'
    _inherit = ['base.importer', 'base.hub.connector']
    _usage = 'record.importer'

    def __init__(self, work_context):
        super(HubImporter, self).__init__(work_context)
        self.external_id = None
        self.hub_record = None

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        return

    def _before_import(self):
        """ Hook called before the import, when we have the Hub data """

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True, **kwargs)

    def _create(self, data):
        """ Create the OpenERP record """
        # special check on data before import
        self._validate_data(data)
        model = self.model.with_context(connector_no_export=True)
        binding = model.create(data)
        _logger.debug('%d created from hub %s', binding, self.external_id)
        return binding

    def _get_hub_data(self):
        """ Return the raw hub data for ``self.external_id `` """
        return self.backend_adapter.read(self.external_id)

    def _get_binding(self):
        return self.binder.to_internal(self.external_id)

    def _is_uptodate(self, binding) -> bool:
        """Check if record is already up-to-date.

        Arguments:
            binding {hub.binder} -- [Binder instance for hub records]

        Returns:
            bool -- Return True if the import should be skipped else False
        """
        if not binding:
            return False  # The record has never been synchronised.

        assert self.hub_record

        sync_date = fields.Datetime.from_string(binding.sync_date)
        hub_date = datetime.fromtimestamp(
            int(self.hub_record['updatedAt']['$date'].get(
                '$numberLong')) / 1000)

        return hub_date < sync_date

    def _import_dependency(
            self, external_id, binding_model, importer=None, always=False):
        """ Import a dependency.
        The importer class is a class or subclass of
        :class:`MagentoImporter`. A specific class can be defined.
        :param external_id: id of the related binding to import
        :param binding_model: name of the binding model for the relation
        :type binding_model: str | unicode
        :param importer_component: component to use for import
                                   By default: 'importer'
        :type importer_component: Component
        :param always: if True, the record is updated even if it already
                       exists, note that it is still skipped if it has
                       not been modified on Magento since the last
                       update. When False, it will import it only when
                       it does not yet exist.
        :type always: boolean
        """
        if not external_id:
            return
        binder = self.binder_for(binding_model)
        if always or not binder.to_internal(external_id):
            if importer is None:
                importer = self.component(
                    usage='record.importer', model_name=binding_model)
            try:
                importer.run(external_id)
            except NothingToDoJob:
                _logger.info(
                    'Dependency import of %s(%s) has been ignored.',
                    binding_model._name, external_id
                )

    def _import_dependencies(self):
        """ Import the dependencies for the record
        Import of dependencies can be done manually or by calling
        :meth:`_import_dependency` for each dependency.
        """
        return

    def _must_skip(self):
        """[summary]
        """

    def _must_block(self, binding) -> str:
        """Must block binding from being updated."""

    def _map_data(self):
        """ Returns an instance of
        :py:class:`~odoo.addons.connector.components.mapper.MapRecord`
        """
        return self.mapper.map_record(self.hub_record)

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding, data):
        """ Update an OpenERP record """
        # special check on data before import
        self._validate_data(data)
        binding.with_context(connector_no_export=True).write(data)
        _logger.debug('%d updated from hub %s', binding, self.external_id)
        return

    def _validate_data(self, data):
        """ Check if the values to import are correct
        Pro-actively check before the ``_create`` or
        ``_update`` if some fields are missing or invalid.
        Raise `InvalidDataError`
        """
        return

    def run(self, external_id, force=False):
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
            self.hub_record = self._get_hub_data()
        except IDMissingInBackend:
            return _('Record does no longer exist in HUB.')

        skip = self._must_skip()
        if skip:
            return skip
        binding = self._get_binding()

        if not force and self._is_uptodate(binding):
            return _('Already up-to-date.')

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


class HubBatchImporter(AbstractComponent):
    """ The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = 'hub.batch.importer'
    _inherit = ['base.importer', 'base.hub.connector']
    _usage = 'batch.importer'

    def run(self, filters=None):
        """ Run the synchronization """
        records = self.backend_adapter.search(filters)
        for record in records:
            self._import_record(record)

    def _import_record(self, external_id, job_options=None, **kwargs):
        """ Delay the import of the records"""
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(self.backend_record, external_id)
