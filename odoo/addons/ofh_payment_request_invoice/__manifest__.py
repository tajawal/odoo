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
        'ofh_sale_order_payment_request',
        'ofh_supplier_invoice_gds',
        'ofh_supplier_invoice_tf',
        'ofh_supplier_invoice_aig',
        'ofh_supplier_invoice_galileo',
        'ofh_supplier_invoice_enett',
        'ofh_supplier_invoice_itl',
        'ofh_supplier_invoice_nile',
        'ofh_supplier_invoice_tv',
        'web_notify',
    ],
    'data': [
        'security/ofh_supplier_invoice.xml',
        'security/connector_importer.xml',
        'wizards/ofh_supplier_invoice_force_match.xml',
        'wizards/ofh_supplier_invoice_run_matching.xml',
        'views/ofh_payment_request.xml',
        'views/ofh_supplier_invoice_line.xml',
    ],
    'demo': [
    ],
}
