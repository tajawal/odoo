# Copyright 2019 Tajwal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import logging
import boto3
import io

try:
    from odoo.addons.server_environment import serv_config
except ImportError:
    logging.getLogger('odoo.module').warning(
        "server_environment not available in addons path.")

_logger = logging.getLogger(__name__)

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
        return ['s3_key_id', 's3_secret_key', 'bucket_name']

    @api.multi
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
        """Import SAP Sale report automatically from S3 bucket."""
        backend = self.env.ref(
            'ofh_payment_request_sap.sap_sale_import_backend')
        from_date = fields.Datetime.from_string(backend.last_sync_date) or None
        import_type = self.env.ref(
            'ofh_payment_request_sap.sap_sale_import_type')

        client = boto3.client(
            's3',
            aws_access_key_id=backend.aws_access_key_id,
            aws_secret_access_key=backend.aws_secret_access_key)

        objects = client.list_objects(Bucket=backend.bucket_name)['Contents']
        if not objects:
            return None
        objects = objects.sort()
        if from_date:
            files_to_import = [
                content['Key'] for content in client.list_objects(
                    Bucket=backend.bucket_name)['Contents'] if
                from_date <= content['LastModified']]
        else:
            files_to_import = [
                content['Key'] for content in client.list_objects(
                    Bucket=backend.bucket_name)['Contents']]

        for filename in files_to_import:
            data = io.StringIO()
            data = client.download_fileobj(
                Bucket=backend.bucket_name, Key=filename, Fileobj=data)

            backend._import_report(import_type, filename, data)

        return None
