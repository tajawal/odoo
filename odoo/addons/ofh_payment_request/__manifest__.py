# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment Request',
    'description': """
        Synchronisation of payment request from HUB""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_hub_connector',
        'mail',
    ],
    'data': [
        'security/groups.xml',
        'security/hub_payment_request.xml',
        'security/ofh_payment_request.xml',
        'security/ofh_hub_backend.xml',
        'views/ofh_payment_request.xml',
    ],
    'demo': [
        'demo/ofh_payment_request.xml',
    ],
}
