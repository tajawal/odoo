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
        'ofh_connector_importer',
        'ofh_sale_order_supplier_invoice',
        'ofh_payment_request_sap',
    ],
    'data': [
        'security/ofh_payment_sap.xml',
        'security/ofh_sale_order_sap.xml',
        'security/ofh_sap_backend.xml',
        'security/ofh_sap_binding.xml',
        'views/ofh_sale_order_sap.xml',
        'views/ofh_sale_order_line_sap.xml',
        'views/ofh_sale_order.xml',
        'views/ofh_payment_sap.xml',
        'views/ofh_payment.xml',
        'views/ofh_sap_backend.xml',
        'views/ofh_payment_request.xml',
        'wizards/ofh_sale_order_sap_import.xml',
        'data/backend.xml',
        'data/sale_auto_send_cron.xml',
    ],
    'demo': [
        # 'demo/sap_backend.xml',
        # 'demo/ofh_sale_order_sap.xml',
        # 'demo/ofh_sale_order_line_sap.xml',
        # 'demo/ofh_payment_sap.xml',
    ],
}
