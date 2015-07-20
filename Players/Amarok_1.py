#!/usr/bin/env python

# Amarok_1 Api 

import os
import urllib
import string
import gobject
import pydcop
from GenericPlayer import GenericAPI

class Amarok_1API(GenericAPI):
	__name__ = 'Amarok 1 API'
	__version__ = '0.3.4.2'
	__author__ = 'vrunner, modified by Alexibaba, modified by BruceLee'
	__desc__ = 'Amarok_1 API to a Music Player'

	playerAPI = playerAPI2 = None

	__timeout = None
	__interval = 2

	callbackFn = None
	__curplaying = None


	def __init__(self, session_bus):
		# Ignore the session_bus. Initialize a dcop connection
		GenericAPI.__init__(self, session_bus)
	
	# Check if the player is active : Returns Boolean
	# A handle to the dbus interface is passed in : doesn't need to be used
	# if there are other ways of checking this (like dcop in amarok)
	def is_active(self, dbus_iface, screenlet_settings):
		app = pydcop.anyAppCalled("amarok")
		if not app: return False
		else: return True

	# Make a connection to the Player
	def connect(self, screenlet_settings):
		self.playerAPI = pydcop.anyAppCalled("amarok").player
		self.playerAPI2 = pydcop.anyAppCalled("amarok").MainApplication-Interface
	
	# The following return Strings
	def get_title(self):
		return self.playerAPI.title()
	
	def get_album(self):
		return self.playerAPI.album()

	def get_artist(self):
		return self.playerAPI.artist()
		
	def get_url(self):
		return self.playerAPI.path()

	def get_cover_path(self):
		cover_path = self.playerAPI.coverImage()
		if cover_path.find('130@nocover.png') == -1:
			# Check for large cache cover
			buff = cover_path.split('cache/')[0] + 'large/' + cover_path.split('@')[1]
			if os.path.exists(buff):
				cover_path = buff
			else:
				# Check for tag cache cover
				buff = cover_path.split('cache/')[0] + 'tagcover/' + cover_path.split('@')[1]
				if os.path.exists(buff):
					cover_path = buff
				else:
					# Check the song folder for any PNG/JPG/JPEG image.
					tmp = self.get_cover_from_path(self.get_url_dir())
					if tmp: cover_path = tmp
		else:
			cover_path = ''
		return cover_path

	# Returns Boolean
	def is_playing(self):
		return self.playerAPI.isPlaying()

	def is_paused(self):
		if self.playerAPI.isPlaying() == True:
			return False
		else:
			return True

	# The following do not return any values
	def play_pause(self):
		self.playerAPI.playPause()

	def next(self):
		self.playerAPI.next()

	def previous(self):
		self.playerAPI.prev()
		
	def stop(self):
		self.playerAPI.stop()
		
	def set_vol(self, value):
		self.playerAPI.setVolume(int(value))
		
	def vol_up(self):
		self.playerAPI.setVolumeRelative(5)
	
	def vol_down(self):
		self.playerAPI.setVolumeRelative(-5)
	
	def vol_mute(self):
		self.playerAPI.mute()
		
	# Rating
	def get_rating(self):
		try:
			ret = float(self.playerAPI.rating)/2
		except:
			ret = False
		self.rating = ret
		return ret
		
	def set_rating(self, value):
		self.rating = value
		self.playerAPI.setRating(int(value*2))
		return True
		

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
		return str(self.playerAPI.nowPlaying())+"\n"+str(self.playerAPI.rating())
		
	def quit(self):
		self.playerAPI2.quit()

