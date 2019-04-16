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


class TestOfhPayment(TransactionCase):

    def setUp(self):
        super(TestOfhPayment, self).setUp()

        self.pr_model = self.env['ofh.payment']
        self.payment_1 = self.env.ref(
            'ofh_payment.ofh_payment_1')

    def test_payment(self):
        # Payment 1
        self.assertEquals(
            self.payment_1.track_id, "f610e7ec-0725-4fa1-bc81-759924f580e2")
        self.assertEquals(self.payment_1.provider, "checkoutcom")
        self.assertAlmostEquals(self.payment_1.total_amount, 310.34)
        self.assertEquals(self.payment_1.auth_code, "081124")
        self.assertEquals(self.payment_1.payment_status, "10000")
        self.assertEquals(self.payment_1.payment_mode, "Visa")
        self.assertEquals(self.payment_1.created_at, "2019-01-20 00:00:00")
        self.assertEquals(self.payment_1.updated_at, "2019-01-20 00:00:00")
