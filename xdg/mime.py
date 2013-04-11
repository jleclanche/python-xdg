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
import struct
from fnmatch import fnmatch
from xml.dom import minidom, XML_NAMESPACE
from . import xdg


FREEDESKTOP_NS = "http://www.freedesktop.org/standards/shared-mime-info"

TEXTCHARS = bytes("".join(map(chr, [7, 8, 9, 10, 12, 13, 27] + list(range(0x20, 0x100)))), "utf-8")

def _isBinaryString(bytes):
	"""
	Determine if a string is classified as binary rather than text.
	Same algorithm as used in file(1)
	"""
	nontext = bytes.translate(None, TEXTCHARS)
	return bool(nontext)

def _readNumber(file):
	"""
	Read a number from a binary stream
	"""
	ret = bytearray()
	c = file.read(1)
	while c:
		if not c.isdigit():
			file.seek(-1, os.SEEK_CUR)
			break
		ret.append(ord(c))
		c = file.read(1)

	return int(ret or 0)

def installPackage(package, base=os.path.join(xdg.XDG_DATA_HOME, "mime")):
	"""
	Helper to install \a package to \a base and update the database
	The base argument defaults to $XDG_DATA_HOME/mime
	"""
	from shutil import copyfile
	path = os.path.join(base, "packages")
	if not os.path.exists(path):
		os.makedirs(path)
	copyfile(package, os.path.join(path, os.path.basename(package)))
	xdg.updateMimeDatabase(base)

def unalias(mime):
	"""
	If \a mime is an alias of another MimeType, return the target MimeType.
	Otherwise, returns the MimeType instance of the given mime.
	"""
	if not isinstance(mime, MimeType):
		mime = MimeType(mime)
	alias = mime.aliasOf()
	if alias:
		return alias
	return mime

class BaseFile(object):
	def __init__(self):
		self._keys = {}

	def __repr__(self):
		return self._keys.__repr__()

	def get(self, name, default=None):
		return self._keys.get(name, default)

class AliasesFile(BaseFile):
	"""
	/usr/share/mime/aliases
	"""
	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.endswith("\n"):
					line = line[:-1]

				mime, alias = line.split(" ")
				self._keys[mime] = alias

ALIASES = AliasesFile()
for path in xdg.getFiles("mime/aliases"):
	ALIASES.parse(path)


class GlobsFile(object):
	"""
	/usr/share/mime/globs2
	"""
	def __init__(self):
		self._extensions = {}
		self._extensionsFor = {}
		self._literals = {}
		self._matches = []

	def extensionsFor(self, mime):
		return self._extensionsFor[str(mime)]

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
						# Add the mime type to the extensionsFor dict
						# It has to keep the order intact, as we want eg. file save dialogs to
						# be able to rely on getting the "best extension" (always the first one)
						# ref: https://bugs.freedesktop.org/show_bug.cgi?id=47950
						if mime not in self._extensionsFor:
							self._extensionsFor[str(mime)] = []
						self._extensionsFor[str(mime)].append(extension)

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

		weight, mime, glob = max(matches, key=lambda weight_mime_glob: (weight_mime_glob[0], len(weight_mime_glob[2])))
		return mime

GLOBS = GlobsFile()
for path in xdg.getFiles("mime/globs2"):
	GLOBS.parse(path)


class IconsFile(BaseFile):
	"""
	/usr/share/mime/icons
	/usr/share/mime/generic-icons
	"""
	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.endswith("\n"):
					line = line[:-1]

				mime, icon = line.split(":")
				self._keys[mime] = icon

ICONS = IconsFile()
for path in xdg.getFiles("mime/generic-icons"):
	ICONS.parse(path)

