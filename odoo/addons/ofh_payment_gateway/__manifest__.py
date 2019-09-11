# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment Gateway',
    'description': """
        Synchronisation of payments from Payment Gateway""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_hub_connector',
        'ofh_payment',
        'ofh_payment_request',
    ],
    'data': [
        # 'security/groups.xml',
        'views/ofh_payment_gateway.xml',
        'views/ofh_payment_gateway_line.xml',
        'wizards/ofh_payment_gateway_line_import.xml',
    ],
}
