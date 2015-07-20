# This application is released under the GNU General Public License 
# v3 (or, at your option, any later version). You can find the full 
# text of the license under http://www.gnu.org/licenses/gpl.txt. 
# By using, editing and/or distributing this software you agree to 
# the terms and conditions of this license. 
# Thank you for using free software!

# Audacious API (c) Whise (Helder Fraga) 2008 <helder.fraga@hotmail.com>


import os
import string
import gobject
from GenericPlayer import GenericAPI
import commands
import urllib

class AudaciousAPI(GenericAPI):
	__name__ = 'Audacious API'
	__version__ = '0.3.4.2'
	__author__ = 'Whise (Helder Fraga), modified by BruceLee'
	__desc__ = 'Audacious API to a Music Player'

	playerAPI = None

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
		if self.bin_runs("audacious"): return True
		return False
			
	def connect(self, screenlet_settings):
		pass
	
	# The following return Strings
	def get_title(self):
		try:
			a =  commands.getoutput('audtool current-song-tuple-data title')
			return a
		except:
			return ''
	
	def get_album(self):
		try:
			a =  commands.getoutput('audtool current-song-tuple-data album')
			return a
		except:
			return ''

	def get_artist(self):
		try:
			a =  commands.getoutput('audtool current-song-tuple-data artist')
			return a
		except:
			return ''
		
	def get_url(self):
		return commands.getoutput('audtool current-song-filename')
	
	def get_cover_path(self):
		try:
			# Check the song folder for any PNG/JPG/JPEG image.
			cover_path = ''
			tmp = self.get_cover_from_path(self.get_url_dir())
			if tmp: cover_path = tmp
			return cover_path
		except:
			return ''

	# Returns Boolean
	def is_playing(self):
		return True

	# The following do not return any values
	def play_pause(self):
		os.system('audtool --playback-playpause &')

	def next(self):
		os.system('audtool --playlist-advance &')

	def previous(self):
		os.system('audtool --playlist-reverse &')
		
	def stop(self):
		os.system('audtool --playback-stop &')
		
	def set_vol(self, value):
		if value > 100: value = 100
		elif value < 0: value = 0
		os.system('audtool --set-volume '+str(int(value))+' &')
		
	def vol_up(self):
		if self.muted_vol != False: self.muted_vol = False
		nv = int(os.popen('audtool --get-volume').read()) + 5
		if nv != 105:
			self.set_vol(nv)
	
	def vol_down(self):
		nv = int(os.popen('audtool --get-volume').read()) - 5
		if nv != -5:
			self.set_vol(nv)
	
	def vol_mute(self):
		if self.muted_vol == False:
			self.muted_vol = int(os.popen('audtool --get-volume').read())
			self.set_vol(0)
		else:
			self.set_vol(self.muted_vol)
			self.muted_vol = False


	def register_change_callback(self, fn):
		self.callback_fn = fn
		# Could not find a callback signal for Listen, so just calling after some time interval
		if self.__timeout:
			gobject.source_remove(self.__timeout)
		self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)
		#self.playerAPI.connect_to_signal("playingUriChanged", self.info_changed)

	def info_changed(self, signal=None):
		# Only call the callback function if Data has changed
		if self.__curplaying != commands.getoutput('audtool --current-song'):
			self.__curplaying = commands.getoutput('audtool --current-song')
			self.callback_fn()

		if self.__timeout:
			gobject.source_remove(self.__timeout)
		self.__timeout = gobject.timeout_add(self.__interval * 1000, self.info_changed)

	def quit(self):
		os.system('audtool --shutdown &')
		
