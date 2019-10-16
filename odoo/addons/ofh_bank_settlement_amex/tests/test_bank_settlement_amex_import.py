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


class TestBankSettlementAmexImport(common.TransactionComponentRegistryCase):

    def setUp(self):
        super(TestBankSettlementAmexImport, self).setUp()
        self._setup_records()
        self._load_module_components('connector_importer')
        self._build_components(
            BankSettlementMapper,
            BankSettlementHandler,
            BankSettlementRecordImporter)

        self.bank_settlement_model = self.env['ofh.bank.settlement']

    def _setup_records(self):
        self.import_type = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_type')
        self.backend = self.env.ref(
            'ofh_bank_settlement_amex.amex_bank_settlement_import_backend')

        path = get_resource_path(
            'ofh_payment_gateway_knet',
            'tests/test_files/amex_test.csv')
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

    def test_bank_settlement_amex(self):
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
            [('name', '=', '73791879230913100000000')])
        self.assertTrue(first_line)
        self.assertEquals(len(first_line), 1)

        # self.assertEquals(first_line.name, 'chg_Pt7c4020192359Bn2t2306458')
        # self.assertEquals(first_line.provider, 'knet')
        # self.assertEquals(first_line.acquirer_bank, 'sabb')
        # self.assertEquals(first_line.track_id, '8ee7c07e-69d7-46f4-9638-d1c5d03c85db')
        # self.assertEquals(first_line.auth_code, '000003')
        # self.assertEquals(first_line.payment_method, 'KNET')
        # self.assertEquals(first_line.currency_id.id, self.env.ref('base.KWD').id)
        # self.assertEquals(first_line.payment_status, 'capture')
        # self.assertEquals(first_line.payment_id, 'chg_Pt7c4020192359Bn2t2306458')
        # self.assertEquals(first_line.entity, 'almosafer')


