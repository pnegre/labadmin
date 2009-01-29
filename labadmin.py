#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
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





class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui = uic.loadUi("mainwindow.ui",self)
		self.ui.hostList.horizontalHeader().setStretchLastSection(True)
		
	def insertHost(self,ip,mac):
		h = HostItem()
		h.setup(ip,mac)
		h.insert(self.ui.hostList)




if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.insertHost("aa","bb")
	mainWin.insertHost("tt","abcdf")
	mainWin.show()
	app.exec_()