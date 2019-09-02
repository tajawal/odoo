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


class TestPaymentGatewayFortImport(common.TransactionComponentRegistryCase):

    def setUp(self):
        super(TestPaymentGatewayFortImport, self).setUp()
        self._setup_records()
        self._load_module_components('connector_importer')
        self._build_components(
            PaymentGatewayLineMapper,
            PaymentGatewayLineHandler,
            PaymentGatewayLineRecordImporter)

        self.payment_gateway_line_model = self.env['ofh.payment.gateway.line']

    def _setup_records(self):
        self.import_type = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_type')
        self.backend = self.env.ref(
            'ofh_payment_gateway_fort.fort_import_backend')

        path = get_resource_path(
            'ofh_payment_gateway_fort',
            'tests/test_files/fort_test.csv')
        with open(path, 'rb') as fl:
            self.source = self.env['import.source.csv'].create({
                'csv_file': base64.encodestring(fl.read()),
                'csv_filename': 'fort_test.csv',
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

    def test_payment_gateway_line_fort(self):
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

        # First Payment Gateway Fort test
        first_line = self.payment_gateway_line_model.search(
            [('name', '=', '156192239100009000')])
        self.assertTrue(first_line)
        self.assertEquals(len(first_line), 1)

        self.assertEquals(first_line.name, '156192239100009000')
        self.assertEquals(first_line.provider, 'fort')
        self.assertEquals(first_line.acquirer_bank, 'mashreq')
        self.assertEquals(first_line.track_id, '59f253e1-79d9-4ac9-a4b7-66846e18b051')
        self.assertEquals(first_line.auth_code, '753080')
        self.assertEquals(first_line.payment_method, 'Visa')
        self.assertEquals(first_line.currency_id.id, self.env.ref('base.AED').id)
        self.assertEquals(first_line.payment_status, 'auth')
        self.assertEquals(first_line.payment_id, '156192387100015000')
        self.assertEquals(first_line.entity, 'tajawal')


