# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Supplier Invoice Aig',
    'description': """
        AIG supplier invoice lines""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_supplier_invoice',
        'connector_importer',
    ],
    'data': [
        'wizards/ofh_supplier_invoice_import.xml',
        'views/ofh_supplier_invoice_line.xml',
        'data/backend.xml',
    ],
    'demo': [
        'demo/ofh_supplier_invoice_line.xml',
    ],
}
