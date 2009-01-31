#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re, time
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
	p = QtCore.QProcess()
	p.start("/usr/sbin/arp", ["-n"])
	f = p.waitForFinished(10)
	while not f:
		f = p.waitForFinished(10)
	dta = p.readAll()
	macs = {}
	for h in hosts:
		macs[h] = None
		m = re.search(h + '\s+ether\s+(\S+)', str(dta))
		if m:
			macs[h] = m.group(1)
	return macs


def search_hosts(network,win):
	p = QtCore.QProcess()
	pBar = QtGui.QProgressBar(win)
	pBar.setRange(0,0)
	pBar.show()
	p.start("nmap", ["-n", "-sP", network])
	f = p.waitForFinished(30)
	while not f:
		QtGui.QApplication.processEvents()
		f = p.waitForFinished(30)
	dta = p.readAll()
	m = re.findall('Host (\S+) appears to be up',str(dta))
	pBar.close()
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
	
	
	def clear(self):
		self.macs = []

	
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
		self.connect(self.ui.buttonSsh,
			QtCore.SIGNAL("clicked()"), self.execSsh)
		
		self.filt = Filter()
		
		
	def execSsh(self):
		pid = os.fork()
		if pid == 0:
			os.execl("/usr/bin/konsole", "konsole", "--script")
		time.sleep(2)
		
		first = 1
		for h in self.hList:
			if first:
				time.sleep(1)
				first = 0
				continue
			com = "dcop konsole-" + str(pid) + " konsole newSession > /dev/null"
			os.system(com)
			time.sleep(1)
		
		i = 1
		for h in self.hList:		
			com = "dcop konsole-" + str(pid) + " session-" + str(i) + ' sendSession "echo %s" >/dev/null' % h.ip
			os.system(com)
			i = i + 1
		
		
		
		
		
	
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
		hosts = search_hosts(n,self)
		macs = get_macs(hosts)
		for h in hosts:
			self.insertHost(h,macs[h])


	def insertHost(self,ip,mac):
		h = HostItem()
		h.setup(ip,mac)
		h.insert(self.ui.hostList)
		self.hList.append(h)
	
	
	def applyFilter(self):
		fn = QtGui.QFileDialog.getOpenFileName(self, "Load File")
		if fn == '': return
		self.filt.clear()
		self.filt.loadFromFile(fn)
		f = self.filt.exe(self.hList)
		self.hList = f
		self.refreshTable()
	




if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	app.exec_()