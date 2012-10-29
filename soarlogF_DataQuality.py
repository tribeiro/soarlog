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
import Queue,threading,logging
import time
import bz2

uipath = os.path.dirname(__file__)

class DataQuality():
    
    #dqStatus = ['','OK','WARN','FAIL']

	_separator = '\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n'

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
					query = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like('%-'+prj[i]+'%' ) ).filter(sqlalchemy.not_(self.Obj_CID.INSTRUME.like('%NOTE%')))[:]
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
		self.connect(self.dataQuality_ui.validTime, QtCore.SIGNAL('timeChanged(QTime)'), 
			     self.dataQuality_ui.obsTime.setMinimumTime)
		self.connect(self.dataQuality_ui.obsTime, QtCore.SIGNAL('timeChanged(QTime)'), 
			     self.dataQuality_ui.validTime.setMaximumTime)
		self.connect(self.dataQuality_ui.comboBox, QtCore.SIGNAL('currentIndexChanged(int)'), self.readDQProject)
		self.connect(self.dataQuality_ui.comboBox_Object, QtCore.SIGNAL('currentIndexChanged(int)'), self.readDQObject)
		self.connect(self.dataQuality_ui.comboBox_config, QtCore.SIGNAL('currentIndexChanged(int)'), self.readCDQ)
		self.connect(self.dataQuality_ui.tabWidget, QtCore.SIGNAL('currentChanged(int)'),self.setDqMessage)
		self.connect(self.dataQuality_ui.pushButton_slog,QtCore.SIGNAL('clicked()'), self.genSOARLOG)
		self.connect(self.dataQuality_ui.pushButton_sRep,QtCore.SIGNAL('clicked()'), self.saveReport)
		self.connect(self.dataQuality_ui.pushButton_copy,QtCore.SIGNAL('clicked()'), self.copyProgramFiles)
		self.connect(self.dataQuality_ui.pushButton_exclude,QtCore.SIGNAL('clicked()'), self.excludeFilesFromProgram)
		self.connect(self.dataQuality_ui.pushButton_filtertable,QtCore.SIGNAL('clicked()'), self.filterMainTable)
		self.connect(self.dataQuality_ui.pushButton_RunReplace,QtCore.SIGNAL('clicked()'), self.runUpdateSelectedColumn)
		self.connect(self.dataQuality_ui.pushButton_loadfromfile,QtCore.SIGNAL('clicked()'), self.loadUpdateSelectedColumnFromFile)
		self.connect(self.dataQuality_ui.pushButton_save2file,QtCore.SIGNAL('clicked()'), self.saveSelectedColumnToFile)
		self.connect(self.dataQuality_ui.comboBiasConf, QtCore.SIGNAL('currentIndexChanged(int)'), self.readBiasConf)
		self.connect(self.dataQuality_ui.comboDarkConf, QtCore.SIGNAL('currentIndexChanged(int)'), self.readDarkConf)
		self.connect(self.dataQuality_ui.comboFlatConf, QtCore.SIGNAL('currentIndexChanged(int)'), self.readFlatConf)

		#self.connect(self.dataQuality_ui.comboBox_FIELD, QtCore.SIGNAL('currentIndexChanged(int)'), self.commitDataQuality)
		#self.connect(self.dataQuality_ui.comboBox_6, QtCore.SIGNAL('currentIndexChanged(int)'), self.commitDataQuality)
		#
		# Never link comboBox_config to commitDataQuality. It will fail since it changes the object before you can 
		# commit to the database.
		#
		self.connect(self.dataQuality_ui.lineEdit_5,QtCore.SIGNAL('editingFinished()'), self.commitDataQuality)
		self.connect(self.dataQuality_ui.lineEdit_6,QtCore.SIGNAL('editingFinished()'), self.commitDataQuality)
		self.connect(self.dataQuality_ui.lineEdit_7,QtCore.SIGNAL('editingFinished()'), self.commitDataQuality)
		self.connect(self.dataQuality_ui.lineEdit_8,QtCore.SIGNAL('editingFinished()'), self.commitDataQuality)
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
		selectionMode = self.ui.tableDB.ExtendedSelection
		self.ui.tableDB.setSelectionMode(selectionMode)
#		self.connect(selectionMode,QtCore.SIGNAL("currentChanged(const QModelIndex &, const QModelIndex &)"),
#			     self.testclick)
		self.connect(self.ui.tableDB,QtCore.SIGNAL('clicked(QModelIndex)'), 
			     self.updateSelectedColumn)


		self.dataQuality_ui.show()
		
		self.dataQuality_ui.exec_()
		
		self.ui.tableDB.setSelectionMode(self.ui.tableDB.SingleSelection)
		self.disconnect(self.ui.tableDB,QtCore.SIGNAL('clicked(QModelIndex)'), 
			     self.testclick)


#
#
################################################################################################
	def testclick(self,a):
#		self.commitDataQuality()
		logging.debug('ckicked')
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
		elif tab == 4:
			self.dataQuality_ui.label.setText('''Replace information on table database and file header (name).
Do NOT remove '?' when doing 'matched' selection (specially for
filenames) unless you REALLY know what you are doing. 
''')	
#
#
################################################################################################

