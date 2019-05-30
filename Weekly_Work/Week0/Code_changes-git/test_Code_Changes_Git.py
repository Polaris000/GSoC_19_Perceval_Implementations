from Code_Changes_Git import Code_Changes
import unittest

class TestCode_Changes_Git(unittest.TestCase):

	def test_init(self):
		pass

	def test__summary(self):
		pass

	def test_total_count(self):
		with open('./git-commits.json') as f:
			content = f.readlines()
		total_count = len(content)
		code_changes = Code_Changes("./git-commits.json")
		self.assertEqual(total_count, code_changes.total_count())

	def test_compute(self):
		pass

	def test__count_master_only(self):
		pass

	def test_compute_testseries(self):
		pass

	def test__is_source_code(self):
		code_changes = Code_Changes("./git-commits.json", source_code_exclude_list=["py"])
		first_commit = code_changes.df.iloc[0]

		expected = True
		self.assertEqual(expected, code_changes._is_source_code(first_commit))

	def test__get_extension(self):
		file = {
				"action":"A",
				"added":"308",
				"file":"perceval/backends/git.py",
				"indexes":["0000000","0506fa5"],
				"modes":["000000","100644"],
				"removed":"0"
				}
		expected = "py"

		code_changes = Code_Changes("./git-commits.json")
		self.assertEqual(expected, code_changes._get_extension(file))


if __name__ == '__main__':
	unittest.main(verbosity=2)
