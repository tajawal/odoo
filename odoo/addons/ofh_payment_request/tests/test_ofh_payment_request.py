
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestOfhPaymentRequest(TransactionCase):

    def setUp(self):
        super(TestOfhPaymentRequest, self).setUp()

        self.payment_request_1 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_1')
        self.payment_request_2 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_2')

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

    def test_compute_payment_request_status(self):
        # Payment Request 1
        self.assertEquals(
            self.payment_request_1.payment_request_status, 'ready')
        self.assertEquals(self.payment_request_1.sap_status, 'pending')
        self.assertEquals(self.payment_request_1.state, 'pending')

        # Payment Request 2
        self.assertEquals(
            self.payment_request_2.payment_request_status, 'ready')
        self.assertEquals(self.payment_request_2.sap_status, 'pending')
        self.assertEquals(self.payment_request_2.state, 'pending')