################################################################################################
#
#
	def commitDataQuality(self):
	
		logging.debug(str(self.dataQuality_ui.comboBox.currentText()))

		self.commitCalibrationDataQuality()
		
		session = self.Session()
		query = session.query(self.Obj_DQ).filter(self.Obj_DQ.PID == str(self.dataQuality_ui.comboBox.currentText()))[:]

		vtime = 0.
		otime = 0.
		if len(query) == 0:
			
			vtime = self.dataQuality_ui.validTime.time().hour() + self.dataQuality_ui.validTime.time().minute() / 60.
			otime = self.dataQuality_ui.obsTime.time().hour() + self.dataQuality_ui.obsTime.time().minute() / 60.
			dqinf = {   'TYPE'		: '',\
					'SEMESTER'	: self.semester_ID[:-4],\
					'PID'		: str(self.dataQuality_ui.comboBox.currentText()),\
					'DATASET'	: '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))),\
					'DQNOTE'	: '',\
					'BIAS'		: '',\
					'DARK'		: '',\
					'FLATFIELD'	: '',\
					'BIASNOTE'	: ''	,\
					'DARKNOTE'	: ''			,\
					'FLATFIELDNOTE'	: ''	,\
					'FROMDB'	: '',\
					'OBSTIME'	: otime,\
					'VALIDTIME'	: vtime
					}
			info = self.Obj_DQ(**dqinf)
			session.add(info)
		else:
			
			vtime = float( self.dataQuality_ui.validTime.time().hour() + self.dataQuality_ui.validTime.time().minute() / 60. )
			otime = float( self.dataQuality_ui.obsTime.time().hour() + self.dataQuality_ui.obsTime.time().minute() / 60. )
			query[0].BIAS = '0'
			query[0].DARK = '0'
			query[0].FLATFIELD = '0'
			query[0].BIASNOTE = ''
			query[0].DARKNOTE = ''
			query[0].FLATFIELDNOTE = ''
			query[0].VALIDTIME = vtime
			query[0].OBSTIME = otime

		session.commit()

		query = session.query(self.Obj_FDQ).filter(self.Obj_FDQ.PID == str(self.dataQuality_ui.comboBox.currentText())).filter(self.Obj_FDQ.OBJECT == str(self.dataQuality_ui.comboBox_Object.currentText()))[:]

		if len(query) == 0 and len(str(self.dataQuality_ui.comboBox.currentText())) > 0:
			fwhm = 0. 
			try:
				fwhm = float( self.dataQuality_ui.lineEdit_7.text() )
			except:
				logging.debug('Could not convert fhwm to float... got {0}'.format(self.dataQuality_ui.lineEdit_7.text()))
				fwhm = 0.
				pass
			ell = 0.
			try:
				ell = float( self.dataQuality_ui.lineEdit_8.text() )
			except:
				logging.debug('Could not convert elipticity to float... got {0}'.format(self.dataQuality_ui.lineEdit_8.text()))
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
				logging.debug('Could not convert fhwm to float... got {0}'.format(self.dataQuality_ui.lineEdit_7.text()))
				fwhm = 0.
				pass
			ell = 0.
			try:
				ell = float( self.dataQuality_ui.lineEdit_8.text() )
			except:
				logging.debug('Could not convert elipticity to float... got {0}'.format(self.dataQuality_ui.lineEdit_8.text()))
				ell = 0.
				pass

			query[0].FIELD = str( self.dataQuality_ui.comboBox_FIELD.currentIndex() )
			query[0].FIELDNOTE = str( self.dataQuality_ui.lineEdit_5.text() )
			#query[0].CONFIG = str( self.dataQuality_ui.comboBox_6.currentIndex() )		
			#query[0].CONFIGNOTE = str( self.dataQuality_ui.lineEdit_6.text() )		
			query[0].FWHM = fwhm			
			query[0].E = ell

		querycfg = session.query(self.Obj_CDQ).filter(self.Obj_CDQ.OBJECT == str(self.dataQuality_ui.comboBox_Object.currentText())).filter( 
							  self.Obj_CDQ.PID == self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())) ).filter(self.Obj_CDQ.CONFIG == str(self.dataQuality_ui.comboBox_config.currentText()) ) [:]

		if len(querycfg) > 0:
	
			querycfg[0].CONFIGNOTE = str( self.dataQuality_ui.lineEdit_6.text() )
			querycfg[0].STATUS = str( self.dataQuality_ui.comboBox_6.currentIndex() )
							     

		query = session.query(self.Obj_RDB).filter(self.Obj_RDB.DATASET == '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))))[:]

		if len(query) == 0:
			#
			# Nothing on the database. Creating default values
			#
			query2 = session.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like('%-{0}%'.format(str(self.dataQuality_ui.comboBox.currentText()))))[:]
			instru_list = np.unique([query2[i].INSTRUME for i in range(len(query2))])
			instru =''
			if len(instru_list) == 1:
				instru = instru_list[0]
			else:
				for i in range(len(instru_list)):
					instru = instru+instru_list[i]+'/'
					
			vals = {'PID':self.semester_ID.format(  str(self.dataQuality_ui.comboBox.currentText() ) )  ,\
				'PI' : 'None' ,\
				'INSTRUME' :  instru,\
				'SETUP':'',\
				'TIMESPENT':otime,\
				'TIMEVALID':vtime,\
				'DATASET':'{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))),\
				'REPORT': ''}
			entry = self.Obj_RDB(**vals)
			session.add(entry)
		else:
			query[0].PI = str( self.dataQuality_ui.PI.text() )
			query[0].INSTRUME = str( self.dataQuality_ui.INSTRUME.text() )
			query[0].SETUP = str( self.dataQuality_ui.SETUP.text() )
			query[0].TIMESPENT = otime
			query[0].TIMEVALID = vtime
			query[0].REPORT = str( self.dataQuality_ui.REPORT.toPlainText() )

	
		session.commit()

		self.makeReport()
				

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
			self.setUpCalibrationDQProject()


		session_CID = self.Session()
		query = session_CID.query(self.Obj_DQ).filter(self.Obj_DQ.PID == str(self.dataQuality_ui.comboBox.currentText()))[:]

		if len(query) > 0:
			vtime = query[0].VALIDTIME
			otime = query[0].OBSTIME

			logging.debug('Obs Time: {0}\nValid Time: {1}'.format(otime,vtime))
			if otime > 0.:
				self.dataQuality_ui.obsTime.setMinimumTime(QtCore.QTime(0.,0.))
				self.dataQuality_ui.obsTime.setMaximumTime(QtCore.QTime(23.,0.))
				self.dataQuality_ui.obsTime.setTime(QtCore.QTime( int(otime) , int( np.ceil(60.*(otime-np.floor(otime)) ) ) ))
				self.dataQuality_ui.validTime.setMinimumTime(QtCore.QTime(0.,0.))
				self.dataQuality_ui.validTime.setMaximumTime(QtCore.QTime(23.,0.))
				self.dataQuality_ui.validTime.setTime(QtCore.QTime( int(vtime) , int( np.ceil(60.*(vtime-np.floor(vtime)) ) ) ) )
			else:
				self.dataQuality_ui.obsTime.setMinimumTime(QtCore.QTime(0.,0.))
				self.dataQuality_ui.obsTime.setMaximumTime(QtCore.QTime(23.,0.))
				self.dataQuality_ui.obsTime.setTime(QtCore.QTime(*self.calcTime(str(self.dataQuality_ui.comboBox.currentText()))))
				self.dataQuality_ui.validTime.setMinimumTime(QtCore.QTime(0.,0.))
				self.dataQuality_ui.validTime.setMaximumTime(QtCore.QTime(23.,0.))
				self.dataQuality_ui.validTime.setTime(QtCore.QTime(*self.calcTime(str(self.dataQuality_ui.comboBox.currentText()))))

		else:
			self.dataQuality_ui.obsTime.setMinimumTime(QtCore.QTime(0.,0.))
			self.dataQuality_ui.obsTime.setMaximumTime(QtCore.QTime(23.,0.))
			self.dataQuality_ui.obsTime.setTime(QtCore.QTime(*self.calcTime(str(self.dataQuality_ui.comboBox.currentText()))))
			self.dataQuality_ui.validTime.setMinimumTime(QtCore.QTime(0.,0.))
			self.dataQuality_ui.validTime.setMaximumTime(QtCore.QTime(23.,0.))
			self.dataQuality_ui.validTime.setTime(QtCore.QTime(*self.calcTime(str(self.dataQuality_ui.comboBox.currentText()))))

		self.dataQuality_ui.comboBox_Object.clear()
		self.dataQuality_ui.comboBox_Object.addItem('')		
		self.dataQuality_ui.pushButton_filtertable.setEnabled(False)

#		self.dataQuality_ui.validTime.setMaximumTime(self.dataQuality_ui.obsTime.time())
#		self.dataQuality_ui.obsTime.setMinimumTime(self.dataQuality_ui.validTime.time())


		#
		# Seting up object list
		#

		query2 = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like('%-'+str(self.dataQuality_ui.comboBox.currentText())+'%')).filter(sqlalchemy.not_(self.Obj_CID.INSTRUME.like('NOTE')))[:]
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

			query_CID = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like('%-'+str(self.dataQuality_ui.comboBox.currentText())+'%')).filter(self.Obj_CID.OBJECT.like(obj_list[i]+'%')).filter(sqlalchemy.not_(self.Obj_CID.INSTRUME.like('NOTE')))[:]
			frameobsConf,frameobsCount = self.getConf(query_CID)

			for j in range(len(frameobsConf)):
				if frameobsConf[j] not in obsConf:
					obsConf.append(frameobsConf[j])
					vals = {'PID':self.semester_ID.format(  str(self.dataQuality_ui.comboBox.currentText() ) )  ,\
				'DATASET':dataset.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(  str(self.dataQuality_ui.comboBox.currentText()) ))		,\
				'NCONF'	        : frameobsCount[j]		,\
				'OBJECT'	: obj_list[i]		,\
				'CONFIG'	: frameobsConf[j],\
				'STATUS'        : 0 ,\
				'CONFIGNOTE'    : ''		}
					entry = self.Obj_CDQ(**vals)
					session_CID.add(entry)
		
		#
		# Setting up object configuration
		#


		self.fillProjectFiles()

		#
		# Setting up data data quality report
		#

		query = session_CID.query(self.Obj_RDB).filter(self.Obj_RDB.DATASET == '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))))[:]

		if len(query) == 0:
			#
			# Nothing done yet. Creating basic table
			# 
			instru_list = np.unique([query2[i].INSTRUME for i in range(len(query2))])
			instru =''
			if len(instru_list) == 1:
				instru = instru_list[0]
			else:
				for i in range(len(instru_list)):
					instru = instru+instru_list[i]+'/'
					

			vals = {'PID':self.semester_ID.format(  str(self.dataQuality_ui.comboBox.currentText() ) )  ,\
				'PI' : 'None' ,\
				'INSTRUME' :  instru,\
				'SETUP':'',\
				'TIMESPENT':0.,\
				'TIMEVALID':0.,\
				'DATASET':'{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))),\
				'REPORT': ''}
			entry = self.Obj_RDB(**vals)
			session_CID.add(entry)
			
			self.dataQuality_ui.PI.setText(vals['PI'])
			self.dataQuality_ui.INSTRUME.setText(vals['INSTRUME'])
			self.dataQuality_ui.SETUP.setText(vals['SETUP'])
			self.dataQuality_ui.REPORT.setText(vals['REPORT'])
			
		else:
			#
			# Already started reading from DB.
			#
			self.dataQuality_ui.PI.setText(        query[0].PI      )
			self.dataQuality_ui.INSTRUME.setText(query[0].INSTRUME)
			self.dataQuality_ui.SETUP.setText(     query[0].SETUP   )
			self.dataQuality_ui.REPORT.setText(    query[0].REPORT  )

		session_CID.commit()
			

#
#
################################################################################################

################################################################################################
#
#

	def fillProjectFiles(self):
		session_CID = self.Session()
		#
		# Setting up data quality files
		#
		query = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.DATASET == '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))))[:]


		nrow = self.tpfModel.rowCount(None)

		if nrow > len(query):
			self.tpfModel.removeRows(len(query)-1,nrow-len(query))
			logging.debug('More row than needed will delete some.')

		for i in range(len(query)):
			if i >= nrow:
				logging.debug('Increasing row in table.')
				self.tpfModel.insertRow(i)
			name_query = session_CID.query(self.Obj_CID.FILENAME).filter(self.Obj_CID.id == query[i].id_tvDB)[:]
			self.tpfModel.setData(self.tpfModel.createIndex(i,0),name_query[0].FILENAME,QtCore.Qt.DisplayRole)
			#logging.debug( name_query[0].FILENAME )


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
			logging.debug('fwhm = {0} , ell = {1}'.format(query[0].FWHM,query[0].E))
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

		logging.debug('{0} {1} {2}'.format( len(querycfg),self.semester_ID.format(self.dataQuality_ui.comboBox.currentText()),str(self.dataQuality_ui.comboBox_Object.currentText()) ))

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
			logging.debug( 'WARNING: {0}'.format( len(querycfg)))
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


		self.setUpCalibrationDQProject()

#
#
################################################################################################

################################################################################################
#
#

	def setUpCalibrationDQProject(self):

		self.dataQuality_ui.comboBias.setCurrentIndex( 0 )
		self.dataQuality_ui.comboDark.setCurrentIndex( 0 )
		self.dataQuality_ui.comboFlatField.setCurrentIndex( 0 )
		self.dataQuality_ui.lineEditBias.setText( '' )
		self.dataQuality_ui.lineEditDark.setText( '' )
		self.dataQuality_ui.lineEditFlatField.setText( '' )

		session = self.Session()
		cb_cal = [self.dataQuality_ui.comboBiasConf,
			  self.dataQuality_ui.comboDarkConf,
			  self.dataQuality_ui.comboFlatConf ]
		ctype = ['bias','dark','flatfield']

		for i in range(len(ctype)):
			qq = session.query(self.Obj_CDQ).filter(self.Obj_CDQ.PID == self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))).filter(self.Obj_CDQ.DATASET == '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())))).filter(self.Obj_CDQ.OBJECT == ctype[i])[:]
			cb_cal[i].clear()
			cb_cal[i].addItem('')
			for j in range(len(qq)):
				cb_cal[i].addItem(str(qq[j].CONFIG))
			cb_cal[i].setCurrentIndex(0)

#
#
################################################################################################

################################################################################################
#
#

	def commitCalibrationDataQuality(self):

		cb_calconf = [self.dataQuality_ui.comboBiasConf,
			      self.dataQuality_ui.comboDarkConf,
			      self.dataQuality_ui.comboFlatConf ]
		cb_calstat = [self.dataQuality_ui.comboBias,
			      self.dataQuality_ui.comboDark,
			      self.dataQuality_ui.comboFlatField ]
		cb_caltext = [self.dataQuality_ui.lineEditBias,
			      self.dataQuality_ui.lineEditDark,
			      self.dataQuality_ui.lineEditFlatField ]
		ctype = ['bias','dark','flatfield']

		session = self.Session()

		for i in range(len(ctype)):
			qq = session.query(self.Obj_CDQ).filter(self.Obj_CDQ.PID == self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))).filter(self.Obj_CDQ.DATASET == '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())))).filter(self.Obj_CDQ.OBJECT == ctype[i]).filter(self.Obj_CDQ.CONFIG == str(cb_calconf[i].currentText()))[:]
			logging.debug('{0} {1}'.format(ctype[i],len(qq)))
			if len(qq) > 0:
				qq[0].CONFIGNOTE = str(cb_caltext[i].text())
				qq[0].STATUS = str(cb_calstat[i].currentIndex())
				session.commit()

			if len(qq) > 1 :
				logging.debug('WARNING: Found duplicate configuration for {0}'.format(ctype[i]))
			
		
#
#
################################################################################################

################################################################################################
#
#

	def readBiasConf(self):

		self.readCalConf('bias')

		return 0

#
#
################################################################################################

################################################################################################
#
#
	def readDarkConf(self):

		self.readCalConf('dark')
		return 0

#
#
################################################################################################

################################################################################################
#
#

	def readFlatConf(self):

		self.readCalConf('flatfield')
		return 0

#
#
################################################################################################

################################################################################################
#
#

	def readCalConf(self,ctype):


		cb_calconf = {'bias'     :self.dataQuality_ui.comboBiasConf,
			      'dark'     :self.dataQuality_ui.comboDarkConf,
			      'flatfield':self.dataQuality_ui.comboFlatConf }
		cb_calstat = {'bias'     :self.dataQuality_ui.comboBias,
			      'dark'     :self.dataQuality_ui.comboDark,
			      'flatfield':self.dataQuality_ui.comboFlatField }
		cb_caltext = {'bias'     :self.dataQuality_ui.lineEditBias,
			      'dark'     :self.dataQuality_ui.lineEditDark,
			      'flatfield':self.dataQuality_ui.lineEditFlatField }

		cb_calstat[ctype].setCurrentIndex(0)
		cb_caltext[ctype].setText('')

		session = self.Session()

		qq = session.query(self.Obj_CDQ).filter(self.Obj_CDQ.PID == self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))).filter(self.Obj_CDQ.DATASET == '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())))).filter(self.Obj_CDQ.OBJECT == ctype).filter(self.Obj_CDQ.CONFIG == str(cb_calconf[ctype].currentText()))[:]

		logging.debug('-> {0} {1}'.format(ctype,str(cb_calconf[ctype].currentText())))
		for i in range(len(qq)):
			logging.debug('--> {0} {1}'.format(qq[0].OBJECT,qq[0].CONFIG))

		if len(qq) > 0:
			logging.debug('--> {0} {1}'.format(int(qq[0].STATUS),str(qq[0].CONFIGNOTE)))
			cb_calstat[ctype].setCurrentIndex(int(qq[0].STATUS))
			cb_caltext[ctype].setText(str(qq[0].CONFIGNOTE))

		return 0

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

		new = self.add2FLDQ('bias')

		self.add2CDQ('bias',new)

		self.setUpCalibrationDQProject()

		return 0
#
#
################################################################################################

################################################################################################
#
#
	def addDark(self):

		new = self.add2FLDQ('dark')

		self.add2CDQ('dark', new)

		self.setUpCalibrationDQProject()

		return 0
#
#
################################################################################################

################################################################################################
#
#

	def addFlatField(self):

		new = self.add2FLDQ('flatfield')

		self.add2CDQ('flatfield',new)

		self.setUpCalibrationDQProject()

		return 0
	
#
#
################################################################################################

################################################################################################
#
#
	def add2CDQ(self,obj=None,new=0):

		indexes = self.ui.tableDB.selectedIndexes()

		session = self.Session()

		query = []
		for i in range(len(indexes)):

			idx = indexes[i].row() # table row should be equal to id
			qq = session.query(self.Obj_CID).filter(self.Obj_CID.id == idx+1)[:]
			query.append(qq[0])

		fconf,nconf = self.getConf(query,obj)

		for i in range(len(fconf)):

			_obj = obj
			if not obj:
				_obj = str(self.dataQuality_ui.comboBox_Object.currentText())
			else:
				logging.debug('OBJECT will be changed to user specified {0}'.format(_obj))


			vals = {'PID': self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())),
				'DATASET':'{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))),
				'NCONF' : nconf[i],
				'OBJECT': _obj,
				'CONFIG': fconf[i],
				'STATUS': '0',
				'CONFIGNOTE' : ''}

			entry = self.Obj_CDQ(**vals)
			qq = session.query(self.Obj_CDQ).filter(self.Obj_CDQ.PID == entry.PID).filter(self.Obj_CDQ.DATASET == entry.DATASET).filter(self.Obj_CDQ.OBJECT == entry.OBJECT).filter(self.Obj_CDQ.CONFIG == entry.CONFIG)[:]

			if len(qq) == 0:
				logging.debug('Entry not in database')
				session.add(entry)
				session.commit()
			elif new > 0:
				logging.debug('Entry already in database, but {0} new files added.'.format(new))
				for i in range(len(qq)):
					qq[0].NCONF += new
				session.commit()
			else:
				logging.debug('Entry already in database')

			

		
