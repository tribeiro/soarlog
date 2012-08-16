# -*- coding: utf-8 -*-
"""
Created on Thu May 10 10:39:00 2012

@author: tiago
"""

from PyQt4 import QtCore,QtGui,uic,QtSql
from soarlogF_TableModel import *
import sqlalchemy
import frame_infos
import os,shutil
import numpy as np
import Queue,threading

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
  
		#
		# Add projects encountered in database
		#

		projInfo = self.getProjects()

		prj = np.append([''],projInfo[0])#np.append(projInfo[0],['all','Calibration'])
		dataset = '{date}-{PID}'
		
		for i in range(len(prj)):

			if i == 0 or len(prj[i]) == 3:
				self.dataQuality_ui.comboBox.addItem(prj[i])
			
			#
			# For each project, test if dataquality has already began. If not, setup automatic file indentification
			# and other miscelaneous
			#

			if len(prj[i]) == 3:
				query = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.DATASET == dataset.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(prj[i])))[:]
	
				if len(query) == 0:
					#
					# Data Quality has not began yet! Including project files in database
					#
					query = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like('%-'+prj[i]+'%' ) )[:]
					for ii in range(len(query)):
						iquery = qInst = session_CID.query(self.Obj_INSTRUMENTS[query[ii].INSTRUME].id).filter(self.Obj_INSTRUMENTS[query[ii].INSTRUME].FILENAME.like('%'+query[ii].FILENAME))[:]
						entry = self.Obj_FLDQ(id_tvDB=query[ii].id,
								      id_INSTRUME=iquery[0].id,
								      PID=self.semester_ID.format(prj[i]),
								      TYPE=query[ii].IMAGETYP,
								      SUBTYPE='night-obs',
								      FILENAME=query[ii].FILENAME,
								      PATH=query[ii].PATH,
								      DATASET=dataset.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(prj[i])))
						session_CID.add(entry)
				
		session_CID.commit()                 



