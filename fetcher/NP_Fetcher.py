#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  NP_Fetcher
#  - Version 0.3.3
#  - Created by Alexibaba
#
# INFO:
# - fetches albumart from different online services 
# 
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.



import os
import threading
import time
from np_fetcher_lastfm import NP_Fetcher_Lastfm
from np_fetcher_amazon import NP_Fetcher_Amazon
from np_fetcher_discogs import NP_Fetcher_Discogs
#from np_fetcher_google import NP_Fetcher_Google


lastfm_done = False
amazon_done = False
discogs_done = False
#google_done = False





class NP_Fetcher(threading.Thread):
	__name__ = 'NP_Fetcher'
	__version__ = '0.3.4.0'
	__author__ = 'Alexibaba, modified by BruceLee'
	__desc__ = 'Fetching albumcover from online sources'
	#artist = ""
	#album = ""

	def __init__(self):
		threading.Thread.__init__(self)

	def initData(self, artist, album, screenlet_settings):
		self.artist = artist.encode("utf-8")
		self.album = album.encode("utf-8")
		self.dest_filename = screenlet_settings['cover_path']+self.artist+'-'+self.album+'.jpg'
		self.lastfm_done = lastfm_done
		self.amazon_done = amazon_done
		self.discogs_done = discogs_done
		#self.google_done = google_done

		self.key_amazon = screenlet_settings['key_amazon']
		if screenlet_settings['key_lastfm'] != '':
			self.key_lastfm = screenlet_settings['key_lastfm']
		else:
			self.key_lastfm = 'ad81082a9a0cde30cc437a39321b7870'
		if screenlet_settings['key_discogs'] != '':
			self.key_discogs = screenlet_settings['key_discogs']
		else:
			self.key_discogs = '5930244593'
		print 'Trying to fetch cover'

	def replaceChar(self, word):
		word = word.replace("%20"," ")
		word = word.replace("%C3%84","Ä")
		word = word.replace("%C3%96","Ö")
		word = word.replace("%C3%9C","Ü")
		word = word.replace("%C3%A4","ä")
		word = word.replace("%C3%B6","ö")
		word = word.replace("%C3%BC","ü")
		#word = word.replace("&amp;","&")
		return word

	def fileExists(self):
		if os.path.exists(self.dest_filename) == True:
			return True
		if os.path.exists(self.dest_filename[:-3]+'png') == True:	
			self.dest_filename = self.dest_filename[:-3]+'png'
			return True
		else:
			return False

	def startFetching(self):
		if self.fileExists() != True:
			self.artist = self.replaceChar(self.artist)
			self.album = self.replaceChar(self.album)

			if self.lastfm_done == False and self.key_lastfm != '' and self.fileExists() != True:
				NP_Fetcher_Lastfm(self.artist, self.album, self.dest_filename, self.key_lastfm)
				self. lastfm_done = True
				self.startFetching()

			if self.amazon_done == False and self.key_amazon != '' and self.fileExists() != True:
				NP_Fetcher_Amazon(self.artist, self.album, self.dest_filename, self.key_amazon)
				self. amazon_done = True
				self.startFetching()

			if self.discogs_done == False and self.key_discogs != '' and self.fileExists() != True:
				NP_Fetcher_Discogs(self.artist, self.album, self.dest_filename, self.key_discogs)
				self.discogs_done = True
				self.startFetching()

			## Do NOT use the following lines, they could be against current law!
			#if self.google_done == False and self.fileExists() != True:
			#	NP_Fetcher_Google(self.artist, self.album, self.dest_filename)
			#	self.google_done = True
			#	self.startFetching()
			
		else:
			x=os.stat(self.dest_filename)
			if x.st_size == 0:
				print 'error while downloading'
				os.remove(self.dest_filename)
			else:
				print 'Cover has been fetched'


	def run ( self ):
		self.startFetching()

