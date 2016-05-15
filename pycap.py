#!/usr/bin/env python

from math import cos, sin
import numpy as np
import numpy.matlib
import subprocess
import re
import os.path

class FastCap:
	def __init__(self):
		self.title = 'Untitled'
		self.fname = 'test.inp'
		self.quads = {}
		self.names = []

	# geometry definition functions

	def add_plate(self, name, plate):
		for quad in plate.quads:
			self.add_quad(name, quad)

	def add_quad(self, name, quad):
		if name not in self.quads:
			self.quads[name] = []
		self.quads[name].append(quad)

		if name not in self.names:
			self.names.append(name)

	# file management functions

	def write(self):
		self.write_title()
		self.write_quads()
		self.write_end()

	def write_title(self):
		with open(self.fname, 'w') as f:
			f.write('0 ' + self.title + '\n')

	def write_quads(self):
		with open(self.fname, 'a') as f:
			for name in self.names:
				f.write('* ' + name + '\n')
				for quad in self.quads[name]:
					f.write('Q ' + name)
					for point in quad:
						f.write(' %0.6g %0.6g %0.6g' % (point[0,0], point[1,0], point[2,0]))
					f.write('\n')

	def write_end(self):
		with open(self.fname, 'a') as f:
			f.write('*\n')

	# running fast cap

	def run(self):
		output = subprocess.check_output(['fastcap', self.fname])
		output = output.split('\n')

		# get the start line and prefix
		index = next(n for n,line in enumerate(output) if line.startswith('CAPACITANCE MATRIX'))
		m = re.match('CAPACITANCE MATRIX, (atto|femto|pico|nano|micro|milli)farads', output[index])
		prefix = m.group(1)
		scalar = {'atto':1e-18,'femto':1e-15,'pico':1e-12,'nano':1e-9,'micro':1e-6,'milli':1e-3}[prefix]
		index += 1
		
		# get the number of results
		nums = output[index].split()
		nums = [int(s) for s in nums]
		total = max(nums)
		index += 1

		# process the remaining lines
		capmat = np.matlib.zeros((total,total))
		names = []
		for row in range(total):
			line = output[index+row].split()

			# get the name of this conductor
			m = re.match(r'([a-zA-Z0-9]+)%GROUP[0-9]+', line[0])
			names.append(m.group(1))

			# add the remaining results to the matrix
			for col, val in enumerate(line[2:]):
				capmat[row,col] = scalar*float(val)

		# create a dictionary representing the results
		capdict = {}
		for row in range(total):
			capdict[names[row]] = {}
			for col in range(total):
				capdict[names[row]][names[col]] = capmat[row,col]

		return capdict

	# drawing the result

	def draw(self):
		subprocess.check_output(['fastcap', '-m', self.fname])
		ps_name = os.path.splitext(self.fname)[0]
		ps_name += '.ps'
		subprocess.check_output(['ps2pdf', ps_name])

class Plate:
	def __init__(self, wx=1, wy=1, nx=1, ny=1):
		self.quads = []

		dx = 1.0*wx/nx
		dy = 1.0*wy/ny
		for x in np.linspace(-wx/2.0 + dx/2.0, wx/2.0 - dx/2.0, nx):
			for y in np.linspace(-wy/2.0 + dy/2.0, wy/2.0 - dy/2.0, ny):
				quad = []
				quad.append(np.matrix([[x-dx/2.0], [y-dy/2.0], [0.0]]))
				quad.append(np.matrix([[x-dx/2.0], [y+dy/2.0], [0.0]]))
				quad.append(np.matrix([[x+dx/2.0], [y+dy/2.0], [0.0]]))
				quad.append(np.matrix([[x+dx/2.0], [y-dy/2.0], [0.0]]))

				self.quads.append(quad)

	def x_rot(self, angle):
		self.quads = [[Plate.x_rot_point(point, angle) for point in quad] for quad in self.quads]

	def y_rot(self, angle):
		self.quads = [[Plate.y_rot_point(point, angle) for point in quad] for quad in self.quads]

	def z_rot(self, angle):
		self.quads = [[Plate.z_rot_point(point, angle) for point in quad] for quad in self.quads]

	def offset(self, vector):
		self.quads = [[Plate.offset_point(point, vector) for point in quad] for quad in self.quads]

	# transformation functions
	# https://en.wikipedia.org/wiki/Rotation_matrix
	@staticmethod
	def x_rot_point(point, angle):
		mul = np.matrix([
			[ 1,          0,           0 ],
			[ 0, cos(angle), -sin(angle) ],
			[ 0, sin(angle),  cos(angle) ],
			])
		return mul*point 
	@staticmethod
	def y_rot_point(point, angle):
		mul = np.matrix([
			[  cos(angle), 0, sin(angle) ],
			[           0, 1,          0 ],
			[ -sin(angle), 0, cos(angle) ],
			])
		return mul*point
	@staticmethod
	def z_rot_point(point, angle):
		mul = np.matrix([
			[ cos(angle), -sin(angle), 0 ],
			[ sin(angle),  cos(angle), 0 ],
			[          0,           0, 1 ],
			])
		return mul*point
	@staticmethod
	def offset_point(point, vector):
		return vector+point