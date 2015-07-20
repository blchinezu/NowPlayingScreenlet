#!/usr/bin/env python

#  NowPlayingScreenlet by magicrobomonkey
#  - Modified by vrunner to be more extensible
#  - Modified by Alexibaba
#  - Modified by BruceLee - new features, optimizations, API updates/upgrades

# INFO:
# - a simple viewer for currently playing (which became more complex)
 
#  This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import screenlets
from screenlets.options import StringOption, IntOption, BoolOption, FloatOption
import cairo
import dbus
import pango
import gtk
import gobject
import os.path
import sys
import re
import traceback

import string

#from dbus.mainloop.glib import DBusGMainLoop
import dbus.glib

# Get the ScreenletPath
ScreenletPath = sys.path[0]

# Add the Player Modules Path
sys.path.append(ScreenletPath+'/Players')

# Add the CoverFetcher search Path
sys.path.append(ScreenletPath+'/fetcher')
import NP_Fetcher

# Add the UI Module
sys.path.append(ScreenletPath+'/UI')
import Theme 

DBUS_NAME = "org.freedesktop.DBus"
DBUS_OBJECT = "/org/freedesktop/DBus"

# List of Module Names (the class name must be the same but with API at the end)
# So for the module "abraca" the class name will be "abracaAPI"
PLAYER_LIST = [	'Abraca',
				'Amarok_1',
				'Amarok_1_no_pydcop',
				'Amarok_2',
				'Audacious',
				'Banshee',
				'DecibelAudioPlayer',
				'Esperanza',
				'Exaile',
				'gXMMS2',
				'Jajuk',
				'Juk',
				'Listen',
				'LXMusic',
				'Muine',
				'qmmp',
				'QuodLibet',
				'Rhythmbox',
				'Songbird',
				'Mpris',
				'Mpd',
				'XMMS2']

PLAYER_LIST_LAUNCH = ['Abraca', 'Amarok 1', 'Amarok 2', 'Audacious', 'Banshee', 'Decibel-Audio-Player', 'Esperanza', 'Exaile', 'gXMMS2', 'Jajuk', 'Juk', 'Listen', 'LXMusic', 'MPRIS', 'Muine', 'MPD', 'qmmp', 'Quod Libet', 'Rhythmbox', 'Songbird', 'XMMS2']

MPRIS_NS_1 = ''
MPRIS_IROOT_1 = ''
MPRIS_IFACE_1 = ''
MPRIS_NS_2 = ''
MPRIS_IROOT_2 = ''
MPRIS_IFACE_2 = ''
MPRIS_NS_3 = ''
MPRIS_IROOT_3 = ''
MPRIS_IFACE_3 = ''

MPD_HOST_1 = ''
MPD_PORT_1 = ''
MPD_PW_1 = ''
MPD_MUSIC_PATH_1 = ''
MPD_HOST_2 = ''
MPD_PORT_2 = ''
MPD_PW_2 = ''
MPD_MUSIC_PATH_2 = ''

COVER_PATH = ''
KEY_AMAZON = ''
KEY_LASTFM = ''
KEY_DISCOGS = ''

# use gettext for translation
import gettext

_ = screenlets.utils.get_translator(__file__)

def tdoc(obj):
	obj.__doc__ = _(obj.__doc__)
	return obj