#
#
################################################################################################

################################################################################################
#
#
	def add2FLDQ(self,ftype):
	
		indexes = self.ui.tableDB.selectedIndexes()
  		
		session_CID = self.Session()
		
		new = 0

		for i in range(len(indexes)):
			idx = self.ui.tableDB.model().index(indexes[i].row(),self.FilenameColumn)
			fname = self.ui.tableDB.model().data(idx)
			if type(fname) == QtCore.QVariant:
				fname = str(fname.toString())
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
				new += 1
        			session_CID.add(entry)
				iidx = self.tpfModel.rowCount(None)
				self.tpfModel.insertRow(iidx)
				self.tpfModel.setData(self.tpfModel.createIndex(iidx,0),fname,QtCore.Qt.DisplayRole)


		session_CID.commit()    
		return new
#
#
################################################################################################

################################################################################################
#
#

	def excludeFilesFromProgram(self):
		
		sIndex = self.dataQuality_ui.tableProjectFiles.selectedIndexes()

		session_CID = self.Session()

		ctype = ['bias','dark','flatfield']

		for i in range(len(sIndex)-1,-1,-1):
			
			query = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.PID == self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))).filter(self.Obj_FLDQ.FILENAME == str(sIndex[i].data().toString() ) )[:]

			query2 = session_CID.query(self.Obj_CID).filter(self.Obj_CID.id == query[0].id_tvDB)[:]

			conf,nfiles = self.getConf(query2)

			query2 = session_CID.query(self.Obj_CDQ).filter(self.Obj_FLDQ.PID == self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))).filter(self.Obj_CDQ.CONFIG.like(conf[0]+'%')).filter(self.Obj_CDQ.OBJECT == query[0].TYPE)[:]

			logging.debug('{0} {1} {2} {3}'.format(query2[0].OBJECT,query2[0].CONFIG,query2[0].NCONF, query[0].TYPE))
			
			if len(query2) > 0 :

				logging.debug('NCONF = {0}...'.format(query2[0].NCONF))

				if int(query2[0].NCONF) > 1 :
					#
					# If there is still frames left with this configuration on CDQ just decrement NCONF (the files couter).
					#
					query2[0].NCONF = query2[0].NCONF-1
					logging.debug('Decrementing NCONF {0}...'.format(query2[0].NCONF))
				else:
					#
					# Otherwise, delete entire entry from CDQ
					#
					session_CID.delete(query2[0])
					logging.debug('Deleting entry from CDQ')
					
				session_CID.commit()
			
			session_CID.delete(query[0])

			self.tpfModel.removeRow(sIndex[i].row())

		session_CID.commit()

		self.setUpCalibrationDQProject()
		
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

		for i in range(len(query)):
			self.ui.tableDB.setRowHidden(query[i].id-1,True)

		self.dataQuality_ui.pushButton_filtertable.setText('unFilter Table')
		self.disconnect(self.dataQuality_ui.pushButton_filtertable,QtCore.SIGNAL('clicked()'), self.filterMainTable)
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
		for i in range(self.ui.tableDB.model().rowCount()):
			if self.ui.tableDB.isRowHidden(i):
				self.ui.tableDB.setRowHidden(i,False)

		self.dataQuality_ui.pushButton_filtertable.setText('Filter Table')
		self.disconnect(self.dataQuality_ui.pushButton_filtertable,QtCore.SIGNAL('clicked()'), self.unfilterMainTable)
		self.connect(self.dataQuality_ui.pushButton_filtertable,QtCore.SIGNAL('clicked()'), self.filterMainTable)	
		self.dataQuality_ui.pushButton_filtertable.setEnabled(True)	
