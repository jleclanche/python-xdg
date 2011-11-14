# -*- coding: utf-8 -*-
"""
Implementation of the XDG MIME actions draft
http://www.freedesktop.org/wiki/Specifications/mime-actions-spec
"""

from ConfigParser import RawConfigParser
import xdg

class ActionsFile(object):
	"""
	~/.local/share/applications/mimeapps.list
	"""
	def __init__(self):
		self._keys = {
			"Added Associations": {},
			"Removed Associations": {},
			#"Default Applications": {},
		}

	def _parseAssociations(self, key, cfg):
		from .mime import MimeType
		d = self._keys[key]

		for mime, apps in cfg.items(key):
			# First, check for aliases and unalias anything we find
			# see http://lists.freedesktop.org/archives/xdg/2010-March/011336.html
			alias = MimeType(mime).aliasOf()
			if alias:
				mime = alias

			if mime not in d:
				d[mime] = []
			assert apps.endswith(";")
			apps = apps.split(";")
			for app in apps:
				if not app:
					# We either got two semicolons in a row
					# or we got the last semicolon
					continue
				d[mime].insert(0, app)

	def __repr__(self):
		return self._keys.__repr__()

	def parse(self, path):
		with open(path, "r") as file:
			cfg = RawConfigParser()
			cfg.readfp(file)

			self._parseAssociations("Added Associations", cfg)
			self._parseAssociations("Removed Associations", cfg)

	def get(self, name):
		return self._keys.get(name)

ACTIONS = ActionsFile()
for f in xdg.getFiles("applications/mimeapps.list"):
	ACTIONS.parse(f)
