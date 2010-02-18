# -*- coding: utf-8 -*-

import os.path

progs = ('cssh', 'nmap')
paths = ('/bin', '/usr/bin', '/sbin', '/usr/sbin')


def checkProg(prog):
	for p in paths:
		if os.path.isfile(p+'/'+prog):
			return True
	return False
		

def checkRequiredPrograms():
	for prog in progs:
		if checkProg(prog) == False:
			print "Required program: " + prog + " NOT FOUND!!!"
			return False
	return True