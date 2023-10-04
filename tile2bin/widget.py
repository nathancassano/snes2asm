# -*- coding: utf-8 -*-

import os
import sys
import argparse

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import *

class Window(QMainWindow):
	def __init__(self, app):
		super().__init__()

		self.app = app

		self.setWindowTitle('tile2bin')

		self.tabs = QTabWidget()
		self.tabs.setDocumentMode(True)
		self.tabs.setTabsClosable(True)
		self.tabs.tabCloseRequested.connect(self.closeTab)
		self.tabs.setMinimumSize(600, 400);

		self.setCentralWidget(self.tabs)

		self.createActions()
		self.createDockWindows()

		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		self.createMenus()
		self.createToolBars()

		self.panelHidden = False

	def createActions(self):
		self.newAct = QAction(QIcon('images/new.png'), "&New", self, shortcut=QKeySequence.New, statusTip="Create a new file", triggered=self.newFile)

		self.openAct = QAction(QIcon('images/open.png'), "&Open...", self, shortcut=QKeySequence.Open, statusTip="Open an existing file", triggered=self.open)

		self.saveAct = QAction(QIcon('images/save.png'), "&Save", self, shortcut=QKeySequence.Save, statusTip="Save the document to disk", triggered=self.save)

		self.saveAsAct = QAction("Save &As...", self, shortcut=QKeySequence.SaveAs, statusTip="Save the document under a new name", triggered=self.saveAs)

		self.exitAct = QAction("E&xit", self, shortcut=QKeySequence.Quit, statusTip="Exit the application", triggered=QApplication.instance().closeAllWindows)

		self.cutAct = QAction(QIcon('images/cut.png'), "Cu&t", self, shortcut=QKeySequence.Cut, statusTip="Cut the current selection's contents to the clipboard", triggered=self.cut)

		self.copyAct = QAction(QIcon('images/copy.png'), "&Copy", self, shortcut=QKeySequence.Copy, statusTip="Copy the current selection's contents to the clipboard", triggered=self.copy)

		self.pasteAct = QAction(QIcon('images/paste.png'), "&Paste", self, shortcut=QKeySequence.Paste, statusTip="Paste the clipboard's contents into the current selection", triggered=self.paste)

		self.separatorAct = QAction(self)
		self.separatorAct.setSeparator(True)

		self.aboutAct = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)

		self.aboutQtAct = QAction("About &Qt", self, statusTip="Show the Qt library's About box", triggered=QApplication.instance().aboutQt)

	def createMenus(self):
		self.fileMenu = self.menuBar().addMenu("&File")
		self.fileMenu.addAction(self.newAct)
		self.fileMenu.addAction(self.openAct)
		self.fileMenu.addAction(self.saveAct)
		self.fileMenu.addAction(self.saveAsAct)
		#self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAct)

		self.editMenu = self.menuBar().addMenu("&Edit")
		self.editMenu.addAction(self.cutAct)
		self.editMenu.addAction(self.copyAct)
		self.editMenu.addAction(self.pasteAct)

		self.windowMenu = self.menuBar().addMenu("&Window")
		self.windowMenu.addAction(self.tileAct)
		#self.updateWindowMenu()
		#self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

		self.menuBar().addSeparator()

		self.helpMenu = self.menuBar().addMenu("&Help")
		self.helpMenu.addAction(self.aboutAct)
		self.helpMenu.addAction(self.aboutQtAct)

	def createToolBars(self):
		self.fileToolBar = self.addToolBar("File")
		self.fileToolBar.addAction(self.newAct)
		self.fileToolBar.addAction(self.openAct)
		self.fileToolBar.addAction(self.saveAct)

	def createDockWindows(self):
		dock = QDockWidget("Tiles")

		dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

		docklayout = QVBoxLayout()
		docklayout.addWidget(TileSetView(128, 128))
		docklayout.addWidget(PaletteView())

		container = QWidget()
		container.setLayout(docklayout)

		self.tileAct = dock.toggleViewAction()
		dock.setWidget(container)
		self.addDockWidget(Qt.RightDockWidgetArea, dock)
		#self.viewMenu.addAction(dock.toggleViewAction())

	def closeTab(self, index):
		answer = QMessageBox.StandardButton.Yes
		if self.app.docs[index].changed:
			answer = QMessageBox.question(self, 'Confirmation', 'Save changes?',
				QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
			)
		if answer == QMessageBox.StandardButton.Yes:
			self.app.docs[index].save()

		self.app.removeDoc(index)
		self.tabs.removeTab(index)

	def newFile(self):
		# TODO prompt detail dialog
		doc = TileDocument()
		self.addDoc(doc)

	def addDoc(self, doc):
		self.app.addDoc(doc)
		self.tabs.addTab(TileMapView(doc.pixWidth(), doc.pixHeight()), doc.title())

	def curDoc(self):
		index = self.tabs.currentIndex()
		return self.app.docs[index]
	
	def open(self):
		fileName, _ = QFileDialog.getOpenFileName(self, "Open Tile Map", '', "Tilemap (*.tilemap);;All Files (*)")
		if fileName:
			doc = TileDocument()
			try:
				doc.loadYaml(fileName)
			except Exception as e:
				QMessageBox.question(self, 'File', 'Error: %s' % e.message)
				return
				
			self.addDoc(doc)
			#self.statusBar().showMessage("File loaded", 2000)

	def save(self):
		self.curDoc().save()
		#self.statusBar().showMessage("File saved", 2000)

	def saveAs(self):
		fileName = QFileDialog.getSaveFileName(self, "Save Tile Map", self.curDoc().filepath(), "Tilemap (*.tilemap);;All Files (*)")
		if fileName:
			self.app.working_dir = os.path.dirname(os.path.realpath(fileName))
			self.app.filename = os.path.basename(fileName)
			self.save()

	def cut(self):
		pass

	def copy(self):
		pass

	def paste(self):
		pass

	def about(self):
		pass


class TileView(QGraphicsView):
	def __init__(self, width, height):
		self.scene = QGraphicsScene(0, 0, width, height)
		super().__init__(self.scene)

class TileSetView(TileView):
	def __init__(self, width, height):
		super().__init__(width, height)

class TileMapView(TileView):
	def __init__(self, width, height):
		super().__init__(width, height)

class PaletteView(QGraphicsView):
	def __init__(self):
		super().__init__()


