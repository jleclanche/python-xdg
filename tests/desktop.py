#!/usr/bin/env python
"""
Desktop file tests for python-xdg

# desktop file tests
>>> from xdg.desktopfile import DesktopFile
>>> desktop = DesktopFile()
>>> desktop.parse("test.desktop")
>>> desktop.formattedExec(["/test"])
['env', 'VAR=/tmp/test folder/foo', '/test', '/test', 'file:///test', 'file:///test', '%', '--args=/test']
>>> desktop.formattedExec(["/test1", "/test2"])
['env', 'VAR=/tmp/test folder/foo', '/test1', '/test1', '/test2', 'file:///test1', 'file:///test1', 'file:///test2', '%', '--args=/test1', '/test2']
>>> desktop.formattedExec(["test_%F_foo"])
['env', 'VAR=/tmp/test folder/foo', 'test_%F_foo', 'test_%F_foo', 'file://test_%25F_foo', 'file://test_%25F_foo', '%', '--args=test_%F_foo']
"""


if __name__ == "__main__":
	import doctest
	doctest.testmod()
