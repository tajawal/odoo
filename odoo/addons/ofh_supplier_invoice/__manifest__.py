
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Supplier Invoice',
    'description': """
        Allow users to upload Vendor incoices""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'mail',
        'ofh_connector_importer',
        'web_notify',
    ],
    'data': [
        'security/groups.xml',
        'security/ofh_supplier_invoice.xml',
        'security/connector_importer.xml',
        'wizards/ofh_supplier_invoice_import.xml',
        'views/ofh_supplier_invoice.xml',
    ],
    'demo': [
    ],
}