class MagicRule(object):
	def __init__(self, file):
		"""
		Parse a section's line
		[ indent ] ">" start-offset "=" value [ "&" mask ] [ "~" word-size ] [ "+" range-length ] "\n"
		"""
		self.next = None
		self.prev = None

		self.nest = 0
		c = file.read(1)
		if not c:
			raise ValueError("Early EOF")

		if c != b">":
			file.seek(-1, os.SEEK_CUR)
			self.nest = _readNumber(file)
			c = file.read(1)
			if c != b">":
				raise ValueError("Missing '>' in section body (got %r)" % (c))

		self.startOffset = _readNumber(file)

		c = file.read(1)

		if c != b"=":
			raise ValueError("Missing '=' in %r section body (got %r)" % (file.name, c))

		self.valueLength, = struct.unpack(">H", file.read(2))
		self.value = file.read(self.valueLength)

		c = file.read(1)

		if c == b"&":
			self.mask = file.read(self.valueLength)
			c = file.read(1)
		else:
			self.mask = None

		if c == b"~":
			self.wordSize = _readNumber(file)
			c = file.read(1)
		else:
			self.wordSize = 1

		if c == b"+":
			self.rangeLength = _readNumber(file)
			c = file.read(1)
		else:
			self.rangeLength = 1

		if c != b"\n":
			raise ValueError("Malformed MIME magic line: %r" % (c))

	def length(self):
		return self.startOffset + self.valueLength + self.rangeLength

	def appendRule(self, rule):
		if self.nest < rule.nest:
			self.next = rule
			rule.prev = self

		elif self.prev:
			self.prev.appendRule(rule)

	def match(self, buffer):
		if self.match0(buffer):
			if self.next:
				return self.next.match(buffer)
			return True

	def match0(self, buffer):
		l = len(buffer)
		for o in range(self.rangeLength):
			s = self.startOffset + o
			e = self.valueLength + s
			if l < e:
				return False
			if self.mask:
				test = ""
				for i in range(self.valueLength):
					c = buffer[s+i] & self.mask[i]
					test += chr(c)
			else:
				test = buffer[s:e]

			if test == self.value:
				return True

	def __repr__(self):
		return "MagicRule(%r)" % (self.__str__())

	def __str__(self):
		return "%r>%r=[%r]%s&%s~%r+%r" % (self.nest, self.startOffset, self.valueLength, repr(self.value)[2:-1] or "", repr(self.mask)[2:-1], self.wordSize, self.rangeLength)


class MagicFile(object):
	"""
	/usr/share/mime/magic
	"""

	class MagicType(object):
		def __init__(self, mime):
			self.mime = mime
			self.topRules = []
			self.lastRule = None

		def getLine(self, file):
			rule = MagicRule(file)

			if rule.nest and self.lastRule:
				self.lastRule.appendRule(rule)
			else:
				self.topRules.append(rule)
				self.lastRule = rule

			return rule

		def match(self, buffer):
			for rule in self.topRules:
				if rule.match(buffer):
					return self.mime

		def __repr__(self):
			return "MagicType(%r)" % (self.mime)

	def __init__(self):
		self.types = {} # Indexed by priority, each entry is a list of type rules
		self.maxLength = 0

	def __repr__(self):
		return "MagicDB(<%i items>)" % (len(self.types))

	def parse(self, fname):
		with open(fname, "rb") as file:
			if file.read(12) != b"MIME-Magic\0\n":
				raise ValueError("Bad header for file %r" % (path))

			while True:
				# Parse the section head
				# Example: "[50:text/x-diff]\n"
				sectionHead = file.readline()
				if not sectionHead:
					break

				if sectionHead[0] != ord(b"[") or sectionHead[-2:] != b"]\n":
					raise ValueError("Malformed section heading: %r" % (sectionHead))

				pri, tname = sectionHead[1:-2].split(b":")
				pri = int(pri)
				mime = str(tname, "utf-8")

				if pri not in self.types:
					self.types[pri] = []
				ents = self.types[pri]

				magictype = self.MagicType(mime)

				c = file.read(1)
				file.seek(-1, os.SEEK_CUR)
				while c and c != b"[":
					rule = magictype.getLine(file)
					if rule and rule.length() > self.maxLength:
						self.maxLength = rule.length()

					c = file.read(1)
					file.seek(-1, os.SEEK_CUR)

				ents.append(magictype)

				if not c:
					break

	def matchData(self, data, max=100, min=0):
		for priority in sorted(self.types.keys(), key=lambda k: -k):
			if priority > max:
				continue
			if priority < min:
				break

			for type in self.types[priority]:
				mime = type.match(data)
				if mime:
					return mime

	def match(self, path, max=100, min=0):
		with open(path, "rb") as f:
			return self.matchData(f.read(self.maxLength), max, min)


MAGIC = MagicFile()
for path in xdg.getFiles("mime/magic"):
	MAGIC.parse(path)


class SubclassesFile(BaseFile):
	"""
	/usr/share/mime/subclasses
	"""
	def parse(self, path):
		with open(path, "r") as file:
			for line in file:
				if line.endswith("\n"):
					line = line[:-1]

				mime, subclass = line.split(" ")
				if mime not in self._keys:
					self._keys[mime] = []
				self._keys[mime].append(subclass)

SUBCLASSES = SubclassesFile()
for path in xdg.getFiles("mime/subclasses"):
	SUBCLASSES.parse(path)


