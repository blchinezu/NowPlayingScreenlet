#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MprisApi

import os
import urllib
import dbus
import string
import gobject
from GenericPlayer import GenericAPI

class MprisAPI(GenericAPI):
	__name__ = 'Mpris API'
	__version__ = '0.3.4.2'
	__author__ = 'Alexibaba, modified by BruceLee'
	__desc__ = 'API to the MPRIS-controlled Music Players'
	
	type = 'mpris'

	playerAPI = playerAPI2 = None

	__timeout = None
	__interval = 2

	callbackFn = None
	__curplaying = None
	__nowisplaying = True
	
	this_mpris_iroot2 = '/'
	this_mpris_iface2 = 'org.freedesktop.MediaPlayer'

	# Extended Functions from the GenericAPI

	def __init__(self, session_bus):
		GenericAPI.__init__(self, session_bus)

	def is_active(self, dbus_iface, screenlet_settings):

		for i in range(1, 4):
			self.screenlet_settings  = screenlet_settings
			self.this_mpris_ns       = self.screenlet_settings['mpris_ns_'+str(i)]
			self.this_mpris_iroot    = self.screenlet_settings['mpris_iroot_'+str(i)]
			self.this_mpris_iface    = self.screenlet_settings['mpris_iface_'+str(i)]

			if self.this_mpris_ns in dbus_iface.ListNames(): 
				return True
				break
		else: 
			return False

	def connect(self, screenlet_settings):
		proxy_obj = self.session_bus.get_object(self.this_mpris_ns, self.this_mpris_iroot)
		self.playerAPI = dbus.Interface(proxy_obj, self.this_mpris_iface)
		proxy_obj = self.session_bus.get_object(self.this_mpris_ns, self.this_mpris_iroot2)
		self.playerAPI2 = dbus.Interface(proxy_obj, self.this_mpris_iface2)

	def get_title(self):
		ret = self.playerAPI.GetMetadata().get("title")
		if not ret: ret = ''
		return ret
	
	def get_album(self):
		ret = self.playerAPI.GetMetadata().get("album")
		if not ret: ret = ''
		return ret

	def get_artist(self):
		ret = self.playerAPI.GetMetadata().get("artist")
		if not ret: ret = ''
		return ret
		
	def get_url(self):
		songurl = self.playerAPI.GetMetadata().get("location")
		if not songurl: songurl = ''
		return urllib.unquote_plus(songurl.encode("utf-8"))
	
	def get_url_dir(self):
		songurl = self.get_url()
		anz = len(songurl.split("/"))
		atom = songurl.split("/")
		arturl = ''
		for i in range(anz-1):
			arturl += atom[i]
			arturl += "/"
		song_path = arturl[7:]
		return song_path

	def get_cover_path(self):
		# arturl is not possible in every application which uses empris
		cover_path = self.playerAPI.GetMetadata().get("arturl")
		if cover_path and os.path.exists(cover_path) == True:
			return cover_path
		else: # Check for any PNG/JPG/JPEG image in the song folder
			cover_path = ''
			tmp = self.get_cover_from_path(self.get_url_dir())
			if tmp: cover_path = tmp
		return cover_path

	def is_playing(self):
		if self.playerAPI.GetStatus()[0] == 0 or self.playerAPI.GetStatus()[0] == 1: 
			return True
		else: 
			return False

	def is_paused(self):
		if self.playerAPI.GetStatus()[0] == 1: 
			return True
		else: 
			return False

	def play_pause(self):
		if self.playerAPI.GetStatus()[0] != 2:
			self.playerAPI.Pause()       # toggle play/pause
		else:
			self.playerAPI.Play()        # after "Stop" start with playing

	def next(self):
		self.playerAPI.Next()

	def previous(self):
		self.playerAPI.Prev()

	def stop(self):
		self.playerAPI.Stop()
		
	def set_vol(self, value):
		if value > 100: value = 100
		elif value < 0: value = 0
		self.playerAPI.VolumeSet(int(value))
		
	def vol_up(self):
		if self.muted_vol != False: self.muted_vol = False
		nv = int(self.playerAPI.VolumeGet()) + 5
		self.set_vol(nv)
	
	def vol_down(self):
		nv = int(self.playerAPI.VolumeGet()) - 5
		self.set_vol(nv)
	
	def vol_mute(self):
		if self.muted_vol == False:
			self.muted_vol = int(self.playerAPI.VolumeGet())
			self.playerAPI.VolumeSet(0)
		else:
			self.playerAPI.VolumeSet(self.muted_vol)
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
			if self.__curplaying != self.playerAPI.GetMetadata().get("location"):
				self.__curplaying = self.playerAPI.GetMetadata().get("location")
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
		self.playerAPI2.Quit()
