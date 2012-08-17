"""
Implementation of the XDG Desktop Entry spec version 1.1.
http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-1.1.html
"""
import os
from xdg.inifile import IniFile


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
