#!/usr/bin/env python

# Licensed under the GPL

import urllib2, urllib
import gzip
import cStringIO 

class NP_Fetcher_Discogs():
	__name__ = 'CoverFetcherDiscogs'
	__version__ = '0.3.3'
	__author__ = 'Alexibaba'
	__desc__ = 'Fetching albumcover online'

	def __init__(self, artist, album, dest_filename, key):
		self.artist = artist
		self.album = album
		self.dest_filename = dest_filename
		self.ident_key = key
		self.download_image_to_filename()

	def getXml(self, url):
		request = urllib2.Request(url)
		request.add_header('Accept-Encoding', 'gzip')
		try:
				response = urllib2.urlopen(request)
				data = response.read()
				return gzip.GzipFile(fileobj = cStringIO.StringIO(data)).read()
		except urllib2.HTTPError, e:
				error = 'Ooops. An error occured :( '
		return False


	def download_image_to_filename(self): 
		self.artist = urllib.quote(self.artist)
		self.album = urllib.quote(self.album)

		search_url = "http://www.discogs.com/search?type=all&q=" \
								+ self.artist \
								+ "%20-%20"\
								+ self.album \
								+ "&f=xml&api_key=" \
								+ self.ident_key

		try:
			f = self.getXml(search_url)
			curr_pos = 5    # Skip header..
			curr_pos = f.find('<uri>', curr_pos+10)
			release_start = f.find('release/', curr_pos)+len('release/')
			release_end = f.find('</uri>', curr_pos)
			release = f[release_start:release_end]
		except:
			print 'no cover (Discogs)'
			return False
		

		release_url = "http://www.discogs.com/release/" \
								+ release \
								+ "?f=xml&api_key="\
								+ self.ident_key


		try:
			g = self.getXml(release_url)
			curr_pos = 5    # Skip header..
			curr_pos = g.find('<image', curr_pos+15)
			url_start = g.find('uri=', curr_pos)+len('uri=')+1
			url_end = g.find(' uri150=', curr_pos)-1
			img_url = g[url_start:url_end]

			if img_url[-3:] == 'png':
				self.dest_filename = self.dest_filename[:-3]+'png'

			try:
				webFile = urllib.urlopen(img_url)
				localFile = open(self.dest_filename, 'w')
				localFile.write(webFile.read())
				webFile.close()
				localFile.close()
				print 'found cover (Discogs)'
				return True
			except IOError:
				print 'no cover (Discogs)'
				return False

		except:
			print 'no cover (Discogs)'
			return False

