#!/usr/bin/env python

# Licensed under the GPL

import urllib2, urllib


class NP_Fetcher_Amazon():
	__name__ = 'CoverFetcherAmazon'
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
		try:
			self.artist = urllib.quote(self.artist.encode('latin1'))
			self.album = urllib.quote(self.album.encode('latin1'))
		except:
			self.artist = urllib.quote(self.artist)
			self.album = urllib.quote(self.album)

		search_url = "http://free.apisigning.com/onca/xml?Service=AWSECommerceService&AWSAccessKeyId=" \
								+ self.ident_key \
								+ "&Operation=ItemSearch&SearchIndex=Music&Artist="\
								+ self.artist \
								+ "&ResponseGroup=Images&Keywords=" \
								+ self.album

		try:
			request = urllib2.Request(search_url)
			opener = urllib2.build_opener()
			f = opener.open(request).read()
			curr_pos = 100    # Skip header..
			curr_pos = f.find("<LargeImage>", curr_pos+10)
			url_start = f.find("<URL>http://", curr_pos)+len("<URL>")
			url_end = f.find("</URL>", curr_pos)
			img_url = f[url_start:url_end]

			if img_url[-3:] == 'png':
				self.dest_filename = self.dest_filename[:-3]+'png'

			try:
				webFile = urllib.urlopen(img_url)
				localFile = open(self.dest_filename, 'w')
				localFile.write(webFile.read())
				webFile.close()
				localFile.close()
				print 'found cover (Amazon)'
				return True
			except IOError:
				print 'no cover (Amazon)'
				return False

		except:
			print 'no cover (Amazon)'
			return False


