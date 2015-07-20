#!/usr/bin/env python

# gXMMS2 API (Extended XMMS2API)

import os
import dbus
import string
import gobject
from XMMS2 import XMMS2API

class gXMMS2API(XMMS2API):
	__name__ = 'gXMMS2 API'
	__version__ = '0.3.4.1'
	__author__ = 'BruceLee'
	__desc__ = 'API for gXMMS2 Audio Player'

	def is_active(self, dbus_iface, screenlet_settings):
		if self.bin_runs("xmms2d") and self.bin_runs("gxmms2"): return True
		return False
		
