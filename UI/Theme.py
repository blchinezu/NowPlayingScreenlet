import pango
import cairo
try:
	import rsvg
except:
	print "\n * You don't have the python-rsvg bindings installed!\n"
import gtk
import screenlets
import cairo
import string
import xml.dom.minidom
import gobject


# Generic fade variables
class FadeModule:
	transparency_orig = 0
	transparency = 0
	can_fade = True
	fading = False
	scale = 1
	draw_buffer = None

	
# The Main Skin Class
# It parses the xml and creates various UI items
class Skin(FadeModule):
	items = []
	width = 500
	height = 200
	name = ""
	
	playername_item = False
	albumcover_item = False
	titlename_item = False
	artistname_item = False
	albumname_item = False
	playercontrols_item = False
	rating_item = False
	
	def __init__(self, xmlfile, obj):
		self.parseSkinXML(xmlfile, obj.theme, obj.window, obj.player)
		self.fade_enabled = obj.fade_enabled
	
	def add_item(self, item):
		self.items.append(item)
	
	def cleanup(self):
		self.items[:] = []
		if self.playercontrols_item: 
			t = self.playercontrols_item
			t.remove_old()
			try:
				t.window.remove(t.window.get_child())
			except:
				pass

	def set_scale(self, scale):
		if self.scale != scale:
			self.scale = scale
			for item in self.items:
				try:
					item.set_scale(scale)
				except:
					pass

	def set_title(self, text):
		if self.titlename_item: self.titlename_item.set_text(text)

	def set_artist(self, text):
		if self.artistname_item: self.artistname_item.set_text(text)

	def set_album(self, text):
		if self.albumname_item: self.albumname_item.set_text(text)

	def set_player(self, text):
		if self.playername_item: 
			if not text: text = ""
			self.playername_item.set_text(text[:text.find("API")].replace('_',' '))

	def set_albumcover(self, pixbuf):
		if self.albumcover_item: self.albumcover_item.set_image(pixbuf)
		
	def set_rating(self, value):
		if self.rating_item: self.rating_item.set_rating(value)

	def parseSkinXML(self, filename, theme, window, player):
		dom = xml.dom.minidom.parse(filename)
		skinobj = dom.getElementsByTagName("skin")[0]
		self.name = skinobj.getAttribute("name")
		self.width = int(skinobj.getAttribute("width"))
		self.height = int(skinobj.getAttribute("height"))
		for domitem in skinobj.childNodes:
			if domitem.nodeType == 1:
				type = domitem.nodeName
				try:
					x = int(domitem.getAttribute("x"))
				except:
					x = 0
				try:
					y = int(domitem.getAttribute("y"))
				except:
					y = 0
				try:
					w = int(domitem.getAttribute("width"))
				except:
					w = 0
				try:
					h = int(domitem.getAttribute("height"))
				except:
					h = 0
				display = domitem.getAttribute("display")
				transparency = domitem.getAttribute("transparency")
				if transparency:
					transparency = float(transparency)
					if transparency < 0: transparency = 0
					elif transparency > 1: transparency = 1
				else: transparency = 0
				
				item = False
				### General Image
				if type == "image":
					src = theme[domitem.getAttribute("src")]
					item = ImageItem(src, x, y, w, h, display, transparency)
				### Album cover
				elif type == "albumcover":
					item = ImageItem(None, x, y, w, h, display, transparency)
					self.albumcover_item = item
					item.categ = "cover"
					item.transparency = 1
				### Text object
				elif type in ("titlename", "artistname", "albumname", "playername"):
					font = domitem.getAttribute("font")
					color = domitem.getAttribute("color")
					shadowcolor = domitem.getAttribute("shadowcolor")
					align = domitem.getAttribute("align")
					maxchars = domitem.getAttribute("maxchars")
					direction = domitem.getAttribute("direction")
					scrollstr = domitem.getAttribute("scroll")
					scroll = False
					if scrollstr and (scrollstr=="1" or string.lower(scrollstr)=="true"):
						scroll = True
					item = TextItem("", font, color, x, y, scroll, display, shadowcolor, 
											  maxchars, align, direction, w, h)
					exec "self."+type+"_item = item"
				### Rating object [Group Creation]
				elif type == 'ratinggroup':
					basename = domitem.getAttribute("basename")
					if not basename: basename = 'star'
					item = Rating(player, theme, basename, x, y, w, h, transparency, display, 'group')
					self.rating_item = item
				### Rating object [Separate Creation]
				elif type == 'rating':
					if not self.rating_item:
						basename = domitem.getAttribute("basename")
						if not basename: basename = 'star'
						item = Rating(player, theme, basename, x, y, w, h, transparency, display, 'separated')
						for controlitem in domitem.childNodes:
							if controlitem.nodeType == 1: 
								try:
									rx = int(controlitem.getAttribute("x"))
								except:
									rx = x
								try:
									ry = int(controlitem.getAttribute("y"))
								except:
									ry = y
								try:
									rw = int(controlitem.getAttribute("width"))
								except:
									rw = w
								try:
									rh = int(controlitem.getAttribute("height"))
								except:
									rh = h
								rt = domitem.getAttribute("transparency")
								if rt:
									rt = float(rt)
									if rt < 0: rt = 0
									elif rt > 1: rt = 1
								else: rt = transparency
								bn = domitem.getAttribute("basename")
								if not bn: bn = basename
								star_nr = int(str(controlitem.nodeName).replace('star',''))
								item.add_star(star_nr,rx,ry,rw,rh,rt,bn)
						self.rating_item = item
					else:
						print "\nWARNING > SKIN > You can't use <ratinggroup> and <rating> at the same time in a skin.\n"
				### Buttons [OLD method]
				elif type == "playercontrols":
					xd = float(x)/self.width
					yd = float(y)/self.height
					spacing = domitem.getAttribute("spacing")
					item = PlayerControls(int(spacing), xd, yd, theme, window, player, display)
					for controlitem in domitem.childNodes:
						if controlitem.nodeType == 1: 
							cw = controlitem.getAttribute("width")
							ch = controlitem.getAttribute("height")
							ctype = controlitem.nodeName
							eval("item.add_%s(%s,%s)" %(ctype,cw,ch))
					self.playercontrols_item = item
				### Buttons
				elif type == "buttons":
					item = NewPlayerControls(player, theme)
					for controlitem in domitem.childNodes:
						if controlitem.nodeType == 1: 
							try:
								cx = int(controlitem.getAttribute("x"))
							except:
								cx = 0
							try:
								cy = int(controlitem.getAttribute("y"))
							except:
								cy = 0
							cw = controlitem.getAttribute("width")
							if not cw: cw = 0
							ch = controlitem.getAttribute("height")
							if not ch: ch = 0
							try:
								ct = float(controlitem.getAttribute("transparency"))
							except:
								ct = 0
							ctype = controlitem.nodeName
							eval("item.add_%s(%s,%s,%s,%s,%s)" %(ctype,cx,cy,cw,ch,ct))
					self.playercontrols_item = item
				if item: self.items.append(item)
	
	
	
	
