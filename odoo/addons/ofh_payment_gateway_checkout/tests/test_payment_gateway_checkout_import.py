# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.addons.component.tests import common
from odoo.addons.ofh_payment_gateway.models.common import \
    PaymentGatewayLineRecordImporter
from odoo.modules.module import get_resource_path

from ..models.common import (PaymentGatewayLineHandler,
                             PaymentGatewayLineMapper)


class TestPaymentGatewayCheckoutImport(
        common.TransactionComponentRegistryCase):

    def setUp(self):
        super(TestPaymentGatewayCheckoutImport, self).setUp()
        self._setup_records()
        self._load_module_components('connector_importer')
        self._build_components(
            PaymentGatewayLineMapper,
            PaymentGatewayLineHandler,
            PaymentGatewayLineRecordImporter)

        self.pg_line_model = self.env['ofh.payment.gateway.line']
        self.pg_model = self.env['ofh.payment.gateway']

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

    def test_payment_gateway_1(self):
        """
        Case 1:
        =======
        Payment Gateway lines have authorized and refund state for the same
        track_id.
        """
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

        payment_gateways = self.pg_model.search(
            [('name', 'ilike', '0782f431-1454-42c3-8d83-b586fcfb5795')])

        self.assertTrue(payment_gateways)
        self.assertEqual(len(payment_gateways), 2)
        refund_pg = payment_gateways.filtered(
            lambda r: r.payment_status == 'refund')
        self.assertTrue(refund_pg)
        self.assertEqual(len(refund_pg.payment_gateway_line_ids), 1)

        auth_pg = payment_gateways - refund_pg
        self.assertTrue(auth_pg)
        self.assertEqual(len(auth_pg.payment_gateway_line_ids), 1)

    def test_payment_gateway_2(self):
        """
        Case 2:
        =======
        Payment Gateway lines have authorized and captured state for the same
        track_id.
        """
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

        payment_gateways = self.pg_model.search(
            [('name', 'ilike', '0baa0588-b38f-46a4-8ae8-6e3d881428f3')])
        self.assertTrue(payment_gateways)
        self.assertEqual(len(payment_gateways), 1)
        self.assertEqual(len(payment_gateways.payment_gateway_line_ids), 2)

    def test_payment_gateway_3(self):
        """
        Case 3:
        =======
        Payment Gateway lines have authorized, captured, refund.
        """
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

        payment_gateways = self.pg_model.search(
            [('name', '=', 'pr-A90630172056-1561903288802')])

        self.assertTrue(payment_gateways)
        self.assertEqual(len(payment_gateways), 2)
        refund_pg = payment_gateways.filtered(
            lambda r: r.payment_status == 'refund')
        self.assertTrue(refund_pg)
        self.assertEqual(len(refund_pg.payment_gateway_line_ids), 1)

        auth_pg = payment_gateways - refund_pg
        self.assertTrue(auth_pg)
        self.assertEqual(len(auth_pg.payment_gateway_line_ids), 2)

    def test_payment_gateway_4(self):
        """
        Case 3:
        =======
        Payment Gateway lines have authorized, authorized, captured, .
        """
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

        payment_gateways = self.pg_model.search(
            [('name', 'ilike', 'pr-A90630172056-1561903288802')])

        self.assertTrue(payment_gateways)
        self.assertEqual(len(payment_gateways), 2)
        refund_pg = payment_gateways.filtered(
            lambda r: r.payment_status == 'refund')
        self.assertTrue(refund_pg)
        self.assertEqual(len(refund_pg.payment_gateway_line_ids), 1)

        auth_pg = payment_gateways - refund_pg
        self.assertTrue(auth_pg)
        self.assertEqual(len(auth_pg.payment_gateway_line_ids), 2)

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
        first_line = self.pg_line_model.search(
            [('name', '=', '0869CE077G1A6CFE90C8')])
        self.assertTrue(first_line)
        self.assertEqual(len(first_line), 1)

        self.assertEqual(first_line.name, '0869CE077G1A6CFE90C8')
        self.assertEqual(first_line.provider, 'checkout')
        self.assertEqual(first_line.acquirer_bank, 'sabb')
        self.assertEqual(
            first_line.track_id, 'b4ce6725-3c4d-4153-9544-5ced68a13a82')
        self.assertEqual(first_line.auth_code, '832208')
        self.assertEqual(first_line.payment_method, 'Visa')
        self.assertEqual(first_line.transaction_date, '2019-06-26 20:09:00')
        self.assertEqual(first_line.total, 531.40)
        self.assertEqual(
            first_line.currency_id.id, self.env.ref('base.SAR').id)
        self.assertEqual(first_line.payment_status, 'auth')
        self.assertEqual(first_line.card_name, 'WALEED S ALHALABI')
        self.assertEqual(first_line.card_number, '455035******0093')
        self.assertEqual(first_line.card_bin, '455035')
        self.assertEqual(first_line.card_bank, 'ARAB NATIONAL BANK')
        self.assertEqual(first_line.card_expiry_year, '2020')
        self.assertEqual(first_line.card_expiry_month, '5')
        self.assertEqual(first_line.customer_email, 'feras-_-13@hotmail.com')
        self.assertEqual(first_line.cvv_check, 'Y')
        self.assertEqual(first_line.arn, '9.17806')
        self.assertEqual(first_line.payment_id, '0869CE077G1A6CFE90C8')
        self.assertEqual(first_line.entity, 'tajawal')

        # Second Payment Gateway Checkout test - Void
        first_line = self.pg_line_model.search(
            [('name', '=', 'C86BEE177G1A6D7D5FA9')])
        self.assertTrue(first_line)
        self.assertEqual(len(first_line), 1)

        self.assertEqual(first_line.name, 'C86BEE177G1A6D7D5FA9')
        self.assertEqual(first_line.provider, 'checkout')
        self.assertEqual(first_line.acquirer_bank, 'sabb')
        self.assertEqual(
            first_line.track_id, '944fec04-625a-4fdc-96f1-71b40f11a7b6')
        self.assertEqual(first_line.auth_code, '106063')
        self.assertEqual(first_line.payment_method, 'Visa')
        self.assertEqual(first_line.payment_status, 'void')
        self.assertEqual(first_line.entity, 'tajawal')

        # Third Payment Gateway Checkout test - Refund
        first_line = self.pg_line_model.search(
            [('name', '=', 'C9FBBE377V1A6E198E5E')])
        self.assertTrue(first_line)
        self.assertEqual(len(first_line), 1)

        self.assertEqual(first_line.name, 'C9FBBE377V1A6E198E5E')
        self.assertEqual(first_line.provider, 'checkout')
        self.assertEqual(first_line.acquirer_bank, 'sabb')
        self.assertEqual(
            first_line.track_id, '5e0bdb38-a186-4b5e-ad82-0d43449f5376')
        self.assertEqual(first_line.auth_code, '149226')
        self.assertEqual(first_line.payment_method, 'Visa')
        self.assertEqual(first_line.payment_status, 'refund')
        self.assertEqual(first_line.entity, 'tajawal')
