#!/usr/bin/env python

# Abraca API (Extended XMMS2API)

import os
import dbus
import string
import gobject
from XMMS2 import XMMS2API

class AbracaAPI(XMMS2API):
	__name__ = 'Abraca API'
	__version__ = '0.3.4.1'
	__author__ = 'BruceLee'
	__desc__ = 'API for Abraca XMMS2 GUI'

	def is_active(self, dbus_iface, screenlet_settings):
		if self.bin_runs("xmms2d") and self.bin_runs("abraca"): return True
		return False
		