### Generic UI class ### XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
class GenericItem(FadeModule):
	type = ""
	categ = ""
	x = 0
	y = 0
	width = 0
	height = 0
	x_orig = 0
	y_orig = 0
	width_orig = 0
	height_orig = 0
	display = True
	regular_updates = False

	def __init__(self, type, x, y, w, h, display, transparency):
		self.type = type
		self.x = x
		self.y = y
		self.width = w
		self.height = h
		self.x_orig = x
		self.y_orig = y
		self.width_orig = w
		self.height_orig = h
		self.transparency = transparency
		self.transparency_orig = transparency
		if display: self.display = display

	def draw(self, ctx):
		pass




### Image object ### XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
class ImageItem(GenericItem):
	imgobj = None
	image_type = None

	def __init__(self, imgobj, x, y, w, h, display, transparency):
		GenericItem.__init__(self, "image", x, y, w, h, display, transparency)
		self.set_image(imgobj)

	def set_image(self, imgobj):
		self.imgobj = imgobj
		cl = imgobj.__class__.__name__
		mod = imgobj.__class__.__module__
		if cl=='Handle': self.image_type = "rsvg"
		elif cl=='ImageSurface': self.image_type = "surface"
		elif cl=='Pixbuf': self.image_type = "pixbuf"
		else: self.image_type = None

	def set_scale(self, scale):
		if self.categ == 'button' and self.scale != scale:
			self.scale = scale
			self.x = self.x_orig * scale
			self.y = self.y_orig * scale
			self.width = self.width_orig * scale
			self.height = self.height_orig * scale

	def draw(self, ctx):
		# Check for the type of the image object (rsvg, surface, pixbuf)
		# Draw accordingly
		if self.imgobj != None:
			if self.transparency < 0:   					self.transparency = 0
			elif self.transparency > 1:						self.transparency = 1
			if self.transparency < self.transparency_orig:	self.transparency = self.transparency_orig
			#print " * " + self.categ + " " + self.type + ": draw(x="+str(self.x)+", y="+str(self.y)+", w="+str(self.width)+", h="+str(self.height)+", transparency="+str(self.transparency)+")"
			if self.image_type == "rsvg":
				size=self.imgobj.get_dimension_data()
				if size:
					# Copy the svg to a cairo surface
					if not self.width: self.width = size[0]
					if not self.height: self.height = size[1]
					png_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
					ctx_tmp = cairo.Context(png_surface)
					self.imgobj.render_cairo(ctx_tmp)
					# Draw the new surface
					pattern = cairo.SurfacePattern(png_surface)
					matrix = cairo.Matrix()
					if self.width and self.height:
						iw = float(size[2])
						ih = float(size[3])
						matrix.scale(iw/self.width, ih/self.height)
					matrix.translate(-self.x, -self.y)
					pattern.set_matrix(matrix)
					ctx.set_source(pattern)
					if self.can_fade: ctx.paint_with_alpha(1-self.transparency)
					else: ctx.paint()
			elif self.image_type == "surface":
				# Draw cairo surface
				pattern = cairo.SurfacePattern(self.imgobj)
				matrix = cairo.Matrix()
				if self.width and self.height:
					iw = float(self.imgobj.get_width())
					ih = float(self.imgobj.get_height())
					matrix.scale(iw/self.width, ih/self.height)
				matrix.translate(-self.x, -self.y)
				pattern.set_matrix(matrix)
				ctx.set_source(pattern)
				if self.can_fade: ctx.paint_with_alpha(1-self.transparency)
				else: ctx.paint()
			elif self.image_type == "pixbuf":
				# Draw pixbuf
				ctx.save()
				pw = float(self.imgobj.get_width())
				ph = float(self.imgobj.get_height())
				ctx.translate(self.x, self.y)
				pixscaled = self.imgobj
				if self.width and self.height:
					pixscaled = self.imgobj.scale_simple(self.width,self.height,1)
				ctx.set_source_pixbuf(pixscaled, 0, 0)
				if self.can_fade: ctx.paint_with_alpha(1-self.transparency)
				else: ctx.paint()
				ctx.restore()




