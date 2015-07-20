#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Rhythmbox API 

import os
import dbus
import urllib
from GenericPlayer import GenericAPI
import urllib
from urlparse import urlparse

class RhythmboxAPI(GenericAPI):
	__name__ = 'Rhythmbox'
	__version__ = '0.3.4.2'
	__author__ = 'vrunner, modified by Alexibaba, modified by BruceLee'
	__desc__ = 'API to the Rhythmbox Music Player'

	ns = "org.gnome.Rhythmbox"
	playerAPI = None
	shellAPI = None

	callback_fn = None

	# Extended Functions from the GenericAPI

	def __init__(self, session_bus):
		GenericAPI.__init__(self, session_bus)

	def is_active(self, dbus_iface, screenlet_settings):
		if self.ns in dbus_iface.ListNames(): return True
		else: return False

	def connect(self, screenlet_settings):
		proxy_obj1 = self.session_bus.get_object(self.ns, '/org/gnome/Rhythmbox/Player')
		proxy_obj2 = self.session_bus.get_object(self.ns, '/org/gnome/Rhythmbox/Shell')
		self.playerAPI = dbus.Interface(proxy_obj1, self.ns+".Player")
		self.shellAPI = dbus.Interface(proxy_obj2, self.ns+".Shell")

	def get_title(self):
		tmp = self.getProperty('rb:stream-song-title')
		if tmp: return tmp
		else: return self.getProperty('title')
	
	def get_album(self):
		tmp = self.getProperty('rb:stream-song-album')
		if tmp: return tmp
		else: return self.getProperty('album')

	def get_artist(self):
		tmp = self.getProperty('rb:stream-song-artist')
		if tmp: return tmp
		else: return self.getProperty('artist')
		
	def get_url(self):
		songurl = self.playerAPI.getPlayingUri()
		return urllib.unquote_plus(songurl.encode("utf-8").replace('file:///', '/'))
	
	def get_cover_path(self):
		coverFile = self.getProperty('rb:coverArt-uri')
		if coverFile != None:
			if os.path.isfile(coverFile):
				return coverFile
		coverFile = os.environ['HOME']+"/.gnome2/rhythmbox/covers/"+self.get_artist()+" - "+self.get_album()+".jpg"
		if not os.path.isfile(coverFile):
			coverFile = os.environ['HOME']+"/.cache/rhythmbox/covers/"+self.get_artist()+" - "+self.get_album()+".jpg"
			if not os.path.isfile(coverFile):
				# Check the song folder for any PNG/JPG/JPEG image.
				tmp =  self.get_cover_from_path(self.get_url_dir())
				if tmp: coverFile = tmp
 		return coverFile

	def is_paused(self):
		if self.playerAPI.getPlaying() == 0: return True
		else: return False

	def is_playing(self):
		if self.playerAPI.getPlaying() == 1: return True
		else: return False

	def play_pause(self):
		if self.is_playing:
			self.playerAPI.playPause(False)
		else:
			self.playerAPI.playPause(True)

	def next(self):
		self.playerAPI.next()

	def previous(self):
		self.playerAPI.previous()
		
	def set_vol(self, value):
		if value > 100: value = 100
		elif value < 0: value = 0
		self.playerAPI.setVolume(float(value)/100)
		
	def vol_up(self):
		if self.muted_vol != False:
			self.vol_mute()
		else:
			self.playerAPI.setVolumeRelative(0.05)
		
	def vol_down(self):
		self.playerAPI.setVolumeRelative(-0.05)
	
	def vol_mute(self):
		if self.muted_vol == False:
			self.muted_vol = self.playerAPI.getVolume()
			self.playerAPI.setVolume(0)
		else:
			self.playerAPI.setVolume(self.muted_vol)
			self.muted_vol = False
			
	def register_change_callback(self, fn):
		if(self.callback_fn == None):
			#print "Registering Callback"
			self.callback_fn = fn
			self.playerAPI.connect_to_signal("playingChanged", self.info_changed)
			self.playerAPI.connect_to_signal("playingUriChanged", self.info_changed)
			self.playerAPI.connect_to_signal("playingSongPropertyChanged", self.info_changed)

	# Internal Functions
	def getProperty(self, name):
		try:
			val = self.shellAPI.getSongProperties(self.playerAPI.getPlayingUri())[name]
			return val
		except:
			return None

	def info_changed(self, *args, **kwargs):
		self.callback_fn()
		
	def quit(self):
		self.shellAPI.quit()

