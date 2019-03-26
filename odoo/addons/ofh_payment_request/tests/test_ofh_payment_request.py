
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

    def test_compute_payment_request_status(self):
        # Payment Request 1
        self.assertEquals(
            self.payment_request_1.payment_request_status, 'ready')

        self.payment_request_1.order_reference = False

        self.assertEquals(
            self.payment_request_1.payment_request_status, 'incomplete')

    def test_action_supplier_status_not_appilicable(self):
        payment_requests = self.payment_request_1 + self.payment_request_2

        # Case 1: both payment request reconcilation status are pending
        payment_requests.action_supplier_status_not_appilicable()

        self.assertEquals(
            self.payment_request_1.reconciliation_status, 'not_applicable')
        self.assertEquals(
            self.payment_request_2.reconciliation_status, 'not_applicable')

        # Case 2: both payment requests reconcilation status are investigate
        payment_requests.write({'reconciliation_status': 'investigate'})
        payment_requests.action_supplier_status_not_appilicable()
        self.assertEquals(
            self.payment_request_1.reconciliation_status, 'not_applicable')
        self.assertEquals(
            self.payment_request_2.reconciliation_status, 'not_applicable')

        # Case 3: one of the payment request is already matched
        payment_requests.write({'reconciliation_status': 'pending'})
        self.payment_request_1.reconciliation_status = 'matched'
        payment_requests.action_supplier_status_not_appilicable()
        self.assertEquals(
            self.payment_request_1.reconciliation_status, 'matched')
        self.assertEquals(
            self.payment_request_2.reconciliation_status, 'not_applicable')

        # Case 4: one of the payment request is already not_applicable
        self.payment_request_1.reconciliation_status = 'pending'
        payment_requests.action_supplier_status_not_appilicable()
        self.assertEquals(
            self.payment_request_1.reconciliation_status, 'not_applicable')
        self.assertEquals(
            self.payment_request_2.reconciliation_status, 'not_applicable')

    def test_compute_need_to_investigate(self):

        # Case 1: reconciliation status is not in `matched` state.
        self.assertFalse(self.payment_request_1.need_to_investigate)

        # Case 2: Payment request is in matched state and has no order creation
        # date.
        self.payment_request_1.reconciliation_status = 'matched'
        self.assertFalse(self.payment_request_1.need_to_investigate)

        # Case 3: Payment is in matched state and has order creation date but
        # it is a refund PR.
        self.payment_request_1.order_created_at = '2018-10-09'
        self.payment_request_1.request_type = 'refund'
        self.assertFalse(self.payment_request_1.need_to_investigate)

        # Case 4: Payment request already investigated
        self.payment_request_1.is_investigated = True
        self.assertFalse(self.payment_request_1.need_to_investigate)

        # Case 5: All conditions are matched
        self.payment_request_1.is_investigated = False
        self.payment_request_1.request_type = 'charge'
        self.assertTrue(self.payment_request_1.need_to_investigate)

        # Case 6 order date is before request date
        self.payment_request_1.order_created_at = '2018-10-08'
        self.assertTrue(self.payment_request_1.need_to_investigate)

        # Case 7 order date is after request date
        self.payment_request_1.order_created_at = '2018-10-11'
        self.assertTrue(self.payment_request_1.need_to_investigate)

        # Case 8 order date is before request date and diff > 2
        self.payment_request_1.order_created_at = '2018-10-06'
        self.assertFalse(self.payment_request_1.need_to_investigate)

        # Case 9 order date is after request date
        self.payment_request_1.order_created_at = '2018-10-13'
        self.assertFalse(self.payment_request_1.need_to_investigate)

    def test_search_need_to_investigate(self):
        payment_requests = self.pr_model.search([])
        count = len(payment_requests)
        pr_no_investigations = self.pr_model.search(
            [('need_to_investigate', '=', False)])
        self.assertEquals(len(pr_no_investigations), count)

        pr_need_investigations = self.pr_model.search(
            [('need_to_investigate', '=', True)])
        self.assertFalse(pr_need_investigations)

        self.payment_request_1.write({
            'order_created_at': '2018-10-11',
            'request_type': 'charge',
            'reconciliation_status': 'matched',
        })

        pr_no_investigations = self.pr_model.search(
            [('need_to_investigate', '=', False)])
        self.assertEquals(len(pr_no_investigations), count - 1)

        pr_need_investigations = self.pr_model.search(
            [('need_to_investigate', '=', True)])
        self.assertTrue(pr_need_investigations)
        self.assertEquals(len(pr_need_investigations), 1)

        # Case created_at date and order_created_at date are timestamp format
        self.payment_request_1.created_at = '2018-10-11 23:50:55'
        self.payment_request_1.order_created_at = '2018-10-09 23:55:00'
        pr_need_investigations = self.pr_model.search(
            [('need_to_investigate', '=', True)])
        self.assertTrue(pr_need_investigations)

        self.payment_request_1.created_at = '2018-10-11 23:50:55'
        self.payment_request_1.order_created_at = '2018-10-08 22:00:00'
        pr_need_investigations = self.pr_model.search(
            [('need_to_investigate', '=', True)])
        self.assertFalse(pr_need_investigations)

        self.payment_request_1.is_investigated = True
        pr_need_investigations = self.pr_model.search(
            [('need_to_investigate', '=', True)])
        self.assertFalse(pr_need_investigations)

    def test_action_mark_as_investigated(self):

        self.payment_request_1.order_created_at = '2018-10-09'
        self.payment_request_1.reconciliation_status = 'matched'
        self.assertTrue(self.payment_request_1.need_to_investigate)

        self.payment_request_1.action_mark_as_investigated()

        self.assertTrue(self.payment_request_1.is_investigated)
        self.assertFalse(self.payment_request_1.need_to_investigate)

        self.payment_request_1.reconciliation_status = 'pending'
        self.payment_request_1.is_investigated = False
        self.payment_request_1.action_mark_as_investigated()

        self.assertFalse(self.payment_request_1.is_investigated)
        self.assertFalse(self.payment_request_1.need_to_investigate)

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

    def test_compute_supplier_reference(self):
        self.assertEquals(
            self.payment_request_1.hub_supplier_reference,
            self.payment_request_1.supplier_reference)

        self.payment_request_1.manual_supplier_reference = 'manual_reference'
        self.assertEquals(
            self.payment_request_1.manual_supplier_reference,
            self.payment_request_1.supplier_reference)

        self.payment_request_1.manual_supplier_reference = False
        self.assertEquals(
            self.payment_request_1.hub_supplier_reference,
            self.payment_request_1.supplier_reference)
