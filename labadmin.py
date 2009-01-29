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


class Filter(object):
	def __init__(self):
		self.macs = []
	
	
	def loadFromFile(self, file):
		f = open(file,"r")
		k = f.readline()
		while k:
			self.macs.append(k.rstrip("\n").lower())
			k = f.readline()
		f.close()
			

	
	def exe(self, hostList = []):
		print self.macs
		r = []
		for h in hostList:
			if h.mac == None: continue
			if h.mac.lower() in self.macs:
				r.append(h)
		return r


class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui = uic.loadUi("mainwindow.ui",self)
		self.ui.hostList.horizontalHeader().setStretchLastSection(True)
		self.hList = []
		
		self.setWindowTitle("Lab Admin")

		self.connect(self.ui.buttonHosts,
			QtCore.SIGNAL("clicked()"), self.getHosts)
		self.connect(self.ui.buttonFilter,
			QtCore.SIGNAL("clicked()"), self.applyFilter)
		
		self.filt = Filter()
		self.filt.loadFromFile("cameva.macs")
		
	
	def clearTable(self):
		while self.ui.hostList.item(0,0):
			self.ui.hostList.removeRow(0)
	
	def refreshTable(self):
		self.clearTable()
		for h in self.hList:
			print h.mac
			h.insert(self.ui.hostList)
		
	def getHosts(self):
		n,c = QtGui.QInputDialog.getText(self,"Network","What network? (ex: 192.168.2.0/24)")
		if not c: return
		self.clearTable()
		self.hList = []
		hosts = search_hosts(n)
		macs = get_macs(hosts)
		for h in hosts:
			self.insertHost(h,macs[h])


	def insertHost(self,ip,mac):
		h = HostItem()
		h.setup(ip,mac)
		h.insert(self.ui.hostList)
		self.hList.append(h)
	
	
	def applyFilter(self):
		f = self.filt.exe(self.hList)
		self.hList = f
		self.refreshTable()
	




if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	mainWin = MainWindow()
	#mainWin.insertHost("aa","bb")
	#mainWin.insertHost("tt","abcdf")
	mainWin.show()
	app.exec_()