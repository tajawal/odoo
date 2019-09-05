# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from odoo import fields, models, api

ACQUIRER_BANK = {
    'Al Rajhi': 'rajhi',
    'TAJAWAL GENERAL TRADING LLC': 'mashreq',
    'Al Mosafer GW Services': 'sabb',
}

PAYMENT_STATUSES = {
    'Capture': 'capture',
    'Authorisation': 'auth',
    'Void Authorisation': 'void',
    'Refund': 'refund',
}

APPLE_PAY = "Apple Pay"


class PaymentGatewayLineMapper(Component):
    _inherit = 'payment.gateway.line.mapper'

    @mapping
    def name(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).name(record)
        return {'name': record.get('Action ID')}

    @mapping
    def provider(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).provider(record)
        return {'provider': 'checkout'}

    @mapping
    def acquirer_bank(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).acquirer_bank(record)
        acquirer_bank = record.get('Business Name')

        return {'acquirer_bank': ACQUIRER_BANK.get(acquirer_bank, 'sabb')}

    @mapping
    def track_id(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).track_id(record)
        return {'track_id': record.get('Reference')}

    @mapping
    def auth_code(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).auth_code(record)
        auth_code = record.get('Auth Code')
        if len(auth_code) < 6:
            auth_code = auth_code.rjust(6, '0')
        return {'auth_code': auth_code}

    @mapping
    def payment_method(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).payment_method(record)
        return {'payment_method': record.get('Payment Method')}

    @mapping
    def transaction_date(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).transaction_date(record)
        # TODO: correct the format 6/30/2019 11:45:23 PM
        dt = datetime.strptime(record.get('Action Date UTC'), '%m/%d/%y %H:%M')
        return {'transaction_date': fields.Datetime.to_string(dt)}

    @mapping
    def total(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).total(record)
        return {'total': float(record.get('Amount'))}

    @mapping
    def currency_id(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).currency_id(record)
        currency = record.get('Currency')
        if not currency:
            return {}
        return {'currency_id': self.env.ref('base.{}'.format(currency)).id}

    @mapping
    def payment_status(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).payment_status(record)
        status = record.get('Action Type', '')
        return {'payment_status': PAYMENT_STATUSES.get(status, '')}

    @mapping
    def card_name(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).card_name(record)
        cc_name = record.get('Card Holder Name')
        if not cc_name:
            return {}
        return {'card_name': record.get('Card Holder Name')}

    @mapping
    def card_number(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).card_number(record)
        card_number = record.get('CC Number')
        if not card_number:
            return {}
        return {'card_number': card_number}

    @mapping
    def card_bin(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).card_bin(record)
        card_bin = record.get('CC BIN')
        if not card_bin:
            return {}
        return {'card_bin': card_bin}

    @mapping
    def card_bank(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).card_bank(record)
        card_bank = record.get('Issuing Bank')
        if not card_bank:
            return {}
        return {'card_bank': card_bank}

    @mapping
    def is_card_mada(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).is_card_mada(record)
        card_type = record.get('UDF1')
        return {'is_card_mada': card_type == 'MADA'}

    @mapping
    def is_apple_pay(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).is_apple_pay(record)
        card_wallet_type = record.get('Card Wallet Type')
        return {'is_apple_pay': card_wallet_type == APPLE_PAY}

    @mapping
    def card_expiry_year(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).card_expiry_year(record)
        card_expiry_year = record.get('Expiry Year')
        if not card_expiry_year:
            return {}
        return {'card_expiry_year': card_expiry_year}

    @mapping
    def card_expiry_month(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).card_expiry_month(record)
        card_expiry_month = record.get('Expiry Month')
        if not card_expiry_month:
            return {}
        return {'card_expiry_month': card_expiry_month}

    @mapping
    def response_description(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).response_description(
                record)
        response_description = record.get('Response Description')
        if not response_description:
            return {}
        return {'response_description': response_description}

    @mapping
    def customer_email(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).customer_email(record)
        customer_email = record.get('Customer Email')
        if not customer_email:
            return {}
        return {'customer_email': customer_email}

    @mapping
    def cvv_check(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).cvv_check(record)
        cvv_check = record.get('CVV Check')
        if not cvv_check:
            return {}
        return {'cvv_check': cvv_check}

    @mapping
    def is_3d_secure(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).is_3d_secure(record)
        return {'is_3d_secure': record.get('3D Secure Payment', False)}

    @mapping
    def arn(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).arn(record)
        arn = record.get('Acquirer Reference ID')
        if not arn:
            return {}
        return {'arn': arn}

    @mapping
    def payment_id(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).payment_id(record)
        payment_id = record.get('Payment ID')
        if not payment_id:
            return {}
        return {'payment_id': payment_id}

    @mapping
    def server_ip(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).server_ip(record)
        server_ip = record.get('Server IP')
        if not server_ip:
            return {}
        return {'server_ip': server_ip}

    @mapping
    def reported_mid(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).reported_mid(record)
        reported_mid = record.get('UDF4')
        if not reported_mid:
            return {}
        return {'reported_mid': reported_mid}

    @mapping
    def entity(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).entity(record)
        return {'entity': record.get('Entity')}

    @mapping
    def payment_gateway_id(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).payment_gateway_id(record)

        response_code = record.get('Response Code', '111111')
        if response_code[0][:1] != '1':
            return {}

        unique_id = record.get('Action ID')
        payment_id = record.get('Payment ID')

        if not unique_id:
            return {}
        pg_model = self.env["ofh.payment.gateway"]
        payment_gateway = pg_model.search(
            [('payment_id', '=', payment_id)], limit=1)

        if payment_gateway:
            if payment_gateway.payment_status in ('refund', 'void'):
                pg_created = pg_model.create({
                    'name': unique_id
                })
                return {'payment_gateway_id': pg_created.id}
            else:
                return {'payment_gateway_id': payment_gateway.id}
        else:
            pg_created = pg_model.create({
                'name': unique_id
            })
            return {'payment_gateway_id': pg_created.id}


class PaymentGatewayLineHandler(Component):
    _inherit = 'payment.gateway.line.handler'

    def odoo_find_domain(self, values, orig_values):
        """Domain to find the GDS invoice line record in odoo."""
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineHandler, self).odoo_find_domain(
                values, orig_values)
        return [
            ('provider', '=', 'checkout'),
            (self.unique_key, '=', values.get('Action ID'))]