#.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())))

	


		self.connect(self.dataQuality_ui.buttonBox, QtCore.SIGNAL('clicked(QAbstractButton*)'), self.commitDataQuality)
		self.connect(self.dataQuality_ui.comboBox, QtCore.SIGNAL('currentIndexChanged(int)'), self.readDQProject)
		self.connect(self.dataQuality_ui.comboBox_Object, QtCore.SIGNAL('currentIndexChanged(int)'), self.readDQObject)
		self.connect(self.dataQuality_ui.comboBox_config, QtCore.SIGNAL('currentIndexChanged(int)'), self.readCDQ)
		self.connect(self.dataQuality_ui.tabWidget, QtCore.SIGNAL('currentChanged(int)'),self.setDqMessage)
		self.connect(self.dataQuality_ui.pushButton_slog,QtCore.SIGNAL('clicked()'), self.genSOARLOG)
		self.connect(self.dataQuality_ui.pushButton_copy,QtCore.SIGNAL('clicked()'), self.copyProgramFiles)
		self.connect(self.dataQuality_ui.pushButton_exclude,QtCore.SIGNAL('clicked()'), self.excludeFilesFromProgram)
		self.connect(self.dataQuality_ui.pushButton_filtertable,QtCore.SIGNAL('clicked()'), self.filterMainTable)
		self.connect(self,QtCore.SIGNAL('copyProgress(int)'), self.updateCopyProgress)
		self.connect(self,QtCore.SIGNAL('copyDone()'), self.enableCopyButton)

		self.dataQuality_ui.lineEditSemesterID.setText(self.semester_ID[:-4])
		self.dataQuality_ui.lineEditPathToData.setText(self.dataStorage.format(SID=self.semester_ID[:-4],PID=self.semester_ID.format('123')))
		
		#self.setAnimated(True)

		self.tpfModel = SOLogTableModel([], ['FILENAME'],self ,commitDB=None)
		
		self.dataQuality_ui.tableProjectFiles.setModel(self.tpfModel)
		self.dataQuality_ui.tableProjectFiles.keyPressEvent = self.handleKeyEvent
		self.dataQuality_ui.tableProjectFiles.setSelectionMode(self.dataQuality_ui.tableProjectFiles.ExtendedSelection)
		
		font = QtGui.QFont("Courier New", 8)
		self.dataQuality_ui.tableProjectFiles.setFont(font)
		self.dataQuality_ui.tableProjectFiles.setAlternatingRowColors(True)
		hh = self.dataQuality_ui.tableProjectFiles.horizontalHeader()
		hh.setStretchLastSection(True)


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
		elif tab == 0:
				self.dataQuality_ui.label.setText('Configure semester and place for files.\n\n')
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
					'FROMDB'	: '',\
					'OBSTIME'	: 0.,\
					'VALIDTIME'	: 0.
					}
			info = self.Obj_DQ(**dqinf)
			session.add(info)
		else:
			
			query[0].BIAS = str( self.dataQuality_ui.comboBias.currentIndex() )
			query[0].DARK = str( self.dataQuality_ui.comboDark.currentIndex() )
			query[0].FLATFIELD = str( self.dataQuality_ui.comboFlatField.currentIndex() )
			query[0].BIASNOTE = str(self.dataQuality_ui.lineEditBias.text() )
			query[0].DARKNOTE = str(self.dataQuality_ui.lineEditDark.text() )
			query[0].FLATFIELDNOTE = str(self.dataQuality_ui.lineEditFlatField.text() )

		session.commit()
		
		query = session.query(self.Obj_FDQ).filter(self.Obj_FDQ.PID == str(self.dataQuality_ui.comboBox.currentText())).filter(self.Obj_FDQ.OBJECT == str(self.dataQuality_ui.comboBox_Object.currentText()))[:]

		if len(query) == 0 and len(str(self.dataQuality_ui.comboBox.currentText())) > 0:
			fwhm = 0. 
			try:
				fwhm = float( self.dataQuality_ui.lineEdit_7.text() )
			except:
				fwhm = 0.
				pass
			ell = 0.
			try:
				ell = float( self.dataQuality_ui.lineEdit_8.text() )
			except:
				ell = 0.
				pass

			dqinf = {	'SEMESTER'	: 	self.semester_ID[:-4]	,\
					'PID'		: 	str(self.dataQuality_ui.comboBox.currentText())		,\
					'DATASET'	: 	'{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))),\
					'OBJECT'	: str(self.dataQuality_ui.comboBox_Object.currentText()),\
					'FIELD'	: 		str( self.dataQuality_ui.comboBox_FIELD.currentIndex() ),\
					'FIELDNOTE'	: str( self.dataQuality_ui.lineEdit_5.text() )		,\
					#'CONFIG'	: str( self.dataQuality_ui.comboBox_6.currentIndex() )		,\
					#'CONFIGNOTE': str( self.dataQuality_ui.lineEdit_6.text() )		,\
					'FWHM'	: fwhm			,\
					'E'	      : ell}
			info = self.Obj_FDQ(**dqinf)
			session.add(info)
		else:

			fwhm = 0. 
			try:
				fwhm = float( self.dataQuality_ui.lineEdit_7.text() )
			except:
				fwhm = 0.
				pass
			ell = 0.
			try:
				ell = float( self.dataQuality_ui.lineEdit_8.text() )
			except:
				ell = 0.
				pass
			query[0].FIELD = str( self.dataQuality_ui.comboBox_FIELD.currentIndex() )
			query[0].FIELDNOTE = str( self.dataQuality_ui.lineEdit_5.text() )
			#query[0].CONFIG = str( self.dataQuality_ui.comboBox_6.currentIndex() )		
			#query[0].CONFIGNOTE = str( self.dataQuality_ui.lineEdit_6.text() )		
			query[0].FHWM = fwhm			
			query[0].E = ell

		querycfg = session.query(self.Obj_CDQ).filter(self.Obj_CDQ.OBJECT == str(self.dataQuality_ui.comboBox_Object.currentText())).filter( 
							  self.Obj_CDQ.PID == self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())) ).filter(self.Obj_CDQ.CONFIG == str(self.dataQuality_ui.comboBox_config.currentText()) ) [:]

		if len(querycfg) > 0:
	
			querycfg[0].CONFIGNOTE = str( self.dataQuality_ui.lineEdit_6.text() )
			querycfg[0].STATUS = str( self.dataQuality_ui.comboBox_6.currentIndex() )
							     
			
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
		else:
			self.commitDataQuality()	


		
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

		self.dataQuality_ui.comboBox_Object.clear()
		self.dataQuality_ui.comboBox_Object.addItem('')		
		self.dataQuality_ui.pushButton_filtertable.setEnabled(False)

		#
		# Setting up object list
		#

		query2 = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like('%-'+str(self.dataQuality_ui.comboBox.currentText())+'%'))[:]
		obj_list = self.getObjects(query2)

		dataset = '{date}-{PID}'

		query3 = session_CID.query(self.Obj_FDQ).filter(self.Obj_FDQ.DATASET == dataset.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(  str(self.dataQuality_ui.comboBox.currentText()) )))[:]

		for i in range(len(query3)):
			if len(query3[i].OBJECT) > 0 and query3[i].OBJECT not in obj_list:
				obj_list = np.append(obj_list,query3[i].OBJECT)

		for i in range(len(obj_list)):
			self.dataQuality_ui.comboBox_Object.addItem(obj_list[i])
			#
			# For each object check all available configurations
			#
			query_CDQ = session_CID.query(self.Obj_CDQ).filter(self.Obj_CDQ.OBJECT.like(obj_list[i]+'%'))[:]
			obsConf = []
			for j in range(len(query_CDQ)):
				obsConf.append(query_CDQ[j].CONFIG)

			query_CID = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like('%-'+str(self.dataQuality_ui.comboBox.currentText())+'%')).filter(self.Obj_CID.OBJECT.like(obj_list[i]+'%'))[:]
			frameobsConf = self.getConf(query_CID)

			for j in range(len(frameobsConf)):
				if frameobsConf[j] not in obsConf:
					obsConf.append(frameobsConf[j])
					vals = {'PID':self.semester_ID.format(  str(self.dataQuality_ui.comboBox.currentText() ) )  ,\
				'DATASET':dataset.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(  str(self.dataQuality_ui.comboBox.currentText()) ))		,\
				'NCONF'	        : 0		,\
				'OBJECT'	: obj_list[i]		,\
				'CONFIG'	: frameobsConf[j],\
				'STATUS'        : 0 ,\
				'CONFIGNOTE'    : ''		}
					entry = self.Obj_CDQ(**vals)
					session_CID.add(entry)
		session_CID.commit()
			
		
		self.dataQuality_ui.timeEdit.setTime(QtCore.QTime(*self.calcTime(str(self.dataQuality_ui.comboBox.currentText()))))


		#
		# Setting up object configuration
		#


		#
		# Setting up data quality files
		#
		query = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.DATASET == '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))))[:]


		for i in range(len(query)):
			self.tpfModel.insertRow(i)
			name_query = session_CID.query(self.Obj_CID.FILENAME).filter(self.Obj_CID.id == query[i].id_tvDB)[:]
			self.tpfModel.setData(self.tpfModel.createIndex(i,0),name_query[0].FILENAME,QtCore.Qt.DisplayRole)
			print name_query[0].FILENAME

		print len(query),str(self.dataQuality_ui.comboBox.currentText())