### Text object ### XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
class TextItem(GenericItem):
	font = "Sans 10"
	text = ""
	align = ""
	color = (0,0,0,1)
	shadowcolor = False
	shadowcolor_transparency_orig = 0
	rotation = False
	layout = 0

	maxchars = False
	scroll_desired = False
	scrolling = False
	cur_index = 0
	scroll_wait = 10
	scrollfiller = "     "

	def __init__(self, text, font, color, x, y, scroll_desired=False, display="", 
					shadowcolor="", maxchars="", align="left", 
					direction = "", w=0, h=0):
		GenericItem.__init__(self, "text", x, y, w, h, display, 0)
		if font: self.font = font
		if color: self.color = self.get_rgba(color)
		if shadowcolor: self.shadowcolor = self.get_rgba(shadowcolor)
		if maxchars: self.maxchars = int(maxchars)
		if direction: self.rotation = self.get_rotation_from_direction(direction)
		self.scroll_desired = scroll_desired
		self.align = align
		self.set_text(text)
		if color:	tr = 1-int(color[7:9], 16)/255.0
		else:		tr = 0
		self.transparency_orig = tr
		self.set_transparency(tr)
		if shadowcolor:	self.shadowcolor_transparency_orig = 1-int(shadowcolor[7:9], 16)/255.0
	
	def set_transparency(self, value):
		if value < 0: value = 0
		elif value > 1: value = 1
		if self.color:
			modvalue = value
			if modvalue < self.transparency_orig: modvalue = self.transparency_orig
			self.transparency = modvalue
			self.color=(self.color[0],self.color[1],self.color[2],1-modvalue)
		if self.shadowcolor:
			modvalue = value
			if modvalue < self.shadowcolor_transparency_orig: modvalue = self.shadowcolor_transparency_orig
			self.shadowcolor=(self.shadowcolor[0],self.shadowcolor[1],self.shadowcolor[2],1-modvalue)
		
	def set_text(self, text):
		self.cur_index = 0
		self.scrolling = False
		self.regular_updates = False
		if self.maxchars and len(text) > self.maxchars:
			if self.scroll_desired:
				self.regular_updates=True
				self.scrolling = True
			else:
				text = text[0:self.maxchars]+"..."
		self.text = text
	
	def draw(self, ctx):
		# Do some Pango Magic here
		# Draw Shadow Text
		text = self.text
		if self.scrolling:
			if self.cur_index > self.scroll_wait:
				text = self.text + self.scrollfiller + self.text
				tmp = self.cur_index - self.scroll_wait
				text = text[tmp:(tmp+ self.maxchars)]
			text = text[0:self.maxchars]
			self.cur_index += 1
			if self.cur_index == len(self.text+self.scrollfiller)+self.scroll_wait: self.cur_index = 0
		ctx.save()
		if self.shadowcolor: 
			self.draw_text(ctx, text, self.shadowcolor, self.x+1, self.y+1)
		self.draw_text(ctx, text, self.color, self.x, self.y)
		ctx.restore()
	
	def draw_text(self, ctx, text, c, x, y):
		ctx.save()
		p_layout = ctx.create_layout()
		p_fdesc = pango.FontDescription(self.font)
		p_layout.set_font_description(p_fdesc)
		p_layout.set_text(text)
		# Clip Pixel Region
		self.set_clip_region(ctx, p_layout, x, y)
		if text: 
			(x,y) = self.get_xy_from_alignment(p_layout, x, y)
		ctx.move_to(x,y)
		if self.rotation:
			ctx.translate(-x,-y)
			ctx.rotate(self.rotation)
		ctx.set_source_rgba(c[0],c[1],c[2],c[3])
		ctx.show_layout(p_layout)
		ctx.restore()

	def get_extents(self, p_layout):
		(extents, lextents) = p_layout.get_pixel_extents()
		return extents

	def get_xy_from_alignment(self, p_layout, x, y):
		if not self.width: return (x, y)
		extents = self.get_extents(p_layout)
		fw = extents[2]+extents[0]
		fh = extents[3]+extents[1]
		if self.align == "left":
			pass
		elif self.align == "center":
			if self.layout==0:
				x = x + self.width/2.0 - fw/2.0
			elif self.layout==1:
				y = y - self.width/2.0 + fw/2.0
			elif self.layout==2:
				x = x - self.width/2.0 + fw/2.0
			elif self.layout==3:
				y = y + self.width/2.0 - fw/2.0
		elif self.align == "right":
			if self.layout==0:
				x = x + self.width - fw
			elif self.layout==1:
				y = y - self.width + fw
			elif self.layout==2:
				x = x - self.width + fw
			elif self.layout==3:
				y = y + self.width - fw
		return (x, y)

	def set_clip_region(self, ctx, p_layout, x, y):
		extents = self.get_extents(p_layout)
		fw = extents[2]+extents[0]
		fh = extents[3]+extents[1]
		if self.width:
			if self.layout == 0:
				ctx.rectangle(x, y, self.width, fh)
			if self.layout == 1:
				ctx.rectangle(x, y-self.width, fh, self.width)
			if self.layout == 2:
				ctx.rectangle(x-self.width, y-fh, self.width, fh)
			if self.layout == 3:
				ctx.rectangle(x-fh, y, fh, self.width)
			ctx.clip()

	def get_rgba(self, color):
		return (
			int(color[1:3], 16)/255.0,
			int(color[3:5], 16)/255.0,
			int(color[5:7], 16)/255.0,
			int(color[7:9], 16)/255.0
		)

	def get_rotation_from_direction(self, dir):
		PI = 3.141596
		if dir == "left-right":
			self.layout = 0
			return 0
		elif dir == "down-up":
			self.layout = 1
			return -PI*0.5
		elif dir == "right-left":
			self.layout = 2
			return PI
		elif dir == "up-down":
			self.layout = 3
			return PI*0.5
		return False




