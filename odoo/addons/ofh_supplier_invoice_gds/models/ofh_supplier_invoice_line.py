# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.addons.ofh_hub_connector.components.backend_adapter import HubAPI
from odoo.addons.queue_job.job import job
from odoo.tools.float_utils import float_is_zero


AIRLINE_IATA_CODE = {
    '165': 'JP', '390': 'A3', '053': 'EI', '708': 'NG',
    '845': 'P5', '555': 'SU', '044': 'AR', '547': '2K', '139': 'AM',
    '546': '8U', '439': 'ZI', '124': 'AH',
    '413': 'SZ', '514': 'G9', '844': 'E5', '311': '9P',
    '452': '3O', '465': 'KC',
    '226': '2J', '760': 'UU', '657': 'BT', '745': 'AB', '636': 'BP',
    '381': 'SM', '190': 'TY', '014': 'AC', '999': 'CA', '146': 'XK',
    '996': 'UX', '057': 'AF',
    '098': 'AI', '120': 'JS', '053': 'EI',
    '675': 'NX', '258': 'MD', '643': 'KM',
    '239': 'MK', '853': 'ML', '572': '9U',
    '186': 'SW', '086': 'NZ', '656': 'PX',
    '694': 'YW', '115': 'JU', '061': 'HM',
    '135': 'VT', '244': 'TN', '649': 'TS',
    '218': 'NF', '139': 'AM', '580': 'RU',
    '063': 'SB', '749': '4Z', '027': 'AS',
    '055': 'AZ', '205': 'NH', '110': 'UJ',
    '001': 'AA', '725': 'W3', '238': 'IZ',
    '988': 'OZ', '369': '5Y', '610': 'KK',
    '143': 'AU', '257': 'OS', '134': 'AV',
    '247': 'O6', '771': 'J2', '577': 'AD',
    '111': 'UP', '829': 'PG', '628': 'B2',
    '366': '8H', '997': 'BG', '474': 'NT',
    '475': '0B', '004': 'BV', '142': 'KF',
    '480': 'BM', '930': 'OB', '276': 'TF',
    '125': 'BA', '082': 'SN', '623': 'FB',
    '188': 'K6', '172': 'CV',
    '106': 'BW', '021': 'V3', '160': 'CX',
    '203': '5J', '297': 'CI', '275': 'APG',
    '112': 'CK', '781': 'MU', '419': 'CF', '784': 'CZ',
    '689': 'WX', '161': 'MN', '881': 'DE', '230': 'CM',
    '005': 'CO', '395': 'XC', '923': 'SS', '831': 'OU', '136': 'CU',
    '064': 'OK', '006': 'DL', '991': 'D3',
    '936': 'D0', '155': 'ES', '181': 'Z6',
    '733': 'D9', '043': 'KA', '787': 'KB',
    '888': 'U2', '000': 'DS', '077': 'MS', '114': 'LY',
    '176': 'EK', '637': 'B8', '071': 'ET', '607': 'EY', '753': 'LC',
    '551': 'YU', '615': 'QY', '104': 'EW',
    '695': 'BR', '023': 'FX', '260': 'FJ', '105': 'AY', '267': 'BE',
    '141': 'FZ', '593': 'XY', '365': 'W2', '126': 'GA', '606': 'A9',
    '246': 'ST', '051': '4U', '072': 'GF',
    '169': 'HR', '880': 'HU', '173': 'HA',
    '851': 'HX', '128': 'UO', '075': 'IB', '108': 'FI', '312': '6E',
    '958': '7I', '837': '4O', '096': 'IR',
    '815': 'EP', '818': '6H', '073': 'IA', '131': 'JL',
    '486': 'J9', '589': '9W',
    '375': '3K', '279': 'B6', '151': 'R5', '316': '5N', '018': 'HO',
    '706': 'KQ', '780': 'Y9', '074': 'KL', '180': 'KE',
    '229': 'KU', '133': 'LR',
    '068': 'TM', '045': 'LA', '469': '4M', '145': 'UC',
    '035': '4C', '544': 'LP',
    '462': 'XL', '140': 'LI', '216': 'N4', '080': 'LO',
    '220': 'LH', '020': 'LH', '683': 'CL', '149': 'LG', '537': 'W5',
    '232': 'MH', '816': 'OD', '803': 'AE', '129': 'MP',
    '865': 'M7', '076': 'ME', '817': 'MJ', '191': 'IG',
    '289': 'OM', '409': 'YM', '599': '8M', '477': 'NE', '325': 'NP',
    '933': 'KZ', '329': 'D8', '328': 'DY', '796': 'BJ', '866': 'BK',
    '050': 'OA', '910': 'WY', '066': '8Q', '291': 'R2',
    '624': 'PC', '685': 'NI',
    '079': 'PR', '214': 'PK', '031': 'PW', '081': 'QF',
    '157': 'QR', '195': 'FV', '482': 'RG', '147': 'AT', '672': 'BI',
    '285': 'RA', '512': 'RJ', '405': 'FR', '459': 'WB',
    '362': '7R', '668': 'TZ', '421': 'S7',
    '083': 'SA', '640': 'FA', '741': '4Q', '249': 'S3',
    '117': 'SK', '737': 'SP',
    '331': 'S4', '065': 'SV', '324': 'SC', '774': 'FM',
    '479': 'ZH', '618': 'SQ',
    '876': '3U', '164': '7L', '629': 'MI', '605': 'H2', '797': 'QS',
    '029': 'XZ', '775': 'SG', '487': 'NK', '603': 'UL', '200': 'SD',
    '564': 'XQ', '192': 'PY', '724': 'LX', '070': 'RB', '118': 'DT',
    '202': 'TA', '530': 'T0', '696': 'VR',
    '692': 'PZ', '957': 'JJ', '269': 'EQ', '047': 'TP',
    '281': 'RO', '515': 'SF', '217': 'TG', '388': 'TR', '979': 'HV',
    '235': 'TK', '826': 'GS', '756': '3V',
    '170': 'GE', '617': 'X3', '178': 'OR', '199': 'TU',
    '566': 'PS', '016': 'UA',
    '037': 'US', '406': '5X', '262': 'U6', '298': 'UT',
    '250': 'HY', '738': 'VN',
    '228': 'UK', '932': 'VS', '795': 'VA', '984': 'VX',
    '693': 'VG', '036': 'Y4',
    '412': 'VI', '127': 'G3', '030': 'VY', '460': 'EB',
    '838': 'WS', '097': 'WI',
    '701': 'WF', '635': 'MF', '571': '6S', '633': 'GQ', '769': 'H9'
}


