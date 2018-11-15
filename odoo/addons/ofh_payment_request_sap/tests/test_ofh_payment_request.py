# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.modules.module import get_resource_path
import base64


class TestOfhPaymentRequest(TransactionCase):

    def setUp(self):
        super(TestOfhPaymentRequest, self).setUp()

        self.wiz_model = self.env['ofh.payment.request.sap.import']

        # Payment Requests
        self.pr_1 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_1')
        self.pr_2 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_2')
        self.pr_3 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_3')
        self.pr_4 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_4')
        self.pr_5 = self.env.ref(
            'ofh_payment_request.ofh_payment_request_gds_5')

        # Update reconciliation, integration and SAP status
        self.pr_1.write(
            {'integration_status': 'payment_sent',
             'sap_xml_sale_ref': '{}_1234'.format(self.pr_1.order_reference)})
        self.pr_3.write(
            {'integration_status': 'payment_sent',
             'sap_xml_sale_ref': '{}_1235'.format(self.pr_1.order_reference)})
        self.pr_4.write(
            {'integration_status': 'sale_sent',
             'sap_xml_sale_ref': '{}_1236'.format(self.pr_1.order_reference)})
        self.pr_5.write(
            {'integration_status': 'sale_payment_sent',
             'sap_xml_sale_ref': '{}_1237'.format(self.pr_1.order_reference)})

    def test_supplier_invoice_import(self):
        # Update reconciliation, integration and SAP status
        path = get_resource_path(
            'ofh_payment_request_sap',
            'tests/test_files/csv_va05_test1.csv')
        with open(path, 'rb') as fl:
            wizard = self.wiz_model.create({
                'report_type': 'va05',
                'upload_file': base64.encode(fl.read()),
                'file_name': 'csv_va05_test1.csv',
            })
        wizard.run_matching()
