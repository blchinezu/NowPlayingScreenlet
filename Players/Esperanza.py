#!/usr/bin/env python

# Esperanza API (Extended XMMS2API)

import os
import dbus
import string
import gobject
from XMMS2 import XMMS2API

class EsperanzaAPI(XMMS2API):
	__name__ = 'Esperanza API'
	__version__ = '0.3.4.1'
	__author__ = 'BruceLee'
	__desc__ = 'API for Esperanza Audio Player'

	def is_active(self, dbus_iface, screenlet_settings):
		if self.bin_runs("xmms2d") and self.bin_runs("esperanza"): return True
		return False
		
