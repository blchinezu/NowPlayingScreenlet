#!/usr/bin/env python

# Exaile API (Extended MprisAPI)

import os
import sys
import dbus
import string
import gobject
from Mpris import MprisAPI

class ExaileAPI(MprisAPI):
	__name__ = 'Exaile API'
	__version__ = '0.3.4.1'
	__author__ = 'BruceLee'
	__desc__ = 'API for Exaile Audio Player'

	playerAPI = playerAPI2 = None

	this_mpris_ns    = 'org.mpris.exaile'
	this_mpris_iroot = '/Player'
	this_mpris_iface = 'org.freedesktop.MediaPlayer'

	ns2    = 'org.exaile.Exaile'
	iroot2 = '/org/exaile/Exaile'
	iface2 = 'org.exaile.Exaile'
	
	def is_active(self, dbus_iface, screenlet_settings):
		if self.this_mpris_ns in dbus_iface.ListNames() and self.iface2 in dbus_iface.ListNames(): return True
		return False

	def connect(self, screenlet_settings):
		proxy_obj = self.session_bus.get_object(self.this_mpris_ns, self.this_mpris_iroot)
		self.playerAPI = dbus.Interface(proxy_obj, self.this_mpris_iface)
		proxy_obj2 = self.session_bus.get_object(self.ns2, self.iroot2)
		self.playerAPI2 = dbus.Interface(proxy_obj, self.iface2)
		
	# Rating
	def get_rating(self):
		try:
			ret = float(self.playerAPI2.GetRating())/20
		except:
			if os.path.exists('/usr/bin/qdbus'):
				try:
					ret = float(os.popen('qdbus '+self.ns2+' '+self.iroot2+' '+self.iface2+'.GetRating').read())/20
				except:
					ret = 'None'
			else:
				ret = 'None'
		self.rating = ret
		return ret
		
	def set_rating(self, value):
		try:
			self.playerAPI2.SetRating(int(value*20))
		except:
			if os.path.exists('/usr/bin/qdbus'):
				try:
					os.system('qdbus '+self.ns2+' '+self.iroot2+' '+self.iface2+'.SetRating '+str(int(value*20))+' &')
				except:
					return False
			else:
				return False
		self.rating = value
		return True

