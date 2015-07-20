#!/usr/bin/env python

# Amarok_1_no_pydcop Api 

import os
import sys
import string
import gobject
import commands
from GenericPlayer import GenericAPI

class Amarok_1_no_pydcopAPI(GenericAPI):
	__name__ = 'Amarok 1 (no pydcop) API'
	__version__ = '0.3.4.2'
	__author__ = 'Alexibaba, modified by BruceLee'
	__desc__ = 'Amarok_1_no_pydcop API to a Music Player'

	playerAPI = None

	__timeout = None
	__interval = 2

	callbackFn = None
	__curplaying = None

	session_bus = False

	def __init__(self, session_bus):
		# Ignore the session_bus. Initialize a dcop connection
		GenericAPI.__init__(self, session_bus)
	
	# Check if the player is active : Returns Boolean
	# A handle to the dbus interface is passed in : doesn't need to be used
	# if there are other ways of checking this (like dcop in amarok)
	def is_active(self, dbus_iface, screenlet_settings):
		if self.bin_runs("amarokapp"):
			if os.popen('printf "$( { dcop; } 2>&1 )" | grep -i amarok').read().replace('\n','') == "amarok":
				return True
		else:
			return False

	# Make a connection to the Player
	def connect(self, screenlet_settings):
		pass

	
	# The following return Strings
	def get_title(self):
		return string.rstrip(os.popen("dcop amarok player title","r").read(),"\n")
	
	def get_album(self):
		return string.rstrip(os.popen("dcop amarok player album","r").read(),"\n").replace("&","&amp;")

	def get_artist(self):
		return string.rstrip(os.popen("dcop amarok player artist","r").read(),"\n")
		
	def get_url(self):
		return os.popen('dcop amarok player path').read()
	
	def get_cover_path(self):
		cover_path = string.rstrip(os.popen("dcop amarok player coverImage","r").read(),"\n")
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
#		if commands.getoutput("dcop amarok player isPlaying") == "call failed": 
#			#sys.exit(0)
#			#return None
#			self.halt = True
#			return False
		if commands.getoutput("dcop amarok player isPlaying") == "true": 
			return True
		else:
			return False

	def is_paused(self):
		if commands.getoutput("dcop amarok player isPlaying") == "false": 
			return True
		else:
			return False

	# The following do not return any values
	def play_pause(self):
		os.system("dcop amarok player playPause &")

	def next(self):
		os.system("dcop amarok player next &")

	def previous(self):
		os.system("dcop amarok player prev &")
		
	def stop(self):
		os.system("dcop amarok player stop &")
		
	def set_vol(self, value):
		os.system('dcop amarok player setVolume '+str(int(value))+' &')
		
	def vol_up(self):
		os.system('dcop amarok player setVolumeRelative 5 &')
	
	def vol_down(self):
		os.system('dcop amarok player setVolumeRelative -5 &')
	
	def vol_mute(self):
		os.system('dcop amarok player mute &')
		
	# Rating
	def get_rating(self):
		try:
			ret = float(os.popen('dcop amarok player rating').read())/2
		except:
			ret = False
		self.rating = ret
		return ret
		
	def set_rating(self, value):
		self.rating = value
		os.system('dcop amarok player setRating '+str(int(value*2))+' &')
		return True
		

	def register_change_callback(self, fn):
		self.callback_fn = fn
		# Could not find a callback signal for Banshee, so just calling after some time interval
		if self.__timeout:
			gobject.source_remove(self.__timeout)
		self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)

	def info_changed(self, signal=None):
		if self.__timeout:
			gobject.source_remove(self.__timeout)
		try:
			# Only call the callback function if Data has changed
			if self.__curplaying != None and not self.is_playing():
				self.__curplaying = None
				self.callback_fn()
			nowplaying = self.now_playing()
			if self.is_playing() and self.__curplaying != nowplaying:
				self.__curplaying = nowplaying
				self.callback_fn()
			self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)
		except:
			# The player exited ? call callback function
			self.callback_fn()
			pass

	def now_playing(self):
		return string.rstrip(os.popen("dcop amarok player nowPlaying","r").read(),"\n")+str(os.popen("dcop amarok player rating").read())
		
	def quit(self):
		os.system('dcop amarok MainApplication-Interface quit &')
		