@tdoc
# The Screenlet Class
class NowPlayingScreenlet(screenlets.Screenlet):
	"""A screenlet to show what\'s currently playing and control the player."""
	
	# default meta-info for Screenlets
	__name__ = 'NowPlayingScreenlet'
	__version__ = '0.3.4.3'
	__author__ = 'magicrobotmonkey, modified by Whise, modified by Alexibaba, modified by BruceLee'
	__desc__ = __doc__
	
	player = False
	player_type = False
	playing = False
	cover_path = False
	actual_cover_path = None

	play_pause_button = False
	prev_button = False

	skin = False

	coverEngine = None

	__timeout = None
	check_interval = 5 # i.e. every 5 seconds, check for a player

	__scroll_timeout = None
	scroll_interval = 300 # scroll every 300 milliseconds by default

	# Sometimes the cover fetch takes time, so wait for it
	__cover_timeout = None
	__cover_check_interval = 1 # i.e. every 2 seconds
	__num_times_cover_checked = 0
	__max_cover_path_searches = 1 # Check 1 times
	__num_times_cover_checked_online = 0
	__max_cover_path_searches_online = 1 # Check 1 times
	__last_played_album = ""

	__buffer_back = None

	session_bus = None
	still_fetching = False

	force_getting_info = False

	player_list = []
	player_start = False
	player_close = False
	default_player = ''
	default_player_old = ''
	
	wallpaper_active = False
	wallpaper_path_current = os.popen('gconftool-2 -g "/desktop/gnome/background/picture_filename"').read().split('\n')[0]
	wallpaper_path_default = wallpaper_path_current
	wallpaper_path_artist = os.popen('printf $HOME').read() + '/'+_('Pictures')
	wallpaper_path_album = wallpaper_path_artist
	if wallpaper_active:
		os.system('gconftool-2 -t bool -s "/desktop/gnome/background/draw_background" TRUE')
	wallpaper_missing_active = False
	wallpaper_missing = ScreenletPath + '/artist-wallpaper.missing'
	
	history_traking = False
	history_file = ScreenletPath + '/player.history'
	history_last_entry = " -  ()"
	history_time_format = "%Y.%m.%d - %H:%M:%S"
	
	cover_copy_active = False
	cover_copy_only_if_album = False
	cover_copy_image_name = _("Cover")
	cover_copy_image_ext = "jpg"
	cover_copy_replace_smaller = True
	cover_copy_remove_others = False
	rating = None
	
	preferred_cover = ''
	
	debugging_enabled = False
	
	if os.popen("ps ax|grep -v grep|grep -i compiz").read().find("compiz") != -1 and os.path.exists("/usr/bin/compiz"):
		fade_enabled = True
	else:
		fade_enabled = False
	fade = False
	fade_in_on_player_start = False
	fade_out_on_no_player = True
	fade_in_on_play = True
	fade_out_on_stop = True
	fade_on_hover = False
	fade_step = 0.20
	fade_step_time = 50
	fade_all = False
	last_fade = False
	
	cover_pixbuf = None
	waiting_cover_change = False
	
	sleep_fading = False
	sleep_fade_duration = 30
	sleep_fade_startvol = 100
	sleep_fade_endvol = 0
	sleep_fade_quit_player = True
	sleep_fade_shutdown = True
	sleep_fade_tmp_x = 0
	sleep_fade_tmp_y = None
	
	theme_xml = None
	waiting_theme_change = False
	
	current_path = '<!NULL!>'
	last_artist = '<!NULL!>'
	last_album = '<!NULL!>'
	last_title = '<!NULL!>'
	last_cover_path = '<!NULL!>'
	last_path = '<!NULL!>'
	last_theme = '<!NULL!>'
	last_rating = '<!NULL!>'
	last_wallpaper_state = '<!NULL!>'
	last_history_state = '<!NULL!>'
	
	image_viewer = '/usr/bin/eog'
	file_browser = '/usr/bin/nautilus'
	
	MPRIS_NS_1 = ''
	MPRIS_IROOT_1 = ''
	MPRIS_IFACE_1 = ''
	MPRIS_NS_2 = ''
	MPRIS_IROOT_2 = ''
	MPRIS_IFACE_2 = ''
	MPRIS_NS_3 = ''
	MPRIS_IROOT_3 = ''
	MPRIS_IFACE_3 = ''

	MPD_HOST_1 = 'localhost'
	MPD_PORT_1 = '6600'
	MPD_PW_1 = ''
	MPD_MUSIC_PATH_1 =  os.popen('printf $HOME').read() + '/'+_('Music')+'/'
	MPD_HOST_2 = ''
	MPD_PORT_2 = ''
	MPD_PW_2 = ''
	MPD_MUSIC_PATH_2 = os.popen('printf $HOME').read() + '/'+_('Music')+'/'

	if ScreenletPath == os.popen('printf $HOME').read() + '/.screenlets/NowPlaying':
		COVER_PATH = ScreenletPath + '/'+_('covers')+'/'
	else:
		COVER_PATH = os.popen('printf $HOME').read() + '/.nowplaying/'+_('covers')+'/'
	KEY_AMAZON = ''
	KEY_LASTFM = ''
	KEY_DISCOGS = ''


	# constructor
	def __init__(self, **keyword_args):
		""" Initialization """
		
		screenlets.Screenlet.__init__(self, uses_theme=True,
									width=int(700), height=int(700),
									**keyword_args)

		#init dbus
		self.dbus_connect()
		# Set the Player List
		self.init_player_list()
		# set theme
		self.theme_name = "default"
		# add menu items
		self.add_menuitem("playpause", _("Play/Pause"))
		self.add_menuitem("next", _("Next"))
		self.add_menuitem("previous", _("Previous"))
		self.add_menuitem("open_cover_with_viewer", _("Open cover with viewer"))
		self.add_menuitem("open_cover_location", _("Open cover location"))
		self.add_menuitem("Show_Hide", _("Show/Hide"))
		self.add_menuitem("sleepfade", _("Sleep Fade"))
		# add default menu items
		self.add_default_menuitems()

		# Options tab: GENERAL
		self.add_options_group(_('General'), _('General settings:\n'))
		self.add_option(IntOption(_('General'), 'scroll_interval',
			self.scroll_interval, _('Scroll Time (ms)'), 
			_('How quickly to scroll long titles ? The smaller the value the faster it is, and more CPU usage'),
			min=50, max=5000))
		self.add_option(StringOption(_('General'), 'image_viewer',
			self.image_viewer, _('Image viewer'),
			_('The path to the image viewer launcher.')))
		self.add_option(StringOption(_('General'), 'file_browser',
			self.file_browser, _('File browser'),
			_('The path to the file browser launcher.')))
		self.add_option(BoolOption(_('General'), 'debugging_enabled',
			self.debugging_enabled, _('Debugging mode'), 
			_('Extra output in the terminal. Useful for maintainers.')))
			
		# Options tab: PLAYER
		self.add_options_group(_('Player'), _('Player settings:\n'))
		self.add_option(BoolOption(_('Player'), 'player_start',
			self.player_start, _('Start it when Screenlet starts'), 
			_('Start Player when Screenlet starts?')))
		self.add_option(StringOption(_('Player'), 'default_player',
			self.default_player, _('Player to Launch'), 
			_('Player that starts when screenlet starts (restart required)'),
			choices=PLAYER_LIST_LAUNCH))
		self.add_option(BoolOption(_('Player'), 'player_close',
			self.player_close, _('Close it when Screenlet quits'), 
			_('Close the Player when Screenlet quits?')))

		# Options tab: FADE
		self.add_options_group(_('Fade'),
			_('Fade:\n  Adds a fade effect for the screenlet.\n'))
		self.add_option(BoolOption(_('Fade'), 'fade_enabled',
			self.fade_enabled, _('Activated'),
			 _('Eyecandy fade transition effect.')))
		self.add_option(BoolOption(_('Fade'), 'fade_in_on_player_start',
			self.fade_in_on_player_start, _('Fade in on player start'),
			_('Fade in on player start.')))
		self.add_option(BoolOption(_('Fade'), 'fade_out_on_no_player',
			self.fade_out_on_no_player, _('Fade out on no player'), 
			_('Fade out on no player.')))
		self.add_option(BoolOption(_('Fade'), 'fade_in_on_play', 
			self.fade_in_on_play, _('Fade in on play'),  
			_('Fade in on play.')))
		self.add_option(BoolOption(_('Fade'), 'fade_out_on_stop',
			self.fade_out_on_stop, _('Fade out on stop'),
			_('Fade out on stop.')))
		self.add_option(BoolOption(_('Fade'), 'fade_on_hover',
			self.fade_on_hover, _('Fade on hover'),
			_('Fade on hover.')))
		self.add_option(FloatOption(_('Fade'), 'fade_step',
			self.fade_step, _('Fade step'),
			_('Transparency amount to add/substract at each fade step'),
			min=0.0, max=1.0, digits=2, increment=0.05))
		self.add_option(IntOption(_('Fade'), 'fade_step_time',
			self.fade_step_time, _('Fade step time'),
			_('Time between 2 fade steps (milliseconds)'),
			min=0, max=1000, increment=5))
	
		# Options tab: MPRIS
		self.add_options_group(_('MPRIS'),
			_('MPRIS settings \n\nUsually you only have to change the "Remote application"\n-  You can configure three different MPRIS settings\n'))
		self.add_option(StringOption(_('MPRIS'), 'MPRIS_NS_1',
			self.MPRIS_NS_1, _('1: Remote application'),
			_('Remote application (restart required)')))
		self.add_option(StringOption(_('MPRIS'), 'MPRIS_IROOT_1',
			self.MPRIS_IROOT_1, _('1: Remote object'),
			_('Remote object (restart required)')))
		self.add_option(StringOption(_('MPRIS'), 'MPRIS_IFACE_1',
			self.MPRIS_IFACE_1, _('1: Interface function'),
			_('Interface function (restart required)')))
		self.add_option(StringOption(_('MPRIS'), 'MPRIS_NS_2',
			self.MPRIS_NS_2, _('2: Remote application'),
			_('Remote application (restart required)')))
		self.add_option(StringOption(_('MPRIS'), 'MPRIS_IROOT_2',
			self.MPRIS_IROOT_2, _('2: Remote object'),
			_('Remote object (restart required)')))
		self.add_option(StringOption(_('MPRIS'), 'MPRIS_IFACE_2',
			self.MPRIS_IFACE_2, _('2: Interface function'),
			_('Interface function (restart required)')))
		self.add_option(StringOption(_('MPRIS'), 'MPRIS_NS_3',
			self.MPRIS_NS_3, _('3: Remote application'),
			_('Remote application (restart required)')))
		self.add_option(StringOption(_('MPRIS'), 'MPRIS_IROOT_3',
			self.MPRIS_IROOT_3, _('3: Remote object'),
			_('Remote object (restart required)')))
		self.add_option(StringOption(_('MPRIS'), 'MPRIS_IFACE_3',
			self.MPRIS_IFACE_3, _('3: Interface function'),
			_('Interface function (restart required)')))

		# Options tab: MPD
		self.add_options_group(_('MPD'),
			_('MPD settings!\n\n-  You need to install python-mpd to use this Player!\n-  Leave the password field blank, if no password is used.\n-  The path to your music will be used\n    for local cover fetching.\n-  You can configure two different MPD settings\n    (the first will be used if both are available)\n'))
		self.add_option(StringOption(_('MPD'), 'MPD_HOST_1',
			self.MPD_HOST_1, _('1: MPD Host'),
			_('Hostadress of MPD server (restart required)')))
		self.add_option(StringOption(_('MPD'), 'MPD_PORT_1',
			self.MPD_PORT_1, _('1: MPD Port'),
			_('Port to connect to the MPD server (restart required)')))
		self.add_option(StringOption(_('MPD'), 'MPD_PW_1',
			self.MPD_PW_1, _('1: MPD Password'),
			_('MPD password. Leave blanc if no password is needed (restart required)')))
		self.add_option(StringOption(_('MPD'), 'MPD_MUSIC_PATH_1',
			self.MPD_MUSIC_PATH_1, _('1: Path to your music.'),
			_('Music-Dir, if MPD works local, or if you have the Music in a share at the server (restart required)')))
		self.add_option(StringOption(_('MPD'), 'MPD_HOST_2',
			self.MPD_HOST_2, _('2: MPD Host'),
			_('Hostadress of MPD server (restart required)')))
		self.add_option(StringOption(_('MPD'), 'MPD_PORT_2',
			self.MPD_PORT_2, _('2: MPD Port'),
			_('Port to connect to the MPD server (restart required)')))
		self.add_option(StringOption(_('MPD'), 'MPD_PW_2',
			self.MPD_PW_2, _('2: MPD Password'),
			_('MPD password. Leave blanc if no password is needed (restart required)')))
		self.add_option(StringOption(_('MPD'), 'MPD_MUSIC_PATH_2',
			self.MPD_MUSIC_PATH_2, _('2: Path to your music.'),
			_('Music-Dir, if MPD works local, or if you have the Music in a share at the server (restart required)')))

		# Options tab: COVER
		self.add_options_group(_('Cover'),
			_('Cover fetcher:\n-  Path: Without this path, the cover-fetcher will not be used.\n-  Amazon: You need your personal key.\n-  LastFM and Discogs: Works without a key.\n\nCover Copy:\n-  Copies the current cover to the song folder.\n-  It needs imagemagick to change the image extension (jpg, png...)\n\nPreferred Cover Name:\n-  The cover name to search for in the song folder (without extension)\n'))
		# cover fetcher
		self.add_option(StringOption(_('Cover'), 'COVER_PATH',
			self.COVER_PATH, _('Path to save covers'),
			_('The downloaded covers will be saved here. (restart required)')))
		self.add_option(StringOption(_('Cover'), 'KEY_AMAZON',
			self.KEY_AMAZON, _('Amazon Key'),
			_('Amazon API-Key. Get it for free (restart required)')))
		self.add_option(StringOption(_('Cover'), 'KEY_LASTFM',
			self.KEY_LASTFM, _('LastFM Key'),
			_('LastFM API-Key. Get it for free (restart required)')))
		self.add_option(StringOption(_('Cover'), 'KEY_DISCOGS',
			self.KEY_DISCOGS, _('Discogs Key'),
			_('Discogs API-Key. Get it for free (restart required)')))
		# cover copy
		self.add_option(BoolOption(_('Cover'), 'cover_copy_active',
			self.cover_copy_active, _('Cover Copy Activated'), 
			_('Activate/Deactivate the Cover Copy function.')))
		self.add_option(BoolOption(_('Cover'), 'cover_copy_only_if_album',
			self.cover_copy_only_if_album, _('Only if album tag exists'), 
			_('Copy cover only for songs which have an album tag.')))
		self.add_option(StringOption(_('Cover'), 'cover_copy_image_name',
			self.cover_copy_image_name, _('Cover Image Name'),
			_('What name should the copied cover image have?')))
		self.add_option(StringOption(_('Cover'), 'cover_copy_image_ext',
			self.cover_copy_image_ext, _('Cover Image Extension'),
			_('What extension should the copied cover image have?')))
		self.add_option(BoolOption(_('Cover'), 'cover_copy_replace_smaller',
			self.cover_copy_replace_smaller, _('Replace Smaller Cover'), 
			_('Should the Cover Copy function replace existent smaller covers?')))
		self.add_option(BoolOption(_('Cover'), 'cover_copy_remove_others',
			self.cover_copy_remove_others, _('Remove other images'), 
			_('Should the Cover Copy function remove other images present in the folder?')))
		# preferred cover
		self.add_option(StringOption(_('Cover'), 'preferred_cover',
			self.preferred_cover, _('Preferred Cover Name'),
			_('Which name should be searched when searching for cover in the song folder?')))

		# Options tab: WALLPAPER
		self.add_options_group(_('Wallpaper'),
			_('Wallpaper settings:\n  Sets wallpaper according to the current album or artist.\n\n-  Use absolute paths\n-  The images must have an extension\n-  The image names must be the album/artist shown in the player (case insensitive)\n-  The following characters encountered in the artist/album name must be\n  written as _ (underline):  \\ / \' " [ ] \n-  For field details check the tooltips\n'))
		self.add_option(BoolOption(_('Wallpaper'), 'wallpaper_active',
			self.wallpaper_active, _('Activated'), 
			_('Activate/Deactivate the wallpaper function.')))
		self.add_option(StringOption(_('Wallpaper'), 'wallpaper_path_default',
			self.wallpaper_path_default, _('Default wallpaper'),
			_('This will be shown when not having a cover or not playing.')))
		self.add_option(StringOption(_('Wallpaper'), 'wallpaper_path_album',
			self.wallpaper_path_album, _('Album Path'),
			_('Search location for album wallpaper.')))
		self.add_option(StringOption(_('Wallpaper'), 'wallpaper_path_artist',
			self.wallpaper_path_artist, _('Artist Path'),
			_('Search location for artist wallpaper.')))
		self.add_option(BoolOption(_('Wallpaper'), 'wallpaper_missing_active',
			self.wallpaper_missing_active, _('Mark missing wallpapers to file'), 
			_('If the track has no wallpaper it writes the artist name to a file.')))
		self.add_option(StringOption(_('Wallpaper'), 'wallpaper_missing',
			self.wallpaper_missing, _('Marker file'),
			_('Contains the artists that don\'t have a wallpaper.')))

		# Options tab: HISTORY
		self.add_options_group(_('History'),
			_('History settings:\n  Logs played songs.\n\n-  Use absolute paths\n'))
		self.add_option(BoolOption(_('History'), 'history_traking',
			self.history_traking, _('Activated'), 
			_('Activate/Deactivate the history function.')))
		self.add_option(StringOption(_('History'), 'history_time_format',
			self.history_time_format, _('Time Format'),
			_('The time format used for the tracks log.')))
		self.add_option(StringOption(_('History'), 'history_file',
			self.history_file, _('History file'),
			_('The file will contain all the played tracks: "%artist% - %title% (%album%)".')))

		# Options tab: SLEEP
		self.add_options_group(_('Sleep'),
			_('Sleep fade:\n  During a determined period of time the volume slowly fades out and at the end of\n the process the player and/or the computer can be shutted down.\n\n-  Slow volume fading is not supported by: Amarok 2, Banshee, Jajuk, MPD, QuodLibet\n-  Player quit option is not supported by: Amarok 2, MPD\n-  The shutdown feature requires zenity to get the user password.\n'))
		self.add_option(IntOption(_('Sleep'), 'sleep_fade_duration',
			self.sleep_fade_duration, _('Duration (minutes)'), 
			_('Duration (minutes)'),min=1, max=9999))
		self.add_option(IntOption(_('Sleep'), 'sleep_fade_startvol',
			self.sleep_fade_startvol, _('Start Volume'), 
			_('Start volume'),min=1, max=100))
		self.add_option(IntOption(_('Sleep'), 'sleep_fade_endvol',
			self.sleep_fade_endvol, _('End Volume'), 
			_('End volume'),min=0, max=100))
		self.add_option(BoolOption(_('Sleep'), 'sleep_fade_quit_player',
			self.sleep_fade_quit_player, _('Quit Player'), 
			_('When finished quit player.')))
		self.add_option(BoolOption(_('Sleep'), 'sleep_fade_shutdown',
			self.sleep_fade_shutdown, _('Shutdown'), 
			_('When finished shutdown the computer.')))
	
		os.system('mkdir -p "'+self.COVER_PATH+'"')

		# Check for Players
		self.check_for_players()
		# Init the timeout function to regularly check for players
		self.check_interval = self.check_interval
		
	def __setattr__(self, name, value):
		screenlets.Screenlet.__setattr__(self, name, value)
		if name == "check_interval":
			if value > 0:
				self.__dict__['check_interval'] = value
				if self.__timeout:
					gobject.source_remove(self.__timeout)
				self.__timeout = gobject.timeout_add(value * 1000, self.check_for_players)
			else:
				pass
		if name == "scroll_interval":
			if value > 0:
				self.__dict__['scroll_interval'] = value
				if self.__scroll_timeout:
					gobject.source_remove(self.__scroll_timeout)
				self.__scroll_timeout = gobject.timeout_add(value, self.update)
			else:
				pass
		if name == "scale":
			try:
				if value >= 1.4 : value = 1.4
				Theme.Skin.set_scale(skinxml,self.scale)
			except:
				pass

	def menuitem_callback(self, widget, id):
		screenlets.Screenlet.menuitem_callback(self, widget, id)
		if id=="playpause":
			if self.player: self.play_pause_wrapped()
		elif id=="next":
			if self.player: self.player.next()
		elif id=="previous":
			if self.player: self.player.previous()
		elif id=="open_cover_with_viewer":
			if self.player: self.open_cover_with_viewer()
		elif id=="open_cover_location":
			if self.player: self.open_cover_location()
		elif id=="Show_Hide":
			self.Show_Hide()
		elif id=="sleepfade":
			self.sleepfade()
	
	def Show_Hide(self):
		if self.fade_enabled:
			if self.last_fade == "in":	self.screenlet_fadeout('manual')
			else:						self.screenlet_fadein('manual')
		else:
			self.GUI_msg('Scr_Nam_Ver',
				_("To use the Show/Hide option you must activate the fade effect."))
	
	def sleepfade_core(self):
		if self.sleep_fading and self.player:
			if self.sleep_fade_tmp_x >= self.sleep_fade_endvol:
				if self.player.is_active(self.dbus_iface, self.screenlet_settings):
					self.player.set_vol(self.sleep_fade_tmp_x)
					self.sleep_fade_tmp_x -= 1
			else:
				self.GUI_msg('Scr_Nam_Ver', _("Shutting down."))
				self.sleep_fading = gobject.source_remove(self.sleep_fading)
				self.sleep_fading = False
				self.player.stop()
				os.system('sleep 7s')
				self.player.set_vol(100)
				os.system('sleep 1s')
				self.set_default_wallpaper()
				if self.sleep_fade_quit_player and self.player:
					self.player.quit()
					os.system('sleep 6s')
				if self.sleep_fade_shutdown:
					os.system('echo "'+str(self.sleep_fade_tmp_y)+'" | sudo -S shutdown -h 1')
					self.sleep_fade_tmp_y = None
				return False
			return True
		return False
	
	def sleepfade(self): 
		if self.sleep_fading:
			self.sleep_fading = gobject.source_remove(self.sleep_fading)
			self.sleep_fading = False
			self.sleep_fade_tmp_y = None
			self.GUI_msg('Scr_Nam_Ver', _("Sleep fade STOPPED."))
		elif self.player:
			step_sleep_time = (float(self.sleep_fade_duration) * 60.0) / (float(self.sleep_fade_startvol) - float(self.sleep_fade_endvol))
			self.sleep_fade_tmp_x = self.sleep_fade_startvol
			if self.sleep_fade_shutdown:
				if os.path.exists('/usr/bin/zenity'):
					self.sleep_fade_tmp_y = os.popen('zenity --password').read()
					if self.sleep_fade_tmp_y and self.sleep_fade_tmp_y != '':
						dir = '/test_np_root'
						os.system('echo "'+str(self.sleep_fade_tmp_y)+'" | sudo -S mkdir -p '+dir)
						if not os.path.exists(dir):
							os.system("zenity --warning --title='"+_('Warning!')+"' --text='"+_('The password is incorrect.')+"' &")
						else:
							os.system('echo "'+str(self.sleep_fade_tmp_y)+'" | sudo -S rmdir '+dir)
							self.GUI_msg('Scr_Nam_Ver', _("The computer will shutdown in ")+str(self.sleep_fade_duration)+_(" minutes."))
							self.sleep_fading = gobject.timeout_add( int(step_sleep_time*1000), self.sleepfade_core)
				else:
					self.GUI_msg('Scr_Nam_Ver', _("This feature requires zenity."))
			else:
				self.sleep_fading = gobject.timeout_add( int(step_sleep_time*1000), self.sleepfade_core)
			
	def open_cover_with_viewer(self):
		if self.image_viewer and os.path.exists(self.image_viewer):
			buff = None
			if self.actual_cover_path and os.path.exists(self.actual_cover_path):	buff = self.actual_cover_path
			elif self.cover_path and os.path.exists(self.cover_path):				buff = self.cover_path
			if buff:
				os.system(self.image_viewer + ' "' + buff + '" &')
		else:
			self.dbg("WARNING: The image viewer path [" + self.image_viewer + "] does not exist.")
			
	def open_cover_location(self):
		if self.file_browser and os.path.exists(self.file_browser):
			buff = None
			if self.actual_cover_path and os.path.exists(self.actual_cover_path):	buff = self.actual_cover_path
			elif self.cover_path and os.path.exists(self.cover_path):				buff = self.cover_path
			if buff:
				for l,foo in enumerate(buff.split('/')): i=l; img=foo
				os.system(self.file_browser + ' "' + buff.replace(img, '') + '" &')
		else:
			self.dbg("WARNING: The file browser path [" + self.file_browser + "] does not exist.")


	def on_load_theme_core(self):
		if not self.fade_all:
			if self.fade:
				self.fade = gobject.source_remove(self.fade)
				self.fade = False
			if self.skin: self.skin.cleanup()
			self.skin = Theme.Skin(self.theme_xml, self)
			if self.fade_enabled:
				self.skin.transparency = 1
				self.set_controls_transparency(self.skin.transparency)
			self.reset_last_known()
			self.width = self.skin.width
			self.height = self.skin.height
			self.mousex = self.mousey = 0
			self.set_player_callbacks()
			self.force_get_info()
			self.scale = self.scale
			self.skin.set_scale(self.scale)
			# Draw it all to a buffer
			self.init_buffers()
