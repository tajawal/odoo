# Copyright 2019 Seera Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class BankSettlementMapper(Component):
    _name = 'bank.settlement.mapper'
    _inherit = 'importer.base.mapper'
    _apply_on = 'ofh.bank.settlement'

    @mapping
    def name(self, record):
        return {}

    @mapping
    def settlement_date(self, record):
        return {}

    @mapping
    def bank_name(self, record):
        return {}

    @mapping
    def reported_mid(self, record):
        return {}

    @mapping
    def account_number(self, record):
        return {}

    @mapping
    def payment_method(self, record):
        return {}

    @mapping
    def is_mada(self, record):
        return {}

    @mapping
    def transaction_date(self, record):
        return {}

    @mapping
    def card_number(self, record):
        return {}

    @mapping
    def currency_id(self, record):
        return {}

    @mapping
    def gross_amount(self, record):
        return {}

    @mapping
    def net_transaction_amount(self, record):
        return {}

    @mapping
    def merchant_charge_amount(self, record):
        return {}

    @mapping
    def merchant_charge_vat(self, record):
        return {}

    @mapping
    def payment_status(self, record):
        return {}

    @mapping
    def auth_code(self, record):
        return {}

    @mapping
    def is_3d_secure(self, record):
        return {}

    @mapping
    def posting_date(self, record):
        return {}


class BankSettlementRecordImporter(Component):

    _name = 'bank.settlement.record.importer'
    _inherit = 'importer.record'
    _apply_on = ['ofh.bank.settlement']

    odoo_unique_key = 'name'

    def skip_it(self, values, origin_values) -> dict:
        """ Return True if the response code does not starts with 1."""
        return {}

    def required_keys(self, create=False):
        """Keys that are mandatory to import a line."""
        return {}

    def run(self, record, **kw):
        result = super(BankSettlementRecordImporter, self).run(
            record, **kw)
        msg = ' '.join([
            '{} import chunk completed'.format(
                self.tracker.log_prefix.upper()),
            '[created: {created}]',
            '[updated: {updated}]',
            '[skipped: {skipped}]',
            '[errored: {errored}]',
        ]).format(**self.tracker.get_counters())
        self.env.user.notify_info(msg)
        return result


class BankSettlementHandler(Component):
    _name = 'bank.settlement.handler'
    _inherit = 'importer.odoorecord.handler'
    _apply_on = ['ofh.bank.settlement']
