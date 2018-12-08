# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Mail Activity',
    'description': """
        Assign activity to list of users instead of only one user""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'mail',
    ],
    'data': [
        'templates/assets.xml',
        'security/mail_activity.xml',
    ],
    'demo': [
    ],
}
