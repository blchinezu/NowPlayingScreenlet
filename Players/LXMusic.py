#!/usr/bin/env python

# LXMusic API (Extended XMMS2API)

import os
import dbus
import string
import gobject
from XMMS2 import XMMS2API

class LXMusicAPI(XMMS2API):
	__name__ = 'LXMusic API'
	__version__ = '0.3.4.1'
	__author__ = 'BruceLee'
	__desc__ = 'API for LXMusic Audio Player'

	def is_active(self, dbus_iface, screenlet_settings):
		if self.bin_runs("xmms2d") and self.bin_runs("lxmusic"): return True
		return False
		
