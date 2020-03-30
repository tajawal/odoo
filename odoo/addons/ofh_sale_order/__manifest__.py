# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Sale Order',
    'description': """
        Synch Sale orders from OMS""",
    'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_hub_connector',
        'ofh_payment',
    ],
    'data': [
        'data/cron.xml',
        'security/groups.xml',
        'security/ofh_sale_order_line.xml',
        'security/ofh_sale_order.xml',
        'security/hub_sale_order_line.xml',
        'security/hub_sale_order.xml',
        'security/ofh_payment.xml',
        'security/hub_payment.xml',
        'security/ofh_payment_charge.xml',
        'security/hub_payment_charge.xml',
        'security/queue_job.xml',
        'security/ofh_hub_backend.xml',
        'views/ofh_sale_order.xml',
        'views/ofh_sale_order_line.xml',
        'views/ofh_hub_backend.xml',
        'views/ofh_sale_order_menu.xml',
    ],
    # 'demo': [
    #     'demo/ofh_sale_order_line.xml',
    #     'demo/ofh_sale_order.xml',
    # ],
}
