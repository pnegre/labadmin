# -*- coding: utf-8 -*-

import os.path

progs = ('cssh', 'nmap', 'arp')
paths = ('/bin', '/usr/bin', '/sbin', '/usr/sbin')

absolutePaths = {}

def completePath(prog):
	return absolutePaths[prog]


def checkProg(prog):
	for p in paths:
		path = p+'/'+prog
		if os.path.isfile(path):
			absolutePaths[prog] = path 
			return True
	return False
		

def checkRequiredPrograms():
	for prog in progs:
		if checkProg(prog) == False:
			print "Required program: " + prog + " NOT FOUND!!!"
			return False
	return True