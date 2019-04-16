from os.path import dirname, join

from odoo.addons.component.tests.common import SavepointComponentCase
from vcr import VCR

recorder = VCR(
    record_mode='once',
    cassette_library_dir=join(dirname(__file__), 'fixtures/cassettes'),
    path_transformer=VCR.ensure_suffix('.yml'),
    filter_headers=['Authorization'],
)


class TestOfhPaymentImport(SavepointComponentCase):

    def setUp(self):
        super(TestOfhPaymentImport, self).setUp()

        self.backend = self.env['hub.backend'].create({
            'name': 'live-hub',
        })

        self.binding_pr_model = self.env['hub.payment']

    @recorder.use_cassette
    def test_import_payment_1(self):
        self.binding_pr_model.import_record(
            backend=self.backend,
            external_id='f610e7ec-0725-4fa1-bc81-759924f580e2')

        binding = self.binding_pr_model.search([
            ('backend_id', '=', self.backend.id),
            ('external_id', '=', 'f610e7ec-0725-4fa1-bc81-759924f580e2')])

        self.assertEquals(len(binding), 1)
        self.assertEquals(binding.track_id,
                          'f610e7ec-0725-4fa1-bc81-759924f580e2')
        self.assertEquals(binding.provider, 'checkoutcom')

        self.assertEquals(binding.total_amount, 310.34)
