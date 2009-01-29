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
		t.setItem(0, 0, HostWgt(self,str(self.ip)))
		t.setItem(0, 1, HostWgt(self,str(self.mac)))


def get_macs(hosts):
	chi,cho = os.popen2( ("/usr/sbin/arp", "-n") )
	r = ''.join(cho.readlines())
	chi.close()
	cho.close()
	macs = {}
	for h in hosts:
		macs[h] = None
		print h + '\s+ether\s+(\S+)'
		#print r
		m = re.search(h + '\s+ether\s+(\S+)', r)
		if m:
			macs[h] = m.group(1)
	return macs


def search_hosts(network):
	chi,cho = os.popen2( ("nmap", "-n", "-sP", network) )
	r = ''.join(cho.readlines())
	chi.close()
	cho.close()
	m = re.findall('Host (\S+) appears to be up',r)
	return m




class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui = uic.loadUi("mainwindow.ui",self)
		self.ui.hostList.horizontalHeader().setStretchLastSection(True)
		
		self.setWindowTitle("Lab Admin")

		self.connect(self.ui.buttonHosts,
			QtCore.SIGNAL("clicked()"), self.getHosts)
		
	
	def clearTable(self):
		while self.ui.hostList.item(0,0):
			self.ui.hostList.removeRow(0)
		
		
	def getHosts(self):
		n,c = QtGui.QInputDialog.getText(self,"Network","What network? (ex: 192.168.2.0/24)")
		if not c: return
		self.clearTable()
		hosts = search_hosts(n)
		macs = get_macs(hosts)
		for h in hosts:
			self.insertHost(h,macs[h])
	
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