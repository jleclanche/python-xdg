"""
Implementation of the XDG Desktop Entry spec version 1.1.
http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-1.1.html
"""
import os
from xdg.inifile import IniFile


def urlify(arg):
	# stub
	return arg


class DesktopFile(IniFile):
	def parseKeys(self):
		d = self.sections["Desktop Entry"] = {}
		for k, v in self.cfg.items("Desktop Entry"):
			d[k] = v

	def translatedValue(self, key, lang=None):
		key = key.lower()
		if lang:
			key = "%s[%s]" % (key, lang)
		return self.sections["Desktop Entry"].get(key)

	def value(self, key):
		key = key.lower()
		return self.sections["Desktop Entry"].get(key)

	def comment(self):
		return self.translatedValue("Comment")

	def executable(self):
		return self.value("Exec")

	def formattedExec(self, *args):
		_exec = self.executable().split()

		for i, arg in enumerate(_exec):
			arg = arg.replace("%f", args[0])
			arg = arg.replace("%F", " ".join(args))
			arg = arg.replace("%f", urlify(args[0]))
			arg = arg.replace("%U", " ".join(urlify(x) for x in args))
			_exec[i] = arg

		return _exec

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
