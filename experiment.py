#!/usr/bin/env python


from math import pi
from pycap import FastCap, Plate

import numpy as np
import numpy.matlib
from random import random

import matplotlib.pyplot as plt

import sys

def main():

	trials = 5000

	results = np.matlib.zeros((1,trials))

	for n in range(trials):

		capdict = None
		while capdict is None:
			try:
				capdict = run_experiment()
			except:
				pass

		fom = calc_fom(capdict)
		results[0,n] = abs(fom)

		printProgress(n+1,trials)

	np.savetxt('test.txt', results)

	print 'Mean: ', results.mean()
	print 'Median: ', np.median(results)
	print 'Standard Dev: ', np.std(results)

	# see http://stackoverflow.com/questions/5328556/histogram-matplotlib
	hist, bins = np.histogram(results, bins=50)
	width = 0.7 * (bins[1] - bins[0])
	center = (bins[:-1] + bins[1:]) / 2
	plt.bar(center, hist, align='center', width=width)
	plt.show()

def calc_fom(capdict):
	C1 = abs(capdict['electrode1']['particle1'])
	C2 = abs(capdict['electrode1']['particle2'])
	C3 = abs(capdict['electrode2']['particle2'])
	C4 = abs(capdict['electrode2']['particle1'])
	Cm = abs(capdict['particle1']['particle2'])

	num = C1*C4-C2*C3
	den = C1*C2+C1*C4+C2*C3+C3*C4+Cm*(C1+C2+C3+C4)

	return 1.0*num/den

def run_experiment():
	f = FastCap()

	capx = capy = capz = 1e-3
	boxx = boxy = boxz = 10e-2

	### build the particle

	# create plates of the right size
	p1 = Plate(wx=capx, wy=capy, nx=10, ny=10)
	p2 = Plate(wx=capx, wy=capy, nx=10, ny=10)

	# separate them
	p1.offset(np.matrix([[0],[0],[-capz/2.0]]))
	p2.offset(np.matrix([[0],[0],[ capz/2.0]]))

	# rotate randomly
	xrot, yrot, zrot = 2*pi*random(), 2*pi*random(), 2*pi*random()
	p1.x_rot(xrot)
	p2.x_rot(xrot)
	p1.y_rot(yrot)
	p2.y_rot(yrot)
	p1.z_rot(zrot)
	p2.z_rot(zrot)

	# position randomly
	vector = np.matrix([[boxx*(random()-0.5)], [boxy*(random()-0.5)], [boxz*(random()-0.5)]])
	p1.offset(vector)
	p2.offset(vector)

	# add plates to the FastCap model
	f.add_plate('particle1', p1)
	f.add_plate('particle2', p2)

	### build the second capacitor

	# create plates of the right size
	p3 = Plate(wx=boxx, wy=boxy, nx=10, ny=10)
	p4 = Plate(wx=boxx, wy=boxy, nx=10, ny=10)

	# separate them
	p3.offset(np.matrix([[0],[0],[-boxz/2.0]]))
	p4.offset(np.matrix([[0],[0],[ boxz/2.0]]))

	# add plates to the FastCap model
	f.add_plate('electrode1', p3)
	f.add_plate('electrode2', p4)

	### run the FastCap simulation

	f.write()
	capdict = f.run()

	return capdict

# see http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '#' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('%s [%s] %s%s %s\r' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if iteration == total:
        print("\n")

if __name__ == '__main__':
	main()