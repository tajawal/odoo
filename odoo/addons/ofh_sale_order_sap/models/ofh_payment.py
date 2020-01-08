# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
from odoo import api, fields, models
from odoo.addons.queue_job.job import job
from odoo.exceptions import ValidationError
import xxhash


class OfhPayment(models.Model):
    _inherit = 'ofh.payment'

    sap_payment_ids = fields.One2many(
        string="SAP Payments",
        comodel_name="ofh.payment.sap",
        inverse_name='payment_id',
        readonly=True,
    )
    is_payment_applicable = fields.Boolean(
        string="Is Payment Applicable?",
        default=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )
    payment_integration_status = fields.Boolean(
        string="Is Payment Sent?",
        readonly=True,
        index=True,
        default=False,
        store=False,
        compute='_compute_payment_integration_status',
        search='_search_payment_integration_status',
    )
    payment_sap_status = fields.Boolean(
        string="Is Payment in SAP?",
        readonly=True,
        index=True,
        default=False,
        store=False,
        compute='_compute_payment_sap_status',
        search='_search_payment_sap_status',
    )

    @api.multi
    @api.depends('sap_payment_ids.state', 'is_payment_applicable')
    def _compute_payment_integration_status(self):
        for rec in self:
            rec.payment_integration_status = rec.sap_payment_ids.filtered(
                lambda p: p.state == 'success') and \
                                             rec.is_payment_applicable

    @api.model
    def _search_payment_integration_status(self, operator, value):
        if operator == '!=':
            self.env.cr.execute("""
                    SELECT id AS payment_id FROM ofh_payment
                    EXCEPT
                        SELECT payment_id
                        FROM ofh_payment_sap 
                        WHERE state = 'success' AND payment_id > 0;
               """)
            payment_ids = [x[0] for x in self.env.cr.fetchall()]
        else:
            self.env.cr.execute("""
                    SELECT payment_id 
                    FROM ofh_payment_sap 
                    WHERE state = 'success' AND payment_id > 0
               """)
            payment_ids = [x[0] for x in self.env.cr.fetchall()]

        if not payment_ids:
            return [('id', '=', 0)]

        return [('id', 'in', payment_ids)]

    @api.multi
    @api.depends('sap_payment_ids.state', 'is_payment_applicable')
    def _compute_payment_sap_status(self):
        for rec in self:
            rec.payment_integration_status = rec.sap_payment_ids.filtered(
                lambda p: p.state == 'success' and
                p.sap_status == 'in_sap') and rec.is_payment_applicable

    @api.model
    def _search_payment_sap_status(self, operator, value):
        if operator == '!=':
            self.env.cr.execute("""
                    SELECT payment_id 
                    FROM ofh_payment_sap 
                    WHERE state = 'success' 
                    AND payment_id > 0 
                    AND sap_status != 'in_sap';
                """)
            payment_ids = [x[0] for x in self.env.cr.fetchall()]
        else:
            self.env.cr.execute("""
                    SELECT payment_id 
                    FROM ofh_payment_sap 
                    WHERE state = 'success' 
                    AND payment_id > 0 
                    AND sap_status = 'in_sap';
                """)
            payment_ids = [x[0] for x in self.env.cr.fetchall()]
        print(len(payment_ids))
        if not payment_ids:
            return [('id', '=', 0)]

        return [('id', 'in', payment_ids)]

    @api.multi
    def _prepare_payment_values(self, visualize=False):
        self.ensure_one()
        dt = fields.Datetime.now()
        backend = self.env['sap.backend'].search([], limit=1)
        values = {
            'send_date': dt,
            'backend_id': backend.id,
            'payment_detail': json.dumps(self.to_dict()),
            'payment_id': self.id
        }
        if visualize:
            values['state'] = 'visualize'

        return values

    @api.multi
    def send_payment_to_sap(self):
        """Create and Send SAP Sale Order Record."""
        self.ensure_one()
        values = self._prepare_payment_values()
        return self.env['ofh.payment.sap'].create(values)

    @api.multi
    def force_send_payment_to_sap(self):
        self.ensure_one()
        values = self._prepare_payment_values()

        return self.env['ofh.payment.sap'].with_context(
            force_send=True).create(values)

    @api.multi
    def visualize_sap_payment(self):
        self.ensure_one()

        values = self._prepare_payment_values(visualize=True)

        return self.env['ofh.payment.sap'].create(values)

    @api.multi
    def to_dict(self) -> dict:
        """Return dict of Sap Sale Order
        Returns:
            [dict] -- Sap Sale Order dictionary
        """
        self.ensure_one()

        adict = {
            "file_id": self._get_file_number(),
            "booking_number": self._get_booking_number(),
            "order_type": '',
            "order_status": '',
            "entity": '',
            "ahs_group_name": self.ahs_group_name,
            "country_code": '',
            "payment_provider": self.provider,
            "payment_source": self.source,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "reference_id": self.reference_id,
            "currency": self.currency_id.name,
            "amount": self.total_amount,
            "document_date": self.created_at,
            "mid": self.mid,
            "successfactor_id": self.successfactors_id,
            "cashier_id": self.cashier_id,
            "card_type": self.card_type,
            "card_bin": self.card_bin,
            "card_owner": self.card_name,
            "card_last_four": self.last_four,
            "auth_code": self.auth_code,
            "is_installment": self.is_installment,
            "is_apple_pay": self.is_apple_pay,
            "is_mada": self.is_mada,
            "is_3d_secure": self.is_3d_secure,
            "is_egypt": self.order_id.is_egypt,
            "is_refund": self.payment_category == 'refund',
        }

        if self.order_id:
            adict["order_type"] = self.order_id.order_type
            adict["order_status"] = self.order_id.order_status
            adict["entity"] = self.order_id.entity
            adict["country_code"] = self.order_id.country_code

        if self.payment_request_id and self.payment_request_id.order_id:
            order = self.payment_request_id.order_id
            adict["order_type"] = order.order_type
            adict["order_status"] = order.order_status
            adict["entity"] = order.entity
            adict["country_code"] = order.country_code

        return adict

    @api.multi
    def _get_file_number(self):
        self.ensure_one()
        if self.file_reference:
            return self.file_reference

        if self.order_id:
            order = self.order_id
        elif self.payment_request_id and self.payment_request_id.order_id:
            order = self.payment_request_id.order_id
        else:
            return ''

        if order.booking_category == 'initial':
            order_id = order.hub_bind_ids.external_id
        else:
            order_id = order.hub_bind_ids.initial_order_id

        hash_order_id = format(xxhash.xxh32_intdigest(order_id), 'x')
        return f"{hash_order_id}{int(order_id[-6:], 16)}"

    @api.multi
    def _get_booking_number(self):
        self.ensure_one()
        if self.file_reference:
            return f"{self.file_reference}_{self._get_file_payment_suffix()}"

        if self.payment_request_id:
            return self.payment_request_id._get_refund_booking_number()

        if self.order_id:
            order = self.order_id
        else:
            return self.track_id[:25]

        if order.booking_category == 'amendment':
            return self._get_amendment_booking_number(order)

        return order.name

    @api.multi
    def _get_amendment_booking_number(self, order):
        self.ensure_one()
        if not order or order.booking_category != 'amendment':
            return ''

        _mongo_id = order.hub_bind_ids.initial_order_id
        order_number = order.initial_order_number
        suffix = order._get_amendment_suffix()

        hash_mongo_id = format(xxhash.xxh32_intdigest(_mongo_id), 'x')
        return f"{order_number}{int(hash_mongo_id[-6:], 16)}{suffix}"

    @api.multi
    def _get_file_payment_suffix(self):
        self.ensure_one()
        payments = self.search([('file_reference', '=', self.file_reference)])
        payment_ids = payments.sorted(lambda r: r.created_at).mapped('id')
        return payment_ids.index(self.id)

    @api.model
    def _auto_send_payments_to_sap(self):
        """Auto Send candidates Payments to SAP."""
        self.env.cr.execute(
            """select id from ofh_payment_auto_send""")
        for record in self.env.cr.fetchall():
            self.with_delay()._auto_send_payment_to_sap(payment_id=record[0])

    @api.model
    @job(default_channel='root.sap')
    def _auto_send_payment_to_sap(self, payment_id):
        """Auto Send a payment to SAP."""
        if not payment_id:
            return

        payment = self.browse(payment_id)
        return payment.send_payment_to_sap()

    # @api.model
    # def create(self, vals):
    #     payment = super(OfhPayment, self).create(vals)

    #     # Only Captured, Refunded
    #     if (payment.payment_method == 'online' and
    #         payment.payment_status in ('11111', '83027')) or \
    #             (payment.payment_method != 'online' and
    #              payment.payment_method == '1000'):
    #         payment.send_payment_to_sap()
    #     return payment

    @api.multi
    def action_payment_not_applicable(self):
        if self.filtered(lambda o: o.payment_integration_status):
            raise ValidationError("Payment already sent to SAP.")
        return self.write({
            'is_payment_applicable': False,
        })

    @api.multi
    def action_payment_applicable(self):
        return self.write({
            'is_payment_applicable': True,
        })

    @api.multi
    @api.depends('is_payment_applicable')
    def action_payment_sent_sap(self):
        for rec in self:
            if rec.is_payment_applicable:
                return self.write({
                    'payment_integration_status': True,
                })

    @api.multi
    def action_payment_to_sap(self):
        for rec in self:
            rec.with_delay().send_payment_to_sap()

    @api.multi
    @job(default_channel='root.sap')
    def send_payment_to_sap(self):
        """Create and Send SAP Sale Order Record."""
        self.ensure_one()

        values = self._prepare_payment_values()
        return self.env['ofh.payment.sap'].create(values)
