# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Sale Order SAP',
    'description': """
        Represent SAP Sale orders""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'connector',
        'ofh_sale_order_supplier_invoice',
    ],
    'data': [
        'views/ofh_sale_order_sap.xml',
        'views/ofh_sale_order_line_sap.xml',
        'views/ofh_sale_order.xml',
        'views/ofh_payment_sap.xml',
        'views/ofh_payment.xml',
        'views/ofh_sap_backend.xml',
    ],
    'demo': [
        # 'demo/sap_backend.xml',
        # 'demo/ofh_sale_order_sap.xml',
        # 'demo/ofh_sale_order_line_sap.xml',
        # 'demo/ofh_payment_sap.xml',
    ],
}
