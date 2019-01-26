# Copyright 2019 Tajwal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import io
import logging

import boto3
import pytz
from botocore.exceptions import ClientError
from odoo import api, fields, models

try:
    from odoo.addons.server_environment import serv_config
except ImportError:
    logging.getLogger('odoo.module').warning(
        "server_environment not available in addons path.")

_logger = logging.getLogger(__name__)
_importer_logger = logging.getLogger('[importer]')

AWS_CONFIG_SECTION_NAME = 'aws.credentials'


class ImportBackend(models.Model):

    _inherit = 'import.backend'

    is_s3_bucket = fields.Boolean(
        string='Use S3 Bucket',
        default=False,
    )
    aws_access_key_id = fields.Char(
        string="AWS access key ID",
        compute='_compute_s3_credentials',
        store=False,
        readonly=True,
    )
    aws_secret_access_key = fields.Char(
        string="AWS secret access key",
        compute='_compute_s3_credentials',
        store=False,
        readonly=True,
    )
    bucket_name = fields.Char(
        string="Bucket Name",
        compute='_compute_s3_credentials',
        store=False,
        readonly=True,
    )
    last_sync_date = fields.Datetime(
        string="Last Sync Date",
    )
    s3_bucket_file_prefix = fields.Char(
        string='File Prefix in bucket',
    )

    @property
    def s3_credentials_fields(self):
        return ['aws_access_key_id', 'aws_secret_access_key', 'bucket_name']

    @api.multi
    @api.depends('is_s3_bucket')
    def _compute_s3_credentials(self):
        section_name = AWS_CONFIG_SECTION_NAME
        for backend in self:
            if not backend.is_s3_bucket:
                continue
            for field_name in self.s3_credentials_fields:
                try:
                    value = serv_config.get(section_name, field_name)
                    backend[field_name] = value
                except Exception:
                    _logger.exception(
                        f"error trying to read field "
                        f"{field_name} in section {section_name}")

    @api.model
    def _import_sap_sale_report(self) -> None:
        """Import SAP sale report automatically from S3 bucket."""
        backend = self.env.ref(
            'ofh_payment_request_sap.sap_sale_import_backend')

        import_type = self.env.ref(
            'ofh_payment_request_sap.sap_sale_import_type')

        _importer_logger.info(
            f"Start importing SAP Sale report from S3 bucket: "
            f"{backend.bucket_name}.")

        client = boto3.client(
            's3',
            aws_access_key_id=backend.aws_access_key_id,
            aws_secret_access_key=backend.aws_secret_access_key)

        _importer_logger.info(
            "Get the list of files to import from the bucket.")
        objects = client.list_objects(Bucket=backend.bucket_name)['Contents']
        if not objects:
            _importer_logger.warning(
                f"The bucket {backend.bucket_name} is empty, "
                "no file to import.")
            return None

        files_to_import = backend._get_files_to_download(client=client)

        for filename in files_to_import:
            _importer_logger.info(f"Start importing: {filename}.")
            try:
                data = io.BytesIO()
                client.download_fileobj(
                    Bucket=backend.bucket_name, Key=filename, Fileobj=data)
            except ClientError:
                _importer_logger.exception(
                    f"Error trying to download the file: {filename}.")
                continue

            _importer_logger.info(f"Importing: {filename}.")
            backend._import_report(
                import_type=import_type,
                file_name=filename,
                data=base64.encodestring(data.getvalue()))

        backend.last_sync_date = fields.Datetime.now()
        return None

    @api.multi
    def _get_files_to_download(self, client) -> list:
        """Return the list of file to import from the S3 bucket.

        :param client: S3 bucket boto3 client
        :return: List of file name to download ['VBAK_1', 'VBAK_2', ...].
        :rtype: list
        """
        self.ensure_one()
        from_date = fields.Datetime.from_string(
            self.last_sync_date).replace(tzinfo=pytz.timezone('UTC')) or None
        if from_date:
            files_to_import = [
                content['Key'] for content in client.list_objects(
                    Bucket=self.bucket_name)['Contents'] if
                from_date <= content['LastModified'].replace(
                    tzinfo=pytz.timezone('UTC')) and
                str(content['Key']).startswith(self.s3_bucket_file_prefix)]
        else:
            files_to_import = [
                content['Key'] for content in client.list_objects(
                    Bucket=self.bucket_name)['Contents'] if
                str(content['Key']).startswith(self.s3_bucket_file_prefix)]

        _importer_logger.info(
            f"Download the following list of files from the bucket: "
            f"{files_to_import}")

        return files_to_import
