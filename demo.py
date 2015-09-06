#!/usr/bin/env python
# $Id: demo.py,v 1.6 2001/06/01 06:12:16 kevint Exp $
# This file is to serve as example code.  Do whatever you like with it!
#  -- Kevin Turner <acapnotic@users.sourceforge.net>

"""Demonstrations of Perlin noise, in 1 through 4 dimensions."""

import perlin
import pygame, pygame.draw, pygame.font, pygame.surfarray
from pygame.locals import *
from OpenGL.GL import *
from Numeric import *
import re

#import peterlin

class DancingLine:
    def __init__(self,surface, noise_array):
	self.surface = surface
	self.array = noise_array

	(self.length, self.max_t) = shape(noise_array)

	self.t = 0

	h = surface.get_height()
	num_points = min(self.length, h)
	self.whys = map(lambda a,h=h,n=num_points: int(round(a * float(h)/n)),
			range(num_points))

    def next(self):
	self.t = (self.t + 1) % (self.max_t-1)

    def draw(self):
	points = self.array[:,self.t]
	num_points = min(self.length, self.surface.get_height())
	w = self.surface.get_width()
	self.surface.fill(0)
	ekses = map(lambda a, w=w: ((a-128)/140.0 + 0.5) * w, points[:num_points])

	pygame.draw.lines(self.surface, 128, 0, zip(ekses,self.whys))


def load_palette(name='Firecode'):
    """Loads a palette file and returns a list suitable for Surface.setpalette()

    Loads a palette file, which is anything that looks like this:

    0 0 0
    0 0  4
    0 64 8
    ...

    GIMP and Fractint palette files both match this description.
    Lines that don't match are silently ignored.
    Only recognizes decimal values, not 0xFF or #AA66FF.
    """

    f = open(name)
    pal = []
    rgb_re = re.compile('^(?:\s+)?(\d+)\s+(\d+)\s+(\d+)')
    for l in f.readlines():
	m = rgb_re.search(l)
	if m:
	    pal.append(tuple(map(int,m.groups())))

    if len(pal) != 256:
	print "Warning: palette \'%s\' does not contain 256 entries." % name
    if pal[0] != (0,0,0):
	print "Warning: palette \'%s\' has entry 0 set to non-black color"\
	      % name, pal[0]
    return pal

def demo():
    pygame.init()

    surface = pygame.display.set_mode((640,480), HWPALETTE | DOUBLEBUF, 8)

    surface.set_palette(load_palette())

    #perlin_palette(surface)
    demo1D(surface)
    demo2D(surface)

def perlin_palette(surface):
    """Generates a palette with Perlin noise.

    Right now the results"""
    surface.fill(0)

    palette=zeros((256,3))

    palette[255] = (0xFF, 0xFF, 0xFF)

    font = pygame.font.Font(None, 36)

    text = font.render("generating palette", 0, (0xFF,) * 3, (0,) *3)

    text_rect = Rect(text.get_size(),(0,0))

    text_rect.right = (639)

    text.convert()

    surface.blit(text, text_rect)

    oh64 = (0,) * 64
    reds = zip(range(64),oh64,oh64)
    greens = zip(oh64,range(64),oh64)
    blues = zip(oh64,oh64,range(64))

    i = 0
    for c in range(64):
	palette[i] = reds[c]
	palette[i+1] = greens[c]
	palette[i+2] = blues[c]
	i += 3

    surface.set_palette(palette)

    y0 = 240
    i = 0
    for c in range(64):
	for chan in range(3):
	    pygame.draw.line(surface,i,(chan*24+8, c + y0),(chan*24+24, c+y0))
	    i += 1

    h_noise = perlin.PerlinNoise((32,),perlin.ease_interpolation)
    s_noise = perlin.PerlinNoise((32,),perlin.ease_interpolation)
    v_noise = perlin.PerlinNoise((32,),perlin.ease_interpolation)

    gray_vector = array((1,1,1))
    row = 0
    res = 72.0
    (h_res,s_res,v_res) = (36.0, 36.0, 72.0)
    for i in range(1,256):
	h = math.acos(h_noise.value_at(i/h_res))
	s = s_noise.value_at(i/s_res)
	v = i * (1 + v_noise.value_at(i/v_res) / 8)

	rgb = gray_vector * v + s

	r = red_noise.value_at((i/res,)) * 128 + 128
	g = green_noise.value_at(((i+res/3)/res,)) * 128 + 128
	b =  blue_noise.value_at(((i+(res*2)/3)/res,)) * 128 + 128

	palette[i] = (r,g,b)
	surface.set_palette(palette)

	if (i % 3) == 0:
	    pygame.draw.line(surface, i, (8, row + y0),(72,row+y0))
	    pygame.display.update(8, row+y0, 64, 1)
	    row += 1

    pygame.display.flip()
    pygame.time.delay(5000)


