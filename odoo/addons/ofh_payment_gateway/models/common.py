# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class PaymentGatewayLineMapper(Component):
    _name = 'payment.gateway.line.mapper'
    _inherit = 'importer.base.mapper'
    _apply_on = 'ofh.payment.gateway.line'

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

    @mapping
    def payment_gateway_id(self, record):
        track_id = self.track_id(record).get('track_id')
        response_code = record.get('Response Code', '111111')

        if not track_id or response_code[0][:1] != '1':
            return {}

        domain = [('track_id', '=', track_id)]

        payment_status = self.payment_status(record).get('payment_status')

        pg_model = self.env['ofh.payment.gateway']

        if payment_status in ('refund', 'void'):
            domain.append(('payment_status', 'in', ('refund', 'void')))
        else:
            domain.append(('payment_status', 'not in', ('refund', 'void')))

        payment_gateway = pg_model.search(domain, limit=1)

        if not payment_gateway or payment_status in ('refund', 'void'):
            payment_gateway = pg_model.create({'name': track_id}
                                              )

        return {'payment_gateway_id': payment_gateway.id}

    @mapping
    def entity(self, record):
        return {}


class PaymentGatewayLineRecordImporter(Component):
    _name = 'payment.gateway.line.record.importer'
    _inherit = 'importer.record'
    _apply_on = ['ofh.payment.gateway.line']

    odoo_unique_key = 'name'

    def skip_it(self, values, origin_values) -> dict:
        """ Return True if the response code does not starts with 1.

        Arguments:
            values {dict} -- Mapped values
            origin_values {dict} -- Original raw data.
        """
        # TODO: logically this should be put in coresponding modules not here.
        # but somehow the inheritance didn't work for me, I may be missing
        # something, we will fix it later on.
        response_code = origin_values.get('Response Code', '111111')
        response_message = origin_values.get('3rd Party Response Message', '')
        provider = values.get('provider')
        acquirer_bank = values.get('acquirer_bank')

        if provider == 'checkout' and response_code[0][:1] != '1':
            return {'message': "Payment Gateway not applicable for import"}
        if provider == 'fort' and response_message != 'Approved':
            return {'message': "Payment Gateway not applicable for import"}
        if provider == 'fort' and acquirer_bank == 'cib':
            return {'message': "Payment Gateway not applicable for import"}
        return {}

    def required_keys(self, create=False):
        """Keys that are mandatory to import a line."""
        return {}

    def run(self, record, **kw):
        result = super(PaymentGatewayLineRecordImporter, self).run(
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


class PaymentGatewayLineHandler(Component):
    _inherit = 'importer.odoorecord.handler'
    _name = 'payment.gateway.line.handler'
    _apply_on = ['ofh.payment.gateway.line']
