# Copyright 2019 Tajawal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Sale Order Supplier Invoice',
    'description': """
        Link Supplier Invoice Lines to Sale Order.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_payment_request_invoice',
    ],
    'data': [
        'views/ofh_sale_order_line.xml',
        'views/ofh_supplier_invoice_line.xml',
        'views/ofh_sale_order.xml',
    ],
    'demo': [
    ],
}
