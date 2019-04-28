
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestOfhPaymentRequest(TransactionCase):

    def setUp(self):
        super(TestOfhPaymentRequest, self).setUp()

        self.pr_model = self.env['ofh.payment.request']
        self.payment_request_1 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_1')

    def test_compute_payment_request_status(self):
        # Payment Request 1
        self.assertEquals(
            self.payment_request_1.payment_request_status, 'ready')

        self.payment_request_1.order_id = False

        self.assertEquals(
            self.payment_request_1.payment_request_status, 'incomplete')
