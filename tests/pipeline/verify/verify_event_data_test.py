import unittest

import pandas as pd

from pipeline.verify.verify_event_data import validate_eligibility_dtype


class EventDataVerifierTest(unittest.TestCase):
    def test_string_false_is_not_accepted_as_boolean_eligibility(self):
        events = pd.DataFrame({"record_eligible_for_era5": ["False"]})
        with self.assertRaisesRegex(ValueError, "boolean"):
            validate_eligibility_dtype(events)

    def test_boolean_eligibility_is_accepted(self):
        events = pd.DataFrame({"record_eligible_for_era5": [False, True]})
        validate_eligibility_dtype(events)


if __name__ == "__main__":
    unittest.main()
