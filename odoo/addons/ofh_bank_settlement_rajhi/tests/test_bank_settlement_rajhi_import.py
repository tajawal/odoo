# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.addons.component.tests import common
from odoo.addons.ofh_bank_settlement.models.common import \
    BankSettlementRecordImporter
from odoo.modules.module import get_resource_path

from ..models.common import (BankSettlementHandler,
                             BankSettlementMapper)


class TestBankSettlementRajhiImport(common.TransactionComponentRegistryCase):

    def setUp(self):
        super(TestBankSettlementRajhiImport, self).setUp()
        self._setup_records()
        self._load_module_components('connector_importer')
        self._build_components(
            BankSettlementMapper,
            BankSettlementHandler,
            BankSettlementRecordImporter)

        self.bank_settlement_model = self.env['ofh.bank.settlement']

    def _setup_records(self):
        self.import_type = self.env.ref(
            'ofh_bank_settlement_rajhi.rajhi_bank_settlement_import_type')
        self.backend = self.env.ref(
            'ofh_bank_settlement_rajhi.rajhi_bank_settlement_import_backend')

        path = get_resource_path(
            'ofh_bank_settlement_rajhi',
            'tests/test_files/rajhi_test.csv')
        with open(path, 'rb') as fl:
            self.source = self.env['import.source.csv'].create({
                'csv_file': base64.encodestring(fl.read()),
                'csv_filename': 'knet_test.csv',
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

    def test_bank_settlement_rajhi_capture_and_mada(self):
        for chunk in self.source.get_lines():
            self.record.set_data(chunk)
            with self.backend.work_on(
                'import.record',
                components_registry=self.comp_registry
            ) as work:
                importer = work.component_by_name(
                    'bank.settlement.record.importer',
                    'ofh.bank.settlement')
                self.assertTrue(importer)
                importer.run(self.record)

        # First Payment Gateway Knet test
        first_line = self.bank_settlement_model.search(
            [('name', '=', '923022024150')])
        self.assertTrue(first_line)
        self.assertEquals(len(first_line), 1)

        self.assertEquals(first_line.name, '923022024150')
        self.assertEquals(first_line.settlement_date, '2019-08-19')
        self.assertEquals(first_line.bank_name, 'rajhi')
        self.assertEquals(first_line.reported_mid, 'ARBS2I010849')
        self.assertEquals(first_line.account_number, '296000010006080000000')
        self.assertEquals(first_line.payment_method, 'none')
        self.assertTrue(first_line.is_mada)
        self.assertEquals(first_line.transaction_date, '2019-08-19')
        self.assertEquals(first_line.card_number, '535825******9878')
        self.assertEquals(first_line.gross_amount, 1385.7)
        self.assertEquals(first_line.payment_status, 'capture')
        self.assertEquals(first_line.auth_code, '720296')

    def test_bank_settlement_rajhi_refund_and_mada(self):
        for chunk in self.source.get_lines():
            self.record.set_data(chunk)
            with self.backend.work_on(
                'import.record',
                components_registry=self.comp_registry
            ) as work:
                importer = work.component_by_name(
                    'bank.settlement.record.importer',
                    'ofh.bank.settlement')
                self.assertTrue(importer)
                importer.run(self.record)

        # First Payment Gateway Knet test
        first_line = self.bank_settlement_model.search(
            [('name', '=', '923022027269')])
        self.assertTrue(first_line)
        self.assertEquals(len(first_line), 1)

        self.assertEquals(first_line.name, '923022027269')
        self.assertEquals(first_line.settlement_date, '2019-08-19')
        self.assertEquals(first_line.bank_name, 'rajhi')
        self.assertEquals(first_line.reported_mid, 'ARBS2I010849')
        self.assertEquals(first_line.account_number, '296000010006080000000')
        self.assertEquals(first_line.payment_method, 'none')
        self.assertTrue(first_line.is_mada)
        self.assertEquals(first_line.transaction_date, '2019-08-19')
        self.assertEquals(first_line.card_number, '537767******7424')
        self.assertEquals(first_line.gross_amount, 2594.6)
        self.assertEquals(first_line.payment_status, 'refund')
        self.assertEquals(first_line.auth_code, '028837')