#
#
################################################################################################

################################################################################################
#
#
	def getConf(self,query,obj=None):
		'''
Receives query list from ObjCID and return an array with string configuration. 
This function is only and interface to instrument selection function. After
figuring out which instrument is used it parses the query to a different function 
which handles the query and return a string with the instrument configuration. 
		'''

		obsConf = []

		for i in range(len(query)):

			conf = frame_infos.instConfDict[query[i].INSTRUME](query[i])
			if obj:
				conf += ' ' 
				conf += str(query[i].OBJECT)
			obsConf.append( conf )

				
		
		uConf = np.unique(obsConf)
		nConf = np.zeros(len(uConf))
		for i in range(len(uConf)):
			mask = np.array(obsConf) == uConf[i]
			nConf[i] = len(mask[mask])
			#if query[i].INSTRUME == 'Spartan IR Camera':
			#	nConf[i] /= 4
		
		return uConf,nConf
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

		ctype = ['bias','flatfield','dark']

		for cal in ctype:
			query = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.PID==pid).filter(self.Obj_FLDQ.TYPE==cal)[:]

			if len(query) > 0:
				query2 = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME == query[0].FILENAME)[:]
				conf = self.getConf(query2,cal)[0]
				logging.debug('--> {0} | {1} | {2}'.format(len(query2),conf,query[0].FILENAME))
				if len(conf) == 0:
					query2 = session_CID.query(self.Obj_CID).filter(self.Obj_CID.id == query[0].id_tvDB)[:]
					conf = self.getConf(query2,cal)[0]
					logging.debug('---> {0} | {1} | {2}'.format(len(query2),conf,query[0].FILENAME))

				logCalib += tmp_logCalib.format(type=str.upper(cal),
								fimg=query[0].FILENAME,
								limg=query[-1].FILENAME,
								conf=conf[0])


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
			logging.debug(solog_file)

			fp = open(solog_file , 'w')

			try:
				fp2 = open(self.logfile,'r')
				for i in range(15):
					fp.write(fp2.readline())
				fp2.close()
				#hdr = subprocess.Popen(['logheader.py'],stdout=fp,stderr=fp)
				#hdr.wait()
			except:
				hdr = 'No header\n'
				fp.write(hdr)
				pass

			fp.write(self.genCalibrations(str(pid)))
			
			fp.write(self.GetWeatherComment())

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

		progress = 0.
		self.copy_queue = Queue.Queue()

		for pid in projInfo[0]:

			solog_dir = os.path.join(self.dataStorage.format(SID=self.semester_ID[:-4],PID=self.semester_ID.format(pid)),
						 self.dir.split('/')[-1])

			if not os.path.exists(solog_dir):
				os.makedirs(solog_dir)

			pfiles_query = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.PID==self.semester_ID.format(pid))[:]


			for i in range(len(pfiles_query)):
				pfiles_cid = session_CID.query(self.Obj_CID).filter(self.Obj_CID.id == pfiles_query[i].id_tvDB)[0]
				self.copy_queue.put([os.path.join(str(pfiles_cid.PATH),str(pfiles_cid.FILENAME)),solog_dir])
				progress+=1

		self.dataQuality_ui.progressBar_copy.setMaximum(progress)

		self.dataQuality_ui.pushButton_copy.setEnabled(False)
		self.dataQuality_ui.pushButton_copy.setText('Cancel')

		self.disconnect(self.dataQuality_ui.pushButton_copy,QtCore.SIGNAL('clicked()'), self.copyProgramFiles)
		self.connect(self.dataQuality_ui.pushButton_copy,QtCore.SIGNAL('clicked()'), self.stopCopyProgramFiles)

		self.cthread = threading.Thread(target=self.runCopyQueue)
		self.cthread_stop = threading.Event()

		logging.debug('Start thread')
		self.cthread.start()
		self.dataQuality_ui.pushButton_copy.setEnabled(True)
		
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

		import grenameF
		import good_class
		grenameF.i.soar(_doprint=0)
		grenameF.i.soi(_doprint=0)

		session_CID = self.Session()
		session_Master = self.MasterSession()

		progress = 0
		lqueue = self.copy_queue.qsize()

		while not self.copy_queue.empty():
			record = self.copy_queue.get()

			logging.debug( 'Copying {0} -> {1} ...'.format(*record))

			query = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME == os.path.basename(record[0]))[:]
			newFileNAME = os.path.basename(record[0])
			newFilePATH = record[1]

			if len(query) > 0:
				queryInstrume = session_CID.query(self.Obj_INSTRUMENTS[query[0].INSTRUME]).filter(self.Obj_INSTRUMENTS[query[0].INSTRUME].FILENAME == record[0])[:]
				queryFLDQ = session_CID.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.FILENAME == query[0].FILENAME)[:]

			else:
				queryInstrume = []
				queryFLDQ = []
			
			if len(queryInstrume) == 1 and os.path.dirname(record[0]) != record[1] and len(queryFLDQ) > 0:

				try:
					shutil.copy2(*record)

					#query[0].PATH = record[1]
					#queryInstrume[0].FILENAME = os.path.join(record[1],query[0].FILENAME)
					inFile =  os.path.join(record[1],query[0].FILENAME)
					t_index = self.ui.tableDB.model().sourceModel().createIndex(query[0].id-1,self.FilenameColumn)
					
					if query[0].INSTRUME == 'Goodman Spectrograph':
						_image_ = good_class.Single(os.path.join(record[1],query[0].FILENAME))
						gname = grenameF.Rename(_image_,True)

						newFileNAME = os.path.basename(gname)
						newFilePATH = os.path.dirname(gname)
						
						os.remove(inFile)
						inFile = gname
						#self.ui.tableDB.model().sourceModel().setData(t_index,os.path.basename(gname),QtCore.Qt.DisplayRole)
					if query[0].INSTRUME == 'SOI':
						logging.debug('SOIFIXHEADER: {0}'.format(query[0].FILENAME))
						grenameF.i.soifixheader(input=os.path.join(record[1],query[0].FILENAME))
					
					#session_CID.commit()
				
					file(inFile+".bz2", "wb").write(bz2.compress(file(inFile, "rb").read()))
					os.remove(inFile)
					newFileNAME = newFileNAME + '.bz2'
					inFile = inFile+'.bz2'
					
					#self.ui.tableDB.model().sourceModel().setData(t_index,os.path.basename(inFile),QtCore.Qt.DisplayRole)
					logging.debug(inFile)
					queryMaster = session_Master.query(self.Obj_CID).filter(self.Obj_CID.FILENAME == newFileNAME).filter(self.Obj_CID.PATH == newFilePATH)[:]
					if len(queryMaster) == 0:
						logging.debug('Adding file {0} to master database...'.format(newFileNAME))
						
						newEntry = self.Obj_CID()
						for c in self.file_table_CID.c:
							if not c.name.endswith('id'):
								setattr(newEntry, c.name, getattr(query[0], c.name))

						newEntry.FILENAME = newFileNAME
						newEntry.PATH = os.path.abspath(newFilePATH)

						session_Master.add(newEntry)

						newEntry = self.Obj_INSTRUMENTS[query[0].INSTRUME]()
						for c in self.file_table_INSTRUMENTS[query[0].INSTRUME].c:
							if not c.name.endswith('id'):
								setattr(newEntry, c.name, getattr(queryInstrume[0], c.name))

						newEntry.FILENAME = os.path.join(os.path.abspath(newFilePATH),newFileNAME)

						session_Master.add(newEntry)

					#queryInstrume[0].FILENAME = inFile
										

				except:
					logging.exception('Exception {0}'.format(sys.exc_info()[2]))
					pass
									

			progress+=1
			self.emit(QtCore.SIGNAL("copyProgress(int)"),progress)    
			session_Master.commit()

			if self.cthread_stop.isSet():
				self.emit(QtCore.SIGNAL("copyProgress(int)"),0)    
				logging.debug('runCopy: Queue size: {0} [Emptying queue]'.format( self.copy_queue.qsize() ))
				with self.copy_queue.mutex:
					self.copy_queue.queue.clear()
				logging.debug( 'runCopy: Queue size should be zero: {0}'.format(self.copy_queue.qsize() ))

		self.cthread_stop.clear()
		logging.debug('Copy done')
		self.emit(QtCore.SIGNAL("copyDone()"))    

		
