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
    ],
    'data': [
        'views/ofh_supplier_invoice_line.xml',
        'views/ofh_payment_request.xml',
    ],
    'demo': [
    ],
}
