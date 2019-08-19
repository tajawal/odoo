# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class PaymentGatewayMapper(Component):
    _name = 'payment.gateway.mapper'
    _inherit = 'importer.base.mapper'
    _apply_on = 'ofh.payment.gateway'

    @mapping
    def name(self, record):
        return {}

    @mapping
    def provider(self, record):
        return {}

    @mapping
    def acquirer_bank(self, record):
        return {}

    @mapping
    def track_id(self, record):
        return {}

    @mapping
    def auth_code(self, record):
        return {}

    @mapping
    def payment_method(self, record):
        return {}

    @mapping
    def payment_by(self, record):
        return {}

    @mapping
    def transaction_date(self, record):
        return {}

    @mapping
    def total(self, record):
        return {}

    @mapping
    def currency_id(self, record):
        return {}

    @mapping
    def payment_status(self, record):
        return {}

    @mapping
    def card_name(self, record):
        return {}

    @mapping
    def card_number(self, record):
        return {}

    @mapping
    def card_bin(self, record):
        return {}

    @mapping
    def card_bank(self, record):
        return {}

    @mapping
    def is_card_mada(self, record):
        return {}

    @mapping
    def is_apple_pay(self, record):
        return {}

    @mapping
    def card_expiry_year(self, record):
        return {}

    @mapping
    def card_expiry_month(self, record):
        return {}

    @mapping
    def response_description(self, record):
        return {}

    @mapping
    def customer_email(self, record):
        return {}

    @mapping
    def cvv_check(self, record):
        return {}

    @mapping
    def arn(self, record):
        return {}

    @mapping
    def payment_id(self, record):
        return {}

    @mapping
    def server_ip(self, record):
        return {}

    @mapping
    def reported_mid(self, record):
        return {}

    @mapping
    def is_3d_secure(self, record):
        return {}


class PaymentGatewayRecordImporter(Component):

    _name = 'payment.gateway.record.importer'
    _inherit = 'importer.record'
    _apply_on = ['ofh.payment.gateway']

    odoo_unique_key = 'name'

    def required_keys(self, create=False):
        """Keys that are mandatory to import a line."""
        return {}

    def run(self, record, **kw):
        result = super(PaymentGatewayRecordImporter, self).run(
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


class PaymentGatewayHandler(Component):
    _inherit = 'importer.odoorecord.handler'
    _name = 'payment.gateway.handler'
    _apply_on = ['ofh.payment.gateway']