#
#
################################################################################################

################################################################################################
#
#

	def stopCopyProgramFiles(self):
		self.cthread_stop.set()
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

		self.dataQuality_ui.pushButton_copy.setText('Copy Files')
		self.disconnect(self.dataQuality_ui.pushButton_copy,QtCore.SIGNAL('clicked()'), self.stopCopyProgramFiles)
		self.connect(self.dataQuality_ui.pushButton_copy,QtCore.SIGNAL('clicked()'), self.copyProgramFiles)

#
#
################################################################################################

################################################################################################
#
#

	def makeReport(self):

		session = self.Session()

		q_cal = session.query(self.Obj_DQ).filter(self.Obj_DQ.PID == str(self.dataQuality_ui.comboBox.currentText()))[:]
		q_repo = session.query(self.Obj_RDB).filter(self.Obj_RDB.DATASET == '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))))[:]

		if len(q_repo) == 0:
			logging.debug('No information on database for project {0}'.format(str(self.dataQuality_ui.comboBox.currentText())))
			return -1
		#
		# start with calibrations
		#
		_repo = '''
- Calibrations:

'''
		_calNote = '\n'
		Count = [0,
			 1,
			 1,
			 1]

		ctype = ['bias','dark','flatfield']

		for i in range(len(ctype)):
			qq = session.query(self.Obj_CDQ).filter(self.Obj_CDQ.PID == self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText()))).filter(self.Obj_CDQ.DATASET == '{date}-{PID}'.format(date=self.dir.split('/')[-1],PID=self.semester_ID.format(str(self.dataQuality_ui.comboBox.currentText())))).filter(self.Obj_CDQ.OBJECT == ctype[i])[:]
			
			for j in range(len(qq)):
				
				config = qq[j].CONFIG
				nf = qq[j].NCONF				

				note = self.dqStatus[int(qq[j].STATUS)]
				cnote = ''
				if len(qq[j].CONFIGNOTE) > 1:
					note += '{0}'.format(Count[int(qq[j].STATUS)])
					cnote = '{0}: {1}\n'.format(note,qq[j].CONFIGNOTE)
					Count[int(qq[j].STATUS)] += 1
		
				if int(qq[j].STATUS) > 0:
					_calNote = _calNote + cnote
					_repo += '     {ctype}: {CONFIG} {NFILES} [{STAT}]\n'.format(CONFIG = config,
												     NFILES = int(nf),
												     STAT=note,
												     ctype=str.upper(ctype[i]))


		_repo +=self._separator

		_repo += '''
- Science:

'''
		
		query = session.query(self.Obj_FDQ).filter(self.Obj_FDQ.PID==str(self.dataQuality_ui.comboBox.currentText()))[:]

		for i in range(len(query)):
			if int(query[i].FIELD) > 0:
				_repo += '''
- {OBJ}:
\tFIELD: [{FLD}]
'''.format(OBJ=query[i].OBJECT,FLD=self.dqStatus[int(query[i].FIELD)])
				query2 = session.query(self.Obj_CDQ).filter(self.Obj_CDQ.DATASET == query[i].DATASET).filter(self.Obj_CDQ.OBJECT == query[i].OBJECT)[:]
				for j in range(len(query2)):
					if int(query2[j].STATUS) > 0:
						note = self.dqStatus[int(query2[j].STATUS)]
						if len(query2[j].CONFIGNOTE) > 1:
							note += '{0}'.format(Count[int(query2[j].STATUS)])
							_calNote = _calNote + '{0}: {1}\n'.format(note,query2[j].CONFIGNOTE)
							Count[int(query2[j].STATUS)] += 1
							
						_repo += '\t{CFG} {NFLS} [{STAT}]\n'.format(CFG=query2[j].CONFIG,
											    NFLS=query2[j].NCONF,
											    STAT=note)
				_repo += '\tSeeing = {0}" | E = {1}\n'.format(query[i].FWHM,query[i].E)
		_repo += self._separator

		_repo += '''
- Notes:

'''

		_repo += _calNote



		#
		# Finishing
		#
		self.dataQuality_ui.REPORT.setText( _repo )
		q_repo[0].REPORT = _repo

		session.commit()