class BaseMimeType(object):
	DEFAULT_TEXT = "text/plain"
	DEFAULT_BINARY = "application/octet-stream"
	SCHEME_FORMAT = "x-scheme-handler/%s"
	ZERO_SIZE = "application/x-zerosize"

	INODE_MOUNTPOINT = "inode/mount-point"
	INODE_BLOCKDEVICE = "inode/blockdevice"
	INODE_CHARDEVICE = "inode/chardevice"
	INODE_DIRECTORY = "inode/directory"
	INODE_FIFO = "inode/fifo"
	INODE_SYMLINK = "inode/symlink"
	INODE_SOCKET = "inode/socket"

	def __init__(self, mime):
		self._name = str(mime)
		self._aliases = []
		self._localized = {
			"acronym": {},
			"comment": {},
			"expanded-acronym": {},
		}

	def __eq__(self, other):
		if isinstance(other, BaseMimeType):
			return self.name() == other.name()
		return self.name() == other

	def __str__(self):
		return self.name()

	def __repr__(self):
		return "<MimeType: %s>" % (self.name())

	@classmethod
	def fromInode(cls, name):
		import stat
		try:
			mode = os.stat(name).st_mode
		except IOError:
			return

		# Test for mount point before testing for inode/directory
		if os.path.ismount(name):
			return cls(cls.INODE_MOUNTPOINT)

		if stat.S_ISBLK(mode):
			return cls(cls.INODE_BLOCKDEVICE)

		if stat.S_ISCHR(mode):
			return cls(cls.INODE_CHARDEVICE)

		if stat.S_ISDIR(mode):
			return cls(cls.INODE_DIRECTORY)

		if stat.S_ISFIFO(mode):
			return cls(cls.INODE_FIFO)

		if stat.S_ISLNK(mode):
			return cls(cls.INODE_SYMLINK)

		if stat.S_ISSOCK(mode):
			return cls(cls.INODE_SOCKET)

	@classmethod
	def fromScheme(cls, uri):
		try:
			from urllib.parse import urlparse
		except ImportError:
			from urlparse import urlparse

		scheme = urlparse(uri).scheme
		if not scheme:
			raise ValueError("%r does not have a scheme or is not a valid URI" % (scheme))

		return cls(cls.SCHEME_FORMAT % (scheme))

	def genericIcon(self):
		return self.genericMime().name().replace("/", "-")

	def genericMime(self):
		return self.__class__("%s/x-generic" % (self.type()))

	def icon(self):
		return self.name().replace("/", "-")

	def isDefault(self):
		name = self.name()
		return name == DEFAULT_BINARY or name == DEFAULT_TEXT

	def isInstance(self, other):
		return self == other or other in self.subClassOf()

	def name(self):
		return self._name

	def subtype(self):
		return self.name().split("/")[1]

	def type(self):
		return self.name().split("/")[0]


class MimeType(BaseMimeType):
	"""
	XDG-based MimeType
	"""

	@classmethod
	def fromName(cls, name):
		mime = GLOBS.match(name)
		if mime:
			return cls(mime)

	@classmethod
	def fromContent(cls, name):
		inode = cls.fromInode(name)
		if inode and inode != cls.INODE_SYMLINK:
			return cls(inode)

		try:
			size = os.stat(name).st_size
		except IOError:
			return

		if size == 0:
			return cls(cls.ZERO_SIZE)

		match = MAGIC.match(name)
		if match:
			return cls(match)

		if not _isBinaryString(open(name, "rb").read(1024)):
			return cls(cls.DEFAULT_TEXT)

		return cls(cls.DEFAULT_BINARY)

	def _localizedTag(self, tag, lang):
		"""
		Gets the value of a tag that can be localized through xml:lang
		"""
		cache = self._localized[tag]
		if lang not in cache:
			files = xdg.getFiles(os.path.join("mime", self.type(), "%s.xml" % (self.subtype())))
			if not files:
				return

			for file in files:
				doc = minidom.parse(file)
				for element in doc.documentElement.getElementsByTagNameNS(FREEDESKTOP_NS, tag):
					nslang = element.getAttributeNS(XML_NAMESPACE, "lang") or "en"
					if nslang == lang:
						cache[lang] = "".join(n.nodeValue for n in element.childNodes).strip()
						break

		return cache.get(lang)

	def acronym(self, lang="en"):
		return self._localizedTag("acronym", lang)

	def aliases(self):
		if not self._aliases:
			files = xdg.getFiles(os.path.join("mime", self.type(), "%s.xml" % (self.subtype())))
			if not files:
				return []

			for file in files:
				doc = minidom.parse(file)
				for node in doc.documentElement.getElementsByTagName("alias"):
					alias = node.getAttribute("type")
					if alias not in self._aliases:
						self._aliases.append(MimeType(alias))

		return self._aliases

	def aliasOf(self):
		mime = ALIASES.get(self.name())
		if mime:
			return MimeType(mime)

	def comment(self, lang="en"):
		return self._localizedTag("comment", lang)

	def expandedAcronym(self, lang="en"):
		return self._localizedTag("expanded-acronym", lang)

	def extensions(self):
		return GLOBS.extensionsFor(self)

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

	def bestApplications(self):
		from . import actions
		return actions.bestApplications(self.name())

	def bestAvailableApplication(self):
		from . import actions
		return actions.bestAvailableApplication(self.name())

	def bestAvailableApplications(self):
		from . import actions
		return actions.bestAvailableApplications(self.name())

	def defaultApplication(self):
		from . import actions
		return actions.defaultApplication(self.name())
