#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re
from subprocess import Popen
from PyQt4 import QtCore, QtGui, uic


class HostWgt(QtGui.QTableWidgetItem):
	def __init__(self,p,t):
		QtGui.QTableWidgetItem.__init__(self,t)
		self.taskObject = p
		self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)


class HostItem(object):
	def setup(self,ip,mac):
		self.ip = ip
		self.mac = mac
	
	def insert(self,t):
		t.insertRow(0)
		t.setItem(0, 0, HostWgt(self,self.ip))
		t.setItem(0, 1, HostWgt(self,self.mac))



def get_mac(host):
	chi,cho = os.popen2( ("/usr/sbin/arp", "-n", host) )
	r = ''.join(cho.readlines())
	m = re.search(host + '\s+ether\s+(\S+)', r)
	if m:
		p = m.group(1)
		return p
	else:
		return None

def do_ping(host):
	chi,cho = os.popen2( ("ping", "-c", "1", "-i", "0.2", host) )
	r = ''.join(cho.readlines())
	m = re.search('Unreachable', r)
	if m: return None
	else:
		m = get_mac(host)
		return m






class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui = uic.loadUi("mainwindow.ui",self)
		self.ui.hostList.horizontalHeader().setStretchLastSection(True)
		
		m = do_ping("192.168.1.1")
		if m: print m
		m = do_ping("192.168.1.3")
		if m: print m
		
		
	def insertHost(self,ip,mac):
		h = HostItem()
		h.setup(ip,mac)
		h.insert(self.ui.hostList)
	




if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	mainWin = MainWindow()
	#mainWin.insertHost("aa","bb")
	#mainWin.insertHost("tt","abcdf")
	mainWin.show()
	app.exec_()