#
#
################################################################################################

################################################################################################
#
#

	def updateSelectedColumn(self):

		sIndex = self.ui.tableDB.selectedIndexes()

		self.dataQuality_ui.lineEdit_SelectedCol.setText(self.ui.tableDB.model().headerData(sIndex[0].column(),QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole).toString())

		firstCol = sIndex[0]
		workCol = []
		for i in range(len(sIndex)):
			if sIndex[i].column() == firstCol.column():
				workCol.append(sIndex[i])
		self.unmatch = False
		self.matchVals = []
		if firstCol.column() in self.ExtraEditableColumns:
			self.dataQuality_ui.pushButton_RunReplace.setEnabled(True)
			self.dataQuality_ui.pushButton_loadfromfile.setEnabled(True)
			fval = self.ui.tableDB.model().data(firstCol).toString()
			flen = len(fval)

#			self.dataQuality_ui.lineEdit_ComunVal.setText(flen)
#			self.dataQuality_ui.lineEdit_ReplaceBy.setText(flen)

			self.unmatch = False
			for i in range(len(workCol)):
				if len(self.ui.tableDB.model().data(workCol[i]).toString()) != flen:
					self.dataQuality_ui.lineEdit_ComunVal.setText('<UNMACHED>')
					self.dataQuality_ui.lineEdit_ReplaceBy.setText(fval)
					self.unmatch = True
					self.dataQuality_ui.textEdit_BatchDialog.setText('''Unmached tables. This hapens when the values have different sizes. The entire values will be replaced by the value in the \'replace by\' box. 

Warning: Do not use this style for filename replacement.
''')
					break
			if not self.unmatch:

				for i in range(len(fval)):
					_tmpMatch = []
					_flagUnMatch = False
					for j in range(len(workCol)):
						oval = self.ui.tableDB.model().data(workCol[j]).toString()[i]
						_tmpMatch.append(oval)
						if fval[i] != oval:# or _flagUnMatch:
							fval = fval[:i] + '?' + fval[i+1:]
							_flagUnMatch = True
							#break
					if _flagUnMatch:
						self.matchVals.append(_tmpMatch)

				self.dataQuality_ui.lineEdit_ComunVal.setText(fval)
				self.dataQuality_ui.lineEdit_ReplaceBy.setText(fval)
				self.dataQuality_ui.textEdit_BatchDialog.setText('''Mached tables. This hapens when the values have same sizes. All '?' in the 'replace by' box will be replaced by the appropriate value on each element in the other they appear. 

Warning: If you are doing filename replacement do not delete any '?' in the user field, unless you REALLY REALLY know what you are doing. Otherwise, feel free to do so, knowing that I will replace the remaining '?' by the order they appear in the entry.
''')
				
			
		else:
			self.dataQuality_ui.pushButton_RunReplace.setEnabled(False)
			self.dataQuality_ui.pushButton_loadfromfile.setEnabled(False)
			self.dataQuality_ui.lineEdit_ComunVal.setText('')
			self.dataQuality_ui.lineEdit_ReplaceBy.setText('')

