#!/usr/bin/env python

# Jajuk API 

import os
import dbus
import string
import gobject
from GenericPlayer import GenericAPI

class JajukAPI(GenericAPI):
	__name__ = 'Jajuk API'
	__version__ = '0.3.4.2'
	__author__ = 'BruceLee'
	__desc__ = 'API to the Jajuk Music Player'

	ns = "org.jajuk.dbus.DBusSupport"
	iroot = "/JajukDBus"
	iface = "org.jajuk.services.dbus.DBusSupport"

	playerAPI = None

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
		buff = str(self.playerAPI.current())
		for l,foo in enumerate(buff.split('(')): i=l; artist=foo
		return buff.replace('('+artist, '').replace('~','')
	
	def get_album(self):
		return ''

	def get_artist(self):
		buff = str(self.playerAPI.current())
		for l,foo in enumerate(buff.split('(')): i=l; artist=foo
		return artist.replace(')~', '')
	
	def get_album(self):
		buff = str(self.playerAPI.currentHTML())
		if buff.find("<b>") != -1:
			try:
				buff = buff.split("<br/>")
				if buff[1] != "</HTML>":
					buff2 = self.get_artist()
					if buff[1] != buff2: buff = buff2
					elif buff[2] != "</HTML>": buff = buff[2]
			except:
				buff = ''
		else:
			buff = ''
		return buff
		
	def get_cover_path(self):
		buff = str(self.playerAPI.currentHTML())
		if buff.find("<img src='") != -1:
			buff = buff.split("<img src='")[1].split("'/>")[0].replace("file:/", "/")
			if buff.find("/50x50/") != -1: re = "/50x50/"
			elif buff.find("/100x100/") != -1: re = "/100x100/"
			elif buff.find("/150x150/") != -1: re = "/150x150/"
			elif buff.find("/200x200/") != -1: re = "/200x200/"
			elif buff.find("/250x250/") != -1: re = "/250x250/"
			elif buff.find("/300x300/") != -1: re = "/300x300/"
			if os.path.exists(buff.replace(re, "/300x300/")): buff = buff.replace(re, "/300x300/")
			elif os.path.exists(buff.replace(re, "/250x250/")): buff = buff.replace(re, "/250x250/")
			elif os.path.exists(buff.replace(re, "/200x200/")): buff = buff.replace(re, "/200x200/")
			elif os.path.exists(buff.replace(re, "/150x150/")): buff = buff.replace(re, "/150x150/")
			elif os.path.exists(buff.replace(re, "/100x100/")): buff = buff.replace(re, "/100x100/")
			elif os.path.exists(buff.replace(re, "/50x50/")): buff = buff.replace(re, "/50x50/")
		else:
			buff = ''
		return buff

	def is_playing(self):
		if str(self.playerAPI.current()) == "not playing right now...":
			return False
		else:
			return True

	def is_paused(self):
		return False

	def play_pause(self):
		self.playerAPI.playPause()

	def next(self):
		self.playerAPI.next()

	def previous(self):
		self.playerAPI.previous()
		
	def stop(self):
		self.playerAPI.stop()
		
	def vol_up(self):
		self.playerAPI.increaseVolume()
		
	def vol_down(self):
		self.playerAPI.decreaseVolume()
		
	def vol_mute(self):
		self.playerAPI.mute()

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
		return self.get_artist()+" - "+self.get_title()
		
	def quit(self):
		self.playerAPI.exit()
	