### The rating buttons classes ### XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
class Star(GenericItem):
	image = image_empty = image_half = image_full = None
	star_is = star_hover_is = 'empty'

	callbackfn = None

	def __init__(self, x, y, w, h, transparency):
		GenericItem.__init__(self, "star", int(x), int(y), int(w), int(h), True, transparency)
        
	def set_callback_fn(self, fn):
		self.callbackfn = fn
	
	def set_images(self, empty, half, full):
		self.image_empty = ImageItem(empty, self.x, self.y, self.width, self.height, self.display, self.transparency)
		self.image_half = ImageItem(half, self.x, self.y, self.width, self.height, self.display, self.transparency)
		self.image_full = ImageItem(full, self.x, self.y, self.width, self.height, self.display, self.transparency)
		self.image_empty.categ = self.image_half.categ = self.image_full.categ = "star"
		self.image = self.image_empty

	def set_transparency(self, value):
		if value < 0: value = 0
		elif value > 1: value = 1
		if value < self.transparency_orig: value  = self.transparency_orig
		self.transparency = value
		if self.image: self.image.transparency = value
		
	def mouse_off(self):
		if self.star_is == 'empty':		self.image = self.image_empty
		elif self.star_is == 'half':	self.image = self.image_half
		elif self.star_is == 'full':	self.image = self.image_full
		self.star_hover_is = 'empty'
		
	def make(self, mode):
		self.star_is = str(mode)
		exec "self.image = self.image_"+str(mode)
		
	def make_hover(self, mode):
		self.star_hover_is = str(mode)
		exec "self.image = self.image_"+str(mode)
		
	def mouse_over(self, mx, my):
		if mx >= self.x and mx < self.x + self.width and my >= self.y and my < self.y + self.height:
			if mx < self.x + (self.width/2): return 'First Half'
			else: return 'Second Half'
		else: return False
	
	def set_scale(self, scale):
		if self.scale != scale:
			self.scale = scale
			self.x=self.x_orig*scale
			self.y=self.y_orig*scale
			self.width=self.width_orig*scale
			self.height=self.height_orig*scale
			self.image_empty.set_scale(scale)
			self.image_half.set_scale(scale)
			self.image_full.set_scale(scale)
	
	def need_update(self, mx, my, bt):
		mo = self.mouse_over(mx, my)
		if mo == 'First Half' and self.star_hover_is != 'half':		return 'Hover Half'
		elif mo == 'Second Half' and self.star_hover_is != 'full':	return 'Hover Full'
		elif not mo and self.star_hover_is != 'empty':				return 'Mouse Off'
		return False

	def draw(self, ctx):
		if self.image:
			#print "THEME > Star Button > draw() > transp = " + str(self.transparency)
			self.set_transparency(self.transparency)
			self.image.draw(ctx)
		else:
			#print "THEME > Star Button > COULD NOT draw(): No image object to draw"
			pass


