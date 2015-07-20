#!/usr/bin/env python

# Banshee API 

import os
import dbus
import string
import gobject
from GenericPlayer import GenericAPI

class BansheeAPI(GenericAPI):
	__name__ = 'Banshee API'
	__version__ = '0.3.4.2'
	__author__ = 'vrunner, modified by Alexibaba, modified by BruceLee'
	__desc__ = 'API to the Banshee Music Player'

	ns = "org.bansheeproject.Banshee"
	iroot_song = "/org/bansheeproject/Banshee/PlayerEngine"
	iface_song = "org.bansheeproject.Banshee.PlayerEngine"

	iroot_control = "/org/bansheeproject/Banshee/PlaybackController"
	iface_control = "org.bansheeproject.Banshee.PlaybackController"

	ns_mpris     = "org.mpris.MediaPlayer2.banshee"
	iroot_mpris  = "/org/mpris/MediaPlayer2"
	iface_mpris  = "org.mpris.MediaPlayer2.Player"
	iface_mpris2 = "org.mpris.MediaPlayer2"

	songAPI = controlAPI = mprisAPI = mprisAPI2 = None
	
	dbus_iface_listnames = None

	__timeout = None
	__interval = 2

	callback_fn = None
	__curplaying = None
	__nowisplaying = True

	# Extended Functions from the GenericAPI
	def __init__(self, session_bus):
		GenericAPI.__init__(self, session_bus)

	def is_active(self, dbus_iface, screenlet_settings):
		if self.ns in dbus_iface.ListNames():
			self.dbus_iface_listnames = dbus_iface.ListNames()
			return True
		else: return False

	def connect(self, screenlet_settings):
		proxy_obj = self.session_bus.get_object(self.ns, self.iroot_song)
		self.songAPI = dbus.Interface(proxy_obj, self.iface_song)

		proxy_obj = self.session_bus.get_object(self.ns, self.iroot_control)
		self.controlAPI = dbus.Interface(proxy_obj, self.iface_control)
		
		if self.ns_mpris in self.dbus_iface_listnames:
			proxy_obj = self.session_bus.get_object(self.ns_mpris, self.iroot_mpris)
			self.mprisAPI  = dbus.Interface(proxy_obj, self.iface_mpris)
			self.mprisAPI2 = dbus.Interface(proxy_obj, self.iface_mpris2)

	def get_title(self):
		ret = self.songAPI.GetCurrentTrack().get("name")
		if not ret: ret = ''
		return ret
	
	def get_album(self):
		ret = self.songAPI.GetCurrentTrack().get("album")
		if not ret: ret = ''
		return ret

	def get_artist(self):
		ret = self.songAPI.GetCurrentTrack().get("artist")
		if not ret: ret = ''
		return ret
		
	def get_url(self):
		ret = self.songAPI.GetCurrentTrack().get("local-path")
		if not ret: ret = ''
		return ret
	
	def get_cover_path(self):
		tmp = self.get_cover_from_path(self.get_url_dir())
		if tmp and os.path.exists(tmp):
			return tmp
		artimg = self.songAPI.GetCurrentTrack().get("artwork-id") + '.jpg'
		arturl = '/home/' + os.getenv("USER") + '/.cache/media-art/' + artimg
		if not os.path.exists(arturl):
			arturl = '/home/' + os.getenv("USER") + '/.cache/album-art/' + artimg
		return arturl

	def is_playing(self):
		if self.songAPI.GetCurrentState() == "playing": 
			return True
		else: 
			return False

	def is_paused(self):
		if self.songAPI.GetCurrentState() == "paused": 
			return True
		else: 
			return False

	def play_pause(self):
		self.songAPI.TogglePlaying()

	def next(self):
		self.controlAPI.Next(1)

	def previous(self):
		self.controlAPI.Previous(1)

	def stop(self):
		if mprisAPI: self.mprisAPI.Stop()
		
	# Rating
	def get_rating(self):
		try:
			ret = float(self.songAPI.GetCurrentTrack().get("rating"))
		except:
			ret = 0
		return ret
		
	def set_rating(self, value):
		self.rating_only_get = True
		return False
		

	def register_change_callback(self, fn):
		self.callback_fn = fn
		# Could not find a callback signal for Listen, so just calling after some time interval
		if self.__timeout:
			gobject.source_remove(self.__timeout)
		self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)

	def info_changed(self, signal=None):
		if self.__timeout:
			gobject.source_remove(self.__timeout)
		# Only call the callback function if Data has changed
		if self.__curplaying != self.now_playing():
			self.__curplaying = self.now_playing()
			self.callback_fn()
		self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)

	def now_playing(self):
		return str(self.songAPI.GetCurrentTrack())+"\n"+str(self.get_rating())
		
	def quit(self):
		if self.mprisAPI2: self.mprisAPI2.Quit()

