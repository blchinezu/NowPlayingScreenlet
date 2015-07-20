#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Amarok_2 Api

import os
import urllib
import dbus
import string
import gobject
from GenericPlayer import GenericAPI

class Amarok_2API(GenericAPI):
	__name__ = 'Amarok 2 API'
	__version__ = '0.3.3.9'
	__author__ = 'Alexibaba, modified by BruceLee'
	__desc__ = 'API to the Amarok2 Music Player'

	ns = "org.kde.amarok"
	iroot = "/Player"
	iface = "org.freedesktop.MediaPlayer"

	controlAPI = None
	songAPI = None

	__timeout = None
	__interval = 2

	callback_fn = None
	__curplaying = None
	__isplaying = None

	playing = False	

	# Extended Functions from the GenericAPI

	def __init__(self, session_bus):
		GenericAPI.__init__(self, session_bus)

	def is_active(self, dbus_iface, screenlet_settings):
		try:
			if self.ns in dbus_iface.ListNames(): return True
			else: return False
		except:
			return False

	def connect(self, screenlet_settings):
		proxy_obj = self.session_bus.get_object(self.ns, self.iroot)
		self.controlAPI = dbus.Interface(proxy_obj, self.iface)
		self.songAPI = self.session_bus.get_object(self.ns, self.iroot)


	def get_title(self):
		return self.songAPI.GetMetadata().get("title")
	
	def get_album(self):
		return self.songAPI.GetMetadata().get("album")

	def get_artist(self):
		return self.songAPI.GetMetadata().get("artist")
		
	def get_cover_path(self):
		coverart = self.songAPI.GetMetadata().get("arturl")[7:]
		return urllib.unquote_plus(coverart.encode("utf-8"))

	def is_playing(self):
		if self.songAPI.GetStatus()[0] == 0 or self.songAPI.GetStatus()[0] == 1: 
			return True
		else: 
			return False

	def is_paused(self):
		if self.songAPI.GetStatus()[0] == 1: 
			return True
		else: 
			return False

	def play_pause(self):
		self.controlAPI.Pause()
		if self.is_playing():
			self.controlAPI.Play()

	def next(self):
		self.controlAPI.Next()

	def previous(self):
		self.controlAPI.Prev()


	def current_playing(self):
		return self.get_artist()+self.get_title()

	def register_change_callback(self, fn):
		self.callback_fn = fn
		# Could not find a callback signal for Listen, so just calling after some time interval
		if self.__timeout:
			gobject.source_remove(self.__timeout)
		self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)
		#self.playerAPI.connect_to_signal("playingUriChanged", self.info_changed)

	def info_changed(self, signal=None):
		# Only call the callback function if Data has changed
		if self.__timeout:
			gobject.source_remove(self.__timeout)
		try:
			if self.__curplaying != self.playerAPI.current_playing():
				self.__curplaying = self.playerAPI.current_playing()
				self.callback_fn()
			if self.__nowisplaying != self.playerAPI.is_playing():
				self.__nowisplaying = self.playerAPI.is_playing()
				self.redraw_background_items()
			self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)
		except:
			# The player exited ? call callback function
			self.callback_fn()
		self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)

