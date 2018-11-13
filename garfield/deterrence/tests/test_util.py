from unittest import TestCase

from deterrence.util import lowercase_sentence


class UtilTestCase(TestCase):
    def test_lowercase_sentence(self):
        test = lowercase_sentence("This is a test.")

        self.assertEqual(test,
                         "this is a test.")