#			self.redraw_background_items()
			#self.scale = self.scale
			if self.cover_path and os.path.exists(self.cover_path):
				pixbuf = gtk.gdk.pixbuf_new_from_file(self.cover_path)
				self.skin.set_albumcover(pixbuf)
			self.fullupdate()
			#if self.scale >= 1.41:
			#	self.scale = 1.40
			#	self.redraw_canvas()
			
			os.popen("sleep 0.5")
			
			if self.fade_enabled:
				self.screenlet_fadein('theme change')
			if self.waiting_theme_change:
				self.waiting_theme_change = gobject.source_remove(self.waiting_theme_change)
				self.waiting_theme_change = False
				return False
		return True

	def on_load_theme(self): 
		if os.path.exists(ScreenletPath + '/themes/' + self.theme_name + '/cover_manip.sh'):
			os.system("rm -f '" + ScreenletPath + '/themes/' + self.theme_name + "/cover.png'")
		skinxml = ScreenletPath+'/themes/'+self.theme_name+"/skin.xml"
		if os.path.exists(skinxml):
			self.theme_xml = skinxml
			if self.skin:
				self.screenlet_fadeout('theme change')
			if self.fade: self.fade = gobject.source_remove(self.fade)
			if self.waiting_cover_change:
				self.waiting_cover_change = gobject.source_remove(self.waiting_cover_change)
				self.waiting_cover_change = False
			if self.waiting_theme_change:
				self.waiting_theme_change = gobject.source_remove(self.waiting_theme_change)
				self.waiting_theme_change = False
			self.waiting_theme_change = gobject.timeout_add( self.fade_step_time, self.on_load_theme_core)

	def on_init(self):
		#helps to load the buttons properly
		if self.default_player == '' : self.default_player = 'Rhythmbox'
		self.dbg('CORE > Default player: ' + self.default_player)
		if self.default_player == 'MPD':
			self.dbg('WARNING: You need python-mpd module, make sure you have it installed.')
		if self.COVER_PATH == '':
			self.dbg('WARNING: Cover fetching engine is NOT running (the cover path is not set)')
		elif os.path.exists(self.COVER_PATH) != True:
			self.dbg('WARNING: Cover fetching engine is NOT running (the cover path doesn\'t exist)')
		self.default_player_old = self.default_player
		self.on_load_theme()
		if self.default_player != '' and self.player_start == True:
			self.dbg('CORE > Launching player ' + self.default_player + '...')
			if self.default_player.find('Amarok') != -1:
				os.system('amarok &')
			elif self.default_player == "XMMS2":
				os.system('nyxmms2 play &')
			else:
				os.system((self.default_player.lower().replace(' ','')) +  '  &')
		# Create Array for the player plugins who needs info from settings
		self.screenlet_settings = {
			'mpris_ns_1'		:	self.MPRIS_NS_1, 
			'mpris_iroot_1'		:	self.MPRIS_IROOT_1, 
			'mpris_iface_1'		:	self.MPRIS_IFACE_1,
			'mpris_ns_2'		:	self.MPRIS_NS_2, 
			'mpris_iroot_2'		:	self.MPRIS_IROOT_2, 
			'mpris_iface_2'		:	self.MPRIS_IFACE_2,
			'mpris_ns_3'		:	self.MPRIS_NS_3, 
			'mpris_iroot_3'		:	self.MPRIS_IROOT_3, 
			'mpris_iface_3'		:	self.MPRIS_IFACE_3,
			'mpd_host_1'		:	self.MPD_HOST_1,
			'mpd_port_1'		:	self.MPD_PORT_1,
			'mpd_pw_1'			:	self.MPD_PW_1,
			'mpd_music_path_1'	:	self.correct_path(self.MPD_MUSIC_PATH_1),
			'mpd_host_2'		:	self.MPD_HOST_2,
			'mpd_port_2'		:	self.MPD_PORT_2,
			'mpd_pw_2'			:	self.MPD_PW_2,
			'mpd_music_path_2'	:	self.correct_path(self.MPD_MUSIC_PATH_2),
			'cover_path'		:	self.correct_path(self.COVER_PATH),
			'key_amazon'		:	self.KEY_AMAZON,
			'key_lastfm'		:	self.KEY_LASTFM,
			'key_discogs'		:	self.KEY_DISCOGS }
		# History function
		if self.history_traking:
			this_entry = 'INFO: ' + self.__name__ + ' v.' + self.__version__ + ' started...'
			if self.history_last_entry != this_entry:
				c_date = os.popen('printf "`date +' + "'" + self.history_time_format + "'" + '`"').read()
				os.system("echo '' >> '" + self.history_file + "'")
				os.system("echo '[" + c_date + "] " + this_entry + "' >> '" + self.history_file + "'")
				self.history_last_entry = this_entry

	def on_scale(self):
		if self.window:
			if self.skin: self.skin.set_scale(self.scale)
			self.init_buffers()
			self.fullupdate()
			#self.redraw_background_items()
		self.redraw_canvas()
		
	def on_quit(self):
		xx = self.default_player_old
		if xx != '' and self.player_close == True:
			for i,player in enumerate(self.player_list):
				if player and player.__class__.__name__.replace('_no_pydcop','').replace('API','').replace('_','') == xx.replace(' ', '').replace('-',''):
					if player.is_active(self.dbus_iface, self.screenlet_settings):
						player.connect(self.screenlet_settings)
						self.player.quit()
					break
		# Restore wallpaper if the wallpaper function is active
		if self.wallpaper_active:
			self.set_default_wallpaper()
		# History function
		if self.history_traking:
			this_entry = 'INFO: ' + self.__name__ + ' ' + self.__version__ + ' exited...'
			if self.history_last_entry != this_entry:
				c_date = os.popen('printf "`date +' + "'" + self.history_time_format + "'" + '`"').read()
				os.system("echo '[" + c_date + "] " + this_entry + "' >> '" + self.history_file + "'")
				self.history_last_entry = this_entry
