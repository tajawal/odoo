# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Sale Order Payment Request',
    'description': """
        Linking fields between payment request and sale order """,
    'version': '11.0.1.1.1',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_payment_request',
        'ofh_sale_order',
    ],
    'data': [
        'views/ofh_payment_request.xml',
        'views/ofh_sale_order.xml',
    ],
    'demo': [
    ],
}
