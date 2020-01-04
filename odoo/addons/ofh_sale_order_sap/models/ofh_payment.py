# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
from odoo import api, fields, models
from odoo.addons.queue_job.job import job
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
                   select id as sale_order_id from ofh_sale_order
                   except
                   select sale_order_id
                   FROM ofh_payment_sap WHERE
                   state = 'success' AND sale_order_id > 0;
               """)
            order_ids = [x[0] for x in self.env.cr.fetchall()]
        else:
            self.env.cr.execute("""
                   SELECT sale_order_id FROM ofh_payment_sap WHERE
                   state = 'success' AND sale_order_id > 0
               """)
            order_ids = [x[0] for x in self.env.cr.fetchall()]

        if not order_ids:
            return [('id', '=', 0)]

        return [('id', 'in', order_ids)]

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
                    SELECT sale_order_id
                    FROM ofh_payment_sap WHERE
                        state = 'success' AND
                        sale_order_id > 0 AND
                        sap_status != 'in_sap';
                """)
            order_ids = [x[0] for x in self.env.cr.fetchall()]
        else:
            self.env.cr.execute("""
                    SELECT sale_order_id
                    FROM ofh_payment_sap WHERE
                        state = 'success' AND
                        sale_order_id > 0 AND
                        sap_status = 'in_sap';
                """)
            order_ids = [x[0] for x in self.env.cr.fetchall()]

        if not order_ids:
            return [('id', '=', 0)]

        return [('id', 'in', order_ids)]

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
        }

        if self.order_id:
            adict["order_type"] = self.order_id.order_type
            adict["order_status"] = self.order_id.order_status
            adict["entity"] = self.order_id.entity
            adict["country_code"] = self.order_id.country_code

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
            return self.file_reference

        if self.order_id:
            order = self.order_id
        elif self.payment_request_id and self.payment_request_id.order_id:
            order = self.payment_request_id.order_id
        else:
            return self.track_id[:25]

        if order.booking_category == 'amendment':
            return order.initial_order_number

        return order.name

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

    @job(default_channel='root.hub')
    @api.multi
    def action_update_hub_data(self):
        self.ensure_one()
        if self.payment_category == 'charge':
            payment_type = 'amendment'
        elif self.payment_category == 'refund':
            payment_type = 'refund'
        elif self.order_id.booking_category:
            payment_type = self.order_id.booking_category
        else:
            payment_type = 'amendment'

        return self.hub_bind_ids.import_record(
            backend=self.hub_bind_ids.backend_id,
            external_id=self.hub_bind_ids.external_id,
            payment_type=payment_type,
            force=True)

    @api.multi
    def open_payment_in_hub(self):
        """Open the order link to the payment request in hub using URL
        Returns:
            [dict] -- URL action dictionary
        """

        self.ensure_one()
        hub_backend = self.env['hub.backend'].search([], limit=1)
        if not hub_backend:
            return

        hub_url = ''
        if self.file_id:
            hub_url = "{}admin/unify/file/{}".format(
                hub_backend.hub_api_location, self.file_id)
        elif self.order_id:
            hub_url = "{}admin/order/air/detail/{}".format(
                hub_backend.hub_api_location, self.order_id.name)

        return {
            "type": "ir.actions.act_url",
            "url": hub_url,
            "target": "new",
        }
