"""
Implementation of the XDG MIME actions draft
http://www.freedesktop.org/wiki/Specifications/mime-actions-spec
"""

from . import xdg
from .desktopfile import getDesktopFilePath
from .inifile import IniFile, NoSectionError
from .mime import unalias

ADDED_ASSOCIATIONS = "Added Associations"
REMOVED_ASSOCIATIONS = "Removed Associations"
DEFAULT_APPLICATIONS = "Default Applications"

class ActionsFile(IniFile):
	"""
	~/.local/share/applications/mimeapps.list
	"""

	def __init__(self):
		super(ActionsFile, self).__init__()
		self.sections = {
			ADDED_ASSOCIATIONS: {},
			REMOVED_ASSOCIATIONS: {},
			DEFAULT_APPLICATIONS: {},
		}

	def _parseAssociations(self, key):
		from .mime import MimeType
		d = self.sections[key]
		try:
			items = self.cfg.items(key)
		except NoSectionError:
			items = []

		for mime, apps in items:
			# Unalias every key
			# see http://lists.freedesktop.org/archives/xdg/2010-March/011336.html
			mime = unalias(mime).name()

			if mime not in d:
				d[mime] = []
			assert apps.endswith(";"), apps
			apps = apps.split(";")
			for app in apps:
				if not app:
					# We either got two semicolons in a row
					# or we got the last semicolon
					continue
				d[mime].insert(0, app)

	def parseKeys(self):
		self._parseAssociations(ADDED_ASSOCIATIONS)
		self._parseAssociations(REMOVED_ASSOCIATIONS)

		# Default apps are not lists
		for mime, app in self.cfg.items(DEFAULT_APPLICATIONS):
			# Check if the desktop file exists
			if getDesktopFilePath(app):
				self.sections[DEFAULT_APPLICATIONS][mime] = app

	def addedAssociations(self, mime):
		return self.get(ADDED_ASSOCIATIONS, mime, [])

	def removedAssociations(self, mime):
		return self.get(REMOVED_ASSOCIATIONS, mime, [])

	def defaultApplication(self, mime):
		return self.get(DEFAULT_APPLICATIONS, mime)

ACTIONS = ActionsFile()
for f in xdg.getFiles("applications/mimeapps.list"):
	ACTIONS.parse(f)


class CacheFile(IniFile):
	"""
	applications/mimeinfo.cache
	Not part of the spec, but generated by desktop-file-utils
	"""

	def parseKeys(self):
		for mime, apps in self.cfg.items("MIME Cache"):
			# Unalias every key
			# see http://lists.freedesktop.org/archives/xdg/2010-March/011336.html
			mime = unalias(mime).name()

			if mime not in self.sections:
				self.sections[mime] = []

			assert apps.endswith(";"), apps
			apps = apps.split(";")
			for app in apps:
				if not app:
					# We either got two semicolons in a row
					# or we got the last semicolon
					continue
				self.sections[mime].insert(0, app)

	def associationsFor(self, mime, exclude=[]):
		if mime in self.sections:
			return [app for app in self.sections[mime] if app not in exclude]
		return []

CACHE = CacheFile()
for f in xdg.getFiles("applications/mimeinfo.cache"):
	CACHE.parse(f)

def defaultApplication(mime):
	return ACTIONS.defaultApplication(mime)

def bestApplication(mime):
	"""
	Convenience function that returns the first best-fitting application
	to open a \a mime

	NOTE: This function does NOT check for the presence of .desktop files
	on the file system. This should be done separately, or you can use
	the convenience function bestAvailableApplication()
	"""
	return next(bestApplications(mime), None)

def bestApplications(mime):
	"""
	Returns a generator of the applications able to open \a mime, from
	most to least fitting choice.
	 - MIME types are always unaliased first.
	 - The default application is next
	 - The user-added associations are next
	 - The cached associations are next
	 - If we still haven't found anything, the process is repeated for
	   each of the MIME type's parents (recursively)

	NOTE: This function does NOT check for the presence of .desktop files
	on the file system. This should be done separately, or you can use
	the convenience function bestAvailableApplications()
	"""
	# Unalias the mime type if necessary
	mime = unalias(mime)

	# First, check if the default app is defined
	ret = ACTIONS.defaultApplication(mime.name())
	if ret and getDesktopFilePath(ret):
		yield ret

	# Then, check the added associations (they have priority)
	associations = ACTIONS.addedAssociations(mime.name())
	for assoc in associations:
		if getDesktopFilePath(assoc):
			yield assoc

	# Finally, check the cached associations
	associations = CACHE.associationsFor(mime.name(), exclude=ACTIONS.removedAssociations(mime.name()))
	for assoc in associations:
		if getDesktopFilePath(assoc):
			yield assoc

	# If we still don't have anything, try the mime's parents one by one
	for mime in mime.subClassOf():
		ret = bestApplication(mime.name())
		if ret:
			yield ret

	# No application found

def bestAvailableApplications(mime):
	"""
	Same as bestApplications(), but checks if the .desktop files are
	available on the file system.
	"""
	for app in bestApplications(mime):
		desktop = getDesktopFilePath(app)
		if desktop:
			yield desktop

def bestAvailableApplication(mime):
	"""
	Same as bestApplication(), but checks if the .desktop files are
	available on the file system.
	"""
	return next(bestAvailableApplications(mime), None)

def associationsFor(mime):
	ret = []
	x = ACTIONS.defaultApplication(mime)
	if x:
		return ret.append(x)

	ret += ACTIONS.addedAssociations(mime)

	ret += CACHE.associationsFor(mime, exclude=ACTIONS.removedAssociations(mime))

	return ret
