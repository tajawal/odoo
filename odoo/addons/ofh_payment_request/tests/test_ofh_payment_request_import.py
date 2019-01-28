from os.path import dirname, join

from odoo.addons.component.tests.common import SavepointComponentCase
from vcr import VCR

recorder = VCR(
    record_mode='once',
    cassette_library_dir=join(dirname(__file__), 'fixtures/cassettes'),
    path_transformer=VCR.ensure_suffix('.yml'),
    filter_headers=['Authorization'],
)


class TestOfhPaymentRequestImport(SavepointComponentCase):

    def setUp(self):
        super(TestOfhPaymentRequestImport, self).setUp()

        self.backend = self.env['hub.backend'].create({
            'name': 'live-hub',
        })

        self.binding_pr_model = self.env['hub.payment.request']

    @recorder.use_cassette
    def test_import_payment_request_refund(self):
        self.binding_pr_model.import_record(
            backend=self.backend,
            external_id='pr-A90126214952-1548581919557')

        binding = self.binding_pr_model.search([
            ('backend_id', '=', self.backend.id),
            ('external_id', '=', 'pr-A90126214952-1548581919557')])

        self.assertEquals(len(binding), 1)
        self.assertEquals(binding.request_type, 'refund')
        self.assertEquals(binding.order_reference, 'A90126214952')
        self.assertEquals(binding.track_id, 'pr-A90126214952-1548581919557')
        self.assertEquals(binding.provider, 'checkoutcom')

    @recorder.use_cassette
    def test_import_payment_request_charge(self):
        self.binding_pr_model.import_record(
            backend=self.backend,
            external_id='pr-A8122509254-1548669730206')

        binding = self.binding_pr_model.search([
            ('backend_id', '=', self.backend.id),
            ('external_id', '=', 'pr-A8122509254-1548669730206')])

        self.assertEquals(len(binding), 1)
        self.assertEquals(binding.request_type, 'charge')
        self.assertEquals(binding.order_reference, 'A8122509254')
        self.assertEquals(binding.track_id, 'pr-A8122509254-1548669730206')
        self.assertEquals(binding.provider, 'checkoutcom')

    @recorder.use_cassette
    def test_import_payment_request_egypt_refund(self):
        self.binding_pr_model.import_record(
            backend=self.backend,
            external_id='pr-A90126251060-1548660909033')

        binding = self.binding_pr_model.search([
            ('backend_id', '=', self.backend.id),
            ('external_id', '=', 'pr-A90126251060-1548660909033')])

        self.assertTrue(binding.is_egypt)

    @recorder.use_cassette
    def test_import_payment_request_egypt_charge(self):
        self.binding_pr_model.import_record(
            backend=self.backend,
            external_id='pr-A90126206860-1548533642417')

        binding = self.binding_pr_model.search([
            ('backend_id', '=', self.backend.id),
            ('external_id', '=', 'pr-A90126206860-1548533642417')])

        self.assertTrue(binding.is_egypt)
