from math import cos, sin
import numpy as np

class FastCapInput:
	def __init__(self):
		self.title = 'Untitled'
		self.quads = []

	def add_plate(self, name='None', origin=(0,0,0), angles=(0,0,0), widths=(1,1), divs=(1,1)):
		dx = 1.0*widths[0]/divs[0]
		dy = 1.0*widths[1]/divs[1]
		for x in np.linspace(-widths[0]/2.0 + dx/2.0, widths[0]/2.0 - dx/2.0, divs[0]):
			for y in np.linspace(-widths[1]/2.0 + dy/2.0, widths[1]/2.0 - dy/2.0, divs[1]):
				quad = []
				quad.append((x-dx/2.0, y-dy/2.0, 0.0))
				quad.append((x-dx/2.0, y+dy/2.0, 0.0))
				quad.append((x+dx/2.0, y+dy/2.0, 0.0))
				quad.append((x+dx/2.0, y-dy/2.0, 0.0))

				# perform the transformations
				quad = map(lambda p: FastCapInput.rotate_x(p, angles[0]), quad)
				quad = map(lambda p: FastCapInput.rotate_y(p, angles[1]), quad)
				quad = map(lambda p: FastCapInput.rotate_z(p, angles[2]), quad)
				quad = map(lambda p: FastCapInput.offset(p, origin), quad)

				self.add_quad(name, quad)

	def add_quad(self, name, quad):
		self.quads.append((name, quad))

	def write(self, fname):
		self.write_title(fname)
		self.write_quads(fname)

	def write_title(self, fname):
		with open(fname, 'w') as f:
			f.write('0 ' + self.title + '\n')

	def write_quads(self, fname):
		with open(fname, 'a') as f:
			for quad in self.quads:
				f.write('Q ' + quad[0])
				for point in quad[1]:
					f.write(' %0.6g %0.6g %0.6g' % (point[0], point[1], point[2]))
				f.write('\n')

	# transformation functions
	# https://en.wikipedia.org/wiki/Rotation_matrix
	@staticmethod
	def rotate_x(point, angle):
		mat = np.matrix([[point[0]],[point[1]],[point[2]]])
		rot = np.matrix([
			[ 1,          0,           0 ],
			[ 0, cos(angle), -sin(angle) ],
			[ 0, sin(angle),  cos(angle) ],
			])
		mat = rot * mat
		return (mat[0,0], mat[1,0], mat[2,0])
	@staticmethod
	def rotate_y(point, angle):
		mat = np.matrix([[point[0]],[point[1]],[point[2]]])
		rot = np.matrix([
			[  cos(angle), 0, sin(angle) ],
			[           0, 1,          0 ],
			[ -sin(angle), 0, cos(angle) ],
			])
		mat = rot * mat
		return (mat[0,0], mat[1,0], mat[2,0])
	@staticmethod
	def rotate_z(point, angle):
		mat = np.matrix([[point[0]],[point[1]],[point[2]]])
		rot = np.matrix([
			[ cos(angle), -sin(angle), 0 ],
			[ sin(angle),  cos(angle), 0 ],
			[          0,           0, 1 ],
			])
		mat = rot * mat
		return (mat[0,0], mat[1,0], mat[2,0])
	@staticmethod
	def offset(point, origin):
		mat = np.matrix([[point[0]],[point[1]],[point[2]]])
		add = np.matrix([
			[ origin[0] ],
			[ origin[1] ],
			[ origin[2] ],
			])
		mat = add + mat
		return (mat[0,0], mat[1,0], mat[2,0])