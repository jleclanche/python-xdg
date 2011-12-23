# -*- coding: utf-8 -*-
"""
Shared definitions and helper functions for xdg
"""

import os
from ConfigParser import RawConfigParser

FREEDESKTOP_NS = "http://www.freedesktop.org/standards/shared-mime-info"

HOME = os.path.expanduser("~")
XDG_DATA_HOME = os.environ.get("XDG_DATA_HOME", os.path.join(HOME, ".local", "share"))
XDG_DATA_DIRS = set([XDG_DATA_HOME] + os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":"))
# XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.join(HOME, ".config"))
# XDG_CONFIG_DIRS = set([XDG_CONFIG_HOME] + os.environ.get("XDG_CONFIG_DIRS", "/etc/xdg").split(":"))
# XDG_CACHE_HOME  = os.environ.get("XDG_CACHE_HOME", os.path.join(HOME, ".cache"))


def getFiles(name):
	ret = []
	for dir in XDG_DATA_DIRS:
		path = os.path.join(dir, name)
		if os.path.exists(path):
			ret.append(path)
	return ret

def getMimeFiles(name):
	paths = []
	for dir in XDG_DATA_DIRS:
		type, subtype = name.split("/")
		path = os.path.join(dir, "mime", type, subtype + ".xml")
		if os.path.exists(path):
			paths.append(path)

	return paths

def getDesktopFilePath(name):
	ret = None
	for path in getFiles(os.path.join("applications", name)):
		if os.path.exists(path):
			ret = path

	return ret

def updateDesktopDatabase():
	from subprocess import Popen
	Popen(["update-desktop-database", base])

def updateMimeDatabase():
	from subprocess import Popen
	Popen(["update-mime-database", base])

class IniFile(object):
	def __init__(self):
		self.keys = {}

	def __repr__(self):
		return self.keys.__repr__()

	def get(self, key, default=None):
		return self.keys.get(key, default)

	def parse(self, path):
		with open(path, "r") as file:
			self.cfg = RawConfigParser()
			self.cfg.readfp(file)
			self.parseKeys()