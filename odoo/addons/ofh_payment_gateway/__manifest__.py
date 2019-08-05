# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment Gateway',
    'description': """
        Synchronisation of payments from Payment Gateway""",
    'version': '11.0.1.1.1',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
    ],
    'data': [
        'security/groups.xml',
        'views/ofh_payment_gateway.xml',
    ],
    'demo': [
        'demo/ofh_payment_gateway.xml',
    ],
}
