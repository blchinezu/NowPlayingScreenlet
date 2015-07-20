#!/usr/bin/env python

# QuodLibet Api

import os
import subprocess
import string
import gobject
from GenericPlayer import GenericAPI

class QuodLibetAPI(GenericAPI):
	__name__ = 'QuodLibet API'
	__version__ = '0.3.4.2'
	__author__ = 'Jonathan Rauprich <joni@noplu.de>, modified by Alexibaba, modified by BruceLee'
	__desc__ = 'API to the QuodLibet Music Player'

	ns = "net.sacredchao.QuodLibet"
	iroot = "/net/sacredchao/QuodLibet"

	playerAPI = None

	callback_fn = None
	__curplaying = None
	__timeout = None
	__interval = 2

	playing = True	

	# Extended Functions from the GenericAPI

	def __init__(self, session_bus):
		GenericAPI.__init__(self, session_bus)

	def is_active(self, dbus_iface, screenlet_settings):
		if self.ns in dbus_iface.ListNames(): return True
		else: return False

	def connect(self, screenlet_settings):
		self.playerAPI = self.session_bus.get_object(self.ns, self.iroot)

	def get_title(self):
		return self.playerAPI.CurrentSong()['title']
	
	def get_album(self):
		return self.playerAPI.CurrentSong()['album']

	def get_artist(self):
		return self.playerAPI.CurrentSong()['artist']
		
	def get_cover_path(self):
		#requires save curent cover art to disc plugin
		cover_path = "/home/" + os.getenv("USER") + "/.quodlibet/current.cover"
		if os.path.exists(cover_path):
			return cover_path
		return ''

	def is_playing(self):
		return self.playing

	def is_paused(self):
		a = self.playerAPI.CurrentSong()['title']
		if a and a != "":
			return False
		else:
			return True

	def play_pause(self):
		self.playerAPI.PlayPause()

	def next(self):
		self.playerAPI.Next()

	def previous(self):
		self.playerAPI.Previous()

	def stop(self):
		self.playerAPI.Pause()

	def register_change_callback(self, fn):
		if(self.callback_fn == None):
			#print "Registering Callback"
			self.callback_fn = fn
			self.playerAPI.connect_to_signal("SongStarted", self.signal_info_changed)
			self.playerAPI.connect_to_signal("SongEnded", self.signal_info_changed)
			self.playerAPI.connect_to_signal("Paused", self.cb_paused)
			self.playerAPI.connect_to_signal("Unpaused", self.cb_unpaused)
		#need also the calling after time-interval, to check if the player is still running
		if self.__timeout:
			gobject.source_remove(self.__timeout)
		self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)


	def signal_info_changed(self, *args, **kwargs):
		self.callback_fn()
	
	#used to save playing status
	def cb_paused(self):
		self.playing = False
		self.callback_fn()

	def cb_unpaused(self):
		self.playing = True
		self.callback_fn()

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
			# The player exited ? call callback function
			self.callback_fn()
		self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)
		
	def quit(self):
		os.system('killall quodlibet &')
		
