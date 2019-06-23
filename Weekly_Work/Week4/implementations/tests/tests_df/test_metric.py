import unittest
import sys
sys.path.append('..')
sys.path.append('../..')
from code_df.metric import Metric
from code_df import utils


class TestMetric(unittest.TestCase):

    def test_init(self):
        pass

    def test__flatten(self):
        """Test whether a NotImplementedError is thrown"""

        items = utils.read_JSON_file('../test_commits_data.json')

        with self.assertRaises(NotImplementedError):
            metric = Metric(items)
            for item in items:
                metric._flatten(item)


if __name__ == '__main__':
    unittest.main(verbosity=2)

