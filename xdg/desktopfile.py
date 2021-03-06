"""
Implementation of the XDG Desktop Entry spec version 1.1.
http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-1.1.html
"""
import os
import shlex
from copy import copy
try:
	from urllib.parse import quote
except ImportError:
	# Python 2 support
	from urllib import quote
from .inifile import IniFile


DESKTOP_ENTRY = "Desktop Entry"
DESKTOP_ACTION = "Desktop Action %s"


def _urlify(arg):
	if ":" in arg:
		return arg
	return "file://" + quote(os.path.realpath(arg))


class InvalidDesktopFile(Exception):
	pass


class DesktopFile(IniFile):
	def __init__(self):
		self.section = DESKTOP_ENTRY
		super(DesktopFile, self).__init__()

	@classmethod
	def lookup(cls, name):
		instance = cls()
		path = getDesktopFilePath(name)
		if path:
			instance.read(path)
			return instance

	def read(self, *args, **kwargs):
		ret = super(DesktopFile, self).read(*args, **kwargs)
		if not self.has_section(DESKTOP_ENTRY):
			raise InvalidDesktopFile("The desktop file is missing a %r section" % (DESKTOP_ENTRY))
		return ret

	def translatedValue(self, key, lang=None):
		key = key.lower()
		if lang:
			key = "%s[%s]" % (key, lang)
		return self.getdefault(self.section, key)

	def value(self, key):
		key = key.lower()
		return self.getdefault(self.section, key)

	def actions(self):
		return self.getlist(self.section, "Actions")

	def action(self, action):
		section = DESKTOP_ACTION % (action)
		ret = copy(self)
		ret.section = section
		return ret

	def comment(self):
		return self.translatedValue("Comment")

	def exec_(self, args=[]):
		import subprocess
		subprocess.Popen(self.formattedExec(args))

	def executable(self):
		return self.value("Exec")

	def formattedExec(self, args):
		_exec = shlex.split(self.executable())
		formatted = []
		for i, arg in enumerate(_exec):
			if i == 0:
				# skip the executable name
				formatted.append(arg)
				continue

			if "%f" in arg:
				formatted.append(arg.replace("%f", args and os.path.realpath(args[0]) or ""))

			elif "%F" in arg:
				formatted += [arg.replace("%F", args and os.path.realpath(args[0]) or "")] + [os.path.realpath(arg) for arg in args[1:]]

			elif "%u" in arg:
				formatted.append(args and _urlify(args[0]) or "")

			elif "%U" in arg:
				formatted += [arg.replace("%U", args and _urlify(args[0]) or "")] + [_urlify(x) for x in args[1:]]

			elif "%%" in arg:
				formatted.append(arg.replace("%%", "%"))

			else:
				formatted.append(arg)

		return [x for x in formatted if x]

	def name(self):
		return self.translatedValue("Name")


def getDesktopFilePath(name):
	"""
	Returns the first existing desktop file named \a name.
	"""
	from .xdg import getFiles

	files = getFiles(os.path.join("applications", name))
	if files:
		return files[0]

	# http://standards.freedesktop.org/menu-spec/menu-spec-1.0.html#merge-algorithm
	# Desktop files have their directories stripped in the process and replaced by
	# a dash. We still prioritize the direct paths, but now check for the dirs.
	files = getFiles(os.path.join("applications", name.replace("-", "/")))
	if files:
		return files[0]