########
#
# 1D
#
# Colour points on a line
# Colour a lamp over time
# 1-D displacement of an image
# As a time index for an animation
# spreading ripples on water?

def demo1D(surface):
    width = 32
    resolution = 20

    noise = perlin.PerlinNoise((width,),perlin.ease_interpolation)

    subsurface = surface.subsurface((0,0,width*resolution,32))
    varray = zeros((width*resolution,))

    for x in range(width * resolution):
	nx = x / float(resolution)
	value = noise.value_at((nx,))

	value = int(value * 128 + 128.5)
	if value < 0:
	    value = 0
	elif value > 255:
	    value = 255

	varray[x] = value

	# Color line
	pygame.draw.line(subsurface,value,(x,0),(x,31))
	surface.set_at((x,32+value/4), 128)
	pygame.display.update(x,0,1,31)

    pygame.display.flip()
    # Color lamp:

    lamp_rect = Rect(0,0,96,32)
    lamp_rect.bottom = 479
    lamp_rect.right = 639

    c = 0
    while 1:
	c = (c + 1) % (width * resolution)
	surface.fill(varray[c],lamp_rect)

	pygame.display.update(lamp_rect)
	pygame.time.delay(50)

    pygame.time.delay(5000)

def demo2D(surface):
    width = 16
    height = 12
    resolution = 12

    noise = perlin.PerlinNoise((width,height),perlin.ease_interpolation)

    subsurface = surface.subsurface(((0,0),(width*resolution,height*resolution)))
    surfarray = pygame.surfarray.array2d(subsurface)

    for y in range(height * resolution):
	for x in range(width * resolution):
	    nx = x / float(resolution)
	    ny = y / float(resolution)
	    value = noise.value_at((nx,ny))

	    value = int(value * 128 + 128.5)
	    if value < 0:
		value = 0
	    elif value > 255:
		value = 255
	    surfarray[x,y] = value

	pygame.surfarray.blit_array(subsurface, surfarray)
	# pygame.display.flip()
	pygame.display.update(0,y, width * resolution, 1)

    pygame.display.flip()

    dlrect = Rect(0,0,300,480)
    dlrect.right = 639

    dline = DancingLine(surface.subsurface(dlrect), surfarray)

    while pygame.event.poll().type not in (QUIT, MOUSEBUTTONDOWN):
	dline.next()
	dline.draw()

	pygame.display.update(dlrect)
	pygame.time.delay(100)
	pass


def draw_histogram(histogram, surface):
    hkeys = histogram.keys()
    hkeys.sort()
    low = hkeys[0]
    high = hkeys[-1]

    if (high - low) > 640:
	low = -320
	high = 320

    start_x = 640 - (high - low)

    surface.lock()
    for i in range(low, high+1):
	if histogram.has_key(i):
	    hits = histogram[i]
	else:
	    hits = 0
	if hits == 1:
	    surface.set_at((start_x + i, 479), (0x80,)*3)
	else:
	    pygame.draw.line(surface,(0xFF,)*3,
			     (start_x + i, 479), (start_x + i, 479 - hits/2))
	print "%3d: %d\t%2f%%" % (i, hits, (hits * 100.0)/(640*480))
    surface.unlock()

def print_histogram(histogram):
    hkeys = histogram.keys()
    hkeys.sort()
    low = hkeys[0]
    high = hkeys[-1]

    for i in range(low, high+1):
	if histogram.has_key(i):
	    hits = histogram[i]
	else:
	    hits = '-'
	print "%3d: %s" % (i, hits)



########
#
# 2D
#
# Points on a surface
# Dancing string
# Height map
#  contours of height map


########
#
# 3D
#
# Solid textures
#  contours in solid textures
# Animated height map


########
#
# 4D
#
# Animated solid textures

########

if __name__ == '__main__':
    demo()
