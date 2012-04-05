# -*- coding: utf-8 -*-
"""
XDG Trash implementation
"""

import os
import shutil
from time import strftime
from .basedir import XDG_DATA_HOME

TRASH_HOME = os.path.join(XDG_DATA_HOME, "Trash")

TRASH_INFO_TEMPLATE = """[Trash Info]
Path=%(path)s
DeletionDate=%(deletionDate)s
"""

class Trash(object):
	def __init__(self, path=TRASH_HOME):
		self._path = path

	def __contains__(self, item):
		"""
		Returns True if the trash contains \a item
		"""
		return item in self.files()

	def __len__(self):
		"""
		Returns the amount of files contained inside the trash
		"""
		return len(self.files())

	def __repr__(self):
		return "Trash(%r)" % (self.path())

	def _cleanup(self, name):
		"""
		Deletes the file \a name and its associated metadata
		from the trash if it exists
		"""
		self._deleteFile(name)
		self._deleteInfo(name)

	def _deleteFile(self, name):
		"""
		Deletes the file \a name from the trash if it exists
		"""
		path = os.path.join(self.filesPath(), name)
		if os.path.exists(path):
			os.remove(path)

	def _deleteInfo(self, name):
		"""
		Deletes the metadata associated with the file
		\a name from the trash if it exists
		"""
		path = os.path.join(self.infoPath(), name + ".trashinfo")
		if os.path.exists(path):
			os.remove(path)

	def _writeInfo(self, name, path, deletionDate):
		with open(os.path.join(self.infoPath(), name + ".trashinfo"), "w") as f:
			f.write(TRASH_INFO_TEMPLATE % {"path": path, "deletionDate": deletionDate})
		return f.name

	def delete(self, name):
		"""
		Deletes the file \a name from the trash
		Raises a KeyError if the file is not in the trash
		"""
		if name not in self:
			raise KeyError(name)
		self._cleanup(name)

	def empty(self):
		"""
		Empties the trash
		"""
		for file in self.files():
			self.delete(file)

	def files(self):
		"""
		Returns a list of file names in the trash
		"""
		return os.listdir(self.filesPath())

	def filesPath(self):
		"""
		Returns the path to the files directory for the trash
		"""
		return os.path.join(self.path(), "files")

	def infoPath(self):
		"""
		Returns the path to the info directory for the trash
		"""
		return os.path.join(self.path(), "info")

	def isEmpty(self):
		"""
		Returns True if the trash is empty; otherwise returns False
		"""
		return len(self) == 0

	def trash(self, path):
		"""
		Moves the file at \a path to the trash
		Raises an IOError if the file does not exist
		"""
		if not os.path.exists(path):
			raise IOError("No such file or directory")

		name = os.path.basename(path)
		if os.path.exists(os.path.join(self.filesPath(), name)):
			_name = name + ".1"
			i = 1
			while os.path.exists(os.path.join(self.filesPath(), _name)):
				i += 1
				_name = "%s.%i" % (name, i)
			name = _name

		self._writeInfo(name=name, path=path, deletionDate=strftime("%Y-%m-%dT%H:%M:%S"))
		try:
			shutil.move(path, os.path.join(self.filesPath(), name))
		except Exception:
			self._cleanup(name)
			raise

	def path(self):
		"""
		Returns the path to the trash
		Note that this is the path to the actual trash, not the directory
		containing the files. For that, use filesPath()
		"""
		return self._path
