
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from vcr import VCR
from os.path import dirname, join

recorder = VCR(
    record_mode='once',
    cassette_library_dir=join(dirname(__file__), 'fixtures/cassettes'),
    path_transformer=VCR.ensure_suffix('.yaml'),
    filter_headers=['Authorization'],
)


class TestOfhPaymentRequest(TransactionCase):

    def setUp(self):
        super(TestOfhPaymentRequest, self).setUp()

        self.pr_model = self.env['ofh.payment.request']
        self.payment_request_1 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_1')
        self.payment_request_2 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_2')
        # Change Fee LineItem test for Refund
        self.payment_request_refund = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_refund')
        # Change Fee LineItem test for Amendment
        self.payment_request_charge = self.env.ref(
            'ofh_payment_request.'
            'ofh_payment_request_gds_charge_with_change_fee')

    def test_compute_fees(self):
        # Paymemnt Request 1
        self.assertAlmostEquals(self.payment_request_1.fare_difference, 280)
        self.assertAlmostEquals(self.payment_request_1.penalty, 300)
        self.assertAlmostEquals(self.payment_request_1.change_fee, 80)
        self.assertAlmostEquals(self.payment_request_1.booking_fee, 0)
        self.assertAlmostEquals(self.payment_request_1.discount, 0)
        self.assertAlmostEquals(self.payment_request_1.input_vat_amount, 0)
        self.assertAlmostEquals(self.payment_request_1.output_vat_amount, 0)
        self.assertAlmostEquals(self.payment_request_1.adm_amount, 0)
        self.assertFalse(self.payment_request_1.loss_type)
        self.assertEqual(self.payment_request_1.tax_code, 'sz')

        self.payment_request_1.fees = \
            '{"fareDifference": 280,"changeFee": 80,"penalty": 300,' \
            '"outputVat": 5}'

        self.assertAlmostEquals(self.payment_request_1.output_vat_amount, 5)
        self.assertEqual(self.payment_request_1.tax_code, 'ss')

        # Payment Request 2
        self.assertAlmostEquals(self.payment_request_2.fare_difference, 900)
        self.assertAlmostEquals(self.payment_request_2.penalty, 420)
        self.assertAlmostEquals(self.payment_request_2.change_fee, 0)
        self.assertAlmostEquals(self.payment_request_2.booking_fee, 15)
        self.assertAlmostEquals(self.payment_request_2.discount, 0)
        self.assertAlmostEquals(self.payment_request_2.input_vat_amount, 0)
        self.assertAlmostEquals(self.payment_request_2.output_vat_amount, 0)
        self.assertAlmostEquals(self.payment_request_2.adm_amount, 0)
        self.assertFalse(self.payment_request_2.loss_type)
        self.assertEqual(self.payment_request_2.tax_code, 'sz')

        # Case where the fees field is not set:
        self.payment_request_1.fees = False
        self.assertAlmostEquals(self.payment_request_1.fare_difference, 0)
        self.assertAlmostEquals(self.payment_request_1.penalty, 0)
        self.assertAlmostEquals(self.payment_request_1.change_fee, 0)
        self.assertAlmostEquals(self.payment_request_1.booking_fee, 0)
        self.assertAlmostEquals(self.payment_request_1.discount, 0)
        self.assertAlmostEquals(self.payment_request_1.input_vat_amount, 0)
        self.assertAlmostEquals(self.payment_request_1.output_vat_amount, 0)
        self.assertAlmostEquals(self.payment_request_1.adm_amount, 0)
        self.assertFalse(self.payment_request_1.loss_type)
        self.assertEqual(self.payment_request_1.tax_code, 'sz')

        # Payment Request Refund with Change Fee
        self.assertAlmostEquals(
            self.payment_request_refund.fare_difference, 1548)
        self.assertAlmostEquals(
            self.payment_request_refund.penalty, 0)
        self.assertAlmostEquals(
            self.payment_request_refund.change_fee, 25)
        self.assertAlmostEquals(
            self.payment_request_refund.booking_fee, 0)
        self.assertAlmostEquals(
            self.payment_request_refund.discount, 0)
        self.assertAlmostEquals(
            self.payment_request_refund.input_vat_amount, 0)
        self.assertAlmostEquals(
            self.payment_request_refund.output_vat_amount, 6)
        self.assertAlmostEquals(
            self.payment_request_refund.adm_amount, 0)
        self.assertFalse(
            self.payment_request_refund.loss_type)
        self.assertEqual(self.payment_request_refund.tax_code, 'ss')

        # Payment Request Amendment with Change Fee
        self.assertAlmostEquals(
            self.payment_request_charge.fare_difference, 100)
        self.assertAlmostEquals(
            self.payment_request_charge.penalty, 50)
        self.assertAlmostEquals(
            self.payment_request_charge.change_fee, 25)
        self.assertAlmostEquals(
            self.payment_request_charge.booking_fee, 0)
        self.assertAlmostEquals(
            self.payment_request_charge.discount, 0)
        self.assertAlmostEquals(
            self.payment_request_charge.input_vat_amount, 44)
        self.assertAlmostEquals(
            self.payment_request_charge.output_vat_amount, 8)
        self.assertAlmostEquals(
            self.payment_request_charge.adm_amount, 0)
        self.assertFalse(
            self.payment_request_charge.loss_type)
        self.assertEqual(
            self.payment_request_charge.tax_code, 'ss')

        # Manual output vat amount
        self.payment_request_charge.manual_output_vat_amount = 5
        self.assertAlmostEquals(
            self.payment_request_charge.output_vat_amount, 5)
        self.payment_request_charge.manual_output_vat_amount = 0
        self.assertAlmostEquals(
            self.payment_request_charge.output_vat_amount, 8)

        # TAX CODE negative output vat
        self.payment_request_charge.manual_output_vat_amount = -5
        self.assertEqual(
            self.payment_request_charge.tax_code, 'sz')

        self.payment_request_charge.manual_output_vat_amount = +5
        self.assertEqual(
            self.payment_request_charge.tax_code, 'ss')

    def test_compute_payment_reference(self):
        self.assertEquals(
            self.payment_request_1.charge_id,
            self.payment_request_1.payment_reference)

        self.payment_request_1.manual_payment_reference = 'manual_charge'
        self.assertEquals(
            self.payment_request_1.manual_payment_reference,
            self.payment_request_1.payment_reference)

        self.payment_request_1.manual_payment_reference = False
        self.assertEquals(
            self.payment_request_1.charge_id,
            self.payment_request_1.payment_reference)
