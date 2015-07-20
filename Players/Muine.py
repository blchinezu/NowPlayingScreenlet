#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MuineApi

import os
import dbus
import string
import gobject
from GenericPlayer import GenericAPI

class MuineAPI(GenericAPI):
	__name__ = 'Muine API'
	__version__ = '0.3.4.1'
	__author__ = 'BruceLee'
	__desc__ = 'API for the Muine Audio Player'

	playerAPI = None

	__timeout = None
	__interval = 2

	callbackFn = None
	__curplaying = None
	__nowisplaying = True
	
	ns    = 'org.gnome.Muine'
	iroot = '/org/gnome/Muine/Player'
	iface = 'org.gnome.Muine.Player'

	# Extended Functions from the GenericAPI
	def __init__(self, session_bus):
		GenericAPI.__init__(self, session_bus)

	def is_active(self, dbus_iface, screenlet_settings):
		if self.ns in dbus_iface.ListNames(): return True
		return False

	def connect(self, screenlet_settings):
		proxy_obj = self.session_bus.get_object(self.ns, self.iroot)
		self.playerAPI = dbus.Interface(proxy_obj, self.iface)

	def get_title(self):
		try:
			ret = self.playerAPI.GetCurrentSong().split('title: ')[1].split('\n')[0]
			if not ret: ret = ''
			return ret
		except:
			return ''
	
	def get_album(self):
		try:
			ret = self.playerAPI.GetCurrentSong().split('album: ')[1].split('\n')[0]
			if not ret: ret = ''
			return ret
		except:
			return ''

	def get_artist(self):
		try:
			ret = self.playerAPI.GetCurrentSong().split('artist: ')[1].split('\n')[0]
			if not ret: ret = ''
			return ret
		except:
			return ''
		
	def get_url(self):
		try:
			ret = self.playerAPI.GetCurrentSong().split('uri: ')[1].split('\n')[0]
			if not ret: ret = ''
			return ret
		except:
			return ''
	
	def get_cover_path(self):
		# Check for any PNG/JPG/JPEG image in the song folder
		cover_path = ''
		tmp = self.get_cover_from_path(self.get_url_dir())
		if tmp: cover_path = tmp
		return cover_path

	def is_playing(self):
		if self.playerAPI.GetPlaying(): return True
		return False

	def is_paused(self):
		if not self.is_playing(): return True
		return False

	def play_pause(self):
		if self.is_playing():
			self.playerAPI.SetPlaying(0)
		else:
			self.playerAPI.SetPlaying(1)

	def next(self):
		self.playerAPI.Next()

	def previous(self):
		self.playerAPI.Previous()
		
	def stop(self):
		self.playerAPI.SetPlaying(0)

	def set_vol(self, value):
		if value > 100: value = 100
		elif value < 0: value = 0
		self.playerAPI.SetVolume(int(value))
		
	def vol_up(self):
		if self.muted_vol != False: self.muted_vol = False
		nv = int(self.playerAPI.GetVolume()) + 5
		self.set_vol(nv)
	
	def vol_down(self):
		nv = int(self.playerAPI.GetVolume()) - 5
		self.set_vol(nv)
	
	def vol_mute(self):
		if self.muted_vol == False:
			self.muted_vol = int(self.playerAPI.GetVolume())
			self.set_vol(0)
		else:
			self.set_vol(self.muted_vol)
			self.muted_vol = False

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
		self.playerAPI.Quit()
	
