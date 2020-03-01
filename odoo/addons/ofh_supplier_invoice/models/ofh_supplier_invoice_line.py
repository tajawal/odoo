
# Copyright 2018 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import json
from odoo.exceptions import ValidationError


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
    '203': '5J', '297': 'CI', '275': 'GP',
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
    '701': 'WF', '635': 'MF', '571': '6S', '633': 'GQ', '769': 'H9', '148': 'LN'
}


class OfhSupplierInvoiceLine(models.Model):

    _name = 'ofh.supplier.invoice.line'
    _description = 'Supplier Invoice lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'invoice_date ASC'

    @api.model
    def _get_default_currency_id(self):
        return self.env.ref('base.AED')

    name = fields.Char(
        string="Unique ID",
        compute='_compute_name',
        readonly=True,
        store=True,
    )
    invoice_type = fields.Selection(
        string="Invoice from",
        selection=[],
        required=True,
        index=True,
        readonly=True,
    )
    invoice_date = fields.Date(
        string="Invoice Date",
        required=True,
        readonly=True,
    )
    ticket_number = fields.Char(
        string="Ticket",
        readonly=True,
    )
    invoice_status = fields.Selection(
        string="Ticket Status",
        selection=[('none', 'Not applicable'),
                   ('TKTT', 'Ticket'),
                   ('RFND', 'Refund')],
        required=True,
        default='none',
        readonly=True,
    )
    locator = fields.Char(
        required=True,
        readonly=True,
    )
    locators = fields.Char(
        string="Locators",
        compute='_compute_locator',
        search='_search_locator',
        store=False,
        readonly=True,
    )
    office_id = fields.Char(
        string="Office ID",
        index=True,
        readonly=True,
    )
    passenger = fields.Char(
        string="Passenger's name",
        readonly=True,
    )
    vendor_id = fields.Char(
        string="Vendor Name",
        # TODO: comodel_name='ofh.vendor',
        required=True,
        readonly=True,
    )
    fees = fields.Char(
        required=True,
        default='{}',
        readonly=True,
    )
    total = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        required=True,
        comodel_name='res.currency',
        default=_get_default_currency_id,
        readonly=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    index = fields.Char()

    order_reference = fields.Char(
        string="Tajawal ID",
    )
    agent_sign_in = fields.Char(
        string="Agent Sign In",
        readonly=True,
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
    iata_code = fields.Char(
        string="IATA Code",
        compute='_compute_iata_code',
        readonly=True,
    )

    _sql_constraints = [
        ('unique_invoice_line', 'unique(name)',
         _("This line has been uploaded"))
    ]

    @api.model
    def _search_locator(self, operator, value):
        if operator == 'ilike':
            ids = value.replace(" ", "").split(",")
            return [('locator', 'in', ids)]
        return [('locator', operator, value)]

    @api.multi
    @api.depends('locator')
    def _compute_locator(self):
        for rec in self:
            rec.locators = rec.locator

    @api.multi
    @api.constrains('invoice_date')
    def _check_invoice_date(self):
        for rec in self:
            if rec.invoice_date >= fields.Datetime.now():
                raise ValidationError(
                    _("Invalid date. Please provide date lesser than today."))

    @api.multi
    @api.depends('ticket_number', 'invoice_status', 'passenger',
                 'locator', 'invoice_date', 'vendor_id')
    def _compute_name(self):
        for rec in self:
            compute_function = '_{}_compute_name'.format(rec.invoice_type)
            if hasattr(rec, compute_function):
                getattr(rec, compute_function)()
            else:
                rec.name = '{}{}'.format(rec.invoice_type, rec.ticket_number)

    @api.multi
    @api.depends('fees', 'invoice_type')
    def _compute_fees(self):
        for rec in self:
            if not rec.fees:
                rec.gds_base_fare_amount = rec.gds_tax_amount = \
                    rec.gds_net_amount = \
                    rec.gds_fee_amount = rec.gds_iata_commission_amount = 0.0
            else:
                fees = json.loads(rec.fees)
                rec.gds_base_fare_amount = fees.get('BaseFare', 0.0)
                rec.gds_tax_amount = fees.get('Tax', 0.0)
                rec.gds_net_amount = fees.get('Net', 0.0)
                rec.gds_fee_amount = fees.get('FEE', 0.0)
                rec.gds_iata_commission_amount = fees.get('IATA COMM', 0.0)

    @api.multi
    @api.depends('vendor_id')
    def _compute_iata_code(self):
        for rec in self:
            rec.iata_code = AIRLINE_IATA_CODE.get(rec.vendor_id, '')
