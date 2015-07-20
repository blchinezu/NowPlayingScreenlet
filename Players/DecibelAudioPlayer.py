#!/usr/bin/env python

# Decibel-Audio-Player API (Extended MprisAPI)

import os
import dbus
import string
import gobject
from Mpris import MprisAPI

class DecibelAudioPlayerAPI(MprisAPI):
	__name__ = 'Decibel-Audio-Player API'
	__version__ = '0.3.4.1'
	__author__ = 'BruceLee'
	__desc__ = 'API for Decibel-Audio-Player'

	this_mpris_ns    = 'org.mpris.dap'
	this_mpris_iroot = '/Player'
	this_mpris_iface = 'org.freedesktop.MediaPlayer'
			
	def is_active(self, dbus_iface, screenlet_settings):
		if self.this_mpris_ns in dbus_iface.ListNames(): return True
		return False

