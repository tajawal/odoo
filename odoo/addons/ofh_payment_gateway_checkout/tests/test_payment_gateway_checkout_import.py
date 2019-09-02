# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.addons.component.tests import common
from odoo.addons.ofh_payment_gateway.models.common import \
    PaymentGatewayLineRecordImporter
from odoo.modules.module import get_resource_path

from ..models.common import (PaymentGatewayLineHandler,
                             PaymentGatewayLineMapper)


class TestPaymentGatewayCheckoutImport(common.TransactionComponentRegistryCase):

    def setUp(self):
        super(TestPaymentGatewayCheckoutImport, self).setUp()
        self._setup_records()
        self._load_module_components('connector_importer')
        self._build_components(
            PaymentGatewayLineMapper,
            PaymentGatewayLineHandler,
            PaymentGatewayLineRecordImporter)

        self.payment_gateway_line_model = self.env['ofh.payment.gateway.line']

    def _setup_records(self):
        self.import_type = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_type')
        self.backend = self.env.ref(
            'ofh_payment_gateway_checkout.checkout_import_backend')

        path = get_resource_path(
            'ofh_payment_gateway_checkout',
            'tests/test_files/checkout_test.csv')
        with open(path, 'rb') as fl:
            self.source = self.env['import.source.csv'].create({
                'csv_file': base64.encodestring(fl.read()),
                'csv_filename': 'checkout_test.csv',
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

    def test_payment_gateway_line_checkout(self):
        for chunk in self.source.get_lines():
            self.record.set_data(chunk)
            with self.backend.work_on(
                'import.record',
                components_registry=self.comp_registry
            ) as work:
                importer = work.component_by_name(
                    'payment.gateway.line.record.importer',
                    'ofh.payment.gateway.line')
                self.assertTrue(importer)
                importer.run(self.record)

        # First Payment Gateway Checkout test
        first_line = self.payment_gateway_line_model.search(
            [('name', '=', '0869CE077G1A6CFE90C8')])
        self.assertTrue(first_line)
        self.assertEquals(len(first_line), 1)

        self.assertEquals(first_line.name, '0869CE077G1A6CFE90C8')
        self.assertEquals(first_line.provider, 'checkout')
        self.assertEquals(first_line.acquirer_bank, 'sabb')
        self.assertEquals(first_line.track_id, 'b4ce6725-3c4d-4153-9544-5ced68a13a82')
        self.assertEquals(first_line.auth_code, '832208')
        self.assertEquals(first_line.payment_method, 'Visa')
        self.assertEquals(first_line.transaction_date, '2019-06-26 00:00:00')
        self.assertEquals(first_line.total, 531.40)
        self.assertEquals(first_line.currency_id.id, self.env.ref('base.SAR').id)
        self.assertEquals(first_line.payment_status, 'auth')
        self.assertEquals(first_line.card_name, 'WALEED S ALHALABI')
        self.assertEquals(first_line.card_number, '455035******0093')
        self.assertEquals(first_line.card_bin, '455035')
        self.assertEquals(first_line.card_bank, 'ARAB NATIONAL BANK')
        self.assertEquals(first_line.card_expiry_year, '2020')
        self.assertEquals(first_line.card_expiry_month, '5')
        self.assertEquals(first_line.customer_email, 'feras-_-13@hotmail.com')
        self.assertEquals(first_line.cvv_check, 'Y')
        self.assertEquals(first_line.arn, '9.17806')
        self.assertEquals(first_line.payment_id, '0869CE077G1A6CFE90C8')
        self.assertEquals(first_line.entity, 'tajawal')

        # Second Payment Gateway Checkout test - Void
        first_line = self.payment_gateway_line_model.search(
            [('name', '=', 'C86BEE177G1A6D7D5FA9')])
        self.assertTrue(first_line)
        self.assertEquals(len(first_line), 1)

        self.assertEquals(first_line.name, 'C86BEE177G1A6D7D5FA9')
        self.assertEquals(first_line.provider, 'checkout')
        self.assertEquals(first_line.acquirer_bank, 'sabb')
        self.assertEquals(first_line.track_id, '944fec04-625a-4fdc-96f1-71b40f11a7b6')
        self.assertEquals(first_line.auth_code, '106063')
        self.assertEquals(first_line.payment_method, 'Visa')
        self.assertEquals(first_line.payment_status, 'void')
        self.assertEquals(first_line.entity, 'tajawal')

        # Third Payment Gateway Checkout test - Refund
        first_line = self.payment_gateway_line_model.search(
            [('name', '=', 'C9FBBE377V1A6E198E5E')])
        self.assertTrue(first_line)
        self.assertEquals(len(first_line), 1)

        self.assertEquals(first_line.name, 'C9FBBE377V1A6E198E5E')
        self.assertEquals(first_line.provider, 'checkout')
        self.assertEquals(first_line.acquirer_bank, 'sabb')
        self.assertEquals(first_line.track_id, '5e0bdb38-a186-4b5e-ad82-0d43449f5376')
        self.assertEquals(first_line.auth_code, '149226')
        self.assertEquals(first_line.payment_method, 'Visa')
        self.assertEquals(first_line.payment_status, 'refund')
        self.assertEquals(first_line.entity, 'tajawal')

