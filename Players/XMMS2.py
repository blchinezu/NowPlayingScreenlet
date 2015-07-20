#!/usr/bin/env python

# XMMS2 API

import os
import urllib
import sys
import string
import gobject
import commands
from GenericPlayer import GenericAPI

class XMMS2API(GenericAPI):
	__name__ = 'XMMS2 API'
	__version__ = '0.3.4.2'
	__author__ = 'BruceLee'
	__desc__ = 'XMMS2 API working with xmms2 and nyxmms2'
	
	type = 'xmms2'

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
		if self.bin_runs('xmms2d') \
			and not self.bin_runs("abraca") \
			and not self.bin_runs("esperanza") \
			and not self.bin_runs("gxmms2") \
			and not self.bin_runs("lxmusic"):
				return True
		return False

	# Make a connection to the Player
	def connect(self, screenlet_settings):
		pass

	# The following return Strings
	def get_track_info(self, inf):
		bin = False
		if os.path.exists('/usr/bin/nyxmms2'):	bin = 'nyxmms2'
		elif os.path.exists('/usr/bin/xmms2'):	bin = 'xmms2'
		if bin:
			buff = string.rstrip(os.popen(bin+' info | grep -i " '+str(inf)+' = "',"r").read(),"\n")
			if buff.find(" = ") != -1: return buff.split(" = ")[1]
		return ''
	
	def get_title(self):
		return self.get_track_info('title')
	
	def get_album(self):
		return self.get_track_info('album')

	def get_artist(self):
		return self.get_track_info('artist')
		
	def get_url(self):
		buff = self.get_track_info('url')
		return urllib.unquote_plus(buff.encode("utf-8").replace("file:///", "/"))
	
	def get_cover_path(self):
		cover_path = ''
		# Check the song folder for any PNG/JPG/JPEG image.
		tmp =  self.get_cover_from_path(self.get_url_dir())
		if tmp: cover_path = tmp
		return cover_path

	# Returns Boolean
	def is_playing(self):	# XXX: No idea how to do this with '/usr/bin/xmms2'
		buff = string.rstrip(os.popen('nyxmms2 status',"r").read(),"\n").split(":")[0]
		if buff == "Playing": 	return True
		elif buff == "Stopped":	return False

	def is_paused(self):	# XXX: Same here :/
		buff = string.rstrip(os.popen('nyxmms2 status',"r").read(),"\n").split(":")[0]
		if buff == "Paused": 	return True
		else:					return False

	# The following do not return any values
	def play_pause(self):
		if os.path.exists('/usr/bin/nyxmms2'):	os.system("nyxmms2 toggle &")
		elif os.path.exists('/usr/bin/xmms2'):	os.system("xmms2 toggleplay &")

	def next(self):
		if os.path.exists('/usr/bin/nyxmms2'):	os.system("nyxmms2 next &")
		elif os.path.exists('/usr/bin/xmms2'):	os.system("xmms2 next &")

	def previous(self):
		if os.path.exists('/usr/bin/nyxmms2'):	os.system("nyxmms2 prev &")
		elif os.path.exists('/usr/bin/xmms2'):	os.system("xmms2 prev &")

	def stop(self):
		if os.path.exists('/usr/bin/nyxmms2'):	os.system("nyxmms2 stop &")
		elif os.path.exists('/usr/bin/xmms2'):	os.system("xmms2 stop &")
		
	def set_vol(self, value):
		if value > 100: value = 100
		elif value < 0: value = 0
		if os.path.exists('/usr/bin/nyxmms2'):	os.system('nyxmms2 server volume '+str(int(value))+' &')
		elif os.path.exists('/usr/bin/xmms2'):	os.system('xmms2 volume '+str(int(value))+' &')
		
	def vol_up(self):
		if self.muted_vol != False: self.muted_vol = False
		if os.path.exists('/usr/bin/nyxmms2'):
			nv = int(os.popen('nyxmms2 server volume').read().replace('master = ','')) + 10
			if nv != 110:
				if nv > 100: nv = 100
				os.system('nyxmms2 server volume '+str(nv)+' &')
		elif os.path.exists('/usr/bin/xmms2'):
			nv = int(os.popen('xmms2 volume_list').read().replace('master = ','')) + 10
			if nv != 110:
				if nv > 100: nv = 100
				os.system('xmms2 volume '+str(nv)+' &')
	
	def vol_down(self):
		if os.path.exists('/usr/bin/nyxmms2'):
			nv = int(os.popen('nyxmms2 server volume').read().replace('master = ','')) - 10
			if nv != -10:
				if nv < 0: nv = 0
				os.system('nyxmms2 server volume '+str(nv)+' &')
		elif os.path.exists('/usr/bin/xmms2'):
			nv = int(os.popen('xmms2 volume_list').read().replace('master = ','')) - 10
			if nv != -10:
				if nv < 0: nv = 0
				os.system('xmms2 volume '+str(nv)+' &')
	
	def vol_mute(self):
		if self.muted_vol == False:
			if os.path.exists('/usr/bin/nyxmms2'):
				self.muted_vol = int(os.popen('nyxmms2 server volume').read().replace('master = ',''))
				os.system('nyxmms2 server volume 0 &')
			elif os.path.exists('/usr/bin/xmms2'):
				self.muted_vol = int(os.popen('xmms2 volume_list').read().replace('master = ',''))
				os.system('xmms2 volume 0 &')
		else:
			if os.path.exists('/usr/bin/nyxmms2'):
				os.system('nyxmms2 server volume '+str(self.muted_vol)+' &')
			elif os.path.exists('/usr/bin/xmms2'):
				os.system('xmms2 volume '+str(self.muted_vol)+' &')
			self.muted_vol = False

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
		return self.get_title()
	
	def quit(self):
		os.system('killall abraca esperanza gxmms2 lxmusic &')
		self.quit_xmms2d()
	
	def quit_xmms2d(self):
		self.stop()
		os.system('sleep 0.5s')
		if os.path.exists('/usr/bin/nyxmms2'):	os.system('nyxmms2 exit &')
		elif os.path.exists('/usr/bin/xmms2'):	os.system('xmms2 exit &')
		os.system('sleep 0.5s')
		os.system('killall xmms2d &')
	
