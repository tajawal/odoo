# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment Request Invoice',
    'description': """
        Link between supplier invoices and payment requests""",
    'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_sale_order_payment_request',
        'web_notify',
        'ofh_supplier_invoice_gds',
        'ofh_supplier_invoice_tf',
        'ofh_supplier_invoice_nile',
        'ofh_supplier_invoice_itl',
        'ofh_supplier_invoice_enett',
        'ofh_supplier_invoice_aig',
    ],
    'data': [
        'security/ofh_supplier_invoice.xml',
        'security/connector_importer.xml',
        'views/ofh_payment_request.xml',
        'views/ofh_supplier_invoice_line.xml',
    ],
    'demo': [
    ],
}
