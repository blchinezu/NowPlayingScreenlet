#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Listen API 

import os
import dbus
import string
import gobject
from GenericPlayer import GenericAPI

class ListenAPI(GenericAPI):
	__name__ = 'Listen API'
	__version__ = '0.3.4.2'
	__author__ = 'vrunner, modified by Alexibaba, modified by BruceLee'
	__desc__ = 'API to the Listen Music Player'

	ns = "org.gnome.Listen"
	iroot = "/org/gnome/listen"
	iface = "org.gnome.Listen"

	playerAPI = None

	volume = 0.5

	__timeout = None
	__interval = 2

	callbackFn = None
	__curplaying = None

	# Extended Functions from the GenericAPI

	def __init__(self, session_bus):
		GenericAPI.__init__(self, session_bus)

	def is_active(self, dbus_iface, screenlet_settings):
		if self.ns in dbus_iface.ListNames(): return True
		else: return False

	def connect(self, screenlet_settings):
		proxy_obj = self.session_bus.get_object(self.ns, self.iroot)
		self.playerAPI = dbus.Interface(proxy_obj, self.iface)

	def get_title(self):
		buff = self.playerAPI.get_title()
		if buff: return buff
		return ''
	
	def get_album(self):
		buff = self.playerAPI.get_album()
		if buff: return buff
		return ''

	def get_artist(self):
		buff = self.playerAPI.get_artist()
		if buff: return buff
		return ''
		
	def get_url(self):
		try:
			ret = self.playerAPI.path()
		except:
			ret = ''
		return ret
	
	def get_cover_path(self):
		# Check for any given cover path.
		cover_path = self.playerAPI.get_cover_path()
		if os.path.exists(cover_path): return cover_path
		
		# Check the song folder for any PNG/JPG/JPEG image.
		cover_path = ''
		tmp = self.get_cover_from_path(self.get_url_dir())
		if tmp: cover_path = tmp
		if os.path.exists(cover_path): return cover_path
		
		# Check standard paths for cover
		artist = string.lower(self.get_artist())
		album = string.lower(self.get_album()).replace("/", "")
		img = artist + "+" + album + ".jpg"
		img2 = album + ".jpg"
		cover_path = os.environ['HOME'] + "/.cache/listen/cover/" + img
		if os.path.exists(cover_path): return cover_path
		cover_path = os.environ['HOME'] + "/.cache/listen/cover/" + img2
		if os.path.exists(cover_path): return cover_path
		cover_path = os.environ['HOME'] + "/.listen/cover/" + img
		if os.path.exists(cover_path): return cover_path
		cover_path = os.environ['HOME'] + "/.listen/cover/" + img2
		return cover_path

	def is_playing(self):
		if self.playerAPI.current_playing() == "": return False
		else: return True

	def is_paused(self):
		if self.playerAPI.current_playing() == "": return True
		else: return False

	def play_pause(self):
		self.playerAPI.play_pause()

	def next(self):
		self.playerAPI.next()

	def previous(self):
		self.playerAPI.previous()
		
	def set_vol(self, value):
		if value > 100: value = 100
		elif value < 0: value = 0
		self.playerAPI.volume(float(value)/100)
		
	def vol_up(self):
		if self.muted_vol: self.muted_vol = False
		self.volume += 0.05
		if self.volume != 1.05: self.set_vol(self.volume*100)
	
	def vol_down(self):
		self.volume -= 0.05
		if self.volume != -0.05: self.set_vol(self.volume*100)
		
	def vol_mute(self):
		if self.muted_vol:
			self.set_vol(self.muted_vol*100)
			self.muted_vol = False
		else:
			self.set_vol(0)
			self.muted_vol = self.volume

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

			self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)
		except:
			# The player exited? call callback function
			self.callback_fn()
			
	def quit(self):
		self.playerAPI.quit()
			
