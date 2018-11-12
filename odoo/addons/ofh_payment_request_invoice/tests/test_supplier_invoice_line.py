# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


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

    def test_1(self):
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
        import pdb; pdb.set_trace()