class Rating(GenericItem):
	type = "rating"
	categ = None
	player = None
	theme = None
	rating = 'None' # When set to none the rating stars are not displayed
	basename = None
	star = [5,None,None,None,None,None]
	
	def __init__(self, player, theme, bn, x, y, w, h, t, display, categ):
		self.player = player
		self.theme = theme
		self.basename = bn
		self.categ = categ
		if not display: display = 'on-playing'
		GenericItem.__init__(self, "rating", x, y, w, h, display, t)
		if categ == 'group':
			mw = w/self.star[0]
			i = 1
			while i <= self.star[0]:
				self.add_star(i, x+(mw*(i-1)), y, mw, h, t, bn)
				i += 1
	
	def set_images(self, star_nr, img):
		try:
			img = str(img)
			self.star[star_nr].set_images(self.theme[img+'-empty.png'], self.theme[img+'-half.png'], self.theme[img+'-full.png'])
		except:
			pass
			
	def add_star(self, star_nr, x, y, w, h, t, basename):
		if star_nr >= 1 and star_nr <= self.star[0]:
			go = False
#			if self.star[star_nr]: 
#				tmp = self.star[star_nr]
#				x = tmp.x_orig
#				y = tmp.x_orig
#				w = tmp.width_orig
#				h = tmp.height_orig
#				t = tmp.transparency_orig
#				fn = tmp.callbackfn
#				go = True
			self.star[star_nr] = Star(x, y, w, h, t)
			self.set_images(star_nr, basename)
#			if go:
#				self.star[star_nr].set_callback_fn(fn)
#				tmp.destroy()
		else:
			print 'WARNING: THEME > RATING > add_star(): Star number out of range: '+str(star_nr)+' [min=1 | max='+str(self.star[0])+']'

	def set_rating(self, value):
		if value != 'None':
			if value >= 0 and value <= 5:
				self.rating = value
				self.make_range('full', 1, int(value))
				if int(value) < value:
					if value - int(value) >= 0.5:
						self.make_range('half', int(value)+1, int(value)+1)
					else:
						self.make_range('empty', int(value)+1, int(value)+1)
					self.make_range('empty', int(value)+2, self.star[0])
				else:
					self.make_range('empty', int(value)+1, self.star[0])
			else:
				print "WARNING: THEME > RATING > set_rating(): Rating out of range: "+str(value)+" (min=0 / max="+str(self.star[0])+")"
		else:
			self.rating = 'None'

	def set_all_normal(self):
		i = 1
		while i <= self.star[0]:
			if self.star[i]: self.star[i].mouse_off()
			i += 1

	def set_scale(self, scale):
		if self.scale != scale:
			self.scale = scale
			i = 1
			while i <= self.star[0]:
				if self.star[i] and self.star[i].scale != scale: self.star[i].set_scale(scale)
				i += 1

	def set_transparency(self, value):
		if value < 0: value = 0
		elif value > 1: value = 1
		if value < self.transparency_orig: value  = self.transparency_orig
		self.transparency = value
		i = 1
		while i <= self.star[0]:
			if self.star[i]: self.star[i].set_transparency(value)
			i += 1
		
	def make_range(self, mode, start, stop):
		if start >= 1 and start <= self.star[0] and stop >= 1 and stop <= self.star[0] and start <= stop:
			i = start
			while i <= stop:
				if self.star[i]: self.star[i].make(mode)
				i += 1
		
	def make_hover_range(self, mode, start, stop):
		if start >= 1 and start <= self.star[0] and stop >= 1 and stop <= self.star[0] and start <= stop:
			i = start
			while i <= stop:
				if self.star[i]: self.star[i].make_hover(mode)
				i += 1
		
	def mouse_over(self, mx, my):
		if self.rating != 'None':
			i = 1
			while i <= self.star[0]:
				if self.star[i] and self.star[i].mouse_over(mx, my): return True
				i += 1
		return False

	def mouse_up(self, mx, my, mb):
		if self.rating != 'None':
			i = 1
			while i <= self.star[0]:
				if self.star[i]:
					t = self.star[i].mouse_over(mx, my)
					if t == 'First Half':		return float(i)-0.5
					elif t == 'Second Half':	return float(i)
				i += 1
		return False

	def need_update(self, mx, my, mb):
		ret = hover = off = False
		if self.rating != 'None':
			if self.player and self.rating != self.player.rating:
				self.rating = self.player.rating
				ret = True
			i = 1
			tn = None
			while i <= self.star[0]:
				if self.star[i]:
					t = self.star[i].need_update(mx, my, mb)
					if t == 'Hover Half':
						self.make_hover_range('empty', i+1, self.star[0])
						self.make_hover_range('full', 1, i-1)
						self.make_hover_range('half', i, i)
						hover = True
					elif t == 'Hover Full':
						self.make_hover_range('empty', i+1, self.star[0])
						self.make_hover_range('full', 1, i)
						hover = True
					elif t == 'Mouse Off':
						if tn and i > tn: self.make_hover_range('empty', i, i)
						off = True
					elif self.star[i].mouse_over(mx, my): tn = i
					if hover or off: ret = True
				i += 1
			if off and not hover and not self.mouse_over(mx, my): self.set_all_normal()
		return ret

	def draw(self, ctx):
		#print "\nTHEME > RATING ("+self.categ+") > draw() > transp = " + str(self.transparency)
		if self.rating != 'None':
			self.set_transparency(self.transparency)
			i = 1
			while i <= self.star[0]:
				if self.star[i]: self.star[i].draw(ctx)
				i += 1
			
			


