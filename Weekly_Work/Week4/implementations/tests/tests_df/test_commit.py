import datetime
import unittest
import sys
sys.path.append('../..')
from code_df.commit import Commit
from code_df import utils


class TestCommit(unittest.TestCase):

    def test_init(self):
        pass

    def test__flatten(self):
        items = utils.read_JSON_file('../test_commits_data.json')
        commit = Commit(items)

        flat_item = commit._flatten(items[0])
        flat_expected = {
            {'repo': 'http://github.com/chaoss/grimoirelab-perceval',
             'hash': 'dc78c254e464ff334892e0448a23e4cfbfc637a3',
             'author': 'Santiago Dueñas <sduenas@bitergia.com>',
             'category': 'commit',
             'created_date': datetime.datetime(2015, 8, 18, 0, 0),
             'committer': 'Santiago Dueñas <sduenas@bitergia.com>',
             'commit_date': datetime.datetime(2015, 8, 18, 0, 0),
             'files_no': 3,
             'refs': [],
             'parents': [],
             'files': [
                {'action': 'A', 'added': '10', 'file': '.gitignore', 'indexes': ['0000000', 'ceaedd5'],
                 'modes': ['000000', '100644'], 'removed': '0'},
                {'action': 'A', 'added': '1', 'file': 'AUTHORS', 'indexes': ['0000000', 'a67f214'],
                 'modes': ['000000', '100644'], 'removed': '0'},
                {'action': 'A', 'added': '674', 'file': 'LICENSE', 'indexes': ['0000000', '94a9ed0'],
                 'modes': ['000000', '100644'], 'removed': '0'}], 'files_action': 3}
        }
        self.assertEqual(flat_item, flat_expected)

if __name__ == '__main__':
    unittest.main(verbosity=2)