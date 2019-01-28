# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.addons.component.tests import common
from odoo.modules.module import get_resource_path

from ..models.common import (PaymentRequestSAPHandler, PaymentRequestSAPMapper,
                             PaymentRequestSAPRecordImporter)


class TestOfhPaymentRequest(common.TransactionComponentRegistryCase):

    def setUp(self):
        super(TestOfhPaymentRequest, self).setUp()

        self._setup_sap_sales_records()
        self._setup_sap_payment_records()
        self._load_module_components('connector_importer')
        self._build_components(
            PaymentRequestSAPRecordImporter,
            PaymentRequestSAPMapper,
            PaymentRequestSAPHandler)

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
        self.pr_1.write({
            'sap_status': 'payment_in_sap',
            'integration_status': 'payment_sent',
            'sap_xml_sale_ref': '{}_1234R0'.format(
                self.pr_1.order_reference)})
        self.pr_3.write({
            'sap_status': 'payment_in_sap',
            'integration_status': 'payment_sent',
            'sap_xml_sale_ref': '{}_1235'.format(self.pr_3.order_reference)
        })
        self.pr_4.write({
            'sap_status': 'sale_in_sap',
            'integration_status': 'sale_sent',
            'sap_xml_file_ref': 'f8e5859f4606826R0',
            'sap_xml_sale_ref': '{}_6042658R0'.format(
                self.pr_4.order_reference)
        })
        self.pr_5.write({
            'sap_status': 'in_sap',
            'integration_status': 'sale_payment_sent',
            'sap_xml_file_ref': 'f8e5859f4606827R0',
            'sap_xml_sale_ref': '{}_148993R0'.format(self.pr_5.order_reference)
        })

    def _setup_sap_sales_records(self):
        self.import_type = self.env.ref(
            'ofh_payment_request_sap.sap_sale_import_type')
        self.backend = self.env.ref(
            'ofh_payment_request_sap.sap_sale_import_backend')

        path = get_resource_path(
            'ofh_payment_request_sap',
            'tests/test_files/csv_va05_test1.csv')
        with open(path, 'rb') as fl:
            self.source = self.env['import.source.csv'].create({
                'csv_file': base64.encodestring(fl.read()),
                'csv_filename': 'csv_va05_test1.csv',
                'csv_delimiter': ','})

        self.recordset = self.env['import.recordset'].create({
            'backend_id': self.backend.id,
            'import_type_id': self.import_type.id,
            'source_id': self.source.id,
            'source_model': 'import.source.csv',
        })
        self.record = self.env['import.record'].create({
            'recordset_id': self.recordset.id,
        })
        self.backend.debug_mode = True

    def _setup_sap_payment_records(self):
        self.payment_import_type = self.env.ref(
            'ofh_payment_request_sap.sap_payment_import_type')
        self.payment_backend = self.env.ref(
            'ofh_payment_request_sap.sap_payment_import_backend')

        path = get_resource_path(
            'ofh_payment_request_sap',
            'tests/test_files/csv_fbl5n_test1.csv')
        with open(path, 'rb') as fl:
            self.payment_source = self.env['import.source.csv'].create({
                'csv_file': base64.encodestring(fl.read()),
                'csv_filename': 'csv_fbl5n_test1.csv',
                'csv_delimiter': ','})

        self.payment_recordset = self.env['import.recordset'].create({
            'backend_id': self.payment_backend.id,
            'import_type_id': self.payment_import_type.id,
            'source_id': self.payment_source.id,
            'source_model': 'import.source.csv',
        })
        self.payment_record = self.env['import.record'].create({
            'recordset_id': self.payment_recordset.id,
        })
        self.payment_backend.debug_mode = True

    def test_sap_sale_report(self):
        for chunk in self.source.get_lines():
            self.record.set_data(chunk)
            with self.backend.work_on(
                'import.record',
                components_registry=self.comp_registry
            ) as work:
                importer = work.component_by_name(
                    'payment.request.sap.record.importer',
                    'ofh.payment.request')
                self.assertTrue(importer)
                importer.run(self.record)

        # Check the result of the import
        self.assertEquals(self.pr_1.sap_status, 'in_sap')
        self.assertEquals(self.pr_3.sap_status, 'payment_in_sap')
        self.assertEquals(self.pr_4.sap_status, 'sale_in_sap')
        self.assertEquals(self.pr_5.sap_status, 'in_sap')

    def test_sap_payment_report(self):
        for chunk in self.payment_source.get_lines():
            self.payment_record.set_data(chunk)
            with self.payment_backend.work_on(
                'import.record',
                components_registry=self.comp_registry
            ) as work:
                importer = work.component_by_name(
                    'payment.request.sap.record.importer',
                    'ofh.payment.request')
                self.assertTrue(importer)
                importer.run(self.payment_record)

        # Check the result of the import
        self.assertEquals(self.pr_1.sap_status, 'payment_in_sap')
        self.assertEquals(self.pr_3.sap_status, 'payment_in_sap')
        self.assertEquals(self.pr_4.sap_status, 'in_sap')
        self.assertEquals(self.pr_5.sap_status, 'in_sap')

    def test_compute_sap_zsel(self):

        # Only matched or not applicable PRs have SAP fields calculated
        self.assertAlmostEquals(self.pr_1.sap_zsel, 0)
        self.assertAlmostEquals(self.pr_1.sap_zdis, 0)
        self.assertAlmostEquals(self.pr_1.sap_payment_amount1, 0)
        self.assertAlmostEquals(self.pr_1.sap_payment_amount2, 0)

        self.pr_1.request_type = 'void'

        # Case 1: Void payment request
        self.assertAlmostEquals(self.pr_1.sap_zsel, 0)
        self.assertAlmostEquals(self.pr_1.sap_zdis, 0)
        self.assertAlmostEquals(self.pr_1.sap_payment_amount1, 0)
        self.assertAlmostEquals(self.pr_1.sap_payment_amount2, 0)

        # Case 2: Charge case
        self.pr_1.reconciliation_status = 'matched'
        self.pr_1.request_type = 'charge'
        self.assertAlmostEquals(self.pr_1.sap_zsel, self.pr_1.total_amount)
        self.assertAlmostEquals(self.pr_1.sap_zdis, self.pr_1.discount)
        self.assertAlmostEquals(
            self.pr_1.sap_payment_amount1, self.pr_1.total_amount * -1)
        self.assertAlmostEquals(
            self.pr_1.sap_payment_amount2, self.pr_1.sap_payment_amount1 * -1)

        # Case 3: Refund case without discount
        self.pr_1.request_type = 'refund'
        self.assertAlmostEquals(self.pr_1.sap_zsel, self.pr_1.total_amount)
        self.assertAlmostEquals(self.pr_1.sap_zdis, 0)
        self.assertAlmostEquals(
            self.pr_1.sap_payment_amount1, self.pr_1.total_amount)
        self.assertAlmostEquals(
            self.pr_1.sap_payment_amount2, self.pr_1.sap_payment_amount1 * -1)

    def test_compute_transaction_type_1(self):
        """
        - Case 1: Refund/void order with checkout as provider
        """
        self.assertFalse(self.pr_1.transaction_type)

        self.pr_1.write({
            'provider': 'checkoutcom',
            'request_type': 'refund'
        })

        self.assertEquals(self.pr_1.transaction_type, 'PV_CARD')

        self.pr_1.request_type = 'void'
        self.assertEquals(self.pr_1.transaction_type, 'PV_CARD')

    def test_compute_transaction_type_2(self):
        """
        - Case 2: charge order with checkout as provider
        """
        self.pr_1.write({
            'provider': 'checkoutcom',
            'request_type': 'charge'
        })

        self.assertEquals(self.pr_1.transaction_type, 'RV_CARD')

    def test_compute_transaction_type_3(self):
        """
        - Case 3: Refund/void order with checkout as provider and Payment Mode
        """
        self.pr_1.write({
            'provider': 'op',
            'request_type': 'refund',
            'payment_mode': 'Bank Transfer',
        })

        self.assertEquals(self.pr_1.transaction_type, 'PV_CASH')

        self.pr_1.request_type = 'void'
        self.assertEquals(self.pr_1.transaction_type, 'PV_CASH')

    def test_compute_transaction_type_4(self):
        """
        - Case 4: Refund/void order with checkout as provider and
        no Payment Mode
        """
        self.pr_1.write({
            'provider': 'op',
            'request_type': 'refund',
        })

        self.assertEquals(self.pr_1.transaction_type, 'PV_CHEQUE')

        self.pr_1.request_type = 'void'
        self.assertEquals(self.pr_1.transaction_type, 'PV_CHEQUE')

    def test_compute_transaction_type_5(self):
        """
        - Case 5: Charge order with checkout as provider and Payment Mode
        """
        self.pr_1.write({
            'provider': 'op',
            'request_type': 'charge',
            'payment_mode': 'Bank Transfer',
        })

        self.assertEquals(self.pr_1.transaction_type, 'BANK_TRANSFER')

    def test_compute_transaction_type_6(self):
        """
        - Case 6: Charge order with checkout as provider and
        no Payment Mode
        """
        self.pr_1.write({
            'provider': 'op',
            'request_type': 'charge',
        })

        self.assertEquals(self.pr_1.transaction_type, 'RV_CHEQUE')