### The new button classes ### XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
class NewPlayerButton(GenericItem):
	image = None
	image_normal = None
	image_hover = None
	image_pressed = None

	callbackfn = None

	def __init__(self, x, y, w, h, transparency):
		GenericItem.__init__(self, "button", x, y, w, h, True, transparency)
        
	def set_callback_fn(self, fn):
		self.callbackfn = fn
	
	def set_images(self, image_normal, image_hover, image_pressed):
		self.image = ImageItem(image_normal, self.x, self.y, self.width, self.height, self.display, self.transparency)
		self.image_normal = self.image
		self.image_hover = ImageItem(image_hover, self.x, self.y, self.width, self.height, self.display, self.transparency)
		self.image_pressed = ImageItem(image_pressed, self.x, self.y, self.width, self.height, self.display, self.transparency)
		self.image.categ = self.image_normal.categ = self.image_hover.categ = self.image_pressed.categ = "button"

	def set_transparency(self, value):
		if value < 0: value = 0
		elif value > 1: value = 1
		if value < self.transparency_orig: value  = self.transparency_orig
		self.transparency = value
		if self.image: self.image.transparency = value
		
	def mouse_down(self):
		self.image = self.image_pressed

	def mouse_up(self):
		self.image = self.image_hover

	def mouse_off(self):
		self.image = self.image_normal
		
	def mouse_over(self, mx, my):
		if mx >= self.x and mx < self.x + self.width and my >= self.y and my < self.y + self.height: return True
		else: return False
	
	def set_scale(self, scale):
		if self.scale != scale:
			self.scale = scale
			self.x=self.x_orig*scale
			self.y=self.y_orig*scale
			self.width=self.width_orig*scale
			self.height=self.height_orig*scale
			self.image_normal.set_scale(scale)
			self.image_hover.set_scale(scale)
			self.image_pressed.set_scale(scale)
	
	def need_update(self, mx, my, bt):
		mo = self.mouse_over(mx, my)
		if mo and self.image == self.image_normal:
			self.image = self.image_hover
			return True
		elif not mo and self.image != self.image_normal:
			self.image = self.image_normal
			return True
		return False

	def draw(self, ctx):
		if self.image:
			#print "THEME > NEW-PlayerButton > draw() > transp = " + str(self.transparency)
			self.set_transparency(self.transparency)
			self.image.draw(ctx)
		else:
			#print "THEME > NEW-PlayerButton > COULD NOT draw(): No image object to draw"
			pass