#
#
################################################################################################

################################################################################################
#
#

	def readDQObject(self,action):


		session_CID = self.Session()

		query = session_CID.query(self.Obj_FDQ).filter(self.Obj_FDQ.PID == str(self.dataQuality_ui.comboBox.currentText())).filter(self.Obj_FDQ.OBJECT == str(self.dataQuality_ui.comboBox_Object.currentText())) [:]
		
		if len(query) > 0 and len(str(self.dataQuality_ui.comboBox_Object.currentText())) > 0:
			self.dataQuality_ui.comboBox_FIELD.setCurrentIndex( int( query[0].FIELD) )
			self.dataQuality_ui.comboBox_6.setCurrentIndex( 0 )
			self.dataQuality_ui.lineEdit_5.setText( str( query[0].FIELDNOTE) )
			self.dataQuality_ui.lineEdit_6.setText( '' )
			self.dataQuality_ui.lineEdit_7.setText( str( query[0].FWHM) )
			self.dataQuality_ui.lineEdit_8.setText( str( query[0].E) )
		else:
			self.dataQuality_ui.comboBox_FIELD.setCurrentIndex( 0 )
			self.dataQuality_ui.comboBox_6.setCurrentIndex( 0 )
			self.dataQuality_ui.lineEdit_5.setText( '' )
			self.dataQuality_ui.lineEdit_6.setText( '' )
			self.dataQuality_ui.lineEdit_7.setText( '0.' )
			self.dataQuality_ui.lineEdit_8.setText( '0.' )
		
		querycfg = session_CID.query(self.Obj_CDQ).filter(self.Obj_CDQ.OBJECT == str(self.dataQuality_ui.comboBox_Object.currentText())).filter( 
								  self.Obj_CDQ.PID == self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())))[:]

		self.dataQuality_ui.comboBox_config.clear()
		self.dataQuality_ui.comboBox_config.addItem('')
		self.dataQuality_ui.comboBox_config.setCurrentIndex(0)
		self.dataQuality_ui.lineEdit_6.setText( '' )

		print len(querycfg),self.semester_ID.format(self.dataQuality_ui.comboBox.currentText()),str(self.dataQuality_ui.comboBox_Object.currentText())

		for i in range(len(querycfg)):
			self.dataQuality_ui.comboBox_config.addItem(querycfg[i].CONFIG)

		self.dataQuality_ui.pushButton_filtertable.setEnabled(True)
