# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.modules.module import get_resource_path
from odoo.addons.component.tests import common
from ..models.common import (
    PaymentRequestSAPSaleRecordImporter,
    PaymentRequestSAPSaleMapper,
    PaymentRequestSAPSaleHandler)
import base64


class TestOfhPaymentRequest(common.TransactionComponentRegistryCase):

    def setUp(self):
        super(TestOfhPaymentRequest, self).setUp()

        self._setup_records()
        self._load_module_components('connector_importer')
        self._build_components(
            PaymentRequestSAPSaleRecordImporter,
            PaymentRequestSAPSaleMapper,
            PaymentRequestSAPSaleHandler)

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
            {'sap_status': 'payment_in_sap',
             'integration_status': 'payment_sent',
             'sap_xml_sale_ref': '{}_1234R0'.format(
                 self.pr_1.order_reference)})
        self.pr_3.write(
            {'sap_status': 'payment_in_sap',
             'integration_status': 'payment_sent',
             'sap_xml_sale_ref': '{}_1235'.format(self.pr_3.order_reference)})
        self.pr_4.write(
            {'sap_status': 'sale_in_sap',
             'integration_status': 'sale_sent',
             'sap_xml_sale_ref': '{}_6042658R0'.format(
                 self.pr_4.order_reference)})
        self.pr_5.write(
            {'sap_status': 'in_sap',
             'integration_status': 'sale_payment_sent',
             'sap_xml_sale_ref': '{}_148993R0'.format(
                 self.pr_5.order_reference)})

    def _setup_records(self):
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

    def test_supplier_invoice_import(self):
        # Update reconciliation, integration and SAP status

        for chunk in self.source.get_lines():
            self.record.set_data(chunk)
            with self.backend.work_on(
                'import.record',
                components_registry=self.comp_registry
            ) as work:
                importer = work.component_by_name(
                    'payment.request.sap.sale.record.importer',
                    'ofh.payment.request')
                self.assertTrue(importer)
                importer.run(self.record)

        self.assertEquals(self.pr_1.sap_xml_sale_ref, 'A8092211814_1234R0')
        # Check the result of the import
        self.assertEquals(self.pr_1.sap_status, 'in_sap')
        self.assertEquals(self.pr_3.sap_status, 'payment_in_sap')
        self.assertEquals(self.pr_4.sap_status, 'sale_in_sap')
        self.assertEquals(self.pr_5.sap_status, 'in_sap')