class NewPlayerControls(GenericItem):
	type = "playercontrols"
	categ = "new"
	player = None
	theme = None

	prev_button = play_pause_button = next_button = False
	
	def __init__(self, player, theme):
		self.player = player
		self.theme = theme
		pass
	
	def set_images(self, btnimg, img):
		try:
			#print "\n"+btnimg+" > "+img+"\n"
			eval("self.%s_button.set_images(self.theme['%s.png'], self.theme['%s-hover.png'], self.theme['%s-pressed.png'])" %(btnimg, img, img, img))
		except:
			#print "\n * Shit happened: Theme > PlayerControls > set_images\n"
			pass
			
	def add_prev(self, x, y, w, h, t):
		go = False
		if self.prev_button: 
			tmp = self.prev_button
			x = tmp.x_orig
			y = tmp.x_orig
			w = tmp.width_orig
			h = tmp.height_orig
			t = tmp.transparency_orig
			fn = tmp.callbackfn
			go = True
		self.prev_button=NewPlayerButton(x, y, w, h, t)
		self.set_images("prev", "prev")
		if go:
			self.prev_button.set_callback_fn(fn)
			tmp.destroy()

	def add_play_pause(self, x, y, w, h, t):
		go = False
		if self.play_pause_button: 
			tmp = self.play_pause_button
			x = tmp.x_orig
			y = tmp.x_orig
			w = tmp.width_orig
			h = tmp.height_orig
			t = tmp.transparency_orig
			fn = tmp.callbackfn
			go = True
		self.play_pause_button=NewPlayerButton(x, y, w, h, t)
		image = "play"
		if self.player and self.player.is_playing(): image = "pause"
		self.set_images("play_pause", image)
		if go:
			self.play_pause_button.set_callback_fn(fn)
			tmp.destroy()

	def add_next(self, x, y, w, h, t):
		go = False
		if self.next_button: 
			tmp = self.next_button
			x = tmp.x_orig
			y = tmp.x_orig
			w = tmp.width_orig
			h = tmp.height_orig
			t = tmp.transparency_orig
			fn = tmp.callbackfn
			go = True
		self.next_button=NewPlayerButton(x, y, w, h, t)
		self.set_images("next", "next")
		if go:
			self.next_button.set_callback_fn(fn)
			tmp.destroy()

	def remove_old(self):
		pass

	def set_all_normal(self):
		if self.prev_button:		self.prev_button.mouse_off()
		if self.play_pause_button:	self.play_pause_button.mouse_off()
		if self.next_button:		self.next_button.mouse_off()
		

	def set_scale(self, scale):
		if self.scale != scale:
			self.scale = scale
			if self.prev_button and self.prev_button.scale != scale:				self.prev_button.set_scale(scale)
			if self.play_pause_button and self.play_pause_button.scale != scale:	self.play_pause_button.set_scale(scale)
			if self.next_button and self.next_button.scale != scale:				self.next_button.set_scale(scale)

	def set_transparency(self, value):
		if value < 0: value = 0
		elif value > 1: value = 1
		if value < self.transparency_orig: value  = self.transparency_orig
		self.transparency = value
		if self.prev_button:		self.prev_button.set_transparency(value)
		if self.play_pause_button:	self.play_pause_button.set_transparency(value)
		if self.next_button:		self.next_button.set_transparency(value)
		
	def mouse_over(self, mx, my):
		if self.prev_button and self.prev_button.mouse_over(mx, my):				return 'prev'
		if self.play_pause_button and self.play_pause_button.mouse_over(mx, my):	return 'play_pause'
		if self.next_button and self.next_button.mouse_over(mx, my):				return 'next'
		return False

	def need_update(self, mx, my, mb):
		ret = False
		if self.prev_button and self.prev_button.need_update(mx, my, mb):				ret = True
		if self.play_pause_button and self.play_pause_button.need_update(mx, my, mb):	ret = True
		if self.next_button and self.next_button.need_update(mx, my, mb):				ret = True
		return ret

	def draw(self, ctx):
		#print "THEME > NEW-PlayerControls > draw() > transp = " + str(self.transparency)
		self.set_transparency(self.transparency)
		if self.prev_button:		self.prev_button.draw(ctx)
		if self.play_pause_button:	self.play_pause_button.draw(ctx)
		if self.next_button:		self.next_button.draw(ctx)




### Old button classes (kept for old skins compatibility) ### XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
class PlayerButton(screenlets.ShapedWidget, FadeModule):
	width = 20
	height = 20

	image = None
	image_normal = None
	image_hover = None
	image_pressed = None

	callbackfn = None

	def __init__(self, w, h):
		super(PlayerButton, self).__init__(w,h)
		self.width = w
		self.height = h
        
	def set_callback_fn(self, fn):
		self.callbackfn = fn
	
	def set_images(self, image_normal, image_hover, image_pressed):
		self.image = image_normal
		self.image_normal = image_normal
		self.image_hover = image_hover
		self.image_pressed = image_pressed

	def button_press(self, widget, event):
		if event.button==1:
			self.image = self.image_pressed
			self.queue_draw()
		return True

	def button_release(self, widget, event):
		if event.button==1:
			self.image = self.image_normal
			self.queue_draw()
			if(self.callbackfn != None): self.callbackfn()
		return False

	def enter_notify(self, widget, event):
		self.image = self.image_hover
		self.queue_draw()
		#print "mouse enter"

	def leave_notify(self, widget, event):
		self.image = self.image_normal
		self.queue_draw()
		#print "mouse leave"
			
	def mouse_over(self, mx, my):
		return False
			
	def draw(self, ctx):
		if(self.image != None):
			iw = float(self.image.get_width())
			ih = float(self.image.get_height())
			matrix = cairo.Matrix(xx=iw/self.width, yy=ih/self.height)
			pattern = cairo.SurfacePattern(self.image)
			pattern.set_matrix(matrix)
			ctx.move_to(0,0)
			ctx.set_source(pattern)
			if self.can_fade: ctx.paint_with_alpha(1-self.transparency)
			else: ctx.paint()
			#print "THEME > PlayerButton > draw() > transp = "+str(self.transparency)


