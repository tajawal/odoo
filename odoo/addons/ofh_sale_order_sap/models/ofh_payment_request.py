# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import logging
from odoo.exceptions import ValidationError

from odoo import _, api, fields, models
from odoo.exceptions import MissingError, UserError
from odoo.tools import float_is_zero
from odoo.addons.queue_job.job import job


_logger = logging.getLogger(__name__)


class OfhPaymentRequest(models.Model):

    _inherit = 'ofh.payment.request'

    sap_order_ids = fields.One2many(
        string="SAP Orders",
        comodel_name="ofh.sale.order.sap",
        inverse_name='payment_request_id',
        readonly=True,
    )
    sap_payment_ids = fields.One2many(
        string="SAP Payments",
        comodel_name="ofh.payment.sap",
        inverse_name='payment_request_id',
        readonly=True,
    )
    new_integration_status = fields.Boolean(
        string="Is Sent?",
        readonly=True,
        index=True,
        default=False,
        store=False,
        compute='_compute_integration_status',
        search='_search_integration_status',
    )
    new_payment_integration_status = fields.Boolean(
        string="Is Payment Sent?",
        readonly=True,
        index=True,
        default=False,
        store=False,
        compute='_compute_payment_integration_status',
        search='_search_payment_integration_status',
    )
    new_sap_status = fields.Boolean(
        string="In SAP?",
        readonly=True,
        index=True,
        default=False,
        compute='_compute_sap_status',
        search='_search_sap_status',
    )
    new_payment_sap_status = fields.Boolean(
        string="Is Payment in SAP?",
        readonly=True,
        index=True,
        default=False,
        store=False,
        compute='_compute_payment_sap_status',
        search='_search_payment_sap_status',
    )
    is_sale_applicable = fields.Boolean(
        string="Is Sale Applicable?",
        default=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    is_payment_applicable = fields.Boolean(
        string="Is Payment Applicable?",
        default=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )

    @api.multi
    @api.depends('sap_order_ids.state', 'sap_order_ids.payment_request_id')
    def _compute_integration_status(self):
        for rec in self:
            rec.new_integration_status = rec.sap_order_ids.filtered(
                lambda s: s.state == 'success' and s.payment_request_id)

    @api.model
    def _search_integration_status(self, operator, value):
        if operator == '!=':
            self.env.cr.execute("""
                select id as payment_request_id from ofh_payment_request
                except
                select payment_request_id
                FROM ofh_sale_order_sap WHERE
                state = 'success' AND payment_request_id > 0;
            """)
        else:
            self.env.cr.execute("""
                SELECT payment_request_id FROM ofh_sale_order_sap WHERE
                state = 'success' AND payment_request_id > 0
            """)

        pr_ids = [x[0] for x in self.env.cr.fetchall()]

        if not pr_ids:
            return [('id', '=', 0)]

        return [('id', 'in', pr_ids)]

    @api.multi
    @api.depends('sap_payment_ids.state', 'sap_payment_ids.payment_request_id')
    def _compute_payment_integration_status(self):
        for rec in self:
            rec.new_payment_integration_status = rec.sap_payment_ids.filtered(
                lambda p: p.state == 'success' and p.payment_request_id)

    @api.model
    def _search_payment_integration_status(self, operator, value):
        if operator == '!=':
            self.env.cr.execute("""
                select id as payment_request_id from ofh_payment_request
                except
                select payment_request_id
                FROM ofh_payment_sap WHERE
                state = 'success' AND payment_request_id > 0;
            """)
        else:
            self.env.cr.execute("""
                SELECT payment_request_id FROM ofh_payment_sap WHERE
                state = 'success' AND payment_request_id > 0
            """)

        pr_ids = [x[0] for x in self.env.cr.fetchall()]

        if not pr_ids:
            return [('id', '=', 0)]

        return [('id', 'in', pr_ids)]

    @api.multi
    @api.depends(
        'sap_order_ids.state',
        'sap_order_ids.sap_status', 'sap_order_ids.payment_request_id')
    def _compute_sap_status(self):
        for rec in self:
            rec.new_sap_status = rec.sap_order_ids.filtered(
                lambda s: s.state == 'success' and s.payment_request_id and
                s.sap_status == 'in_sap')

    @api.model
    def _search_sap_status(self, operator, value):
        if operator == '!=':
            self.env.cr.execute("""
                SELECT payment_request_id
                FROM ofh_sale_order_sap WHERE
                    state = 'success' AND
                    payment_request_id > 0 AND
                    sap_status != 'in_sap';
            """)
        else:
            self.env.cr.execute("""
                SELECT payment_request_id
                FROM ofh_sale_order_sap WHERE
                    state = 'success' AND
                    payment_request_id > 0 AND
                    sap_status = 'in_sap';
            """)

        pr_ids = [x[0] for x in self.env.cr.fetchall()]

        if not pr_ids:
            return [('id', '=', 0)]

        return [('id', 'in', pr_ids)]

    @api.multi
    @api.depends(
        'sap_payment_ids.state', 'sap_payment_ids.sap_status',
        'sap_payment_ids.payment_request_id')
    def _compute_payment_sap_status(self):
        for rec in self:
            rec.new_payment_sap_status = rec.sap_payment_ids.filtered(
                lambda p: p.state == 'success' and p.payment_request_id and
                p.sap_status == 'in_sap')

    @api.model
    def _search_payment_sap_status(self, operator, value):
        if operator == '!=':
            self.env.cr.execute("""
                SELECT payment_request_id
                FROM ofh_payment_sap WHERE
                    state = 'success' AND
                    payment_request_id > 0 AND
                    sap_status != 'in_sap';
            """)
        else:
            self.env.cr.execute("""
                SELECT payment_request_id
                FROM ofh_payment_sap WHERE
                    state = 'success' AND
                    payment_request_id > 0 AND
                    sap_status = 'in_sap';
            """)

        pr_ids = [x[0] for x in self.env.cr.fetchall()]

        if not pr_ids:
            return [('id', '=', 0)]

        return [('id', 'in', pr_ids)]

    @api.multi
    def _get_payment_request_suffix(self) -> str:
        self.ensure_one()
        payment_requests = self.order_id.payment_request_ids.filtered(
            lambda r: r.request_type == self.request_type).sorted(
                lambda r: r.created_at).mapped('id')
        suffix = 'A' if self.request_type == 'charge' else 'R'
        index = payment_requests.index(self.id)
        return f"{suffix}{index}"

    @api.multi
    def _get_payment_request_order(self):
        self.ensure_one()
        order_detail = self.order_id.to_dict()
        order_detail['created_at'] = self.updated_at
        if self.request_type != 'charge':
            order_detail['is_refund'] = True
        order_detail['is_payment_request'] = True
        order_detail['suffix'] = self._get_payment_request_suffix()
        return order_detail

    @api.multi
    def _get_payment_request_lines(self) -> list:
        self.ensure_one()
        # Case no matching required for payment request.
        if not self.order_id.line_ids:
            return []
        if self.matching_status == 'not_applicable':
            sap_zsel = abs(self.sap_zsel) - abs(self.sap_zdis)
            line_dict = self.order_id.line_ids[0].to_dict()[0]

            line_dict['custom1'] = self.updated_at
            line_dict['billing_date'] = self.updated_at
            line_dict["vat_tax_code"] = self.tax_code
            line_dict["item_currency"] = self.currency_id.name

            line_dict['cost_price'] = abs(
                self.currency_id.round(self.sap_zvd1))

            line_dict['sale_price'] = abs(self.currency_id.round(sap_zsel))

            line_dict['discount'] = abs(self.currency_id.round(self.sap_zdis))

            line_dict['output_vat'] = abs(
                self.currency_id.round(self.sap_zvt1))

            if self.manual_sap_zvd1_currency:
                line_dict['cost_currency'] = \
                    self.manual_sap_zvd1_currency.name
            elif self.supplier_currency_id:
                line_dict['cost_currency'] = self.supplier_currency_id.name
            else:
                line_dict['cost_currency'] = self.currency_id.name

            lines = [line_dict]

        # Case matched with supplier add the line depending the supplier
        # requirement
        else:
            invoice_type = self.supplier_invoice_ids.mapped('invoice_type')[0]
            compute_function = f'_get_{invoice_type}_payment_request_dict'
            if hasattr(self, compute_function):
                lines = getattr(self, compute_function)()

            else:
                raise MissingError(_("Method not implemented."))

        # Add a change fee line if there is any.
        if not float_is_zero(
                self.change_fee,
                precision_rounding=self.currency_id.rounding):
            line_dict = dict(lines[0])
            line_dict['cost_price'] = 0.0
            line_dict['sale_price'] = abs(self.sap_change_fee_zsel)
            line_dict['discount'] = 0.0
            line_dict['output_vat'] = abs(self.sap_change_fee_zvt1)
            line_dict['is_change_fee'] = True
            if float_is_zero(
                    self.sap_change_fee_zvt1,
                    precision_rounding=self.currency_id.rounding):
                line_dict['vat_tax_code'] = 'SZ'
            else:
                line_dict['vat_tax_code'] = 'SS'
            lines.append(line_dict)

        return lines

    @api.multi
    def _get_payment_request_payment(self):
        self.ensure_one()
        if self.order_id.line_ids:
            validating_carrier = self.order_id.line_ids[0].validating_carrier
        else:
            validating_carrier = ''

        charges = self.payment_ids.charge_ids.sorted(lambda c: c.created_at, reverse=True)
        payment_dict = {
            "id": self.order_id.hub_bind_ids.external_id,
            "name": self.order_id.name,
            "order_type": self.order_id.order_type,
            "order_status": self.order_id.order_status,
            "validating_carrier": validating_carrier,
            "order_owner": self.order_id.order_owner,
            "entity": self.order_id.entity,
            "ahs_group_name": self.order_id.ahs_group_name,
            "country_code": self.order_id.country_code,
            "is_egypt": self.order_id.is_egypt,
            "amount": abs(self.total_amount),
            "currency": self.currency_id.name,
            "document_date": self.updated_at,
            "auth_code": '',
            "payment_provider": '',
            "payment_source": '',
            "payment_mode": '',
            "payment_status": charges[0].status if charges else '',
            "mid": '',
            "card_bin": '',
            "card_last_four": '',
            "card_type": '',
            "payment_method": '',
            "reference_id": '',
            "bank_name": '',
            "card_owner": '',
            "is_installment": False,
            "is_3d_secure": False,
            "suffix": self._get_payment_request_suffix(),
        }

        if self.request_type != 'charge':
            payment_dict['is_refund'] = True

        for charge in charges:
            if charge.auth_code:
                payment_dict['auth_code'] = charge.auth_code

            if charge.provider:
                payment_dict['payment_provider'] = charge.provider

            if charge.source:
                payment_dict['payment_source'] = charge.source

            if charge.payment_mode:
                payment_dict['payment_mode'] = charge.payment_mode

            if charge.mid:
                payment_dict['mid'] = charge.mid

            if charge.card_bin:
                payment_dict['card_bin'] = charge.card_bin

            if charge.last_four:
                payment_dict['card_last_four'] = charge.last_four

            if charge.card_type:
                payment_dict['card_type'] = charge.card_type

            if charge.payment_method:
                payment_dict['payment_method'] = charge.payment_method

            if charge.reference_id:
                payment_dict['reference_id'] = charge.reference_id

            if charge.bank_name:
                payment_dict['bank_name'] = charge.bank_name

            if charge.card_owner:
                payment_dict['card_owner'] = charge.card_owner

            if charge.is_3d_secure:
                payment_dict['is_3d_secure'] = charge.is_3d_secure

            if charge.is_installment:
                payment_dict['is_installment'] = charge.is_installment

        return payment_dict

    @api.multi
    def _prepare_sap_lines_values(self):
        self.ensure_one()
        lines = []
        dt = fields.Datetime.now()
        backend = self.env['sap.backend'].search([], limit=1)
        for line in self._get_payment_request_lines():
            lines.append((0, 0, {
                'send_date': dt,
                'backend_id': backend.id,
                'payment_request_id': self.id,
                'line_detail': json.dumps(line)}))
        return lines

    @api.multi
    def _prepare_payment_values(self, visualize=False):
        self.ensure_one()
        payments = []
        dt = fields.Datetime.now()
        backend = self.env['sap.backend'].search([], limit=1)
        values = {
            'send_date': dt,
            'backend_id': backend.id,
            'payment_detail': json.dumps(self._get_payment_request_payment()),
            'payment_request_id': self.id
        }
        if visualize:
            values['state'] = 'visualize'
        payments.append((0, 0, values))
        return payments

    @api.multi
    def _prepare_sap_order_values(self, visualize=False):
        backend = self.env['sap.backend'].search([], limit=1)
        values = {
            'send_date': fields.Datetime.now(),
            'payment_request_id': self.id,
            'backend_id': backend.id,
            'order_detail': json.dumps(self._get_payment_request_order()),
            'sap_line_ids': self._prepare_sap_lines_values(),
            'sap_payment_ids': self._prepare_payment_values(visualize),
            'is_refund': True,
        }
        if visualize:
            values['state'] = 'visualize'

        return values

    @api.multi
    def visualize_sap_order(self):
        self.ensure_one()
        if self.request_type == 'void':
            raise UserError("Void Payment Request.")
        if self.matching_status not in ('matched', 'not_applicable'):
            raise UserError("Unmatched Payment Request.")
        values = self._prepare_sap_order_values(visualize=True)

        return self.env['ofh.sale.order.sap'].create(values)

    @api.multi
    @job(default_channel='root')
    def send_payment_request_to_sap(self):
        # TODO: remove the method from ofh_payment_request_sap.
        if self.request_type == 'void':
            _logger.warn(f"PR# {self.track_id} is `void`. Skipp it.")
            return False

        if self.matching_status not in ('matched', 'not_applicable'):
            _logger.warn(f"PR# {self.track_id} is not matched yet. Skipp it.")
            return False

        if self.payment_request_status == 'incomplete':
            _logger.warn(f"PR# {self.track_id} is incomplete. Skipp it.")
            return False

        values = self._prepare_sap_order_values()
        return self.env['ofh.sale.order.sap'].create(values)

    @api.multi
    def force_send_payment_request_order_to_sap(self):
        self.ensure_one()
        if self.request_type == 'void':
            _logger.warn(f"PR# {self.track_id} is `void`. Skipp it.")
            return False

        if self.matching_status not in ('matched', 'not_applicable'):
            _logger.warn(f"PR# {self.track_id} is not matched yet. Skipp it.")
            return False

        if self.payment_request_status == 'incomplete':
            _logger.warn(f"PR# {self.track_id} is incomplete. Skipp it.")
            return False

        values = self._prepare_sap_order_values()
        # When force sending, for send only the sale part.
        values.pop('sap_payment_ids')

        return self.env['ofh.sale.order.sap'].with_context(
            force_send=True).create(values)

    @api.multi
    def force_send_payment_of_payment_request_to_sap(self):
        self.ensure_one()
        if self.request_type == 'void':
            _logger.warn(f"PR# {self.track_id} is `void`. Skipp it.")
            return False

        if self.matching_status not in ('matched', 'not_applicable'):
            _logger.warn(f"PR# {self.track_id} is not matched yet. Skipp it.")
            return False

        if self.payment_request_status == 'incomplete':
            _logger.warn(f"PR# {self.track_id} is incomplete. Skipp it.")
            return False

        values = self._prepare_payment_values()
        for value in values:
            self.env['ofh.payment.sap'].with_context(
                force_send=True).create(value[2])

    @api.multi
    def action_not_applicable(self):
        if self.filtered(
                lambda o:
                o.new_integration_status or o.new_payment_integration_status):
            raise ValidationError(
                "Sale Order or Payment already sent to SAP.")
        return self.write({
            'is_sale_applicable': False,
            'is_payment_applicable': False,
        })

    @api.multi
    def action_applicable(self):
        return self.write({
            'is_sale_applicable': True,
            'is_payment_applicable': True,
        })

    @api.multi
    def action_sale_not_applicable(self):
        if self.filtered(lambda o: o.new_integration_status):
            raise ValidationError("Sale Order already sent to SAP.")
        return self.write({
            'is_sale_applicable': False,
        })

    @api.multi
    def action_sale_applicable(self):
        return self.write({
            'is_sale_applicable': True,
        })

    @api.multi
    def action_payment_not_applicable(self):
        if self.filtered(lambda o: o.new_payment_integration_status):
            raise ValidationError("Payment already sent to SAP.")
        return self.write({
            'is_payment_applicable': False,
        })

    @api.multi
    def action_payment_applicable(self):
        return self.write({
            'is_payment_applicable': True,
        })
