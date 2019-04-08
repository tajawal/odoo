# -*- coding: utf-8 -*-
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.addons.component.tests import common
from odoo.addons.ofh_supplier_invoice.models.common import \
    SupplierInvoiceLineRecordImporter
from odoo.modules.module import get_resource_path

from ..models.common import (SupplierInvoiceLineHandler,
                             SupplierInvoiceLineMapper)


class TestSupplierInvoiceEnettImport(common.TransactionComponentRegistryCase):

    def setUp(self):
        super(TestSupplierInvoiceEnettImport, self).setUp()
        self._setup_records()
        self._load_module_components('connector_importer')
        self._build_components(
            SupplierInvoiceLineMapper,
            SupplierInvoiceLineHandler,
            SupplierInvoiceLineRecordImporter)

        self.invoice_line_model = self.env['ofh.supplier.invoice.line']

    def _setup_records(self):
        self.import_type = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_type')
        self.backend = self.env.ref(
            'ofh_supplier_invoice_enett.enett_import_backend')

        path = get_resource_path(
            'ofh_supplier_invoice_enett',
            'tests/test_files/enett_test.csv')
        with open(path, 'rb') as fl:
            self.source = self.env['import.source.csv'].create({
                'csv_file': base64.encodestring(fl.read()),
                'csv_filename': 'enett_test.csv',
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

    def test_supplier_invoice_line_enett(self):
        for chunk in self.source.get_lines():
            self.record.set_data(chunk)
            with self.backend.work_on(
                'import.record',
                components_registry=self.comp_registry
            ) as work:
                importer = work.component_by_name(
                    'supplier.invoice.line.record.importer',
                    'ofh.supplier.invoice.line')
                self.assertTrue(importer)
                importer.run(self.record)

        # First test case
        first_line = self.invoice_line_model.search(
            [('locator', '=', '48701998417570')])
        self.assertTrue(first_line)
        self.assertEquals(len(first_line), 1)
        self.assertEquals(first_line.passenger, 'ALSUWAIDI/ABDUL')
        self.assertEquals(first_line.total, 526.58)
        self.assertEquals(first_line.invoice_status, "TKTT")
        self.assertEquals(first_line.office_id, "Travel Fusion")
        self.assertEquals(first_line.invoice_type, "enett")
        self.assertEquals(first_line.order_reference, "A446832297546")
        self.assertEquals(first_line.ticket_number, "48701998417570")

        # Second test case
        second_line = self.invoice_line_model.search(
            [('locator', '=', '48701997614560')])
        self.assertTrue(second_line)
        self.assertEquals(len(second_line), 1)
        self.assertEquals(second_line.passenger, 'ALOBAIDAN/HADI')
        self.assertEquals(second_line.total, 268.29)
        self.assertEquals(second_line.invoice_status, "TKTT")
        self.assertEquals(second_line.office_id, "Travel Fusion")
        self.assertEquals(second_line.invoice_type, "enett")
        self.assertEquals(second_line.order_reference, "A444366566766")
        self.assertEquals(second_line.ticket_number, "48701997614560")
