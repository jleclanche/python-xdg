"""
Implementation of the XDG MIME actions draft
http://www.freedesktop.org/wiki/Specifications/mime-actions-spec

The implementation is in two parts:
 - mimeinfo.cache, which is autogenerated by update-desktop-database
   and contains a single-file cache of all desktop files
 - mimeapps.list, which contains user associations, exclusions and
   default apps

-> A user association is an association between an app and, for
   example, a MIME type, which the user has added themselves.
-> A user exclusion is an application association which has been
   rejected by the user (marked as invalid; eg "Never present this
   option again)
-> The default application is an application that has been set as
   the default to be used when executing a specific action.
"""

from . import xdg
from .desktopfile import getDesktopFilePath
from .inifile import IniFile, NoSectionError
from .mime import unalias

ADDED_ASSOCIATIONS = "Added Associations"
REMOVED_ASSOCIATIONS = "Removed Associations"
DEFAULT_APPLICATIONS = "Default Applications"

class MimeActionsListFile(IniFile):
	"""
	~/.local/share/applications/mimeapps.list
	"""

	def __init__(self):
		super(MimeActionsListFile, self).__init__()
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

MIME_ACTIONS_LIST = MimeActionsListFile()
for f in xdg.getFiles("applications/mimeapps.list"):
	MIME_ACTIONS_LIST.parse(f)


class MimeActionsCacheFile(IniFile):
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

	def applicationsFor(self, mime, exclude=[]):
		if mime in self.sections:
			return [app for app in self.sections[mime] if app not in exclude]
		return []

MIME_ACTIONS_CACHE = MimeActionsCacheFile()
for f in xdg.getFiles("applications/mimeinfo.cache"):
	MIME_ACTIONS_CACHE.parse(f)


def bestApplications(mime):
	# Unalias the mime type if necessary
	mime = unalias(mime)

	# First, check if the default app is defined
	ret = MIME_ACTIONS_LIST.defaultApplication(mime.name())
	if ret and getDesktopFilePath(ret):
		yield ret

	# Then, check the added associations (they have priority)
	associations = MIME_ACTIONS_LIST.addedAssociations(mime.name())
	for assoc in associations:
		if getDesktopFilePath(assoc):
			yield assoc

	# Finally, check the cached associations
	associations = MIME_ACTIONS_CACHE.applicationsFor(mime.name(), exclude=MIME_ACTIONS_LIST.removedAssociations(mime.name()))
	for assoc in associations:
		if getDesktopFilePath(assoc):
			yield assoc

	# If we still don't have anything, try the mime's parents one by one
	for mime in mime.subClassOf():
		ret = bestApplication(mime.name())
		if ret:
			yield ret

	# No application found