#		TODO: fadeout @ quit; not yet done because of screenlets engine restriction.. maybe i'll find a workaround
#		step=0
#		while step*self.fade_step < 1:
#			self.screenlet_fadeout_core()
#			os.popen("sleep " + str(self.fade_step_time/1000))
#			step += 1
				
	def init_buffers(self):
		self.__buffer_back = gtk.gdk.Pixmap(self.window.window, 
			int(self.width * self.scale), int(self.height * self.scale), -1)
		
	def redraw_background_items(self):
		self.dbg("GFX > REDRAW: redraw__background_items()")
		if not self.__buffer_back: return
		ctx_ns = self.__buffer_back.cairo_create()
		self.clear_cairo_context(ctx_ns)
		ctx_ns.scale(self.scale, self.scale)

		playing = self.check_playing()
		# to draw the right play/pause button when changed by player
		if self.player:
			if self.skin and self.skin.playercontrols_item:
				c = self.skin.playercontrols_item
				image = "play"
				if playing: image = "pause"
				else: image = "play"
				c.set_images("play_pause", image)
				if c.play_pause_button and c.play_pause_button.mouse_over(self.mousex*self.scale, self.mousey*self.scale):
					c.play_pause_button.image = c.play_pause_button.image_hover
		if self.theme and self.skin:
			for item in self.skin.items:
				try:
					if item.regular_updates: continue # Omit items that need regular updating
				except:
					pass
				try:
					if item.type == "playercontrols" and item.categ == "new": continue
					#if item.type == "rating": continue
				except:
					pass
				if playing and item.display=="on-stopped": pass
				elif not playing and item.display=="on-playing": pass
				else: 
					item.draw(ctx_ns)
	
	def dbus_connect(self):
		self.session_bus = dbus.SessionBus()
		dbus_object = self.session_bus.get_object(DBUS_NAME, DBUS_OBJECT)
		self.dbus_iface = dbus.Interface(dbus_object, DBUS_NAME)
		#self.dbus_iface.connect_to_signal("NameOwnerChanged", self._callback)
		#self.session_bus.add_signal_reciever(self._callback)#,LISTEN_NAME

	def init_player_list(self):
		for p in PLAYER_LIST:
			try: 
				mod = __import__(p)
				self.player_list.append(eval("mod."+p+"API(self.session_bus)"))
			except:
				self.dbg("WARNING > LOADING API > init_player_list(): Couldn't load "+p+" API")
		
	def fullupdate(self):
		self.dbg("GFX > UPDATE > FULL: fullupdate()")
		self.redraw_background_items()
		self.draw_player_buttons()
		self.redraw_canvas()

	def update(self):
		self.dbg("GFX > UPDATE: update()")
		self.redraw_canvas()
		#self.update_shape()
		return True
	
	def redraw_canvas (self):
		self.dbg("GFX > REDRAW: redraw_canvas()")
		if self.disable_updates:
			return
		if self.window:
			x, y, w, h = self.window.get_allocation()
			rect = gtk.gdk.Rectangle(x, y, w, h)
			if self.window.window:
				self.window.window.invalidate_rect(rect, True)
				self.window.window.process_updates(True)
	
	def draw_player_buttons(self):
		if self.__buffer_back and self.skin and self.skin.playercontrols_item and self.skin.playercontrols_item.categ == 'new':
			ctx_ns = self.__buffer_back.cairo_create()
			self.skin.playercontrols_item.set_transparency(self.skin.transparency)
			self.skin.playercontrols_item.set_scale(self.scale)
			self.skin.playercontrols_item.draw(ctx_ns)
	
	def check_for_players(self):
		gobject.idle_add(self.dbus_check_player)
		return True

	def dbus_check_player(self):
		#first check if the current player is running
		if self.player and self.player.is_active(self.dbus_iface, self.screenlet_settings):
			return

		# not running so cleaning the player data
		self.halt_API()
		
		if self.skin:
			# searching for running player
			self.dbg("\nCORE > PLAYER > Searching...")
			for i,player in enumerate(self.player_list):
				if player:
					self.dbg("CORE > PLAYER > Testing: "+str(player.__class__.__name__))
					if player.is_active(self.dbus_iface, self.screenlet_settings):
						self.dbg("CORE > PLAYER > Found: "+str(player.__class__.__name__)+"\n")
						# History function
						if self.history_traking:
							this_entry = 'INFO: Player ' + player.__class__.__name__ + ' is active...'
							if self.history_last_entry != this_entry:
								c_date = os.popen('printf "`date +' + "'" + self.history_time_format + "'" + '`"').read()
								os.system("echo '[" + c_date + "] " + this_entry + "' >> '" + self.history_file + "'")
								self.history_last_entry = this_entry
						if player:
							self.player = player
							self.player.connect(self.screenlet_settings)
							self.skin.set_player(self.player.__class__.__name__)
							self.get_info()
							self.dbg("CORE > PLAYER > Setting callbacks")
							self.player.callback_fn = None
							self.player.register_change_callback(self.get_info)
							self.set_player_callbacks()
							# Fade in
							if self.fade_in_on_player_start: self.screenlet_fadein('on startup')
							elif self.player.is_playing(): self.screenlet_fadein('on play')
							self.fullupdate()
							break

	def halt_API(self):
		if self.fade_out_on_no_player: self.screenlet_fadeout('on player')
		if self.player: up = True
		else: up = False
		self.player = False
		self.player_type = False
		self.playing = False
		self.cover_path = False
		self.unset_player_callbacks()
		if up:
			if self.skin: self.skin.set_player(_("No Player"))
			self.fullupdate()

	def check_playing(self):
		if self.player:
			if self.player.halt:
				self.player.halt = False
				self.halt_API()
			else:
				if self.player.is_active(self.dbus_iface, self.screenlet_settings):
					self.playing = self.player.is_playing()
					return self.playing
				else:
					self.dbus_check_player()
		self.playing = False
		return self.playing

	### Cover changing functions
	def change_cover_core(self):
		self.dbg("SKIN > COVER > CHANGE > CORE > change_cover_core()")
		if not self.fade:
			self.skin.set_albumcover(self.cover_pixbuf)
			if self.cover_path and os.path.exists(self.cover_path) and self.check_playing():
				if self.fade_all:
					self.skin.albumcover_item.transparency = 0
					self.fullupdate()
				else:
					self.cover_fadein()
			if self.waiting_cover_change:
				self.waiting_cover_change = gobject.source_remove(self.waiting_cover_change)
				self.waiting_cover_change = False
		return True

	def change_cover(self, pixbuf):
		self.dbg("SKIN > COVER > CHANGE > START > change_cover("+str(pixbuf)+")")
		if self.skin and self.skin.albumcover_item:
			if self.fade_enabled:
				if self.fade_all:
					self.skin.albumcover_item.transparency = 0
					self.skin.set_albumcover(pixbuf)
					self.fullupdate()
				else:
					self.cover_fadeout()
					self.cover_pixbuf = pixbuf
					if self.waiting_cover_change:
						self.waiting_cover_change = gobject.source_remove(self.waiting_cover_change)
						self.waiting_cover_change = False
					if self.cover_path and os.path.exists(self.cover_path):
						self.waiting_cover_change = gobject.timeout_add( self.fade_step_time, self.change_cover_core)
			else:
				self.skin.set_albumcover(pixbuf)
				self.skin.albumcover_item.transparency = 0
	
	def set_cover_cb(self, path):
		self.dbg("SKIN > COVER > SET > set_cover_cb("+str(path)+")")
		#print "\n\n last_cover_path"+str(self.last_cover_path)+"\n diferit de\n"+str(self.cover_path)+"\n\n" # FIXME
		if path and os.path.exists(str(path)):
			if self.actual_cover_path: self.actual_cover_path = None
			self.cover_path = path
			if self.skin and os.path.exists(ScreenletPath + '/themes/' + self.theme_name + '/cover_manip.sh'):
				th = ScreenletPath + '/themes/' + self.theme_name + '/'
				self.dbg("SKIN > COVER > Executing 'cover_manip.sh'")
				self.last_cover_path = self.cover_path
				os.system('cp --remove-destination "' + self.cover_path + '" "' + th + 'cover.png"')
				buff = os.popen('bash "' + th + 'cover_manip.sh"').read()
				if buff != '': dbg("COVER > SET > Output of the execution of cover_manip.sh script:\n"+str(buff)+"\n")
				if os.path.exists(th + 'cover.png'):
					self.actual_cover_path = self.cover_path
					self.cover_path = th + 'cover.png'
			pixbuf = gtk.gdk.pixbuf_new_from_file(self.cover_path)
			self.change_cover(pixbuf)
		elif path == None:
			if self.cover_path != path:
				self.cover_path = path
				self.actual_cover_path = None
				self.change_cover(None)
		else:
			self.dbg("WARNING: COVER > SET > set_cover_cb("+str(path)+"): tried to set invalid cover \""+str(path)+"\"")
			self.cover_path = None
			self.actual_cover_path = None

	def cover_update_cb(self):
		if self.__cover_timeout:
			gobject.source_remove(self.__cover_timeout)
		if self.coverEngine.isAlive():
			self.dbg('COVER FETCHER: still fetching')
			if self.still_fetching != True:
				if os.path.exists(ScreenletPath+'/themes/'+self.theme_name+'/fetching.png'):
					self.set_cover_cb(ScreenletPath+'/themes/'+self.theme_name+'/fetching.png')
				else: 
					self.set_cover_cb(ScreenletPath+'/UI/fetching.png')
			self.still_fetching = True
			self.__cover_timeout = gobject.timeout_add(200, self.cover_update_cb)
			return
		self.dbg("COVER FETCHER: Cover fetcher ended, update")
		self.still_fetching = False
		self.force_get_info()
		self.fullupdate()
		
	def correct_path(self, path):
		if path != '':
			if path[-1:] != '/':
				path = path+'/'
			path = os.path.expanduser(path)
			if os.path.exists(path) == True:
				return path
			else:
				return ''
		else:
			return ''
			
	def check_for_cover_path(self):
		if self.check_playing():	# check if cover is already stored on harddisk
			artist = self.player.get_artist()
			album = self.player.get_album()
			self.cover_path = ''
			if os.path.exists(self.correct_path(self.COVER_PATH)+artist+'-'+album+'.jpg'):
				self.cover_path = self.correct_path(self.COVER_PATH)+artist+'-'+album+'.jpg'
			if os.path.exists(self.correct_path(self.COVER_PATH)+artist+'-'+album+'.png'):
				self.cover_path = self.correct_path(self.COVER_PATH)+artist+'-'+album+'.png'
			if artist and album and self.correct_path(self.COVER_PATH) != '' and self.cover_path != '':
				self.dbg('COVER FETCHER: found cover on harddisk')
				self.still_fetching = False
				if self.__cover_timeout:
					gobject.source_remove(self.__cover_timeout)
				self.__num_times_cover_checked = 0
				self.set_cover_cb(self.cover_path)
				return True
			else:	# get cover from player API
				self.cover_path = self.player.get_cover_path()
				self.dbg("CORE > PLAYER API > GOT COVER:: " + self.cover_path)
				if self.cover_path and os.path.exists(self.cover_path):
					self.dbg('SKIN > COVER > Found cover from player API')
					self.still_fetching = False
					if self.__cover_timeout:
						gobject.source_remove(self.__cover_timeout)
					self.__num_times_cover_checked = 0
					self.set_cover_cb(self.cover_path)
					self.fullupdate()
					return True
				else:
					self.dbg("COVER FETCHER: lets try to search again to find local cover")
					if self.__num_times_cover_checked < self.__max_cover_path_searches:
						if self.__cover_timeout:
							gobject.source_remove(self.__cover_timeout)
						self.__num_times_cover_checked += 1
						self.__cover_timeout = gobject.timeout_add(self.__cover_check_interval * 1000, self.check_for_cover_path)
					else:	# get the cover from online fetcher
						if self.__last_played_album != album:
							self.__last_played_album = album
							self.__num_times_cover_checked_online = 0
						if self.__num_times_cover_checked_online < self.__max_cover_path_searches_online and self.correct_path(self.COVER_PATH) != '':
							if self.__cover_timeout:
								gobject.source_remove(self.__cover_timeout)
							self.__num_times_cover_checked_online += 1
							###self.__num_times_cover_checked = 0
							# Cannot get it from the Player, try to retreive it yourself
							artist = self.player.get_artist()
							album = self.player.get_album()
							if artist and album:
								self.still_fetching = False
								# Need to make this a thread
								self.screenlet_settings['cover_path'] = self.correct_path(self.COVER_PATH)
								self.coverEngine = NP_Fetcher.NP_Fetcher()
								self.coverEngine.initData(artist, album, self.screenlet_settings)
								self.coverEngine.start()
						#		if os.path.exists(self.correct_path(self.COVER_PATH)+artist+'-'+album+'.jpg'):
						#			self.cover_path = self.correct_path(self.COVER_PATH)+artist+'-'+album+'.jpg'
						#		if os.path.exists(self.correct_path(self.COVER_PATH)+artist+'-'+album+'.png'):
						#			self.cover_path = self.correct_path(self.COVER_PATH)+artist+'-'+album+'.png'
						#		self.set_cover_cb(self.cover_path)
								self.__cover_timeout = gobject.timeout_add(200, self.cover_update_cb)
					return False
		elif self.__cover_timeout:
			gobject.source_remove(self.__cover_timeout)
	
	def set_current_wallpaper(self):
		if self.wallpaper_active:
			buff = os.popen('gconftool-2 -g "/desktop/gnome/background/picture_filename"').read().split('\n')[0]
			if buff != self.wallpaper_path_current:
				self.dbg("WALLPAPER: setting wallpaper: "+self.wallpaper_path_current)
				os.system('gconftool-2 -t string -s "/desktop/gnome/background/picture_filename" "' + self.wallpaper_path_current + '"')
	
	def set_default_wallpaper(self):
		if self.wallpaper_active:
			buff = os.popen('gconftool-2 -g "/desktop/gnome/background/picture_filename"').read().split('\n')[0]
			if buff != self.wallpaper_path_default:
				self.dbg("WALLPAPER: setting default wallpaper: "+self.wallpaper_path_default)
				self.wallpaper_path_current = self.wallpaper_path_default
				os.system('gconftool-2 -t string -s "/desktop/gnome/background/picture_filename" "' + self.wallpaper_path_default + '"')
			
	def reset_last_known(self):
		self.last_artist = '<!NULL!>'
		self.last_album = '<!NULL!>'
		self.last_title = '<!NULL!>'
		self.last_cover_path = '<!NULL!>'
		self.last_theme = '<!NULL!>'
		self.last_path = '<!NULL!>'
		self.last_rating = '<!NULL!>'
		self.last_wallpaper_state = '<!NULL!>'
		self.last_history_state = '<!NULL!>'
		if self.skin:
			self.skin.set_rating(0)
			self.fullupdate()
				
	def force_get_info(self):
		self.dbg("CORE > PLAYER API > get_info() [FORCED]")
		self.force_getting_info = True
		self.get_info()
				
	def get_info(self):
		s = self.skin
		if s:
			try:
				if self.check_playing():
					x_artist = self.player.get_artist()
					x_title = self.player.get_title()
					x_album = self.player.get_album().replace('&amp;', '&')
					x_rating = self.player.get_rating()
					self.current_path = self.player.get_url_dir()
					
					if self.last_rating != x_rating:
						s.set_rating(x_rating)
						self.last_rating = x_rating
						self.fullupdate()
					
					if x_artist != self.last_artist or x_title != self.last_title or x_album != self.last_album or self.theme_name != self.last_theme or self.wallpaper_active != self.last_wallpaper_state or self.last_path != self.current_path or self.force_getting_info:
						self.dbg("CORE > PLAYER API > get_info()")
						s.set_player(self.player.__class__.__name__)
						s.set_title(x_title)
						s.set_artist(x_artist)
						s.set_album(x_album)
						self.player.preferred_cover = self.preferred_cover
					
						if self.wallpaper_active or self.history_traking:
							y_album = x_album.replace('\\','_').replace('/','_').replace('"','_').replace("'",'_').replace('[','_').replace(']','_')
							y_artist = x_artist.replace('\\','_').replace('/','_').replace('"','_').replace("'",'_').replace('[','_').replace(']','_')
							y_title = x_title.replace('\\','_').replace('/','_').replace('"','_').replace("'",'_').replace('[','_').replace(']','_')
					
						# Wallpaper function
						if self.wallpaper_active:
							z_album = y_album.replace('.', "\\.")
							z_artist = y_artist.replace('.', "\\.")
							# Check for album wallpaper
							if os.path.exists(self.wallpaper_path_album):
								buff = os.popen('ls -1 "' + self.wallpaper_path_album + '" | grep -i "' + z_album + '\."').read().split('\n')[0]
							else: buff = ''
							if buff != '' and x_album != '':
								self.wallpaper_path_current = self.wallpaper_path_album + '/' + buff
								self.set_current_wallpaper()
							else:
								# Check for artist wallpaper
								if os.path.exists(self.wallpaper_path_artist):
									buff = os.popen('ls -1 "' + self.wallpaper_path_artist + '" | grep -i "' + z_artist + '\."').read().split('\n')[0]
								else: buff = ''
								if buff != '' and x_artist != '':
									self.wallpaper_path_current = self.wallpaper_path_artist + '/' + buff
									self.set_current_wallpaper()
								else:
									# Set default wallpaper
									self.set_default_wallpaper()
									# Mark missing wallpaper for this artist
									if self.wallpaper_missing_active:
										os.system('echo "' + y_artist + '" >> "' + self.wallpaper_missing + '"')
										os.system('cat "' + self.wallpaper_missing + '" | sort -u -o "' + self.wallpaper_missing + '"')
						elif self.last_wallpaper_state == True:
							self.set_default_wallpaper()
					
						# History function
						if self.history_traking:
							this_entry = y_artist + " - " + y_title + " (" + y_album + ")"
							if this_entry != " -  ()" and this_entry != self.history_last_entry:
								c_date = os.popen('printf "`date +' + "'" + self.history_time_format + "'" + '`"').read()
								os.system("echo '[" + c_date + "] " + this_entry + "' >> '" + self.history_file + "'")
								self.history_last_entry = this_entry
					
						if not self.check_for_cover_path():
							self.set_cover_cb(None)
						if self.still_fetching != True:
							self.fullupdate()
							
						# Cover Copy function FIXME
						if self.cover_copy_active and self.cover_path != True and self.cover_path != False:
							if self.cover_copy_only_if_album and not x_album: foo = 0
							else:
								if self.current_path == 'NOT SUPPORTED':
									self.dbg("WARNING: "+self.player.__name__ + " doesn't support url grabbing so the Cover Copy function won't work.")
								elif os.path.exists(self.current_path):
									if self.cover_path and os.path.exists(self.cover_path):
										dest = self.current_path + "/" + self.cover_copy_image_name + "." + self.cover_copy_image_ext
										if self.cover_path != dest:
											if os.path.exists(dest):
												if self.cover_copy_replace_smaller:
													if os.path.exists('/usr/bin/identify'):
														src_size = os.popen("identify -format '%wx%h' '" + self.cover_path + "'").read().replace('\n','').split('x')
														dest_size = os.popen("identify -format '%wx%h' '" + dest + "'").read().replace('\n','').split('x')
														try:
															if src_size[0] > dest_size[0] or src_size[1] > dest_size[1]:
																os.system('convert "'+self.cover_path+'" "'+dest+'"')
																self.cover_path = dest
														except:
															self.dbg("ERROR > COVER COPY > get_info(): Shit happened while getting the images dimensions.")
													else:
														self.dbg("WARNING: Cover Copy:\n "+
															"You don't have the \'imagemagick\' package installed so the script won't be able to compare images dimensions.\n "+
															"For the ubuntu users this is the install command:\nsudo apt-get install imagemagick")
											else:
												if os.path.exists('/usr/bin/convert'):
													os.system('convert "'+self.cover_path+'" "'+dest+'"')
													self.cover_path = dest
												else:
													self.dbg("WARNING: Cover Copy:\n"+
														" You don't have the \'imagemagick\' package installed so the cover will be only copied and not converted to the required format.\n"+
														" For the ubuntu users this is the install command:\n"+
														"sudo apt-get install imagemagick")
													os.system('cp --remove-destination "'+self.cover_path+'" "'+dest+'"')
													self.cover_path = dest
										
										
											if self.cover_copy_remove_others and os.path.exists(dest):
												os.system('mv "'+dest+'" "'+dest+'.tmp"')
												os.system('rm -f "'+self.current_path+'"/*.jpg')
												os.system('rm -f "'+self.current_path+'"/*.JPG')
												os.system('rm -f "'+self.current_path+'"/*.jpeg')
												os.system('rm -f "'+self.current_path+'"/*.JPEG')
												os.system('rm -f "'+self.current_path+'"/*.png')
												os.system('rm -f "'+self.current_path+'"/*.PNG')
												os.system('rm -f "'+self.current_path+'"/*.gif')
												os.system('rm -f "'+self.current_path+'"/*.GIF')
												os.system('mv "'+dest+'.tmp" "'+dest+'" ')
								else:
									self.dbg("WARNING: Cover Copy: The directory path received does not exist:\nPATH: "+self.current_path)
						
						# Update last known values
						self.last_artist = x_artist
						self.last_album = x_album
						self.last_title = x_title
						self.last_theme = self.theme_name
						self.last_path = self.current_path
						self.last_wallpaper_state = self.wallpaper_active
						self.last_history_state = self.history_traking
						self.force_getting_info = False
						if self.fade_in_on_play: self.screenlet_fadein('on play')
				else:
					if self.fade_out_on_stop: self.screenlet_fadeout('on play')
					s.set_title("")
					s.set_artist("")
					s.set_album("")
					self.set_cover_cb(None)
					self.reset_last_known()
					# Set default wallpaper
					if self.wallpaper_active: self.set_default_wallpaper()
					self.fullupdate()
			except:
				# History function
				if self.history_traking:
					this_entry = 'INFO: Player exited'
					if self.history_last_entry != this_entry:
						c_date = os.popen('printf "`date +' + "'" + self.history_time_format + "'" + '`"').read()
						os.system("echo '[" + c_date + "] " + this_entry + "' >> '" + self.history_file + "'")
						self.history_last_entry = this_entry
				self.halt_API()
				self.dbg("\nCORE > get_info(): Player exited\n")
				# The player most probably exited. Invalidate the Player
				s.set_player("")
				s.set_title("")
				s.set_artist("")
				s.set_album("")
				self.set_cover_cb(None)
				self.reset_last_known()
				self.player = False
				# Set default wallpaper
				if self.wallpaper_active: self.set_default_wallpaper()
				self.fullupdate()


	def set_player_callbacks(self):
		if self.player and self.skin and self.skin.playercontrols_item:
			c = self.skin.playercontrols_item
			if c.prev_button:
				c.prev_button.set_callback_fn(self.player.previous)
			if c.play_pause_button:
				c.play_pause_button.set_callback_fn(self.play_pause_wrapped)
			if c.next_button:
				c.next_button.set_callback_fn(self.player.next)
			
	def play_pause_wrapped(self):
		if self.player:
			if self.skin and self.skin.playercontrols_item:
				c = self.skin.playercontrols_item
				image = "pause"
				playing = self.check_playing()
				if playing: image = "play"
				if not playing: image = "pause"
				c.set_images("play_pause", image)
			self.player.play_pause()
		
	def unset_player_callbacks(self):
		if self.player and self.skin and self.skin.playercontrols_item:
			c = self.skin.playercontrols_item
			if c.prev_button:
				c.prev_button.set_callback_fn(None)
			if c.play_pause_button:
				c.play_pause_button.set_callback_fn(None)
			if c.next_button:
				c.next_button.set_callback_fn(None)

	def on_draw(self, ctx):
		# Draw Non-Scrolling (not-regularly updated) Items from the Buffer
		if self.__buffer_back:
			ctx.set_operator(cairo.OPERATOR_OVER)
			ctx.set_source_pixmap(self.__buffer_back, 0, 0)
			if self.fade_enabled and self.skin:
				if self.skin.transparency < 0: self.skin.transparency = 0
				elif self.skin.transparency > 1: self.skin.transparency = 1
				self.dbg("GFX > DRAW > on_draw > skin.transparency = " + str(self.skin.transparency))
				ctx.paint_with_alpha(1-self.skin.transparency)
			else:
				ctx.paint()
				self.dbg("GFX > DRAW > on_draw")

		# set scale rel. to scale-attribute
		ctx.scale(self.scale, self.scale)
		# Draw Items that need regular updates (like scrolling text)
		playing = False
		if self.player and self.player.is_playing(): playing = True 
		if self.theme and self.skin:

			needUpdates = False
			for item in self.skin.items:
				try:
					if item.regular_updates: # Only draw items here that require regular updates
						if playing and item.display=="on-stopped": pass
						elif not playing and item.display=="on-playing": pass
						else: 
							# Need items to be updated - Set a timeout
							needUpdates = True
							try:
								item.set_transparency(self.skin.transparency)
							except:
								self.dbg('WARNING > SKIN > ITEM (Type='+item.type+') > Got no "set_transparency(float)" function or something went wrong.')
							item.draw(ctx)
				except:
					continue

			if self.__scroll_timeout:
				gobject.source_remove(self.__scroll_timeout)
			if needUpdates:
				self.__scroll_timeout = gobject.timeout_add(int(self.scroll_interval), self.update)

	def on_draw_shape(self, ctx):
		ctx.scale(self.scale, self.scale)
		ctx.set_source_rgba(1,1,1,1)
		ctx.rectangle(0,0,self.width,self.height)
		ctx.paint()

	def close(self):
		if self.__timeout:
			gobject.source_remove(self.__timeout)
		if self.__cover_timeout:
			gobject.source_remove(self.__cover_timeout)
		screenlets.Screenlet.close(self)
			
	def on_mouse_enter (self, event):
		self.dbg("MOUSE > ENTERED WINDOW")
		if self.fade_on_hover: self.screenlet_fadein('on hover')
		
	def on_mouse_leave (self, event):
		self.dbg("MOUSE > LEFT WINDOW")
		if self.fade_on_hover: self.screenlet_fadeout('on hover')
		if self.skin and self.skin.playercontrols_item:
			nf = False
			if self.skin.playercontrols_item.categ == "new":
				self.mousex = self.mousey = -1
				self.skin.playercontrols_item.set_all_normal()
				nf = True
			if self.skin.rating_item:
				self.mousex = self.mousey = -1
				self.skin.rating_item.set_all_normal()
				nf = True
			if nf: self.fullupdate()

	def on_unfocus (self, event):
		self.dbg("WINDOW > UNFOCUSED")
		if self.skin:
			mark = False
			if self.skin.playercontrols_item and self.skin.playercontrols_item.need_update(self.mousex*self.scale, self.mousey*self.scale, 0): mark = True
			if self.skin.rating_item and self.skin.rating_item.need_update(self.mousex*self.scale, self.mousey*self.scale, 0): mark = True
			if mark: self.fullupdate()

	### Button clicked
	def on_mouse_down(self, event):
		self.dbg("MOUSE > PRESS: "+str(int(event.x))+"x"+str(int(event.y)))
		if self.skin and self.skin.playercontrols_item and self.player:
			cc = self.skin.playercontrols_item
			if event.button == 1:
				if cc.prev_button and cc.prev_button.mouse_over(event.x, event.y):					cc.prev_button.mouse_down()
				elif cc.play_pause_button and cc.play_pause_button.mouse_over(event.x, event.y):	cc.play_pause_button.mouse_down()
				elif cc.next_button and cc.next_button.mouse_over(event.x, event.y):				cc.next_button.mouse_down()
			if cc.mouse_over(event.x, event.y):
				self.fullupdate()
		return False
		
	### Button released > Apply action
	def on_mouse_up(self, event):
		self.dbg("MOUSE > RELEASE: "+str(int(event.x))+"x"+str(int(event.y)))
		if self.skin and self.player:
			mark_update = False
			if self.skin.playercontrols_item:
				cc = self.skin.playercontrols_item
				if event.button == 1:
					if cc.prev_button and cc.prev_button.mouse_over(event.x, event.y):
						cc.prev_button.mouse_up()
						self.player.previous()
					elif cc.play_pause_button and cc.play_pause_button.mouse_over(event.x, event.y):
						cc.play_pause_button.mouse_up()
						self.player.play_pause()
					elif cc.next_button and cc.next_button.mouse_over(event.x, event.y):
						cc.next_button.mouse_up()
						self.player.next()
				elif event.button == 2:
					self.player.vol_mute()
				if cc.need_update(event.x, event.y, event.button) or cc.mouse_over(event.x, event.y): mark_update = True
			if self.skin.rating_item:
				if event.button == 1:
					rr = self.skin.rating_item.mouse_up(event.x, event.y, event.button)
					if rr:
						if not self.player.set_rating(rr) and self.player.rating_only_get:
							self.GUI_msg('Scr_Nam_Ver', self.player.__name__+_(" can't set the rating value."))
						else:
							self.skin.set_rating(rr)
						mark_update = True
			#if mark_update and not self.on_mouse_move(event): self.fullupdate()
			if mark_update: self.fullupdate()
		return False
		
	### Buttons hover
	def on_mouse_move(self, event):
		self.dbg("MOUSE > MOVE: "+str(int(event.x))+"x"+str(int(event.y)))
		if self.skin:
			mark = False
			if self.skin.playercontrols_item and self.skin.playercontrols_item.need_update(event.x, event.y, 0):	mark = True
			if self.skin.rating_item and self.skin.rating_item.need_update(event.x, event.y, 0):					mark = True
			if mark: self.fullupdate()
			return mark
		
	### Set player controls transparency
	def set_controls_transparency(self, value):
		if self.skin:
			if self.skin.playercontrols_item:	self.skin.playercontrols_item.set_transparency(value)
			if self.skin.rating_item:			self.skin.rating_item.set_transparency(value)

	### Screenlet Fade functions
	def screenlet_fadeout_core(self):
		self.dbg("GFX > FADE > OUT > SCREENLET > CORE: screenlet_fadeout_core()")
		ret = True
		if self.fade_enabled and self.skin:
			self.skin.transparency += self.fade_step
			if self.skin.transparency >= 1: ret = False
			self.set_controls_transparency(self.skin.transparency)
		else: ret = False
		mark = False
		if self.skin:
			if self.skin.playercontrols_item and self.skin.playercontrols_item.categ == "new": mark = True
			elif self.skin.rating_item: mark = True
		if mark:	self.fullupdate()
		else:		self.update()
		if not ret:
			self.fade_all = gobject.source_remove(self.fade_all)
			self.fade_all = False
			self.last_fade = "out"
		return ret
		
	def screenlet_fadein_core(self):
		self.dbg("GFX > FADE > IN > SCREENLET > CORE: screenlet_fadein_core()")
		ret = True
		if self.fade_enabled and self.skin:
			self.skin.transparency -= self.fade_step
			if self.skin.transparency <= 0: ret = False
			self.set_controls_transparency(self.skin.transparency)
		else: ret = False
		mark = False
		if self.skin:
			if self.skin.playercontrols_item and self.skin.playercontrols_item.categ == "new": mark = True
			elif self.skin.rating_item: mark = True
		if mark:	self.fullupdate()
		else:		self.update()
		if not ret:
			self.fade_all = gobject.source_remove(self.fade_all)
			self.fade_all = False
			self.last_fade = "in"
		return ret
		
	def screenlet_fadeout(self, act=""):
		self.dbg("GFX > FADE > OUT > SCREENLET > START: screenlet_fadeout("+act+")")
		if self.fade_enabled and self.skin:
			if self.fade_all:
				self.fade_all = gobject.source_remove(self.fade_all)
				self.fade_all = False
			if self.skin.transparency < 1:
				self.fade_all = gobject.timeout_add( self.fade_step_time, self.screenlet_fadeout_core)
		
	def screenlet_fadein(self, act=""):
		self.dbg("GFX > FADE > IN > SCREENLET > START: screenlet_fadein("+act+")")
		if self.fade_enabled and self.skin:
			if self.fade_all:
				self.fade_all = gobject.source_remove(self.fade_all)
				self.fade_all = False
			if self.skin.transparency > 0:
				self.fade_all = gobject.timeout_add( self.fade_step_time, self.screenlet_fadein_core)
		
	### Cover Fade functions
	def cover_fadeout_core(self):
		self.dbg("GFX > FADE > OUT > COVER > CORE: cover_fadeout_core()")
		ret = True
		if self.skin and self.skin.albumcover_item:
			self.skin.albumcover_item.fading = True
			self.skin.albumcover_item.transparency += self.fade_step
			if self.skin.albumcover_item.transparency >= 1: ret = False
		self.fullupdate()
		if not ret:
			if self.fade:
				self.fade = gobject.source_remove(self.fade)
				self.fade = False
		return ret
		
	def cover_fadein_core(self):
		self.dbg("GFX > FADE > IN > COVER > CORE: cover_fadein_core()")
		ret = True
		if self.skin and self.skin.albumcover_item:
			it = self.skin.albumcover_item
			it.fading = True
			it.transparency -= self.fade_step
			if it.transparency <= 0 or it.transparency <= it.transparency_orig: ret = False
		self.fullupdate()
		if not ret:
			if self.fade:
				self.fade = gobject.source_remove(self.fade)
				self.fade = False
		return ret
		
	def cover_fadeout(self):
		self.dbg("GFX > FADE > OUT > COVER > START: cover_fadeout()")
		if self.fade_enabled and self.skin and self.skin.albumcover_item and self.skin.albumcover_item.transparency < 1:
			if self.fade:
				self.fade = gobject.source_remove(self.fade)
				self.fade = False
