from __future__ import division
import Image
#import ImageDraw
import math
import random
from numpy import *

RESOLUTION = [640,480]
BACKGROUND = "rgb(255,255,255)"

def interpolate(x0, x1, alpha): #alpha lies between 0 and 1
	lerp = ((1 - alpha) * x0 + alpha * x1)
	#print(lerp)
	return lerp

#def interp_bilinear(

def smooth_noise(noise, point, mask):
	(x,y) = point
	(n_w, n_h) = noise.shape
	(m_w, m_h) = mask.shape
	if (m_w != m_h): return 0 # Mask must be square
	delta = (m_w-1)/2
	sum = 0
	for i in range(m_w):
		for j in range(m_h):
			sum = sum + (mask[i,j]*noise[(x-(i-delta))%n_w, (y-(j-delta))%n_h])
	return sum

def noise(res):
	ar = zeros((res[1],res[0]), 'uint32')
	for x in range(res[0]):
		for y in range(res[1]):
			v = int(math.floor(random.random() * 256))
			ar[y,x] = v
	return ar

def smoothNoise(noise, octave):
	(w,h) = noise.shape
	period = 1 << octave # 2^k
	frequency = 1.0
	#frequency = 1 << octave
	#period = 1/frequency
	#print("period=%d, freq=%f"%(period, frequency))
	
	smooth = zeros((w,h),'uint32')
	for i in range(0,w):
		sample_i0 = (i/period)*period
		sample_i1 = sample_i0 % w
		horizontal_blend = (i-sample_i0)*frequency
		for j in range(0,h):
			sample_j0 = (j/period)*period
			sample_j1 = (sample_j0 + 1) % h
			verticle_blend = (j - sample_j0) * frequency
			top = interpolate(noise[sample_i0,sample_j0],noise[sample_i1,sample_j1],horizontal_blend)
			bottom = interpolate(noise[sample_i0,sample_j1],noise[sample_i1,sample_j0],horizontal_blend)
			smooth[i,j] = interpolate(top,bottom,verticle_blend)
	return smooth
	

def perlin_noise(noise, octave, persistence):
	(w,h) = noise.shape
	perlin = zeros((w,h),'uint32')
	
	if (persistence < 0 or persistence > 1): return perlin
	
	frequency = 1 << octave # 2^octave
	amplitude = persistence ** octave
	print("frequency=%d, amplitude=%f"%(frequency, amplitude))
	
	
	for i in range(0,w):
		sample_i0 = (i/period)*period
		sample_i1 = sample_i0 % w
		horizontal_blend = (i-sample_i0)*frequency
		for j in range(0,h):
			sample_j0 = (j/period)*period
			sample_j1 = (sample_j0 + 1) % h
			verticle_blend = (j - sample_j0) * frequency
			top = interpolate(noise[sample_i0,sample_j0],noise[sample_i1,sample_j1],horizontal_blend)
			bottom = interpolate(noise[sample_i0,sample_j1],noise[sample_i1,sample_j0],horizontal_blend)
			smooth[i,j] = interpolate(top,bottom,verticle_blend)
	return smooth
	
def perlin(noise, octave):
	(w,h) = noise.shape
	period = 1 << octave # 2^k
	frequency = 1.0
	smooth = zeros((w,h),'uint32')
	for i in range(0,w):
		for j in range(0,h):
			
			top    = interpolate(,noise[i,j+period])
			bottom = 
			lerp   = 

def do_smooth(noise):
	(w,h)=noise.shape
	smooth = zeros((w,h),'uint32')
	mask_1 = array([
	1/16,2/16,1/16,
	2/16,4/16,2/16,
	1/16,2/16,1/16])
	mask_2 = array([
	0,0,1/1003,2/1003,1/1003,0,0,	
	0,3/1003,13/1003,22/1003,13/1003,3/1003,0,	
	1/1003,13/1003,59/1003,97/1003,59/1003,13/1003,1/1003,
	2/1003,22/1003,97/1003,159/1003,97/1003,22/1003,2/1003,	
	1/1003,13/1003,59/1003,97/1003,59/1003,13/1003,1/1003,	
	0,3/1003, 13/1003,22/1003,13/1003,3/1003,0,	
	0,0,1/1003,2/1003,1/1003,0,0])
	mask_1.shape = (3,3)
	print(mask_1)
	mask_2.shape = (7,7)
	for i in range(w):
		for j in range(h):
			v = smooth_noise(noise,(i,j),mask_2)
			#print(color)
			smooth[i,j] = v
	return smooth

def make_image(array):
	(w,h,c)=array.shape
	img_array = zeros((w,h),'uint32')
	for i in range(w):
		for j in range(h):
			red   = array[i,j,0]
			green = array[i,j,1]
			blue  = array[i,j,2]
			alpha = array[i,j,3]
			# Color order is 0xAABBGGRR
			bitcolor = (alpha << 24) | (blue << 16) | (green << 8) | red
			img_array[i,j] = bitcolor
	img = Image.fromarray(img_array, 'RGBA')
	return img

def demo():
	n = noise(RESOLUTION)
	ar = smoothNoise(n, 8)
	#ar = do_smooth(n)
	img = Image.fromarray(ar, 'I')
	#img = Image.frombuffer('RGBA',RESOLUTION,ar,'raw','RGBA',0,1)
	#img = make_image(ar)
	img.save("perlin.png", "PNG")
	img.show()

demo()
