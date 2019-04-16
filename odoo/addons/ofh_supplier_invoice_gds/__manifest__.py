# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Supplier Invoice Gds',
    'description': """
        GDS Supplier Invoice""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_supplier_invoice',
        'connector_importer',
        'ofh_hub_connector',
    ],
    'data': [
        'wizards/ofh_gds_daily_report.xml',
        'data/backend.xml',
        'data/ofh_gds_office.xml',
        'wizards/ofh_supplier_invoice_import.xml',
        'views/ofh_supplier_invoice_line.xml',
        'views/ofh_gds_office.xml',
    ],
    'demo': [
        'demo/ofh_supplier_invoice_gds.xml',
    ],
}
