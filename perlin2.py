from __future__ import division
import Image
#import math
import random
from numpy import *

MASKLEVELS = (# Level 1 (1x1)
			  array([1]),
			  # Level 2 (3x3)
			  array([
			  1/16,2/16,1/16,
			  2/16,4/16,2/16,
			  1/16,2/16,1/16]),
			  # Level 3 (5x5)
			  array([1]), # TODO
			  # Level 4 (7x7)
			  array([
			  0,0,1/1003,2/1003,1/1003,0,0,
			  0,3/1003,13/1003,22/1003,13/1003,3/1003,0,
			  1/1003,13/1003,59/1003,97/1003,59/1003,13/1003,1/1003,
			  2/1003,22/1003,97/1003,159/1003,97/1003,22/1003,2/1003,
			  1/1003,13/1003,59/1003,97/1003,59/1003,13/1003,1/1003,
			  0,3/1003, 13/1003,22/1003,13/1003,3/1003,0,
			  0,0,1/1003,2/1003,1/1003,0,0]))
MASKLEVELS[0].shape = (1,1)
MASKLEVELS[1].shape = (3,3)
#MASKLEVELS[2].shape = (5,5)
MASKLEVELS[3].shape = (7,7)

def progress(atvalue, ofvalue):
	pass

def interpolate(x0, x1, alpha): #alpha lies between 0 and 1
	lerp = ((1 - alpha) * x0 + alpha * x1)
	#print(lerp)
	return lerp

def makeNoise(res):
	''' Create a noisy image. '''
	ar = zeros((res[1],res[0]), 'uint32')
	for x in range(res[0]):
		for y in range(res[1]):
			v = int(math.floor(random.random() * 256))
			ar[y,x] = v
	return ar

def noise2D(pt):
	(x,y) = pt
	n = x + y * 57L
	n = (n << 13L) ** n
	r = (1L - ((n * (n * n * 15731L + 789221L) + 1376312589L) & 0xfffffff7) / 1073741854L)
	return r
	
def smoothNoise(noise, (x,y), level):
	''' Smooths the point (x,y) using Gaussian blur mask level.'''
	mask = MASKLEVELS[level-1]
	(n_w, n_h) = noise.shape
	(m_w, m_h) = mask.shape
	if (m_w != m_h):
		print("Error: Non-square blur mask")
		return 0 # Mask must be square
	delta = (m_w-1)/2
	sum = 0
	for i in range(m_w):
		for j in range(m_h):
			sum = sum + (mask[i,j]*noise[(x-(i-delta))%n_w, (y-(j-delta))%n_h])
	return sum
	
def interpolatedNoise(noise, (x,y)):
	(n_w, n_h) = noise.shape
	integer_x = int(x)%n_w
	fract_x   = (x - integer_x)%n_w
	integer_y = int(y)%n_w
	fract_y   = (y - integer_y)%n_h
	
	v1 = noise[integer_x,           integer_y]
	v2 = noise[(integer_x + 1)%n_w, integer_y]
	v3 = noise[integer_x,           (integer_y + 1)%n_h]
	v4 = noise[(integer_x + 1)%n_w, (integer_y + 1)%n_h]
	i1 = interpolate(v1, v2, fract_x)
	i2 = interpolate(v3, v4, fract_x)
	
	return interpolate(i1, i2, fract_y)

def test(persistence, octaves):
	(w,h) = (640,480)
	n = octaves
	(n_w,n_h) = (w*(2**n),h*(2**n))
	noise = makeNoise((n_w,n_h))
	smooth = zeros((h,w), 'uint32')
	for x in range(n_w):
		for y in range(n_h):
			smooth[y,x] = smoothNoise(noise, (x,y), 2)
	perlin = zeros((h,w), 'uint32')
	for x in range(w):
		for y in range(h):
			total = 0
			for i in range(n):
				frequency = 1<<i
				amplitude = persistence ** i
				print ("freq=%f, amp=%f"%(frequency,amplitude))
				total = total + interpolatedNoise(smooth, (x*frequency,y*frequency))*amplitude
				print ("total=%f"%(total))
			print ("(%d,%d)=%f"%(x,y,total))
			perlin[y,x] = total
	#img = Image.fromarray(noise, 'I')
	#img = Image.fromarray(smooth, 'I')
	#img = Image.fromarray(interp, 'I')
	img = Image.fromarray(perlin, 'I')
	img.show()
	
#test(1/4,4)
	
	
	
	