#
#
################################################################################################

################################################################################################
#
#
	def readCDQ(self,action):

		session_CID = self.Session()

		querycfg = session_CID.query(self.Obj_CDQ).filter(self.Obj_CDQ.OBJECT == str(self.dataQuality_ui.comboBox_Object.currentText())).filter( 
							  self.Obj_CDQ.PID == self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())) ).filter(
							  self.Obj_CDQ.CONFIG == str(self.dataQuality_ui.comboBox_config.currentText()) ) [:]

		if len(querycfg) == 1:
			self.dataQuality_ui.comboBox_6.setCurrentIndex( int(querycfg[0].STATUS ) )
			self.dataQuality_ui.lineEdit_6.setText( querycfg[0].CONFIGNOTE )
		elif len(querycfg) > 1:
			self.dataQuality_ui.comboBox_6.setCurrentIndex( 0 )#int(querycfg[0].STATUS ) )
			self.dataQuality_ui.lineEdit_6.setText( querycfg[0].CONFIGNOTE )
			print 'WARNING:', len(querycfg)
		else:
			self.dataQuality_ui.comboBox_6.setCurrentIndex( 0 )
			self.dataQuality_ui.lineEdit_6.setText( '' )

		return 0


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
		
		self.connect(self.dataQuality_ui.Bias, QtCore.SIGNAL('clicked()'), self.addBias)
		self.connect(self.dataQuality_ui.Dark, QtCore.SIGNAL('clicked()'), self.addDark)
		self.connect(self.dataQuality_ui.FlatField, QtCore.SIGNAL('clicked()'), self.addFlatField)
#
#
################################################################################################

################################################################################################
#
#
	def setUpCienceDQ(self):

		#self.setDqMessage(2)
  
		for status in self.dqStatus:
			self.dataQuality_ui.comboBox_FIELD.addItem(status)
			self.dataQuality_ui.comboBox_6.addItem(status)
			
		self.dataQuality_ui.comboBox_FIELD.setCurrentIndex(0)
		self.dataQuality_ui.comboBox_6.setCurrentIndex(0)
#
#
################################################################################################

################################################################################################
#
#
	def addBias(self):

		self.add2FLDQ('bias')

		return 0
#
#
################################################################################################

################################################################################################
#
#
	def addDark(self):

		self.add2FLDQ('dark')

		return 0
#
#
################################################################################################

################################################################################################
#
#

	def addFlatField(self):

		self.add2FLDQ('flatfield')

		return 0
	
				
#
#
################################################################################################

