"""
Desktop Application Autostart Specification
http://standards.freedesktop.org/autostart-spec/autostart-spec-latest.html
"""

import os
from .basedir import XDG_CONFIG_HOME, XDG_CONFIG_DIRS

AUTOSTART_DIRS = [os.path.join(path, "autostart") for path in XDG_CONFIG_DIRS]

def localAutostartPrograms():
	return []

def globalAutostartPrograms():
	return []

def allAutostartPrograms():
	return localAutostartPrograms() + globalAutostartPrograms()

def autorunForMedium(path):
	for f in [".autorun", "autorun", "autorun.sh"]:
		path = os.path.join(path, f)
		if os.path.exists(path):
			return path

# TODO autoopen files
