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


ADDED_ASSOCIATIONS = "Added Associations"
REMOVED_ASSOCIATIONS = "Removed Associations"
DEFAULT_APPLICATIONS = "Default Applications"

MIME_CACHE = "MIME Cache"
MIME_VIEW_CACHE = "MIME View Cache"
MIME_EDIT_CACHE = "MIME Edit Cache"
CATEGORY_CACHE = "Category Cache"

# MIME actions
ACTION_OPEN = 0x01
ACTION_VIEW = 0x02
ACTION_EDIT = 0x04
ACTION_ALL = ACTION_OPEN | ACTION_VIEW | ACTION_EDIT


class ActionsListFile(IniFile):
	"""
	applications/mimeapps.list
	NOTE: Theoretically, this file should only be in $XDG_DATA_HOME
	"""

	def addedAssociations(self, mime):
		return self.getlist(ADDED_ASSOCIATIONS, mime, [])

	def removedAssociations(self, mime):
		return self.getlist(REMOVED_ASSOCIATIONS, mime, [])

	def defaultApplication(self, mime):
		return self.getdefault(DEFAULT_APPLICATIONS, mime, None)

ACTIONS_LIST = ActionsListFile()
ACTIONS_LIST.read_merged(xdg.getFiles("applications/mimeapps.list")[::-1])


class ActionsCacheFile(IniFile):
	"""
	applications/mimeinfo.cache
	Generated by desktop-file-utils
	"""

	def _get_apps(self, section, option, exclude):
		if self.has_option(section, option):
			return [app for app in self.getlist(section, option) if app not in exclude]
		return []

	def applicationsForMimeType(self, mime, exclude=[], action=ACTION_ALL):
		ret = []
		action_keys = {
			ACTION_OPEN: MIME_CACHE,
			ACTION_VIEW: MIME_VIEW_CACHE,
			ACTION_EDIT: MIME_EDIT_CACHE,
		}
		for key in (ACTION_EDIT, ACTION_VIEW, ACTION_OPEN):
			if action & key:
				ret += [app for app in self._get_apps(action_keys[key], mime, exclude) if app not in ret]
		return ret

	def applicationsForCategory(self, category, exclude=[]):
		return self._get_apps(CATEGORY_CACHE, category, exclude)

ACTIONS_CACHE = ActionsCacheFile()
ACTIONS_CACHE.read_merged(xdg.getFiles("applications/mimeinfo.cache")[::-1])


def associationsForMimeType(mime):
	# First, check if the default app is defined
	ret = ACTIONS_LIST.defaultApplication(mime.name())
	if ret and getDesktopFilePath(ret):
		yield ret

	# Then, check the added associations (they have priority)
	associations = ACTIONS_LIST.addedAssociations(mime.name())
	for assoc in associations:
		yield assoc

	# Finally, check the cached associations
	associations = ACTIONS_CACHE.applicationsForMimeType(mime.name(), exclude=ACTIONS_LIST.removedAssociations(mime.name()))
	for assoc in associations:
		yield assoc

	# If we still don't have anything, try the mime's parents one by one
	for mime in mime.subClassOf():
		for assoc in associationsForMimeType(mime):
			yield assoc

	# No application found
