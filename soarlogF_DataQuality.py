# -*- coding: utf-8 -*-
"""
Created on Thu May 10 10:39:00 2012

@author: tiago
"""

from PyQt4 import QtCore,QtGui,uic,QtSql
import os
import numpy as np

uipath = os.path.dirname(__file__)

class DataQuality():
    
    #dqStatus = ['','OK','WARN','FAIL']
    
################################################################################################
#
#
#    def __init__(self):
#        self.dqStatus = ['','OK','WARN','FAIL']
#
#
################################################################################################
        
################################################################################################
#
#
	def startDataQuality(self):

		session_CID = self.Session()
		self.dataQuality_ui = DataQualityUI()
		self.dqStatus = ['','OK','WARN','FAIL']
  
		projInfo = self.getProjects()
		#model = QtGui.QStandardItemModel()
		# generate test data for the example here...

		prj = np.append([''],projInfo[0])#np.append(projInfo[0],['all','Calibration'])
		
		for i in range(len(prj)):
			self.dataQuality_ui.comboBox.addItem(prj[i])
			
		
		#self.dataQuality_ui.buttonBox.addButton()
		
		self.connect(self.dataQuality_ui.buttonBox, QtCore.SIGNAL('clicked(QAbstractButton*)'), self.commitDataQuality)
		self.connect(self.dataQuality_ui.comboBox, QtCore.SIGNAL('currentIndexChanged(int)'), self.readDQProject)
		self.connect(self.dataQuality_ui.tabWidget, QtCore.SIGNAL('currentChanged(int)'),self.setDqMessage)
		self.dataQuality_ui.lineEditSemesterID.setText(self.semester_ID[:-4])
		self.dataQuality_ui.lineEditPathToData.setText(self.dataStorage.format(SID=self.semester_ID[:-4],PID=self.semester_ID.format('123')))
		#self.setAnimated(True)

		#model.setRootPath('/')
		#dataQuality_ui.dq_ui.columnDQ.setModel(model)
		#dataQuality_ui.dq_ui.columnDQ.setDragDropMode(QtGui.QAbstractItemView.DragDrop)

		#label = QtGui.QLabel('HELLO')
		#dataQuality_ui.dq_ui.columnDQ.setPreviewWidget(label)
		
		self.ui.tableDB.setSelectionMode(self.ui.tableDB.ExtendedSelection)

		self.dataQuality_ui.show()
		
		self.dataQuality_ui.exec_()
		
		self.ui.tableDB.setSelectionMode(self.ui.tableDB.SingleSelection)

#
#
################################################################################################
 
################################################################################################
#
#
	def setDqMessage(self,tab):
     
		if tab == 1:
        		self.dataQuality_ui.label.setText('1) Select the calibration files for this\nproject and select type.\n')
		elif tab == 2:
        		self.dataQuality_ui.label.setText('2) Select objects and fill Data Quality\n form.\n')
#
#
################################################################################################

################################################################################################
#
#
	def commitDataQuality(self):
	
		session = self.Session()
		query = session.query(self.Obj_DQ).filter(self.Obj_DQ.PID == str(self.dataQuality_ui.comboBox.currentText()))[:]

		if len(query) == 0:
			
			dqinf = {   'TYPE'		: '',\
					'SEMESTER'	: self.semester_ID[:-4],\
					'PID'		: str(self.dataQuality_ui.comboBox.currentText()),\
					'DATASET'	: '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))),\
					'DQNOTE'	: '',\
					'BIAS'		: str( self.dataQuality_ui.comboBias.currentIndex() ),\
					'DARK'		: str( self.dataQuality_ui.comboDark.currentIndex() ),\
					'FLATFIELD'	: str( self.dataQuality_ui.comboFlatField.currentIndex() ),\
					'BIASNOTE'	: str( self.dataQuality_ui.lineEditBias.text() )	,\
					'DARKNOTE'	: str( self.dataQuality_ui.lineEditDark.text() )			,\
					'FLATFIELDNOTE'	: str( self.dataQuality_ui.lineEditFlatField.text() )	,\
					'FROMDB'	: ''
					}
			info = self.Obj_DQ(**dqinf)
			session.add(info)
		else:
			
			query[0].BIAS = str( self.dataQuality_ui.comboBias.currentIndex() )
			query[0].DARK = str( self.dataQuality_ui.comboDark.currentIndex() )
			query[0].FLATFIELD = str( self.dataQuality_ui.comboFlatField.currentIndex() )
			query[0].BIASNOTE = self.dataQuality_ui.lineEditBias.text() 
			query[0].DARKNOTE = self.dataQuality_ui.lineEditDark.text() 
			query[0].FLATFIELDNOTE = self.dataQuality_ui.lineEditFlatField.text() 
			
		session.commit()