#			if self.skin.albumcover_item.transparency < 1:
			self.fade = gobject.timeout_add( self.fade_step_time, self.cover_fadeout_core)
		
	def cover_fadein(self):
		self.dbg("GFX > FADE > IN > COVER > START: cover_fadein()")
		if self.fade_enabled and self.skin and self.skin.albumcover_item and self.skin.albumcover_item.transparency > 0:
			if self.fade:
				self.fade = gobject.source_remove(self.fade)
				self.fade = False
#			if self.skin.albumcover_item.transparency > 0:
			self.fade = gobject.timeout_add( self.fade_step_time, self.cover_fadein_core)
			
	### Function used to display GUI messages
	def GUI_msg(self, title, text):
		if title == 'Scr_Nam_Ver': title = self.__name__+" v."+self.__version__
		self.dbg("GUI MESSAGE:\n "+title+":\n "+text+"\n")
		# Try Notify-Send
		if os.path.exists("/usr/bin/notify-send"):
			os.system('notify-send -i "'+ScreenletPath+'/icon.svg" "'+title+'" "'+text+'" &')
		# Try Zenity
		elif os.path.exists("/usr/bin/zenity"):
			os.system('zenity --info --title="'+title+'" --text="'+text+'" &')
		# Try gtk MessageDialog
		else:
			try:
				md = gtk.MessageDialog(None, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK)
				md.set_title(title)
				md.set_markup(text)
				md.run()
				md.destroy()
			except:
				self.dbg("ERROR > GUI MESSAGE: Shit happened while trying to display gtk.MessageDialog")
				
	def on_scroll_up (self):
		if self.player: self.player.vol_up()

	def on_scroll_down (self):
		if self.player: self.player.vol_down()
	
	### Display debug text
	def dbg(self, text):
		text = str(text)
		if text.find("ERROR > ") != -1:
			print "\n"+text
			print sys.exc_value
			traceback.print_exc(file=sys.stdout)
			print
		elif text.find("WARNING > ") != -1:
			print "\n"+text+"\n        > "+str(sys.exc_value)+"\n"
		elif text.find("WARNING: ") != -1:
			print "\n"+text+"\n"
		elif self.debugging_enabled:
			print text
		pass
	
        
# If the program is runned directly or passed as an argument to the python
# interpreter then create a Screenlet instance and show it
if __name__ == "__main__":
	import screenlets.session
	screenlets.session.create_session(NowPlayingScreenlet)

