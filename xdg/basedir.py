"""
XDG Base Directory Specification
http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html

This module provides the following variables:

HOME:
 A helper that always points to the user's home directory

XDG_DATA_HOME / XDG_CONFIG_HOME / XDG_CACHE_HOME:
 Provide their respective environment variables defaulting according to the spec

XDG_DATA_DIRS and XDG_CONFIG_DIRS:
 Provide a list of directories for their respective environment variable, defaulting according to the spec
 They always include, in the first index, XDG_DATA_HOME and XDG_CONFIG_HOME, respectively

XDG_RUNTIME_DIR:
 Provides its respective environment variable. Does not have a default, applications should find their own fallback.

"""

import os

__all__ = (
	"HOME",
	"XDG_DATA_HOME",
	"XDG_CONFIG_HOME",
	"XDG_DATA_DIRS",
	"XDG_CONFIG_DIRS",
	"XDG_CACHE_HOME",
	"XDG_RUNTIME_DIR",
)

# Always points to the user's home directory
HOME = os.path.expanduser("~")

# Single directory where user-specific data files should be written
XDG_DATA_HOME = os.environ.get("XDG_DATA_HOME", os.path.join(HOME, ".local", "share"))

# Single directory where user-specific configuration files should be written
XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.join(HOME, ".config"))

# List of directories where data files should be searched.
XDG_DATA_DIRS = set([XDG_DATA_HOME] + os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":"))

# List of directories where configuration files should be searched.
XDG_CONFIG_DIRS = set([XDG_CONFIG_HOME] + os.environ.get("XDG_CONFIG_DIRS", "/etc/xdg").split(":"))

# Single directory where user-specific non-essential (cached) data should be written
XDG_CACHE_HOME  = os.environ.get("XDG_CACHE_HOME", os.path.join(HOME, ".cache"))

# Single directory where user-specific runtime files and other file objects should be placed.
XDG_RUNTIME_DIR = os.environ.get("XDG_RUNTIME_DIR")
