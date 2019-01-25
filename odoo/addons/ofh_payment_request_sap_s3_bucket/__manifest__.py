# Copyright 2019 Tajwal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'SAP Report Import from S3 Bucket',
    'description': """
        Connect to S3 Bucket to get SAP files to import""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Tajwal LLC',
    'website': 'https://tajawal.com/',
    'depends': [
        'ofh_payment_request_sap',
    ],
    'external_dependencies': {
        'python': ['boto3'],
    },
    'data': [
        'data/backend.xml',
        'views/import_backend.xml',
    ],
}
