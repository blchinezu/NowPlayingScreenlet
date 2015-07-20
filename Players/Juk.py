#!/usr/bin/env python
# -*- coding: utf-8 -*-

# JukApi

import os
import dbus
import string
import gobject
from GenericPlayer import GenericAPI

class JukAPI(GenericAPI):
	__name__ = 'Juk API'
	__version__ = '0.3.4.2'
	__author__ = 'BruceLee'
	__desc__ = 'API for the Juk Audio Player'

	playerAPI = playerAPI2 = None

	__timeout = None
	__interval = 2

	callbackFn = None
	__curplaying = None
	__nowisplaying = True
	
	ns    = 'org.kde.juk'
	iroot = '/Player'
	iface = 'org.kde.juk.player'
	
	iroot2 = '/MainApplication'
	iface2 = 'org.kde.KApplication'

	# Extended Functions from the GenericAPI
	def __init__(self, session_bus):
		GenericAPI.__init__(self, session_bus)

	def is_active(self, dbus_iface, screenlet_settings):
		if self.ns in dbus_iface.ListNames(): return True
		return False

	def connect(self, screenlet_settings):
		proxy_obj = self.session_bus.get_object(self.ns, self.iroot)
		self.playerAPI = dbus.Interface(proxy_obj, self.iface)
		proxy_obj = self.session_bus.get_object(self.ns, self.iroot2)
		self.playerAPI2 = dbus.Interface(proxy_obj, self.iface2)

	def get_title(self):
		ret = self.playerAPI.trackProperty('Title')
		if not ret: ret = ''
		return ret
	
	def get_album(self):
		ret = self.playerAPI.trackProperty('Album')
		if not ret: ret = ''
		return ret

	def get_artist(self):
		ret = self.playerAPI.trackProperty('Artist')
		if not ret: ret = ''
		return ret
		
	def get_url(self):
		ret = self.playerAPI.trackProperty('Path')
		if not ret: ret = ''
		return ret
	
	def get_cover_path(self):
		# Check for any PNG/JPG/JPEG image in the song folder
		cover_path = ''
		tmp = self.get_cover_from_path(self.get_url_dir())
		if tmp: cover_path = tmp
		return cover_path

	def is_playing(self):
		if int(self.playerAPI.status()) == 2: return True
		return False

	def is_paused(self):
		if int(self.playerAPI.status()) == 1: return True
		return False

	def play_pause(self):
		self.playerAPI.playPause()

	def next(self):
		self.playerAPI.forward()

	def previous(self):
		self.playerAPI.back()
		
	def stop(self):
		self.playerAPI.stop()
		
	def set_vol(self, value):
		if value > 100: value = 100
		elif value < 0: value = 0
		self.playerAPI.setVolume(float(value)/100)
		
	def vol_up(self):
		nv = float(self.playerAPI.volume()) + 0.05
		if nv != 1.05: self.set_vol(nv*100)
	
	def vol_down(self):
		nv = float(self.playerAPI.volume()) - 0.05
		if nv != -0.05: self.set_vol(nv*100)
	
	def vol_mute(self):
		self.playerAPI.mute()

	def register_change_callback(self, fn):
		self.callback_fn = fn
		# Could not find a callback signal for Listen, so just calling after some time interval
		if self.__timeout:
			gobject.source_remove(self.__timeout)
		self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)


	def info_changed(self, signal=None):
		# Only call the callback function if Data has changed
		if self.__timeout:
			gobject.source_remove(self.__timeout)
		try:
			if self.__curplaying != self.get_url():
				self.__curplaying = self.get_url()
				self.callback_fn()
			if self.__nowisplaying != self.playerAPI.is_playing():
				self.__nowisplaying = self.playerAPI.is_playing()
				self.callback_fn()
			self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)
		except:
			# The player exited ? call callback function
			self.callback_fn()
		self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)
		
	def quit(self):
		self.playerAPI2.quit()
		
