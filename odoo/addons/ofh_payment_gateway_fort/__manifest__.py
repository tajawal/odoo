# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment Gateway Fort',
    'description': """
        Synchronisation of payments from Payment Gateway for Fort""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_payment_gateway',
        'ofh_hub_connector',
    ],
    'data': [
        'data/backend.xml',
        'wizards/ofh_payment_gateway_line_import.xml',
        'views/ofh_payment_gateway.xml',
    ],
    'demo': [
        # 'demo/ofh_payment_gateway.xml',
    ],
}
