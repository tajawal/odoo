# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestOfhPaymentRequest(TransactionCase):

    def setUp(self):
        super(TestOfhPaymentRequest, self).setUp()
        self.invoice_line_model = self.env['ofh.supplier.invoice.line']
        self.pr_model = self.env['ofh.payment.request']

        # Payment requests
        self.payment_request_1 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_generic_1')

        # Supplier Invoices
        self.supplier_invoice_1 = self.env.ref(
            'ofh_supplier_invoice_gds.ofh_supplier_invoice_line_gds_1')
        self.supplier_invoice_2 = self.env.ref(
            'ofh_supplier_invoice_gds.ofh_supplier_invoice_line_gds_2')
        self.supplier_invoice_3 = self.env.ref(
            'ofh_supplier_invoice_tf.ofh_supplier_invoice_line_tf_1')

        self.payment_request_1.supplier_invoice_ids = \
            self.supplier_invoice_1 | self.supplier_invoice_2
        self.payment_request_1.matching_status = 'matched'
        self.payment_request_1.supplier_invoice_ids.write(
            {'state': 'forced'})

    def test_compute_supplier_total_amount(self):

        self.assertAlmostEquals(
            self.payment_request_1.supplier_total_amount, 600)

        self.payment_request_1.supplier_invoice_ids = False
        self.assertAlmostEquals(
            self.payment_request_1.supplier_total_amount, 0)
        self.payment_request_1.matching_status = 'not_applicable'
        self.assertAlmostEquals(
            self.payment_request_1.supplier_total_amount,
            self.payment_request_1.fare_difference)

        # Case of hotel order
        # self.payment_request_1.order_type = 'hotel'
        # self.assertEquals(self.payment_request_1.supplier_total_amount, 0)

        # Set initial order amount
        # self.payment_request_1.order_amount = 10000
        # self.assertEquals(self.payment_request_1.supplier_total_amount, 0)

        # Set initial order supplier cost
        self.payment_request_1.order_supplier_cost = 7000
        self.assertEquals(
            self.payment_request_1.supplier_total_amount,
            (self.payment_request_1.total_amount /
             self.payment_request_1.order_amount) *
            self.payment_request_1.order_supplier_cost)

        # Case of a charge hotel PR
        self.payment_request_1.request_type = 'charge'
        self.assertEquals(
            self.payment_request_1.supplier_total_amount,
            self.payment_request_1.total_amount)

    def test_compute_office_id(self):
        self.assertEquals(
            self.payment_request_1.supplier_office_id, 'DXBAD31DO')

        self.payment_request_1.supplier_invoice_ids = False

        self.assertFalse(self.payment_request_1.supplier_office_id)

    def test_search_office_id(self):
        payment_request = self.pr_model.search(
            [('supplier_office_id', '=', 'DXBAD31DO')])
        self.assertTrue(payment_request)
        self.assertEquals(len(payment_request), 1)

        self.payment_request_1.supplier_invoice_ids = False

        payment_request = self.pr_model.search(
            [('supplier_office_id', '=', 'DXBAD31DO')])
        self.assertFalse(payment_request)