class OfhSupplierInvoiceLine(models.Model):

    _inherit = 'ofh.supplier.invoice.line'

    invoice_type = fields.Selection(
        selection_add=[('gds', 'GDS')],
    )
    gds_base_fare_amount = fields.Monetary(
        string="Base Fare",
        compute='_compute_fees',
        currency_field='currency_id',
        readonly=True,
    )
    gds_tax_amount = fields.Monetary(
        string="Tax",
        compute='_compute_fees',
        currency_field='currency_id',
        readonly=True,
    )
    gds_net_amount = fields.Monetary(
        string="Net",
        compute='_compute_fees',
        currency_field='currency_id',
        readonly=True,
    )
    gds_fee_amount = fields.Monetary(
        string="Fee",
        compute='_compute_fees',
        currency_field='currency_id',
        readonly=True,
    )
    gds_iata_commission_amount = fields.Monetary(
        string="IATA Commission",
        compute='_compute_fees',
        currency_field='currency_id',
        readonly=True,
    )
    gds_alshamel_cost = fields.Monetary(
        string='Alshamel Cost',
        currency_field='currency_id',
        compute='_compute_gds_alshamel_cost',
    )
    invoice_status = fields.Selection(
        selection_add=[('AMND', 'Amendment')],
    )
    iata_code = fields.Char(
        string="IATA Code",
        compute='_compute_iata_code',
        readonly=True,
    )

    @api.multi
    def _gds_compute_name(self):
        self.ensure_one()
        self.name = '{}_{}{}'.format(
            self.invoice_type, self.ticket_number, self.invoice_status)

    @api.multi
    @api.depends('currency_id', 'total')
    def _compute_gds_alshamel_cost(self):
        """Shamel cost is 1% of the invoice line total price."""
        currency = self.env.ref('base.KWD')
        for rec in self:
            if rec.currency_id != currency:
                continue
            rec.gds_alshamel_cost = rec.total * 0.01

    @api.multi
    def _gds_compute_fees(self, fees: dict) -> None:
        self.ensure_one()
        if not fees:
            self.gds_base_fare_amount = self.gds_tax_amount = \
                self.gds_net_amount = \
                self.gds_fee_amount = self.gds_iata_commission_amount = 0.0
        else:
            self.gds_base_fare_amount = fees.get('BaseFare', 0.0)
            self.gds_tax_amount = fees.get('Tax', 0.0)
            self.gds_net_amount = fees.get('Net', 0.0)
            self.gds_fee_amount = fees.get('FEE', 0.0)
            self.gds_iata_commission_amount = fees.get('IATA COMM', 0.0)

    @api.model
    def cron_download_gds_report(self):
        offices = self.env['ofh.gds.office'].search([])
        report_day = (datetime.now() - timedelta(days=1)).\
            strftime("%d%b").upper()
        for office in offices:
            self.with_delay()._import_gds_daily_report(
                office=office, report_day=report_day)

    @job(default_channel='root.hub')
    @api.model
    def _import_gds_daily_report(self, office, report_day):
        if not office or not report_day:
            return False
        source_model = 'import.source.command_cryptic'
        source = self.env[source_model].search(
            [('office_id', '=', office.name), ('report_day', '=', report_day)],
            limit=1)
        if not source:
            source = self.env[source_model].create({
                'office_id': office.name, 'report_day': report_day})

        backend = self.env.ref('ofh_supplier_invoice_gds.gds_import_backend')
        import_type = self.env.ref('ofh_supplier_invoice_gds.gds_import_type')

        recordset = self.env['import.recordset'].create({
            'backend_id': backend.id,
            'import_type_id': import_type.id,
            'source_id': source.id,
            'source_model': source_model,
        })

        return recordset.run_import()

    @api.multi
    def action_gds_record_locator(self):
        for line in self.filtered(lambda l: l.invoice_type == 'gds'):
            line.with_delay().gds_retrieve_pnr()

    @api.multi
    @job(default_channel='root.import')
    def gds_retrieve_pnr(self):
        self.ensure_one()
        backend = self.env['hub.backend'].search([], limit=1)
        if not backend:
            return {}

        hub_api = HubAPI(oms_finance_api_url=backend.oms_finance_api_url)

        self.order_reference = hub_api.gds_retrieve_pnr(
            office_id=self.office_id, locator=self.locator)

    @api.model
    def create(self, vals):
        record = super(OfhSupplierInvoiceLine, self).create(vals)
        if record.invoice_type == 'gds':
            if float_is_zero(
                    record.total,
                    precision_rounding=record.currency_id.rounding) or \
                    not record.locator:
                record.active = False
        return record

    @api.multi
    @api.depends('vendor_id')
    def _compute_iata_code(self):
        for rec in self:
            rec.iata_code = ''
            if rec.invoice_type == 'gds':
                rec.iata_code = AIRLINE_IATA_CODE.get(rec.vendor_id, '')
