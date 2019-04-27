from os.path import dirname, join

from odoo.addons.component.tests.common import SavepointComponentCase

from vcr import VCR

recorder = VCR(
    record_mode='once',
    cassette_library_dir=join(dirname(__file__), 'fixtures/cassettes'),
    path_transformer=VCR.ensure_suffix('.yml'),
    filter_headers=['Authorization'],
)


class TestOfhSaleOrderImport(SavepointComponentCase):

    def setUp(self):
        super(TestOfhSaleOrderImport, self).setUp()

        self.backend = self.env['hub.backend'].create({
            'name': 'live-hub',
        })

        self.binding_order_model = self.env['hub.sale.order']
        self.binding_order_line_model = self.env['hub.sale.order.line']
        self.binding_payment_model = self.env['hub.payment']
        self.binding_payment_charge_model = self.env['hub.payment.charge']

    @recorder.use_cassette(record_mode='multi')
    def test_sale_order(self):
        self.binding_order_model.import_record(
            backend=self.backend,
            external_id='5caa5fd82280adfa3978fb54'
        )

        binding = self.binding_order_model.search([
            ('backend_id', '=', self.backend.id),
            ('external_id', '=', '5caa5fd82280adfa3978fb54')])

        self.assertEquals(len(binding), 1)

        self.assertEquals(len(binding.hub_line_ids), 7)

        self.assertEquals(len(binding.hub_payment_ids), 1)
        self.assertEquals(
            len(binding.hub_payment_ids.hub_charge_ids), 2)

        # Force resync a record a make sure the order lines and payments are
        # not duplicated.

        old_binding = binding

        self.binding_order_model.import_record(
            backend=self.backend,
            external_id='5caa5fd82280adfa3978fb54'
        )

        binding = self.binding_order_model.search([
            ('backend_id', '=', self.backend.id),
            ('external_id', '=', '5caa5fd82280adfa3978fb54')])

        self.assertEquals(len(binding), 1)
        self.assertEquals(binding, old_binding)
        self.assertEquals(len(binding.hub_line_ids), 7)
        self.assertEquals(
            len(binding.hub_line_ids.mapped('external_id')), 7)
        self.assertEquals(len(binding.hub_payment_ids), 1)
        self.assertEquals(
            binding.hub_payment_ids.external_id, 'charge_FB79CC175T1B627E2A8D')
        self.assertEquals(
            len(binding.hub_payment_ids.hub_charge_ids), 2)
        charges = binding.hub_payment_ids.hub_charge_ids
        self.assertTrue(
            'charge_FB79CC175T1B627E2A8D' in charges.mapped('external_id'))
        self.assertTrue(
            'charge_18EAECF75P1B630A1FA3' in charges.mapped('external_id'))
