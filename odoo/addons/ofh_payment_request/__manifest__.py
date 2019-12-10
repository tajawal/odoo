# Copyright 2018 Tajawal LCC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ofh Payment Request',
    'description': """
        Synchronisation of payment request from HUB""",
    'version': '11.0.1.2.0',
    'license': 'AGPL-3',
    'author': 'Tajawal LLC',
    'website': 'https://tajawal.com',
    'depends': [
        'ofh_hub_connector',
        'ofh_mail_activity',
        'ofh_base_currency',
        'ofh_payment',
    ],
    'data': [
        'security/groups.xml',
        'security/hub_payment_request.xml',
        'security/ofh_payment_request.xml',
        'security/ofh_hub_backend.xml',
        'security/queue_job.xml',
        'security/ofh_payment.xml',
        'security/hub_payment.xml',
        'views/ofh_payment_request.xml',
        'data/mail_activity_type.xml',
    ],
    'demo': [
        'demo/ofh_payment_request.xml',
    ],
}
