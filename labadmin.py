#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re, time
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



class PBarDlg(QtGui.QDialog):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui = uic.loadUi("pbar.ui",self)



class ClusterDlg(QtGui.QDialog):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui = uic.loadUi("cluster.ui",self)



def get_macs(hosts):
	p = QtCore.QProcess()
	p.start("/usr/sbin/arp", ["-n"])
	p.waitForFinished(-1)
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
	pBar = PBarDlg(win)
	pBar.show()
	p.start("nmap", ["-n", "-sP", network])
	while not p.waitForFinished(30):
		QtGui.QApplication.processEvents()
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
		self.filteredList = self.hList
		
		self.setWindowTitle("Lab Admin")

		self.connect(self.ui.buttonHosts,
			QtCore.SIGNAL("clicked()"), self.getHosts)
		self.connect(self.ui.buttonFilter,
			QtCore.SIGNAL("clicked()"), self.applyFilter)
		self.connect(self.ui.buttonSsh,
			QtCore.SIGNAL("clicked()"), self.execSsh)
		self.connect(self.ui.buttonCluster,
			QtCore.SIGNAL("clicked()"), self.execCluster)
		
		self.filt = Filter()
		self.center()
		
	
	def center(self):
		screen = QtGui.QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
	
	
	def execCluster(self):
		d = ClusterDlg()
		if not d.exec_(): return
		us = d.username.text()
		tl = "-G"
		if d.tileWindows.isChecked(): tl = "-g"
		hosts = []
		for h in self.filteredList:
			hosts.append(str(h.ip))
		pid = os.fork()
		if pid == 0:
			os.execl("/usr/bin/cssh", "cssh", tl, "-l" + us, *hosts)
	
	
	def execSsh(self):
		pid = os.fork()
		if pid == 0:
			os.execl("/usr/bin/konsole", "konsole", "--script")
		time.sleep(2)
		
		first = 1
		for h in self.filteredList:
			if first:
				time.sleep(1)
				first = 0
				continue
			com = "dcop konsole-" + str(pid) + " konsole newSession > /dev/null"
			os.system(com)
			time.sleep(1)
		
		i = 1
		for h in self.filteredList:
			com = "dcop konsole-" + str(pid) + " session-" + str(i) + ' sendSession "echo %s" >/dev/null' % h.ip
			os.system(com)
			i = i + 1		
	
	
	def clearTable(self):
		while self.ui.hostList.item(0,0):
			self.ui.hostList.removeRow(0)
	
	
	def refreshTable(self):
		self.clearTable()
		for h in self.filteredList:
			h.insert(self.ui.hostList)
		
		
	def getHosts(self):
		n,c = QtGui.QInputDialog.getText(self,"Network","What network? (ex: 192.168.2.0/24)")
		if not c: return		
		hosts = search_hosts(n,self)
		macs = get_macs(hosts)
		self.hList = []
		for h in hosts:
			hi = HostItem()
			hi.setup(h,macs[h])
			self.hList.append(hi)
		
		self.filteredList = self.hList
		self.refreshTable()
	
	
	def applyFilter(self):
		fn = QtGui.QFileDialog.getOpenFileName(self, "Load File")
		if fn == '': return
		self.filt.clear()
		self.filt.loadFromFile(fn)
		self.filteredList = self.filt.exe(self.hList)
		self.refreshTable()
	




if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	app.exec_()