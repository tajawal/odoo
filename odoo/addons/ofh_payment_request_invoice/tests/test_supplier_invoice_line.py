# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSupplierInvoiceLine(TransactionCase):

    def setUp(self):
        super(TestSupplierInvoiceLine, self).setUp()
        self.invoice_line_model = self.env['ofh.supplier.invoice.line']

        # Payment requests
        self.payment_request_1 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_1')
        self.payment_request_2 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_2')
        self.payment_request_3 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_3')
        self.payment_request_4 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_4')
        self.payment_request_5 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_5')

        self.payment_request_6 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_tf_1')
        self.payment_request_7 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_tf_2')
        self.payment_request_8 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_tf_3')
        self.payment_request_9 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_tf_4')
        self.payment_request_10 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_tf_5')

        self.payment_request_11 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_aig_1')
        self.payment_request_12 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_aig_2')
        self.payment_request_13 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_aig_3')

        # Supplier Invoices
        self.supplier_invoice_1 = self.env.ref(
            'ofh_supplier_invoice_gds.ofh_supplier_invoice_line_gds_1')
        self.supplier_invoice_2 = self.env.ref(
            'ofh_supplier_invoice_gds.ofh_supplier_invoice_line_gds_2')
        self.supplier_invoice_3 = self.env.ref(
            'ofh_supplier_invoice_gds.ofh_supplier_invoice_line_gds_3')
        self.supplier_invoice_4 = self.env.ref(
            'ofh_supplier_invoice_gds.ofh_supplier_invoice_line_gds_4')
        self.supplier_invoice_5 = self.env.ref(
            'ofh_supplier_invoice_gds.ofh_supplier_invoice_line_gds_5')

        self.supplier_invoice_6 = self.env.ref(
            'ofh_supplier_invoice_tf.ofh_supplier_invoice_line_tf_1')
        self.supplier_invoice_7 = self.env.ref(
            'ofh_supplier_invoice_tf.ofh_supplier_invoice_line_tf_2')
        self.supplier_invoice_8 = self.env.ref(
            'ofh_supplier_invoice_tf.ofh_supplier_invoice_line_tf_3')
        self.supplier_invoice_9 = self.env.ref(
            'ofh_supplier_invoice_tf.ofh_supplier_invoice_line_tf_4')
        self.supplier_invoice_10 = self.env.ref(
            'ofh_supplier_invoice_tf.ofh_supplier_invoice_line_tf_5')
        self.supplier_invoice_11 = self.env.ref(
            'ofh_supplier_invoice_tf.ofh_supplier_invoice_line_tf_6')

        self.supplier_invoice_12 = self.env.ref(
            'ofh_supplier_invoice_aig.ofh_supplier_invoice_line_aig_1')
        self.supplier_invoice_13 = self.env.ref(
            'ofh_supplier_invoice_aig.ofh_supplier_invoice_line_aig_2')
        self.supplier_invoice_14 = self.env.ref(
            'ofh_supplier_invoice_aig.ofh_supplier_invoice_line_aig_3')
        self.supplier_invoice_15 = self.env.ref(
            'ofh_supplier_invoice_aig.ofh_supplier_invoice_line_aig_4')

    def test_gds_match_supplier_invoice_lines(self):
        # Case where one PR matches one or multiple supplier invoice
        self.invoice_line_model.match_supplier_invoice_lines()
        self.assertEquals(self.supplier_invoice_1.state, 'matched')
        self.assertEquals(self.supplier_invoice_2.state, 'matched')
        self.assertEquals(
            self.supplier_invoice_1.payment_request_id, self.payment_request_1)
        self.assertEquals(
            self.supplier_invoice_2.payment_request_id, self.payment_request_1)
        self.assertEquals(
            self.payment_request_1.reconciliation_status, 'matched')
        self.assertEquals(
            len(self.payment_request_1.supplier_invoice_ids), 2)

        # Case where the PR doesn't match any supplier invoice
        self.assertEquals(
            self.payment_request_2.reconciliation_status, 'investigate')
        self.assertEquals(len(self.payment_request_2.supplier_invoice_ids), 0)
        self.assertEquals(
            self.supplier_invoice_3.state, 'not_matched')

        # Case Suggest matching
        self.assertEquals(
            self.payment_request_3.reconciliation_status, 'matched')
        self.assertEquals(
            len(self.payment_request_3.supplier_invoice_ids), 1)
        self.assertEquals(self.supplier_invoice_4.state, 'suggested')
        self.assertEquals(
            self.supplier_invoice_4.payment_request_id, self.payment_request_3)

        # Case Multiple payment requests against one supplier invoice
        self.assertEquals(
            self.payment_request_4.reconciliation_status, 'investigate')
        self.assertEquals(
            self.payment_request_5.reconciliation_status, 'investigate')
        self.assertEquals(
            self.supplier_invoice_5.state, 'not_matched')

    def test_tf_match_supplier_invoice_lines(self):
        # Case where one PR matches one or multiple supplier invoices
        self.invoice_line_model.match_supplier_invoice_lines()
        self.assertEquals(self.supplier_invoice_6.state, 'matched')
        self.assertEquals(self.supplier_invoice_7.state, 'matched')
        self.assertEquals(
            self.supplier_invoice_6.payment_request_id, self.payment_request_6)
        self.assertEquals(
            self.supplier_invoice_7.payment_request_id, self.payment_request_6)
        self.assertEquals(
            self.payment_request_6.reconciliation_status, 'matched')
        self.assertEquals(
            len(self.payment_request_6.supplier_invoice_ids), 2)

        # Case where the PR doesn't match any supplier invoice
        self.assertEquals(self.supplier_invoice_8.state, 'not_matched')
        self.assertEquals(
            self.payment_request_7.reconciliation_status, 'investigate')
        self.assertEquals(
            len(self.payment_request_7.supplier_invoice_ids), 0)

        # Case Suggest matching
        self.assertEquals(self.supplier_invoice_9.state, 'suggested')
        self.assertEquals(
            self.payment_request_8.reconciliation_status, 'matched')
        self.assertEquals(
            len(self.payment_request_8.supplier_invoice_ids), 1)

        # Case Multiple payment requests against one supplier invoice
        self.assertEquals(
            self.payment_request_9.reconciliation_status, 'investigate')
        self.assertEquals(
            self.payment_request_10.reconciliation_status, 'investigate')
        self.assertEquals(self.supplier_invoice_10.state, 'not_matched')
        self.assertEquals(self.supplier_invoice_11.state, 'not_matched')

    def test_aig_match_supplier_invoice_lines(self):
        # Case where one PR matches one or multiple supplier invoices
        self.invoice_line_model.match_supplier_invoice_lines()
        self.assertEquals(self.supplier_invoice_12.state, 'matched')
        self.assertEquals(
            self.supplier_invoice_12.payment_request_id,
            self.payment_request_11)

        self.assertEquals(self.supplier_invoice_13.state, 'suggested')
        self.assertEquals(
            self.supplier_invoice_13.payment_request_id,
            self.payment_request_12)

        self.assertEquals(
            self.payment_request_13.reconciliation_status, 'investigate')
        self.assertEquals(self.supplier_invoice_14.state, 'not_matched')
        self.assertEquals(self.supplier_invoice_15.state, 'not_matched')

    def test_force_match(self):
        self.payment_request_1.order_type = 'flight'
        self.payment_request_7.order_type = 'flight'

        wizard = self.env['ofh.supplier.invoice.force.match'].with_context(
            active_model='ofh.supplier.invoice.line',
            active_id=self.supplier_invoice_1.id).create(
                {'new_payment_request_id': self.payment_request_1.id})
        wizard.force_match()

        self.assertEquals(
            self.payment_request_1.reconciliation_status, 'matched')
        self.assertEquals(
            self.supplier_invoice_1.state, 'forced')

        # Raise error if payment request type is refund and ticket is charge
        with self.assertRaises(ValidationError):
            wizard.new_payment_request_id = self.payment_request_7
            wizard.force_match()

        # Raise error if invoice is refund and payment request ticket
        with self.assertRaises(ValidationError):
            wizard.write(
                {'line_id': self.supplier_invoice_3.id,
                 'new_payment_request_id': self.payment_request_1.id})
            wizard.force_match()
