# -*- coding: utf-8 -*-
"""
Implementation of the XDG Shared MIME Info spec version 0.20.
http://standards.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-0.20.html

Loosely based on python-xdg and following the Qt code style.

Applications can install information about MIME types by storing an
XML file as <MIME>/packages/<application>.xml and running the
update-mime-database command, which is provided by the freedesktop.org
shared mime database package.
"""

import os
from fnmatch import fnmatch
from xml.dom import minidom, XML_NAMESPACE
from . import xdg
from ..basemime import BaseMime


class AliasesFile(object):
	"""
	/usr/share/mime/aliases
	"""
	def __init__(self):
		self._keys = {}

	def __repr__(self):
		return self._keys.__repr__()

	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.endswith("\n"):
					line = line[:-1]

				mime, alias = line.split(" ")
				self._keys[mime] = alias

	def get(self, name):
		return self._keys.get(name)

ALIASES = AliasesFile()
for f in xdg.getFiles("mime/aliases"):
	ALIASES.parse(f)


class GlobsFile(object):
	"""
	/usr/share/mime/globs2
	"""
	def __init__(self):
		self._extensions = {}
		self._literals = {}
		self._matches = []

	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.startswith("#"): # comment
					continue

				if line.endswith("\n"):
					line = line[:-1]

				weight, _, line = line.partition(":")
				mime, _, line = line.partition(":")
				glob, _, line = line.partition(":")
				flags, _, line = line.partition(":")
				flags = flags and flags.split(",") or []

				if "*" not in glob and "?" not in glob and "[" not in glob:
					self._literals[glob] = mime

				elif glob.startswith("*.") and "cs" not in flags:
					extension = glob[1:]
					if "*" not in extension and "?" not in extension and "[" not in extension:
						self._extensions[extension] = mime

				else:
					self._matches.append((int(weight), mime, glob, flags))

	def match(self, name):
		if name in self._literals:
			return self._literals[name]

		_, extension = os.path.splitext(name)
		if extension in self._extensions:
			return self._extensions[extension]
		elif extension.lower() in self._extensions:
			return self._extensions[extension.lower()]

		matches = []
		for weight, mime, glob, flags in self._matches:
			if fnmatch(name, glob):
				matches.append((weight, mime, glob))

			elif "cs" not in flags and fnmatch(name.lower(), glob):
				matches.append((weight, mime, glob))

		if not matches:
			return ""

		weight, mime, glob = max(matches, key=lambda (weight, mime, glob): (weight, len(glob)))
		return mime

GLOBS = GlobsFile()
for f in xdg.getFiles("mime/globs2"):
	GLOBS.parse(f)


class IconsFile(object):
	"""
	/usr/share/mime/icons
	/usr/share/mime/generic-icons
	"""
	def __init__(self):
		self._keys = {}

	def __repr__(self):
		return self._keys.__repr__()

	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.endswith("\n"):
					line = line[:-1]

				mime, icon = line.split(":")
				self._keys[mime] = icon

	def get(self, name):
		return self._keys.get(name)

ICONS = IconsFile()
for f in xdg.getFiles("mime/generic-icons"):
	ICONS.parse(f)


class SubclassesFile(object):
	"""
	/usr/share/mime/subclasses
	"""
	def __init__(self):
		self._keys = {}

	def __repr__(self):
		return self._keys.__repr__()

	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.endswith("\n"):
					line = line[:-1]

				mime, subclass = line.split(" ")
				if mime not in self._keys:
					self._keys[mime] = []
				self._keys[mime].append(subclass)

	def get(self, name, default=None):
		return self._keys.get(name, default)

SUBCLASSES = SubclassesFile()
for f in xdg.getFiles("mime/subclasses"):
	SUBCLASSES.parse(f)

class MimeType(BaseMime):

	@staticmethod
	def installPackage(package, base=os.path.join(xdg.XDG_DATA_HOME, "mime")):
		from shutil import copyfile
		path = os.path.join(base, "packages")
		if not os.path.exists(path):
			os.makedirs(path)
		copyfile(package, os.path.join(path, os.path.basename(package)))
		xdg.updateMimeDatabase()

	@classmethod
	def fromName(cls, name):
		mime = GLOBS.match(name)
		if mime:
			return cls(mime)

	@classmethod
	def fromContent(cls, name):
		try:
			stat = os.stat(name)
		except IOError:
			return

		if stat.st_size == 0:
			return cls(cls.ZERO_SIZE)

	def aliases(self):
		if not self._aliases:
			files = xdg.getMimeFiles(self.name())
			if not files:
				return

			for file in files:
				doc = minidom.parse(file)
				for node in doc.documentElement.getElementsByTagName("alias"):
					alias = node.getAttribute("type")
					if alias not in self._aliases:
						self._aliases.append(alias)

		return self._aliases

	def aliasOf(self):
		return ALIASES.get(self.name())

	def comment(self, lang="en"):
		if lang not in self._comment:
			files = xdg.getMimeFiles(self.name())
			if not files:
				return

			for file in files:
				doc = minidom.parse(file)
				for comment in doc.documentElement.getElementsByTagNameNS(xdg.FREEDESKTOP_NS, "comment"):
					nslang = comment.getAttributeNS(XML_NAMESPACE, "lang") or "en"
					if nslang == lang:
						self._comment[lang] = "".join(n.nodeValue for n in comment.childNodes).strip()
						break

		if lang in self._comment:
			return self._comment[lang]

	def genericIcon(self):
		return ICONS.get(self.name()) or super(MimeType, self).genericIcon()

	def subClassOf(self):
		return [MimeType(mime) for mime in SUBCLASSES.get(self.name(), [])]

	# MIME Actions

	def associations(self):
		from . import actions
		return actions.associationsFor(self.name())

	def bestApplication(self):
		from . import actions
		return actions.bestApplication(self.name())

	def defaultApplication(self):
		from . import actions
		return actions.defaultApplication(self.name())
