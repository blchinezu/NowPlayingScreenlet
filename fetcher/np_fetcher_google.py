#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the GPL

# Do NOT use this, it could be against current law!

import urllib2, urllib


class NP_Fetcher_Google():
	__name__ = 'CoverFetcherGoogle'
	__version__ = '0.3.3'
	__author__ = 'Alexibaba'
	__desc__ = 'Fetching albumcover online'

	def __init__(self, artist, album, dest_filename):
		self.artist = artist
		self.album = album
		self.dest_filename = dest_filename
		self.download_image_to_filename()

	def getTheCode(self, url):
		try:
			request = urllib2.Request(url)
			opener = urllib2.build_opener()
			f = opener.open(request).read()
			return f
		except:
			return ''

	def getMediumSizeUrl(self):
		url_medium = self.search_url+'&hl=de&imgsz=m'
		f = self.getTheCode(url_medium)
		if f != '':
			try:
				curr_pos = 5    # Skip header..
				curr_pos = f.find('width=23%', curr_pos)
				url_start = f.find('href=', curr_pos)+len('href=')
				url_end = f.find('><img src=', curr_pos)+len('><img src=')-10
				url_medium_back = f[url_start:url_end]
				##print url_medium_back
				return url_medium_back
			except:
				return ''
		else:
			return ''

	def getAllSizeUrl(self):
		url_all = self.search_url
		f = self.getTheCode(url_all)
		if f != '':
			try:
				curr_pos = 5    # Skip header..
				curr_pos = f.find('width=23%', curr_pos)
				url_start = f.find('href=', curr_pos)+len('href=')
				url_end = f.find('><img src=', curr_pos)+len('><img src=')-10
				url_all_back = f[url_start:url_end]
				##print url_all_back
				return url_all_back
			except:
				return ''
		else:
			return ''



	def download_image_to_filename(self): 
		self.artist = urllib.quote(self.artist)
		self.album = urllib.quote(self.album)
		self.query = '%22'+self.album+'%22+%22'+self.artist+'%22+album+jpg'
		self.query = self.query.replace(" ","+")
		self.search_url = "http://anonymouse.org/cgi-bin/anon-www_de.cgi/http://images.google.de/images?q=" \
									+ self.query

		## At first search the image in medium size
		response_url = self.getMediumSizeUrl()
		if response_url == '':
			response_url = self.getAllSizeUrl()
		if response_url == '':
			print 'no cover (Google)'
			return False
		else:
			f = self.getTheCode(response_url)
			if f == '':
				print 'no cover (Google)'
				return False
			else:
				curr_pos = 20    # Skip header..
				curr_pos = f.find('zu den Bildergebnissen', curr_pos)
				url_start = f.find('href=', curr_pos)+len('href=')+1
				url_end = f.find('.jpg', curr_pos)+len('.jpg')
				img_url = f[url_start:url_end]
				#print img_url
				try:
					webFile = urllib.urlopen(img_url)
					localFile = open(self.dest_filename, 'w')
					localFile.write(webFile.read())
					webFile.close()
					localFile.close()
					print 'found cover (Google)'
					return True
				except IOError:
					print 'no cover (Google)'
					return False


