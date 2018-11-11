# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSupplierInvoiceLineGds(TransactionCase):

    def setUp(self):
        super(TestSupplierInvoiceLineGds, self).setUp()
        self.invoice_line_1 = self.env.ref(
            'ofh_supplier_invoice_gds.ofh_supplier_invoice_line_gds_1')
        self.invoice_line_3 = self.env.ref(
            'ofh_supplier_invoice_gds.ofh_supplier_invoice_line_gds_3')

    def test_gds_compute_fees(self):

        # Invoice line 1
        self.assertAlmostEquals(
            self.invoice_line_1.gds_base_fare_amount, 100.0)
        self.assertAlmostEquals(self.invoice_line_1.gds_tax_amount, 200.00)
        self.assertAlmostEquals(self.invoice_line_1.gds_net_amount, 300)
        self.assertAlmostEquals(self.invoice_line_1.gds_fee_amount, 0)
        self.assertAlmostEquals(
            self.invoice_line_1.gds_iata_commission_amount, 0)

        # Invoice line 3
        self.assertAlmostEquals(
            self.invoice_line_3.gds_base_fare_amount, -465)
        self.assertAlmostEquals(self.invoice_line_3.gds_net_amount, -465)
        self.assertAlmostEquals(self.invoice_line_3.gds_tax_amount, 0)
        self.assertAlmostEquals(self.invoice_line_3.gds_fee_amount, 0)
        self.assertAlmostEquals(
            self.invoice_line_3.gds_iata_commission_amount, 0)

    def test_gds_compute_name(self):

        # Invoice line 1
        self.assertEquals(
            self.invoice_line_1.name, 'gds_2770018289TKTT')

        # Invoice line 3
        self.assertEquals(self.invoice_line_3.name, 'gds_2678745993RFND')
