# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment Request Sap',
    'description': """
        Match SAP Reports with payment
        request to determine the status in SAP""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_payment_request_invoice',
        'connector_importer',
        'web_notify',
    ],
    'data': [
        'wizards/ofh_payment_request_integration_update.xml',
        'data/backend.xml',
        'data/cron.xml',
        'views/ofh_payment_request.xml',
        'wizards/ofh_payment_request_sap_import.xml',
    ],
    'demo': [
    ],
    'external_dependencies': {
        'python': ['pymongo'],
    },
}
