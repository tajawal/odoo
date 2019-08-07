# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from odoo import fields


class PaymentGatewayMapper(Component):
    _inherit = 'payment.gateway.mapper'

    @mapping
    def created_at(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).created_at(record)
        return {'created_at': datetime.today().strftime("%d-%m-%y")}

    @mapping
    def updated_at(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).updated_at(record)
        return {'updated_at': datetime.today().strftime("%d-%m-%y")}

    @mapping
    def name(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).name(record)
        return {'name': 'checkout'}

    @mapping
    def provider(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).provider(record)
        return {'provider': 'checkout'}

    @mapping
    def payment_gateway_id(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).payment_gateway_id(record)
        return {'payment_gateway_id': record.get('Action ID')}

    @mapping
    def acquirer_bank(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).acquirer_bank(record)
        acquirer_bank = record.get('Business Name')
        if acquirer_bank == 'Al Rajhi':
            return {'acquirer_bank': 'rajhi'}
        elif acquirer_bank == 'TAJAWAL GENERAL TRADING LLC':
            return {'acquirer_bank': 'mashreq'}
        elif acquirer_bank == 'Al Mosafer GW Services':
            return {'acquirer_bank': 'sabb'}

    @mapping
    def track_id(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).track_id(record)
        return {'track_id': record.get('Reference')}

    @mapping
    def auth_code(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).auth_code(record)
        return {'auth_code': record.get('Auth Code')}

    @mapping
    def payment_method(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).payment_method(record)
        return {'payment_method': record.get('Payment Method')}

    @mapping
    def payment_by(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).payment_by(record)
        if not record.get('CC Number'):
            return {}
        return {'payment_by': 'Credit Card'}

    @mapping
    def transaction_date(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).transaction_date(record)
        # TODO: correct the format 6/30/2019 11:45:23 PM
        dt = datetime.strptime(record.get('Action Date UTC'), '%m/%d/%y %H:%M')
        return {'transaction_date': fields.Date.to_string(dt)}

    @mapping
    def total(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).total(record)
        return {'total': float(record.get('Amount'))}

    @mapping
    def currency_id(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).currency_id(record)
        currency = record.get('Currency')
        if not currency:
            return {}
        return {'currency_id': self.env.ref('base.{}'.format(currency)).id}

    @mapping
    def payment_status(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).payment_status(record)
        return {'payment_status': record.get('Action Type')}

    @mapping
    def card_name(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).card_name(record)
        cc_name = record.get('Card Holder Name')
        if not cc_name:
            return {}
        return {'card_name': record.get('Card Holder Name')}

    @mapping
    def card_number(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).card_number(record)
        card_number = record.get('CC Number')
        if not card_number:
            return {}
        return {'card_number': card_number}

    @mapping
    def card_bin(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).card_bin(record)
        card_bin = record.get('CC BIN')
        if not card_bin:
            return {}
        return {'card_bin': card_bin}

    @mapping
    def card_bank(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).card_bank(record)
        card_bank = record.get('Issuing Bank')
        if not card_bank:
            return {}
        return {'card_bank': card_bank}

    @mapping
    def card_type(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).card_type(record)
        card_type = record.get('UDF1')
        if not card_type:
            return {}
        if card_type == 'MADA':
            return {'card_type': 'Yes'}
        else:
            return {'card_type': 'No'}

    @mapping
    def card_wallet_type(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).card_wallet_type(record)
        card_wallet_type = record.get('Card Wallet Type')
        if not card_wallet_type:
            return {}
        return {'card_wallet_type': card_wallet_type}

    @mapping
    def card_expiry_year(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).card_expiry_year(record)
        card_expiry_year = record.get('Expiry Year')
        if not card_expiry_year:
            return {}
        return {'card_expiry_year': card_expiry_year}

    @mapping
    def card_expiry_month(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).card_expiry_month(record)
        card_expiry_month = record.get('Expiry Month')
        if not card_expiry_month:
            return {}
        return {'card_expiry_month': card_expiry_month}

    @mapping
    def response_description(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).response_description(record)
        response_description = record.get('Response Description')
        if not response_description:
            return {}
        return {'response_description': response_description}

    @mapping
    def customer_email(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).customer_email(record)
        customer_email = record.get('Customer Email')
        if not customer_email:
            return {}
        return {'customer_email': customer_email}

    @mapping
    def cvv_check(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).cvv_check(record)
        cvv_check = record.get('CVV Check')
        if not cvv_check:
            return {}
        return {'cvv_check': cvv_check}

    @mapping
    def is_3d_secure(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).is_3d_secure(record)
        is_3d_secure = record.get('3D Secure Payment')
        if not is_3d_secure:
            return {}
        return {'is_3d_secure': is_3d_secure}

    @mapping
    def arn(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).arn(record)
        arn = record.get('Acquirer Reference ID')
        if not arn:
            return {}
        return {'arn': arn}

    @mapping
    def payment_id(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).payment_id(record)
        payment_id = record.get('Payment ID')
        if not payment_id:
            return {}
        return {'payment_id': payment_id}

    @mapping
    def server_ip(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).server_ip(record)
        server_ip = record.get('Server IP')
        if not server_ip:
            return {}
        return {'server_ip': server_ip}

    @mapping
    def reported_mid(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayMapper, self).reported_mid(record)
        reported_mid = record.get('UDF4')
        if not reported_mid:
            return {}
        return {'reported_mid': reported_mid}


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