#
#
################################################################################################

################################################################################################
#
#

	def readDQProject(self,action):
	
		if not self.dataQuality_ui.tabWidget.isEnabled():
			self.dataQuality_ui.tabWidget.setEnabled(True)
			self.setUpCalibrationDQ()
			self.setUpCienceDQ()               
		
		session_CID = self.Session()
		query = session_CID.query(self.Obj_DQ).filter(self.Obj_DQ.PID == str(self.dataQuality_ui.comboBox.currentText()))[:]

		if len(query) > 0:
			self.dataQuality_ui.comboBias.setCurrentIndex( int( query[0].BIAS) )
			self.dataQuality_ui.comboDark.setCurrentIndex( int( query[0].DARK) )
			self.dataQuality_ui.comboFlatField.setCurrentIndex( int( query[0].FLATFIELD) )
			self.dataQuality_ui.lineEditBias.setText( str( query[0].BIASNOTE) )
			self.dataQuality_ui.lineEditDark.setText( str( query[0].DARKNOTE) )
			self.dataQuality_ui.lineEditFlatField.setText( str( query[0].FLATFIELDNOTE) )
		else:
			self.dataQuality_ui.comboBias.setCurrentIndex( 0 )
			self.dataQuality_ui.comboDark.setCurrentIndex( 0 )
			self.dataQuality_ui.comboFlatField.setCurrentIndex( 0 )
			self.dataQuality_ui.lineEditBias.setText( '' )
			self.dataQuality_ui.lineEditDark.setText( '' )
			self.dataQuality_ui.lineEditFlatField.setText( '' )
				
		print len(query),str(self.dataQuality_ui.comboBox.currentText())

#
#
################################################################################################

################################################################################################
#
#
	def setUpCalibrationDQ(self):

		self.setDqMessage(1)
  
		for status in self.dqStatus:
			self.dataQuality_ui.comboBias.addItem(status)
			self.dataQuality_ui.comboDark.addItem(status)
			self.dataQuality_ui.comboFlatField.addItem(status)

		self.dataQuality_ui.comboBias.setCurrentIndex(0)
		self.dataQuality_ui.comboDark.setCurrentIndex(0)
		self.dataQuality_ui.comboFlatField.setCurrentIndex(0)

		
		self.dataQuality_ui.fromDB.setEnabled(False)
		self.dataQuality_ui.comboFromDB.setEnabled(False)
		self.dataQuality_ui.lineEditFromDB.setEnabled(False)
		
		self.connect(self.dataQuality_ui.Bias, QtCore.SIGNAL('clicked()'), self.test)
		self.connect(self.dataQuality_ui.Dark, QtCore.SIGNAL('clicked()'), self.test)
		self.connect(self.dataQuality_ui.FlatField, QtCore.SIGNAL('clicked()'), self.test)
#
#
################################################################################################

################################################################################################
#
#
	def setUpCienceDQ(self):

		#self.setDqMessage(2)
  
		for status in self.dqStatus:
			self.dataQuality_ui.comboBox_5.addItem(status)
			self.dataQuality_ui.comboBox_6.addItem(status)
			
		self.dataQuality_ui.comboBox_5.setCurrentIndex(0)
		self.dataQuality_ui.comboBox_6.setCurrentIndex(0)
		
				
#
#
################################################################################################

################################################################################################
#
#
	def test(self):
	
		indexes = self.ui.tableDB.selectedIndexes()
  		
		session_CID = self.Session()
		

		for i in range(len(indexes)):
			fname = self.ui.tableDB.model().getData(indexes[i].row(),self.FilenameColumn)
        		query = session_CID.query(self.Obj_CID.id,self.Obj_CID.INSTRUME).filter(self.Obj_CID.FILENAME == fname)[:]
        		qInst = session_CID.query(self.Obj_INSTRUMENTS[query[0].INSTRUME].id).filter(self.Obj_INSTRUMENTS[query[0].INSTRUME].FILENAME.like('%'+fname))[:]
        		print fname,query[0].id,qInst[0].id,query[0].INSTRUME
        				
#
#
################################################################################################

################################################################################################
#
#

#
#
################################################################################################

class DataQualityUI(QtGui.QDialog):
	
################################################################################################
#
#	
	
	def __init__(self):
		
		QtGui.QDialog.__init__(self)
		
		##########################################################
		#
		# Set up preferences menu
		self.dq_ui = uic.loadUi(os.path.join(uipath,'dataquality.ui'),self)

#
#
################################################################################################

