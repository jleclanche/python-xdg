"""
Shared definitions and helper functions for xdg
"""

import os
from .basedir import *


def getFiles(name):
	ret = []
	for dir in XDG_DATA_DIRS:
		path = os.path.join(dir, name)
		if os.path.exists(path):
			ret.append(path)
	return ret

def updateDesktopDatabase(base):
	from subprocess import Popen
	Popen(["update-desktop-database", base])

def updateMimeDatabase(base):
	from subprocess import Popen
	Popen(["update-mime-database", base])
