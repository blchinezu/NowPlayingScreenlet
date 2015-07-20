#!/usr/bin/env python

# Licensed under the GPL

import urllib2, urllib


class NP_Fetcher_Lastfm():
	__name__ = 'CoverFetcherLastFM'
	__version__ = '0.3.3'
	__author__ = 'Alexibaba'
	__desc__ = 'Fetching albumcover online'

	def __init__(self, artist, album, dest_filename, key):
		self.artist = artist
		self.album = album
		self.dest_filename = dest_filename
		self.ident_key = key
		self.download_image_to_filename()


	def download_image_to_filename(self): 
		self.artist = urllib.quote(self.artist)
		self.album = urllib.quote(self.album)

		search_url = "http://ws.audioscrobbler.com/2.0/?method=album.getInfo&artist=" \
								+ self.artist \
								+ "&album="\
								+ self.album \
								+ "&api_key=" \
								+ self.ident_key

		try:
			request = urllib2.Request(search_url)
			opener = urllib2.build_opener()
			f = opener.open(request).read()
			curr_pos = 100    # Skip header..
			curr_pos = f.find("<image size=\"large\">", curr_pos+5)
			url_start = f.find("http://", curr_pos)
			url_end = f.find("</image>", curr_pos)
			img_url = f[url_start:url_end]

			if img_url[-3:] == 'png':
				self.dest_filename = self.dest_filename[:-3]+'png'
			try:
				webFile = urllib.urlopen(img_url)
				localFile = open(self.dest_filename, 'w')
				localFile.write(webFile.read())
				webFile.close()
				localFile.close()
				print 'found cover (LastFM)'
				return True
			except IOError:
				print 'no cover (LastFM)'
				return False

		except:
			print 'no cover (LastFM)'
			return False



