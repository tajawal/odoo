# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment Request Invoice',
    'description': """
        Link between supplier invoices and payment requests""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_payment_request',
        'ofh_supplier_invoice_gds',
        'ofh_supplier_invoice_tf',
        'web_notify',
    ],
    'data': [
        'wizards/ofh_supplier_invoice_run_matching.xml',
        'views/ofh_payment_request.xml',
        'views/ofh_supplier_invoice_line.xml',
    ],
    'demo': [
    ],
}
