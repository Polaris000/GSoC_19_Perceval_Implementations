import pandas as pd
import utils

class SourceCode:

	def __init__(self):
		pass

	# The methods below will pertain to other methods of determining the condition
	# for source code: like excluding the tests/ directory for example.

	def x():
		pass

	def y():
		pass

	@staticmethod
	def _is_source_code(commit, source_code_exclude_list):
		"""
		Given a commit structure, which is a dictionary returned by the _summary function, 
		and given a list of files to exclude using source_code_exclude_list while instantiating 
		an object, decide whether all the files in a commit are to be excluded or not
		
		:param commit: a commit structure, returned by the _summary method.
		"""
		extension_set = set()
		for file in commit['files']:
			extension_set.add(SourceCode._get_extension(file))

		if source_code_exclude_list is None or len(extension_set.difference(source_code_exclude_list)) > 0:
			return True
		return False
	
	@staticmethod
	def _get_extension(file):
		"""
		Given a file structure, which is a dictionary and an element of commit['files'], 
		return the extension of that file. 
		For files without a standard ".xyz" extension, like LICENCE or AUTHORS, the "others" 
		extension is used. 
		
		:param file: a file structure which is a dictionary, an element of commit["files"]
		"""
			
		file_name = file['file']
		if '.' in file_name:
			file_extension = file_name.split('.')[1]
		else:
			file_extension = "other"
		return file_extension