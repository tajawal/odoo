# Copyright 2019 Tajawal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Sale Order Supplier Invoice',
    'description': """
        Link Supplier Invoice Lines to Sale Order.""",
    'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_supplier_invoice_tv',
        'ofh_payment_request_invoice',
    ],
    'data': [
        'security/connector_importer.xml',
        'security/ofh_supplier_invoice.xml',
        'security/ofh_gds_office.xml',
        'wizards/ofh_sale_order_line_reconciliation_tag.xml',
        'wizards/ofh_sale_order_line_investigation_tag.xml',
        'wizards/ofh_supplier_invoice_line_investigation_tag.xml',
        'wizards/ofh_payment_request_not_applicable.xml',
        'wizards/ofh_payment_request_reconciliation_tag.xml',
        'wizards/ofh_sale_order_not_applicable.xml',
        'wizards/ofh_sale_order_line_not_applicable.xml',
        'wizards/ofh_supplier_invoice_run_matching.xml',
        'wizards/ofh_supplier_invoice_force_match.xml',
        'views/ofh_sale_order_line.xml',
        'views/ofh_supplier_invoice_line.xml',
        'views/ofh_sale_order.xml',
        'views/ofh_payment_request.xml',
    ],
    'demo': [
    ],
    'post_init_hook': 'post_init_hook',
}
