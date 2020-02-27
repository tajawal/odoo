# Copyright 2019 Tajawal LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import xxhash

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.queue_job.job import job


class OfhSaleOrder(models.Model):
    _inherit = 'ofh.sale.order'

    sap_order_ids = fields.One2many(
        string="SAP Orders",
        comodel_name="ofh.sale.order.sap",
        inverse_name='sale_order_id',
        readonly=True,
    )
    is_sale_applicable = fields.Boolean(
        string="Is Sale Applicable?",
        default=True,
        readonly=True,
        index=True,
        track_visibility='onchange',
    )

    integration_status = fields.Boolean(
        string="Is Sent?",
        readonly=True,
        index=True,
        default=False,
        store=False,
        compute='_compute_integration_status',
        search='_search_integration_status',
    )

    sap_status = fields.Boolean(
        string="In SAP?",
        readonly=True,
        index=True,
        default=False,
        compute='_compute_sap_status',
        search='_search_sap_status',
    )

    sale_not_payment_sap_status = fields.Boolean(
        string="Sale not Payment in SAP?",
        readonly=True,
        store=False,
        help="Technical field to search Sale Order which the Sale part is "
             "in SAP and the payment is not in SAP.",
        search='_search_sale_not_payment_sap_status',
    )
    payment_not_sale_sap_status = fields.Boolean(
        string="Payment not Sale in SAP?",
        readonly=True,
        store=False,
        search='_search_payment_not_sale_sap_status',
        help="Technical field to search Sale Order which the Sale part is "
             "not in SAP and the payment is in SAP.",
    )

    @api.multi
    @api.depends('sap_order_ids.state', 'is_sale_applicable')
    def _compute_integration_status(self):
        for rec in self:
            rec.integration_status = rec.sap_order_ids.filtered(
                lambda s: s.state == 'success' and s.sale_order_id) and \
                rec.is_sale_applicable

    @api.model
    def _search_integration_status(self, operator, value):
        if operator == '!=':
            self.env.cr.execute("""
                select id as sale_order_id from ofh_sale_order
                except
                select sale_order_id
                FROM ofh_sale_order_sap WHERE
                state = 'success' AND sale_order_id > 0;
            """)
            order_ids = [x[0] for x in self.env.cr.fetchall()]
        else:
            self.env.cr.execute("""
                SELECT sale_order_id FROM ofh_sale_order_sap WHERE
                state = 'success' AND sale_order_id > 0
            """)
            order_ids = [x[0] for x in self.env.cr.fetchall()]

        if not order_ids:
            return [('id', '=', 0)]

        return [('id', 'in', order_ids)]

    @api.multi
    @api.depends('sap_order_ids.state', 'is_sale_applicable')
    def _compute_sap_status(self):
        for rec in self:
            rec.sap_status = rec.sap_order_ids.filtered(
                lambda s: s.state == 'success' and s.sale_order_id and
                s.sap_status == 'in_sap') and rec.is_sale_applicable

    @api.model
    def _search_sap_status(self, operator, value):
        if operator == '!=':
            self.env.cr.execute("""
                SELECT sale_order_id
                FROM ofh_sale_order_sap WHERE
                    state = 'success' AND
                    sale_order_id > 0 AND
                    sap_status != 'in_sap';
            """)
            order_ids = [x[0] for x in self.env.cr.fetchall()]
        else:
            self.env.cr.execute("""
                SELECT sale_order_id
                FROM ofh_sale_order_sap WHERE
                    state = 'success' AND
                    sale_order_id > 0 AND
                    sap_status = 'in_sap';
            """)
            order_ids = [x[0] for x in self.env.cr.fetchall()]

        if not order_ids:
            return [('id', '=', 0)]

        return [('id', 'in', order_ids)]

    @api.model
    def _search_sale_not_payment_sap_status(self, operator, value):
        if operator == '!=':
            return [('id', '=', 0)]

        self.env.cr.execute("""
            SELECT sale_order_id
            FROM ofh_payment_sap WHERE
                state = 'success' AND
                sale_order_id > 0 AND
                sap_status != 'in_sap'
            INTERSECT
            SELECT sale_order_id
            FROM ofh_sale_order_sap WHERE
                state = 'success' AND
                sale_order_id > 0 AND
                sap_status = 'in_sap';
            """)
        order_ids = [x[0] for x in self.env.cr.fetchall()]
        if not order_ids:
            return [('id', '=', 0)]

        return [('id', 'in', order_ids)]

    @api.model
    def _search_payment_not_sale_sap_status(self, operator, value):
        if operator == '!=':
            return [('id', '=', 0)]

        self.env.cr.execute("""
            SELECT sale_order_id
            FROM ofh_sale_order_sap WHERE
                state = 'success' AND
                sale_order_id > 0 AND
                sap_status != 'in_sap'
            INTERSECT
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
    def action_send_order_to_sap(self):
        for rec in self:
            rec.with_delay().send_order_to_sap()

    @api.multi
    def _prepare_sap_lines_values(self):
        self.ensure_one()
        lines = []
        dt = fields.Datetime.now()
        backend = self.env['sap.backend'].search([], limit=1)
        for line in self.line_ids:
            inv_lines = line.to_dict()
            for inv_line in inv_lines:
                lines.append((0, 0, {
                    'send_date': dt,
                    'backend_id': backend.id,
                    'sale_order_line_id': line.id,
                    'line_detail': json.dumps(inv_line)}))
        return lines

    @api.multi
    def _prepare_sap_order_values(self, visualize=False):
        backend = self.env['sap.backend'].search([], limit=1)
        values = {
            'send_date': fields.Datetime.now(),
            'sale_order_id': self.id,
            'backend_id': backend.id,
            'order_detail': json.dumps(self.to_dict()),
            'sap_line_ids': self._prepare_sap_lines_values(),
        }
        if visualize:
            values['state'] = 'visualize'

        return values

    @api.multi
    @job(default_channel='root.sap')
    def send_order_to_sap(self):
        """Create and Send SAP Sale Order Record."""
        self.ensure_one()

        values = self._prepare_sap_order_values()
        return self.env['ofh.sale.order.sap'].create(values)

    @api.multi
    def force_send_order_to_sap(self):
        self.ensure_one()

        values = self._prepare_sap_order_values()

        return self.env['ofh.sale.order.sap'].with_context(
            force_send=True).create(values)

    @api.multi
    def visualize_sap_order(self):
        self.ensure_one()

        values = self._prepare_sap_order_values(visualize=True)

        return self.env['ofh.sale.order.sap'].create(values)

    @api.multi
    def to_dict(self) -> dict:
        """Return dict of Sap Sale Order
        Returns:
            [dict] -- Sap Sale Order dictionary
        """

        self.ensure_one()
        ahs_group_name = self.ahs_group_name
        if not ahs_group_name and self.line_ids:
            ahs_group_name = self.line_ids.mapped('ahs_group_name')[0]

        return {
            "name": self._get_order_number(),
            "file_number": self._get_file_number(),
            "booking_id": self._get_order_name(),
            "order_type": self.order_type,
            "created_at": self.created_at,
            "currency": self.currency_id.name,
            "ahs_group_name": ahs_group_name,
            "entity": self.entity,
            "country_code": self.country_code,
            "is_egypt": self.is_egypt,
            "payment_provider":
            self.payment_ids[0].provider if self.payment_ids else '',
            'is_payment_request': self.booking_category == 'amendment',
        }

    @api.multi
    def _get_order_number(self):
        self.ensure_one()
        if self.booking_category == 'initial' or (
                        self.booking_category == 'amendment' and self.is_unify):
            return self.name
        else:
            return self.initial_order_number

    @api.multi
    def _get_file_number(self):
        self.ensure_one()
        if self.file_reference:
            return self.file_reference

        if self.booking_category == 'initial':
            order_id = self.hub_bind_ids.external_id
        else:
            order_id = self.hub_bind_ids.initial_order_id

        hash_order_id = format(xxhash.xxh32_intdigest(order_id), 'x')
        return f"{hash_order_id}{int(order_id[-6:], 16)}"

    @api.multi
    def _get_order_name(self):
        self.ensure_one()
        mongo_id = self.hub_bind_ids.external_id
        if self.store_id == '1000':
            return f"{self.name}_{int(mongo_id[-6:], 16)}"

        if self.booking_category == 'amendment':
            return self._get_amendment_booking_number()

        return f"{self.name}_{int(mongo_id[-6:], 16)}"

    @api.multi
    def _get_amendment_booking_number(self):
        self.ensure_one()

        _mongo_id = self.hub_bind_ids.initial_order_id
        order_number = self.initial_order_number
        suffix = self._get_amendment_suffix()

        hash_mongo_id = format(xxhash.xxh32_intdigest(_mongo_id), 'x')
        return f"{order_number}_{int(hash_mongo_id[-6:], 16)}_{suffix}"

    @api.multi
    def _get_amendment_suffix(self) -> str:
        self.ensure_one()
        amendments = self.search(
            [('initial_order_number', '=', self.initial_order_number)])
        amendment_ids = amendments.sorted(
            lambda r: r.created_at).mapped('id')
        suffix = 'A'
        index = amendment_ids.index(self.id)
        return f"{suffix}{index}"

    @api.multi
    def action_applicable(self):
        return self.write({
            'is_sale_applicable': True,
        })

    @api.multi
    def action_sale_not_applicable(self):
        if self.filtered(lambda o: o.integration_status):
            raise ValidationError("Sale Order already sent to SAP.")
        return self.write({
            'is_sale_applicable': False,
        })

    @api.multi
    def action_sale_applicable(self):
        return self.write({
            'is_sale_applicable': True,
        })

    @api.model
    def _auto_send_flight_orders_to_sap(self):
        """Auto Send candidates orders to SAP."""
        self.env.cr.execute(
            """select id from ofh_sale_order_flight_auto_send""")
        for record in self.env.cr.fetchall():
            self.with_delay()._auto_send_to_sap(order_id=record[0])

    @api.model
    def _auto_send_hotel_orders_to_sap(self):
        """Auto Send candidates orders to SAP."""
        self.env.cr.execute(
            """select id from ofh_sale_order_hotel_auto_send""")
        for record in self.env.cr.fetchall():
            self.with_delay()._auto_send_to_sap(order_id=record[0])

    @api.model
    @job(default_channel='root.sap')
    def _auto_send_to_sap(self, order_id):
        """Auto Send a sale order to SAP."""
        if not order_id:
            return

        order = self.browse(order_id)
        return order.send_order_to_sap()