class PlayerControls(FadeModule):
	type = "playercontrols"
	categ = "old"

	box = False
	window = False
	theme = False
	player = False
	
	prev_button = False
	play_pause_button = False
	next_button = False
	
	display = True
	dims = [0,0,0,0,0,0] # prev width, prev height, play_pause width ....
	
	def __init__(self, spacing, xratio, yratio, theme, window, player, display, w=0, h=0):
		self.box = gtk.HBox(spacing=spacing)
		alignment = gtk.Alignment(xalign=xratio, yalign=yratio)
		alignment.add(self.box)
		self.theme = theme
		self.window = window
		self.player = player
		self.window.add(alignment)
		if display: self.display = display
	
	def set_images(self, btnimg, img):
		try:
			eval("self.%s_button.set_images(self.theme['%s.png'], self.theme['%s-hover.png'], self.theme['%s-pressed.png'])" %(btnimg, img, img, img))
		except:
			#print "\n * Shit happened: Theme > PlayerControls > set_images\n"
			pass
			
	def add_prev(self, w, h):
		self.add_prev_t(w, h)
		self.dims[0]=w; self.dims[1]=h
		self.window.show_all()

	def add_prev_t(self, w, h):
		self.prev_button=PlayerButton(w,h)
		self.set_images("prev", "prev")
		self.box.add(self.prev_button)
	
	def add_play_pause(self, w, h):
		self.add_play_pause_t(w, h)
		self.dims[2]=w; self.dims[3]=h
		self.window.show_all()

	def add_play_pause_t(self, w, h):
		self.play_pause_button=PlayerButton(w,h)
		image = "play"
		if self.player and self.player.is_playing(): image = "pause"
		self.set_images("play_pause", image)
		self.box.add(self.play_pause_button)
	
	def add_next(self, w, h):
		self.add_next_t(w, h)
		self.dims[4]=w; self.dims[5]=h
		self.window.show_all()

	def add_next_t(self, w, h):
		self.next_button=PlayerButton(w,h)
		self.set_images("next", "next")
		self.box.add(self.next_button)

	def remove_old(self):
		if self.box:
			for oldwidget in self.box.get_children(): 
				self.box.remove(oldwidget)

	def set_scale(self, scale):
		self.scale = scale
		self.remove_old()
		b = self.dims
		if self.prev_button: 
			tmp = self.prev_button
			fn = tmp.callbackfn
			self.add_prev_t(int(b[0]*scale), int(b[1]*scale))
			self.prev_button.set_callback_fn(fn)
			tmp.destroy()
		if self.play_pause_button: 
			self.play_pause_button.scale = scale
			tmp = self.play_pause_button
			fn = tmp.callbackfn
			self.add_play_pause_t(int(b[2]*scale), int(b[3]*scale))
			self.play_pause_button.set_callback_fn(fn)
			tmp.destroy()
		if self.next_button: 
			self.next_button.scale = scale
			tmp = self.next_button
			fn = tmp.callbackfn
			self.add_next_t(int(b[4]*scale), int(b[5]*scale))
			self.next_button.set_callback_fn(fn)
			tmp.destroy()
		self.window.show_all()

	def set_transparency(self, value):
		if value < 0: value = 0
		elif value > 1: value = 1
		if value < self.transparency_orig: value  = self.transparency_orig
		self.transparency = value
		if self.prev_button:		self.prev_button.transparency = value
		if self.play_pause_button:	self.play_pause_button.transparency = value
		if self.next_button:		self.next_button.transparency = value
		
	def need_update(self, mx, my, mb):
		return False
	def mouse_over(self, mx, my):
		return False

	def draw(self, ctx):
		#print "THEME > PlayerControls > draw()"
		if self.transparency < 0:   self.transparency = 0
		elif self.transparency > 1:	self.transparency = 1
		if self.prev_button:
			self.prev_button.transparency = self.transparency
		if self.play_pause_button:
			self.play_pause_button.transparency = self.transparency
		if self.next_button:
			self.next_button.transparency = self.transparency
		self.window.show_all()