#
#
################################################################################################

################################################################################################
#
#
	def runUpdateSelectedColumn(self):

		sIndex = self.ui.tableDB.selectedIndexes()
		workCol = []

		for i in range(len(sIndex)):
			if sIndex[i].column() == sIndex[0].column():
				workCol.append(sIndex[i])

		if self.unmatch:
			for i in range(len(workCol)):
				self.CommitDBTable(workCol[i],str(self.dataQuality_ui.lineEdit_ReplaceBy.text()))
				self.ui.tableDB.model().setData(workCol[i],str(self.dataQuality_ui.lineEdit_ReplaceBy.text()),QtCore.Qt.DisplayRole)
		else:
			for i in range(len(workCol)):
				newVal = str(self.dataQuality_ui.lineEdit_ReplaceBy.text())
				oldVal = self.ui.tableDB.model().data(workCol[i])
				for j in range(len(self.matchVals)):
					idx = str(newVal).find('?')
					if idx >= 0:
						newVal = newVal[:idx] + self.matchVals[j][i] + newVal[idx+1:]
				self.CommitDBTable(workCol[i],newVal)
				self.ui.tableDB.model().setData(workCol[i],newVal,QtCore.Qt.DisplayRole)
		self.dataQuality_ui.textEdit_BatchDialog.setText('Replace done.')

#
#
################################################################################################

