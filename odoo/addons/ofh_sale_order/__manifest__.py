# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Sale Order',
    'description': """
        Synch Sale orders from OMS""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_hub_connector',
    ],
    'data': [
        'security/ofh_sale_order_line.xml',
        'views/ofh_sale_order_line.xml',
        'security/ofh_sale_order.xml',
        'views/ofh_sale_order.xml',
    ],
    # 'demo': [
    #     'demo/ofh_sale_order_line.xml',
    #     'demo/ofh_sale_order.xml',
    # ],
}
