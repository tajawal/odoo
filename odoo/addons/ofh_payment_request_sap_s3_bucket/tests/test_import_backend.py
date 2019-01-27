# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import boto3
from dateutil.relativedelta import relativedelta
from moto import mock_s3
from odoo import fields
from odoo.modules.module import get_resource_path
from odoo.tests.common import SavepointCase


class TestImportBackend(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestImportBackend, cls).setUpClass()

        cls.backend = cls.env.ref(
            'ofh_payment_request_sap.sap_sale_import_backend')

        cls.client = boto3.client(
            's3',
            aws_access_key_id=cls.backend.aws_access_key_id,
            aws_secret_access_key=cls.backend.aws_secret_access_key)

    @mock_s3
    def test_get_files_to_download(self):
        client = boto3.client(
            's3',
            aws_access_key_id=self.backend.aws_access_key_id,
            aws_secret_access_key=self.backend.aws_secret_access_key)

        client.create_bucket(Bucket=self.backend.bucket_name)

        result = self.backend._get_files_to_download(client)
        self.assertFalse(result)

        path = get_resource_path(
            'ofh_payment_request_sap_s3_bucket',
            'tests/test_files/csv_va05_test1.csv')

        client.upload_file(
            Filename=path,
            Bucket=self.backend.bucket_name,
            Key=f"{self.backend.s3_bucket_file_prefix}1")

        result = self.backend._get_files_to_download(client)
        self.assertTrue(result)
        self.assertEquals(len(result), 1)

        self.backend.last_sync_date = fields.Datetime.from_string(
            fields.Datetime.now()) + relativedelta(days=10)

        result = self.backend._get_files_to_download(client)
        self.assertFalse(result)
