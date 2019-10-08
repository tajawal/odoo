# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import fields
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

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

APPLE_PAY = "apple pay"
BANK_MASHREQ = 'mashreq'
BANK_SABB = 'sabb'
BANK_AMEX = 'amex'

CURRENCY_SAR = 'SAR'

MID_1 = "80000404"
MID_2 = "80000455"


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

        return {'acquirer_bank': self._get_acquirer_bank(record)}

    def _get_acquirer_bank(self, record):
        acquirer_bank = record.get('Business Name')
        acquirer_bank = ACQUIRER_BANK.get(acquirer_bank, 'sabb')
        payment_method = record.get('Payment Method', '').lower()

        if acquirer_bank == BANK_MASHREQ and payment_method == BANK_AMEX:
            acquirer_bank = BANK_AMEX

        return acquirer_bank

    @mapping
    def track_id(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).track_id(record)
        return {'track_id': record.get('Reference', '')}

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
            return super(PaymentGatewayLineMapper, self).transaction_date(
                record)
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
        return {'is_card_mada': self._get_is_card_mada(record)}

    def _get_is_card_mada(self, record):
        card_type = record.get('UDF1')
        return card_type.lower() == 'MADA'

    @mapping
    def is_apple_pay(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).is_apple_pay(record)
        return {'is_apple_pay': self._get_is_apple_pay(record)}

    def _get_is_apple_pay(self, record):
        card_wallet_type = record.get('Card Wallet Type')
        return card_wallet_type.lower() == APPLE_PAY

    @mapping
    def card_expiry_year(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).card_expiry_year(
                record)
        card_expiry_year = record.get('Expiry Year')
        if not card_expiry_year:
            return {}
        return {'card_expiry_year': card_expiry_year}

    @mapping
    def card_expiry_month(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')
        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).card_expiry_month(
                record)
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

        udf4 = record.get('UDF4')
        udf1 = record.get('UDF1')

        reported_mid = udf4

        if not reported_mid:
            currency = record.get('Currency')
            card_bin = record.get('CC BIN')
            acquirer_bank = self._get_acquirer_bank(record)
            is_apple_pay = self._get_is_apple_pay(record)
            is_card_mada = self._get_is_card_mada(record)

            if acquirer_bank == BANK_SABB and is_card_mada and currency == CURRENCY_SAR:
                return {'reported_mid': MID_1}

            if acquirer_bank == BANK_SABB and is_apple_pay and card_bin == '506968':
                return {'reported_mid': MID_1}

            if acquirer_bank == BANK_SABB and is_apple_pay and currency == CURRENCY_SAR:
                return {'reported_mid': MID_2}

            if acquirer_bank == BANK_SABB and currency == CURRENCY_SAR and not udf4 and not udf1:
                return {'reported_mid': MID_2}

        return {'reported_mid': reported_mid}

    @mapping
    def entity(self, record):
        checkout_backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')

        if self.backend_record != checkout_backend:
            return super(PaymentGatewayLineMapper, self).entity(record)

        return {'entity': record.get('Entity').lower()}


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
