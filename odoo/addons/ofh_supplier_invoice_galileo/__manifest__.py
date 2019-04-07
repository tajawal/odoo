# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Supplier Invoice Galileo',
    'description': """
        Galileo Supplier Invoice""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_supplier_invoice_gds',
        'connector_importer',
        'ofh_hub_connector',
    ],
    'data': [
        'data/backend.xml',
        'wizards/ofh_supplier_invoice_import.xml',
        'views/ofh_supplier_invoice_line.xml',
    ],
    'demo': [
        'demo/ofh_supplier_invoice_galileo.xml',
    ],
}
