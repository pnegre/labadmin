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
		self.tag = None
	
	
	def insert(self,t):
		t.insertRow(0)
		t.setItem(0, 0, HostWgt(self,str(self.ip)))
		t.setItem(0, 1, HostWgt(self,str(self.mac)))
		t.setItem(0, 2, HostWgt(self,str(self.tag)))


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
			macs[h] = m.group(1).lower()
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
		self.clear()
	
	
	def loadFromFile(self, file):
		self.clear()
		try:
			f = open(file,"r")
		except(IOError), e:
			print "error opening", file
			return False
		lines = f.readlines()
		f.close()
		mac = ""; tag=""
		for l in lines:
			l = l.rstrip("\n")
			m = re.search("^(..:..:..:..:..:..)\s+(\S*)$",l)
			if m:
				mac = m.group(1)
				tag = m.group(2)
			else:
				m = re.search("^(..:..:..:..:..:..)\s*$",l)
				if not m: continue
				mac = m.group(1)
				tag = None
			mac = mac.lower()
			self.macs.append(mac)
			self.tags[mac] = tag
		return True
	
	
	def clear(self):
		self.macs = []
		self.tags = {}

	
	def exe(self, hostList = []):
		r = []
		for h in hostList:
			if h.mac == None: continue
			if h.mac in self.macs:
				h.tag = self.tags[h.mac]
				r.append(h)
		return r


class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui = uic.loadUi("mainwindow.ui",self)
		self.ui.hostList.horizontalHeader().setStretchLastSection(True)
		self.hList = []
		self.filteredList = self.hList
		self.fnameList = []
		
		self.setWindowTitle("Lab Admin")

		self.connect(self.ui.buttonHosts,
			QtCore.SIGNAL("clicked()"), self.getHosts)
		self.connect(self.ui.buttonFilter,
			QtCore.SIGNAL("clicked()"), self.loadFilter)
		self.connect(self.ui.buttonClearFilters,
			QtCore.SIGNAL("clicked()"), self.clearFilters)
		self.connect(self.ui.buttonCluster,
			QtCore.SIGNAL("clicked()"), self.execCluster)
		self.connect(self.ui.filterBox,
			QtCore.SIGNAL("activated(int)"), self.applyFilter)
		
		self.center()
		self.ui.buttonCluster.setDisabled(True)
		self.ui.hostList.setColumnWidth(0,150)
		self.ui.hostList.setColumnWidth(1,150)
		
		self.settings = QtCore.QSettings("labadmin","labadmin")
		s = self.settings.value("filters").toString()
		if s:
			self.loadFilter(str(s))
		else:
			l = self.settings.value("filters").toList()
			for f in l:
				print str(f.toString())
				self.loadFilter(str(f.toString()))
		
	
	def center(self):
		screen = QtGui.QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
	
	
	
	def closeEvent(self,e):
		print self.fnameList
		self.settings.setValue("filters", QtCore.QVariant(self.fnameList))
		e.accept()
	
	
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
	
	
	def clearTable(self):
		while self.ui.hostList.item(0,0):
			self.ui.hostList.removeRow(0)
	
	
	def refreshTable(self):
		self.clearTable()
		for h in self.filteredList:
			h.insert(self.ui.hostList)
		
		if len(self.filteredList):
			self.ui.buttonCluster.setDisabled(False)
		else:
			self.ui.buttonCluster.setDisabled(True)
		
		
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
	
	
	def loadFilter(self, fnd=''):
		fn = ''
		if fnd == '':
			fn = QtGui.QFileDialog.getOpenFileName(self, "Load File")
			if fn == '': return
		else:
			fn = fnd
		if fn in self.fnameList: return
		f = Filter()
		f.clear()
		if not f.loadFromFile(fn): return
		self.ui.filterBox.addItem("..." + fn[-20:], QtCore.QVariant(f))
		self.fnameList.append(fn)


	def applyFilter(self,i):
		if i==0:
			self.filteredList = self.hList
		else:
			f = self.ui.filterBox.itemData(i).toPyObject()
			self.filteredList = f.exe(self.hList)
		self.refreshTable()

	def clearFilters(self):
		self.fnameList = []
		self.ui.filterBox.clear()
		self.ui.filterBox.addItem('All hosts')



if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	app.exec_()