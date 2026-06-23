import unittest

from v8unpack.decoder import available_types
from v8unpack.MetaObject.ExternalDataProcessor import ExternalDataProcessor


class TestExternalReportSupport(unittest.TestCase):
    """ExternalReport (.erf) must be registered in available_types
    and map to ExternalDataProcessor — same as ExternalDataProcessor (.epf).
    """

    def test_external_report_registered(self):
        self.assertIn(
            'ExternalReport',
            available_types,
            "ExternalReport not found in available_types — .erf files will fail to decode"
        )

    def test_external_report_maps_to_external_data_processor(self):
        self.assertIs(
            available_types['ExternalReport'],
            ExternalDataProcessor,
            "ExternalReport must map to ExternalDataProcessor (same binary format as .epf)"
        )


if __name__ == '__main__':
    unittest.main()
