# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Hub Connector',
    'description': """
        Hub Connector""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'http://tajawal.com/',
    'depends': [
        'connector',
    ],
    'data': [
        # 'security/ofh_hub_backend.xml',
        'views/ofh_hub_backend.xml',
    ],
    'demo': [
        'demo/hub_backend.xml',
    ],
}