################################################################################################
#
#
	def loadUpdateSelectedColumnFromFile(self):
		
		filename = str(QtGui.QFileDialog.getOpenFileName(self, 
								 'Selecione arquivo com entradas para colunas',
								 filter='Text files (*.txt)'))
		if filename:
			logging.debug(filename)
			fcont = np.loadtxt(filename,dtype='S',usecols=(0,),ndmin=1)
			sIndex = self.ui.tableDB.selectedIndexes()
			workCol = []
			for i in range(len(sIndex)):
				if sIndex[i].column() == sIndex[0].column():
					workCol.append(sIndex[i])

			if len(fcont) != len(workCol):
				self.dataQuality_ui.textEdit_BatchDialog.setText('Size of input list \'{0}\'[{1}] and selected columns [{2}] does not match.'.format(os.path.basename(filename),len(fcont),len(workCol)))
			else:
				mess = '''File {0} selected and successfuly readed. 

{1}
'''
				self.dataQuality_ui.textEdit_BatchDialog.setText(mess.format(os.path.basename(filename),'Running...'))
				for i in range(len(workCol)):
					logging.debug(fcont[i])
					self.CommitDBTable(workCol[i],str(fcont[i]))
					self.ui.tableDB.model().setData(workCol[i],str(fcont[i]),QtCore.Qt.DisplayRole)

				self.dataQuality_ui.textEdit_BatchDialog.setText(mess.format(os.path.basename(filename),'Done...'))				

		else:
			logging.debug('No file selected')
			self.dataQuality_ui.textEdit_BatchDialog.setText('No file selected.')

		
#
#
################################################################################################

################################################################################################
#
#
	def saveSelectedColumnToFile(self):
		
		filename = str(QtGui.QFileDialog.getSaveFileName(self, 
								 'Selecione arquivo para salvar dados das colunas',
								 filter='Text files (*.txt)'))
		if filename:
			sIndex = self.ui.tableDB.selectedIndexes()
			workCol = []

			for i in range(len(sIndex)):
				if sIndex[i].column() == sIndex[0].column():
					workCol.append(sIndex[i])

			self.dataQuality_ui.textEdit_BatchDialog.setText('Saving {0} data from column {1} to {2}.'.format(len(workCol),
															  str(self.tm.headerData(sIndex[0].column(),
																	     QtCore.Qt.Horizontal,
																	     QtCore.Qt.DisplayRole).toString())
															  , filename))
			fp = open(filename,'w')
			for i in range(len(workCol)):
				fp.write('{0}\n'.format(str(self.ui.tableDB.model().data(workCol[i]).toString() )))
			fp.close()

		else:
			self.dataQuality_ui.textEdit_BatchDialog.setText('No file selected.')

		
#
#
################################################################################################

################################################################################################
#
#
	def saveReport(self):
		
		filename = str(QtGui.QFileDialog.getSaveFileName(self, 
								 'Selecione arquivo para salvar data quality.',
								 filter='Text files (*.txt)'))

		self.purgeDQ2MDB()

		if filename:
			session = self.Session()

			q_repo = session.query(self.Obj_RDB)[:]

			fp = open(filename,'w')

			for i in range(len(q_repo)):
				tm_h = q_repo[i].TIMESPENT
				tm_m = int( (tm_h - np.floor(tm_h))*60.)
				otime = '{hh:02d}:{mm:02d}'.format(hh=int(np.floor(tm_h)),mm=tm_m)
				tm_h = q_repo[i].TIMEVALID
				tm_m = int( (tm_h - np.floor(tm_h))*60.)
				vtime = '{hh:02d}:{mm:02d}'.format(hh=int(np.floor(tm_h)),mm=tm_m)
				fp.write('''   PROJECT: {PID}
        PI: {PI}
INSTRUMENT: {INST}
  OBS-TIME: {OTIME}
VALID-TIME: {VTIME}
'''.format(PID=q_repo[i].PID,PI=q_repo[i].PI,INST=q_repo[i].INSTRUME,OTIME=otime,VTIME=vtime))

				fp.write(self._separator)

				fp.write(q_repo[i].REPORT)
				
				fp.write(self._separator)
				fp.write(self._separator)
		else:
			return -1

		return 0

#
#
################################################################################################

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
	def purgeDQ2MDB(self):

		session = self.Session()
		sMaster = self.MasterSession()

		q_repo = session.query(self.Obj_RDB)[:]

		for i in range(len(q_repo)):
			mq_rep = sMaster.query(self.Obj_RDB).filter(self.Obj_RDB.PID == q_repo[i].PID).filter(self.Obj_RDB.DATASET == q_repo[i].DATASET)[:]
			if len(mq_rep) > 0:
				mq_rep[0].clone(q_repo[i],self.file_table_RDB)
			else:
				mq_rep = self.Obj_RDB()
				mq_rep.clone(q_repo[i],self.file_table_RDB)
				sMaster.add(mq_rep)

		q_cal = session.query(self.Obj_DQ)[:]

		for i in range(len(q_cal)):
			mq_cal = sMaster.query(self.Obj_DQ).filter(self.Obj_DQ.DATASET == q_cal[i].DATASET)[:]
			
			if len(mq_cal) == 0:
				mq_cal = self.Obj_DQ()
				mq_cal.clone(q_cal[i],self.file_table_DQ)
				sMaster.add(mq_cal)
			else:
				mq_cal[0].clone(q_cal[i],self.file_table_DQ)

		q_fdq = session.query(self.Obj_FDQ)[:]

		for i in range(len(q_fdq)):
			if len(q_fdq[i].OBJECT) > 1:
				mq_fdq = sMaster.query(self.Obj_FDQ).filter(self.Obj_FDQ.OBJECT == q_fdq[i].OBJECT).filter(self.Obj_FDQ.PID == q_fdq[i].PID)[:]
			
				if len(mq_fdq) == 0:
					mq_fdq = self.Obj_FDQ()
					mq_fdq.clone(q_fdq[i],self.file_table_frameDQ)
					sMaster.add(mq_fdq)
				else:
					mq_fdq[0].clone(q_fdq[i],self.file_table_frameDQ)


		q_fldq = session.query(self.Obj_FLDQ)[:]

		for i in range(len(q_fldq)):
			mq_fldq = sMaster.query(self.Obj_FLDQ).filter(self.Obj_FLDQ.id_tvDB == q_fldq[i].id_tvDB)[:]
			
			if len(mq_fldq) == 0:
				mq_fldq = self.Obj_FLDQ()
				mq_fldq.clone(q_fldq[i],self.file_table_frameListDQ)
				sMaster.add(mq_fldq)
			else:
				mq_fldq[0].clone(q_fldq[i],self.file_table_frameListDQ)

		q_cdq = session.query(self.Obj_CDQ)[:]

		for i in range(len(q_cdq)):
			mq_cdq = sMaster.query(self.Obj_CDQ).filter(self.Obj_CDQ.DATASET == q_cdq[i].DATASET).filter(self.Obj_CDQ.CONFIG == q_cdq[i].CONFIG)[:]
			
			if len(mq_cdq) == 0:
				mq_cdq = self.Obj_CDQ()
				mq_cdq.clone(q_cdq[i],self.file_table_CDQ)
				sMaster.add(mq_cdq)
			else:
				mq_cdq[0].clone(q_cdq[i],self.file_table_CDQ)


		sMaster.commit()

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

