#!/usr/bin/env python
# $Id: prof.py,v 1.5 2001/05/31 04:57:05 kevint Exp $
# This file is to serve as example code.  Do whatever you like with it!
#  -- Kevin Turner <acapnotic@users.sourceforge.net>

"""Profiling PerlinNoise"""

import perlin
from Numeric import *
import profile, pstats
import pygame

import peterlin

TRUE = 1==1
FALSE = not TRUE

def f8_i(x):
    """using an integer clock, so cut out the floating-point"""

    return string.rjust(`x`,8)

pstats.f8 = f8_i

class PygameProfile(profile.Profile):
    def __init__(self):
	profile.Profile.__init__(self, pygame.time.get_ticks)

    def trace_dispatch_i(self, frame, event, arg):
	t = self.timer() - self.t # - 0 # Calibration constant
	# (but this needs to calibration constant on my machine)

	if self.dispatch[event](frame,t):
	    self.t = self.timer()
	else:
	    self.t = self.timer() - t # put back unrecorded delta
	return


def prof():
    if 0:
	callers_prof()
    else:
	comparitive_prof()


def callers_prof():
    pr = do_prof((3,3), 6, runs=3)

    stats = pstats.Stats(pr).strip_dirs()

    stats.sort_stats('time')
    stats.print_stats()
    stats.print_callers()


def comparitive_prof():
    do_prof((9,),6,runs=6)

    do_prof((9,),6,dynamic=FALSE,runs=6)

    do_prof((3,3), 6, runs=3)

    do_prof((3,3), 6, dynamic=FALSE, runs=3)

    do_prof((3,3), 6, None, optimize=FALSE, runs=3)

    do_prof((3,3), 6, perlin.ease_interpolation, runs=3)

    do_prof((3,3), 6, perlin.ease_interpolation,
	    optimize=FALSE, runs=3)


def do_prof(size, frequency, interp_func=None,
	    optimize=TRUE, dynamic=TRUE, runs=1):

    pr=PygameProfile()

    dimensions = len(size)

    try:
	funcname = interp_func.__name__
    except:
	funcname = `None`

    print "%dD %sx%s ifunc=%s %s %s" % (len(size),size,frequency,funcname,
				       optimize and 'Optimized' or 'general',
				       dynamic and 'Dynamic' or 'static')

    if optimize:
	perlin._FORCE_GENERIC_CASE = FALSE
    else:
	perlin._FORCE_GENERIC_CASE = TRUE

    if dynamic:
	perlin._DISABLE_DYNAMIC_CODE = FALSE
    else:
	perlin._DISABLE_DYNAMIC_CODE = TRUE

    build_func = globals()['build_%dD' % dimensions]

    old_t = 0
    for i in range(1,runs+1):
	pr.runcall(build_func, size, frequency, interp_func)

	t = pstats.Stats(pr).total_tt
	print "Run %2d:" % i,t - old_t
	old_t = t

    print "Average:", t / runs
    # XXX: add stats_dumping

    return pr


def build_1D((width,), frequency, interp_func=None):

    resolution = frequency

    noise = perlin.PerlinNoise((width,),interp_func)

    surfarray = zeros((width*resolution,), Int)

    histogram = {}
    for x in range(width * resolution):
	nx = x / float(resolution)
	value = noise.value_at((nx,))

	#if histogram.has_key(int(value * 10)):
	#histogram[int(value * 10)] += 1
	#else:
	#histogram[int(value * 10)] = 1

	value = int(value * 128 + 128.5)
	if value < 0:
	    value = 0
	elif value > 255:
	    value = 255
	surfarray[x] = value

    # draw_histogram(histogram, surface)

def build_2D((width, height), frequency, interp_func=None):

    resolution = frequency

    noise = perlin.PerlinNoise((width,height),interp_func)

    surfarray = zeros((width*resolution, height*resolution),Int)

    histogram = {}
    for x in range(width * resolution):
	for y in range(height * resolution):
	    nx = x / float(resolution)
	    ny = y / float(resolution)
	    value = noise.value_at((nx,ny))

	    #if histogram.has_key(int(value * 10)):
	    #histogram[int(value * 10)] += 1
	    #else:
	    #histogram[int(value * 10)] = 1

	    value = int(value * 128 + 128.5)
	    if value < 0:
		value = 0
	    elif value > 255:
		value = 255
	    surfarray[x,y] = value

    # draw_histogram(histogram, surface)


def build_petelin_prof(size, frequency, runs=1):
    print "2D %sx%s petelin" % (size,frequency)

    pr=PygameProfile()

    old_t = 0
    for i in range(1,runs+1):
	pr.runcall(build_petelin, size, frequency)

	t = pstats.Stats(pr).total_tt
	print "Run %2d:" % i,t - old_t
	old_t = t

    print "Average:", t / runs
    # XXX: add stats_dumping

    return pr


def build_petelin((width, height), frequency):

    resolution = frequency

    #print " * %dD size: %10s freq: %3d, interp: %s... " %\
    # (2, (width, height), resolution, interp_func)

    surfarray = zeros((width*resolution, height*resolution),Int)

    histogram = {}
    for x in range(width * resolution):
	for y in range(height * resolution):
	    nx = x / float(resolution)
	    ny = y / float(resolution)
	    value = peterlin.perlin_noise(nx,ny)

	    #if histogram.has_key(int(value * 10)):
	    #histogram[int(value * 10)] += 1
	    #else:
	    #histogram[int(value * 10)] = 1

	    value = int(value * 256)
	    if value < 0:
		value = 0
	    elif value > 255:
		value = 255
	    surfarray[x,y] = value

    # draw_histogram(histogram, surface)


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


########

if __name__ == '__main__':
    prof()