################################################################################################
#
#
	def add2FLDQ(self,ftype):
	
		indexes = self.ui.tableDB.selectedIndexes()
  		
		session_CID = self.Session()
		
		for i in range(len(indexes)):
			fname = self.ui.tableDB.model().getData(indexes[i].row(),self.FilenameColumn)
        		query = session_CID.query(self.Obj_CID.id,self.Obj_CID.INSTRUME,self.Obj_CID.PATH).filter(self.Obj_CID.FILENAME == fname)[:]
        		qInst = session_CID.query(self.Obj_INSTRUMENTS[query[0].INSTRUME].id).filter(self.Obj_INSTRUMENTS[query[0].INSTRUME].FILENAME.like('%'+fname))[:]
        		vals = {'id_tvDB':query[0].id,
				'id_INSTRUME' : qInst[0].id,
				'PID': self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())),
				'TYPE': ftype,
				'SUBTYPE':ftype,
				'FILENAME':fname,
				'PATH':query[0].PATH,
				'DATASET'	: '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())))}
        		entry = self.Obj_FLDQ(**vals)		
        		query2 = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.id_tvDB == entry.id_tvDB).filter(self.Obj_FLDQ.DATASET == entry.DATASET)[:]

        		if len(query2) == 0:
        			session_CID.add(entry)
				iidx = self.tpfModel.rowCount(None)
				self.tpfModel.insertRow(iidx)
				self.tpfModel.setData(self.tpfModel.createIndex(iidx,0),fname,QtCore.Qt.DisplayRole)


		session_CID.commit()                 
#
#
################################################################################################

################################################################################################
#
#

	def excludeFilesFromProgram(self):
		
		sIndex = self.dataQuality_ui.tableProjectFiles.selectedIndexes()

		session_CID = self.Session()

		for i in range(len(sIndex)-1,-1,-1):
			
			query = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.FILENAME == str(sIndex[i].data().toString() ) )[:]
			
			session_CID.delete(query[0])

			self.dataQuality_ui.tableProjectFiles.model().removeRow(sIndex[i].row(),sIndex[i])

		session_CID.commit()
		
		return 0

#
#
################################################################################################

################################################################################################
#
#

	def filterMainTable(self):

		self.dataQuality_ui.pushButton_filtertable.setEnabled(False)
		session_CID = self.Session()

		pid = str(self.dataQuality_ui.comboBox.currentText())
		obj = str(self.dataQuality_ui.comboBox_Object.currentText())

		query = session_CID.query(self.Obj_CID).filter(sqlalchemy.not_(self.Obj_CID.OBJECT.like('{0}%'.format(obj))))[:] 
		
#.filter(self.Obj_CID.FILENAME.like('%-{0}%'.format(pid)))
		#print len(query)
		for i in range(len(query)):
			self.ui.tableDB.setRowHidden(query[i].id-1,True)

		self.dataQuality_ui.pushButton_filtertable.setText('unFilter Table')
		self.connect(self.dataQuality_ui.pushButton_filtertable,QtCore.SIGNAL('clicked()'), self.unfilterMainTable)	
		self.dataQuality_ui.pushButton_filtertable.setEnabled(True)
#
#
################################################################################################

################################################################################################
#
#

	def unfilterMainTable(self):

		self.dataQuality_ui.pushButton_filtertable.setEnabled(False)
		for i in range(self.ui.tableDB.model().rowCount(None)):
			if self.ui.tableDB.isRowHidden(i):
				self.ui.tableDB.setRowHidden(i,False)

		self.dataQuality_ui.pushButton_filtertable.setText('Filter Table')
		self.connect(self.dataQuality_ui.pushButton_filtertable,QtCore.SIGNAL('clicked()'), self.filterMainTable)	
		self.dataQuality_ui.pushButton_filtertable.setEnabled(True)	
#
#
################################################################################################

################################################################################################
#
#
	def getConf(self,query):
		'''
Receives query list from ObjCID and return an array with string configuration. 
This function is only and interface to instrument selection function. After
figuring out which instrument is used it parses the query to a different function 
which handles the query and return a string with the instrument configuration. 
		'''

		obsConf = []

		for i in range(len(query)):

			obsConf.append( frame_infos.instConfDict[query[i].INSTRUME](query[i]) )
		
		return np.unique(obsConf)
#
#
################################################################################################

