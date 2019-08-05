# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Bank Settlement',
    'description': """
        Synchronisation of payments from Bank Settlement""",
    'version': '11.0.1.1.1',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
    ],
    'data': [
        'security/groups.xml',
        'views/ofh_bank_settlement.xml',
    ],
    'demo': [
        'demo/ofh_bank_settlement.xml',
    ],
}
