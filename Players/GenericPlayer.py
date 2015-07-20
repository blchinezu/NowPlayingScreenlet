#!/usr/bin/env python

import os

# A Generic API to a Music Player. 
# All Players must extend this class

class GenericAPI:
	__name__ = 'GenericAPI'
	__version__ = '0.3.4.3'
	__author__ = 'vrunner, modified by BruceLee'
	__desc__ = 'A Generic API to a Music Player. All Players must extend this.'

	session_bus = False
	halt = False
	
	preferred_cover = None
	cover_names = [ 'cover', 'folder', 'front' ]
	cover_extensions = [ 'png', 'jpg', 'jpeg', 'bmp' ]
	
	type = 'independent'

	muted_vol = False
	rating = 'None'
	rating_only_get = False

	def __init__(self, session_bus):
		self.session_bus = session_bus
	
	# Check if the player is active : Returns Boolean
	# A handle to the dbus interface is passed in : doesn't need to be used
	# if there are other ways of checking this (like dcop in amarok)
	def is_active(self, dbus_iface, screenlet_settings):
		print str(self.__name__)+" has no function to check if it's active or not."
		return False

	# Make a connection to the Player
	def connect(self, screenlet_settings):
		print str(self.__name__)+" has no connect function."
	
	# The following return Strings
	def get_title(self):
		print str(self.__name__)+" can't return title string."
		return ''
	
	def get_album(self):
		print str(self.__name__)+" can't return album string."
		return ''

	def get_artist(self):
		print str(self.__name__)+" can't return artist string."
		return ''

	def get_cover_path(self):
		print str(self.__name__)+" can't return cover_path string."
		return ''
		
	def get_url(self):
		print str(self.__name__)+" can't get uri string."
		return 'NOT SUPPORTED'
	
	def get_url_dir(self):
		buff = self.get_url()
		if buff != 'NOT SUPPORTED':
			for l,foo in enumerate(buff.split('/')): i=l; song=foo
			return buff.replace(song, '')
		print str(self.__name__)+" can't get directory uri string."
		return 'NOT SUPPORTED'
		
	def get_cover_from_path(self, path):
		if os.path.exists(str(path)):
			song_path = str(path)
			# Check for preferred image
			if self.preferred_cover and self.preferred_cover != '':
				for ext in self.cover_extensions:
					buff = os.popen('ls -1 "' + song_path + '" | grep -i "'+str(self.preferred_cover)+'\.'+str(ext)+'"').read().split('\n')[0]
					if buff != '': return song_path + buff
			# Check for preferred cover names
			for ext in self.cover_extensions:
				for name in self.cover_names:
					buff = os.popen('ls -1 "' + song_path + '" | grep -i "'+str(name)+'\.'+str(ext)+'"').read().split('\n')[0]
					if buff != '': return song_path + buff
			# Check for any image with preferred extension
			for ext in self.cover_extensions:
				buff = os.popen('ls -1 "' + song_path + '" | grep -i "\.'+str(ext)+'"').read().split('\n')[0]
				if buff != '': return song_path + buff
		return False
				
	# Return Float
	def get_rating(self):
		print str(self.__name__)+" can't provide ratings."
		return 'None'

	# Returns Boolean
	def set_rating(self, value):
		print str(self.__name__)+" can't modify ratings."
		return False
		
	def is_playing(self):
		print str(self.__name__)+" can't check if player is playing."
		return False

	def is_paused(self):
		print str(self.__name__)+" can't check if player is paused."
		return False
		
	def bin_runs(self, bin): # No need to extend this. It's used only locally
		if os.popen('ps axo "%p|%a" | grep -v grep | grep -i '+str(bin)).read().find(str(bin)) != -1: return True
		return False

	# The following do not return any values
	def play_pause(self):
		print str(self.__name__)+" can't play/pause playback."

	def next(self):
		print str(self.__name__)+" can't switch to the next track."

	def previous(self):
		print str(self.__name__)+" can't switch to the previous track."
		
	def stop(self):
		print str(self.__name__)+" can't stop playback."
		
	def set_vol(self, value):
		print str(self.__name__)+" can't set the volume."
		
	def vol_up(self):
		print str(self.__name__)+" can't increase volume."
	
	def vol_down(self):
		print str(self.__name__)+" can't decrease volume."
	
	def vol_mute(self):
		print str(self.__name__)+" can't mute/unmute volume."

	# The following calls the passed Callback function when one of the following event occurs:
	# - Song Change, Play/Pause, Info Change
	# If no dbus api to support it, then just do call the callback fn every few seconds
	def register_change_callback(self, fn):
		print str(self.__name__)+" can't register callback !!!"

	def quit(self):
		print str(self.__name__)+" has no function for quitting the player."
		return 'NOT SUPPORTED'
		