################################################################################################
#
#

	def genCalibrations(self,ipid):

		session_CID = self.Session()

		tmp_logCalib = '''
     TYPE: {type}
FROM FILE: {fimg}
  TO FILE: {limg}
   CONFIG: {conf}
'''

		logCalib = ''

		pid = self.semester_ID.format(ipid)

		query = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.PID==pid).filter(self.Obj_FLDQ.TYPE=='bias')[:]

		if len(query) > 0:
			query2 = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME == query[0].FILENAME)[:]

			logCalib += tmp_logCalib.format(type='BIAS',
							fimg=query[0].FILENAME,
							limg=query[-1].FILENAME,
							conf=self.getConf(query2)[0])

		query = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.PID==pid).filter(self.Obj_FLDQ.TYPE=='flatfield')[:]

		if len(query) > 0:
			query2 = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME == query[0].FILENAME)[:]

			logCalib += tmp_logCalib.format(type='FLAT',
							fimg=query[0].FILENAME,
							limg=query[-1].FILENAME,
							conf=self.getConf(query2)[0])
		
		query = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.PID==pid).filter(self.Obj_FLDQ.TYPE=='dark')[:]
		
		if len(query) > 0:
			query2 = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME == query[0].FILENAME)[:]

			logCalib += tmp_logCalib.format(type='DARK',
							fimg=query[0].FILENAME,
							limg=query[-1].FILENAME,
							conf=self.getConf(query2)[0])

		print '--> ',pid,logCalib

		return logCalib

#
#
################################################################################################

################################################################################################
#
#
	def genSOARLOG(self):

		projInfo = self.getProjects()

		for pid in projInfo[0]:

			solog_dir = os.path.join(self.dataStorage.format(SID=self.semester_ID[:-4],PID=self.semester_ID.format(pid)),
						 self.dir.split('/')[-1])

			if not os.path.exists(solog_dir):
				os.makedirs(solog_dir)

			solog_file = os.path.join(solog_dir,self.logfile)
			print solog_file

			fp = open(solog_file , 'w')

			try:
				hdr = subprocess.Popen(['logheader.py'],stdout=fp,stderr=fp)
				hdr.wait()
			except:
				hdr = 'No header\n'
				fp.write(hdr)
				pass

			fp.write(self.genCalibrations(str(pid)))
			
			fp.write(self.GetWeatherComment())

			#print str(pid)
			fp.write(self.GetFrameLog(str(pid)))
			
			fp.close()
		

		return 0
#
#
################################################################################################

################################################################################################
#
#
	def copyProgramFiles(self):

		session_CID = self.Session()

		projInfo = self.getProjects()

		p3 = 100./len(projInfo[0]) # Percent per project

		progress = 0.
		self.copy_queue = Queue.Queue()

		for pid in projInfo[0]:

			solog_dir = os.path.join(self.dataStorage.format(SID=self.semester_ID[:-4],PID=self.semester_ID.format(pid)),
						 self.dir.split('/')[-1])

			if not os.path.exists(solog_dir):
				os.makedirs(solog_dir)

			pfiles_query = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.PID==self.semester_ID.format(pid))[:]


			for i in range(len(pfiles_query)):
				self.copy_queue.put([os.path.join(str(pfiles_query[i].PATH),str(pfiles_query[i].FILENAME)),solog_dir])
				progress+=1
		self.dataQuality_ui.pushButton_copy.setEnabled(False)
		self.dataQuality_ui.progressBar_copy.setMaximum(progress)

		cthread = threading.Thread(target=self.runCopyQueue)
		cthread.start()
		
				#shutil.copy2(,solog_dir)
				#progress += p4
				#self.dataQuality_ui.progressBar_copy.setValue(int(progress))

		return 0

#
#
################################################################################################

################################################################################################
#
#

	def runCopyQueue(self):

		progress = 0
		lqueue = self.copy_queue.qsize()

		while not self.copy_queue.empty():
			record = self.copy_queue.get()
			#print record
			shutil.copy2(*record)
			progress+=1
			self.emit(QtCore.SIGNAL("copyProgress(int)"),progress)    
		self.emit(QtCore.SIGNAL("copyDone()"))    

		
#
#
################################################################################################

################################################################################################
#
#

	def updateCopyProgress(self,progress):
		self.dataQuality_ui.progressBar_copy.setValue(progress)	

#
#
################################################################################################

################################################################################################
#
#
	def enableCopyButton(self):
		self.dataQuality_ui.pushButton_copy.setEnabled(True)

################################################################################################
#
#
	def purge2MasterDB(self):
		
		return 0
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

