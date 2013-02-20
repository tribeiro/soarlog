# Author				version		Up-date			Description
#------------------------------------------------------------------------
# T. Ribeiro (SOAR)		0.0			09 Jun 2011     Creation

'''
soarlogF - This file provide class definition for SoarLog, a GUI based 
application for in-site automated production of observations log.

-> Automatic loads incoming calibration/science frames.
-> Add observer note to specific frame or time.
-> Version with multitheads

Ribeiro, T. 2011.
'''

#from soarlogF_GUI import *
from soarlogF_TableModel import *
from mylineedit import *
import sys,os,shutil

import thread

import os,sys,subprocess
import numpy as np
import pyfits


from soarlogF_watch import *
from soarlogF_watch import __FALSEWATCHER__

from dbComF import *
from soarlogF_DataQuality import *
from soarlogF_DataTransfer import *

import time

import ds9 

#try:
#	from pyraf.iraf import set as IrafSet
#	from pyraf.iraf import display
#	from pyraf.iraf import mscred
#	from pyraf.irafglobals import IrafError
#	IrafSet(stdimage='imt4096')
#except:
#	pass

uipath = os.path.dirname(__file__)

def LongestCommonSubstring(S1, S2):
    M = [[0]*(1+len(S2)) for i in xrange(1+len(S1))]
    longest, x_longest = 0, 0
    for x in xrange(1,1+len(S1)):
        for y in xrange(1,1+len(S2)):
            if S1[x-1] == S2[y-1]:
                M[x][y] = M[x-1][y-1] + 1
                if M[x][y]>longest:
                    longest = M[x][y]
                    x_longest  = x
            else:
                M[x][y] = 0
    return S1[x_longest-longest: x_longest]

		
class SoarLog(QtGui.QMainWindow,soarDB,DataQuality,DataTransfer):

	def __init__(self,*args):
	
		super(SoarLog, self).__init__()
		self.Queue = args[0]
		self.recordQueue = args[1]
		self.commitLock = threading.Lock()
		#self.emmitFileEventLock = threading.Lock()
		
	##########################################################
	# See if configuration directory exists. Create one 
	# otherwise.
	#
		self._CFGFilePath_ = os.path.join(os.path.expanduser('~/'),'.soarlogGUI_v2')
	
		if not os.path.exists(self._CFGFilePath_):
			os.mkdir(self._CFGFilePath_)
		
		self._CFGFiles_ = { 'OrderInfo' : 'orderInfo.txt'	,\
							'ShowInfo' : 'showPar.txt'		,\
							'LogHeader' : 'logheader.txt'	,\
							'ColumnWidth' : 'colwidth.txt'}
		
	#
	#
	#
	##########################################################
	
		self.dir = ''
		self.logfile = 'SOARLOG_%s.txt'
		self.semester_ID = 'SO2013A-%s'
		self.dataCalib = '/data/data_calib/2013A/SO2013A-%s.txt'
		self.dataStorage = '/data/data_%(SID)s/%(PID)s'
		self.dbname = 'soarlog_%s.db'
		self.masterDBName = '/data/database/soarlog_database.db' # master database.
		self.CommentColumn = 16
		self.FilenameColumn = 12
		self.ImtypeColumn = 11
		self.ExtraEditableColumns = [0,11,12,16]
		self.LocalTime = -4
		self.AskFile2Watch()
		self.dqStatus = ['','OK','WARN','FAIL']

		self.logfile = self.logfile%(self.dir.split('/')[-1])
		self.dbname  = self.dbname%(self.dir.split('/')[-1])
		soarDB.__init__(self,self.Queue)
		#DataQuality.__init__()
#		self.imageTYPE = ['','OBJECT','FLAT','DFLAT','BIAS','ZERO','DARK','COMP','FAILED','Object']
		self.imageTYPE = databaseF.frame_infos.imageTYPE
		
		self.header_CID = databaseF.frame_infos.tvDB.keys()
		
		self.header_dict = { 'OSIRIS' : databaseF.frame_infos.OSIRIS_ID.keys(),\
							 'Goodman Spectrograph' : databaseF.frame_infos.GOODMAN_ID.keys() ,\
							  'SOI' : databaseF.frame_infos.SOI_ID.keys()}
		#self.__FileWeatherComments__ = '.weatherComments.txt'
		#if not os.path.isfile(self.__FileWeatherComments__):
		#	_file = open(self.__FileWeatherComments__,'w')
		#	_file.write("No info available\n")
		#self.__WeatherComments__ = "No info available\n"

		self.currentSelectedItem = 0 #QtCore.QModelIndex()

		self.start()

		#self.initDB()
		
		#self.AskFile2Watch()
		
		#self.initGUI()
		
		#self.initWatch()
		
#
#
################################################################################################

################################################################################################
#
#
	def AddSelectFrame(self):
		        

		fn = QtGui.QFileDialog.getOpenFileNames(self, 'Open file',self.dir)
		
		ff =  [str(i) for i in fn]
		
		for f in ff:
			self.Queue.put(f)
		
		self.wake.set()

#		self.model.select()

#		self.model.insertRows(self.model.rowCount(),1)		
#		self.model.select()
		
		#self.AddFrame(fn)
		

#
#
################################################################################################

################################################################################################
#
#

	def updateTable(self,infos):
	
            index = self.ui.tableDB.model().rowCount()
		
            #self.emmitFileEventLock.acquire()
            
            try:
                test = self.ui.tableDB.model().sourceModel().insertRow(index) #,self.tm.createIndex(index,-1))

                check = np.zeros(len(infos)) == 0
                for i in range(len( infos ) ):
                    #logging.debug(infos[i])
                    iidx = self.ui.tableDB.model().sourceModel().createIndex(index,i)
                    check[i] = self.ui.tableDB.model().sourceModel().setData(iidx,infos[i],QtCore.Qt.DisplayRole)
                    #check[i] = self.ui.tableDB.model().setData(SOLogTableModel.createIndex(index,i,self.tm) ,infos[i])
                

                #self.ui.tableDB.model().setData(self.ui.tableDB.model().index(index,0) ,infos[0])
            except:
                logging.debug('Exception in updateTable')
                logging.debug(sys.exc_info()[1])
                pass
            #finally:
            #    self.emmitFileEventLock.release()
#
#
################################################################################################
				
################################################################################################
#
#
	def reloadTable(self,frame):
		
		session_CID = self.Session()
		
		#self.model.select()
				
		if self.ui.actionGot_to_last_frame.isChecked():
			scrollBar = self.ui.tableDB.verticalScrollBar();
			scrollBar.setValue(scrollBar.maximum());
		
		if self.ui.actionDisplay_last_frame.isChecked() and frame != -1:
			d = None
			_targets = ds9.ds9_targets()
		
			# Check if ds9 is opened
			if not _targets == 0:
				try:
					d = ds9.ds9()
				except:
					return -1
			else: 
				d = ds9.ds9(_targets[1].split(' ')[1])
			d.set('preserve regions yes')
                        d.set('preserve pan yes')
                        d.set('preserve scale yes')
		
			if os.path.isfile(frame):
				
				try:
					query = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME == os.path.basename(frame))[0]
				except:
					return -1
				try:
					if query.INSTRUME == 'SOI':
					#mscred.mscdisplay(frame,1)
						for iext in range(4):
							data = pyfits.getdata(frame,ext=iext+1)
						d.set('file mosaicimage wcs %s'%(frame))
						if self.ui.actionZoom_to_fit.isChecked():
							d.set('zoom to fit')
						if self.ui.actionZscale.isChecked():
							d.set('scale mode zscale')
						return 0
					elif query.INSTRUME == 'Spartan IR Camera':
						query2 = session_CID.query(self.Obj_INSTRUMENTS['Spartan IR Camera']).filter(self.Obj_INSTRUMENTS['Spartan IR Camera'].FILENAME.like(frame))[0]
						zoom = d.get('zoom')
                                                pan = d.get('pan')

						if self.ui.actionSpartan_showall.isChecked():
							if query2.DETSERNO == '102':
								#zoom = d.get('zoom')
								d.set('frame clear')
								d.set('zoom '+zoom)
							d.set('file mosaic iraf %s'%(frame))
						elif query2.DETSERNO == '66':
							zoom = d.get('zoom')
							d.set('frame clear')
							d.set('zoom '+zoom)
							d.set('file %s'%(frame))
						if self.ui.actionZoom_to_fit.isChecked():
							d.set('zoom to fit')
						if self.ui.actionZscale.isChecked():
							d.set('scale mode zscale')
                                                d.set('pan to '+pan)
                                                        
						return 0					
					elif query.INSTRUME == 'OSIRIS':
						data = pyfits.getdata(frame)

						if d.set_np2arr(np.array(data,dtype=np.float))==1:
							d.set('file %s'%(frame))
						if self.ui.actionZoom_to_fit.isChecked():
							d.set('zoom to fit')
						if self.ui.actionZscale.isChecked():
							d.set('scale mode zscale')
						#display(frame,1)
						return 0
						
					else:
						d.set('file %s'%(frame))
						if self.ui.actionZoom_to_fit.isChecked():
							d.set('zoom to fit')
						if self.ui.actionZscale.isChecked():
							d.set('scale mode zscale')
						#display(frame,1)
						return 0
				except:
					logging.debug(sys.exc_info()[1])
					logging.debug('Could not display file %s'%(frame))
					return -1
			
				return 0
			else:
				print 'File %s does not exists...'%(frame)
				return -1


#
#
################################################################################################
		
################################################################################################
#
#

	def initGUI(self):
	
		#print os.path.join(uipath,'soarlog_qt4.ui')
		self.ui = uic.loadUi(os.path.join(uipath,'soarlog_qt4.ui'),self)
		
		
	##########################################################
	# Set tab for CID
	#
			
		#self.ShowInfoOrder = range(len(self.header_CID))
		
		#print len(list(np.array(self.header_CID)[self.ShowInfoOrder])), list(np.array(self.header_CID)[self.ShowInfoOrder])
		#print len(self.header_CID),self.header_CID
		
		#self.header_CID
		
		#self.tm = SOLogTableModel(self.getCIDdata(),[self.header_CID[i] for i in self.ShowInfoOrder ],self, commitDB=self.emmitTableDataChanged)
		
		tm = SOLogTableModel(self.getTableData(), databaseF.frame_infos.tvDB.keys(),self ,commitDB=self.emmitTableDataChanged)
                self.tm = QtGui.QSortFilterProxyModel(self)
                self.tm.setSourceModel(tm)
                self.searchText = ''
                self.searchColumn = self.FilenameColumn # Default is filename
                self.searchInitialized = False
		self.ui.tableDB.setModel(self.tm)
		self.ui.tableDB.keyPressEvent = self.handleKeyEvent
		#self.ui.tableDB.setSelectionMode(self.ui.tableDB.SingleSelection)
                hh = self.ui.tableDB.horizontalHeader()
                hh.setStretchLastSection(True)

		
		font = QtGui.QFont("Courier New", 8)
		self.ui.tableDB.setFont(font)
		self.ui.tableDB.setAlternatingRowColors(True)
		self.ui.tableDB.setItemDelegateForColumn(11,ComboBoxDelegate(self.ui.tableDB.model(), self.imageTYPE))
		#self.ui.tableDB.resizeColumnsToContents()
		#print self.tm.rowCount(self)
		
	#
	#	
	##########################################################

	##########################################################
	# Set up menubar (connect apropriate function for each
	# option)
	#
		self.GTLF = True
		self.DLF = True
	
		self.connect(self.ui.actionAdd_Frame, QtCore.SIGNAL('triggered()'), self.AddSelectFrame)
		self.connect(self.ui.actionGot_to_last_frame, QtCore.SIGNAL('triggered()'), self.ChangeGTLF)
		self.connect(self.ui.actionDisplay_last_frame, QtCore.SIGNAL('triggered()'), self.ChangeDLF)	
		self.connect(self.ui.actionSave_Log,QtCore.SIGNAL('triggered()'), self.SaveLogThreaded)
		self.connect(self.ui.actionPreferences,QtCore.SIGNAL('triggered()'),self.OpenPreferences)
		self.connect(self, QtCore.SIGNAL('reloadTableEvent(char*)'), self.reloadTable)
		#self.connect(self, QtCore.SIGNAL('reloadTableEvent()'), self.reloadTable)
		self.connect(self, QtCore.SIGNAL('runQueueEvent()'), self.wake.set)
		self.connect(self, QtCore.SIGNAL('TableDataChanged(QModelIndex,QString)'), self.CommitDBTable)
		
		## Deprecated ################
		#self.connect(self, QtCore.SIGNAL('insertRecord()'), self.insertRecord)
		##############################

		#self.connect(self, QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.CommitDBTable)

		self.connect(self.ui.actionAddComment, QtCore.SIGNAL('triggered()'),self.askForCommentLinePID)
		self.connect(self.ui.actionDQ, QtCore.SIGNAL('triggered()'),self.startDataQuality)
		self.connect(self.ui.actionDT, QtCore.SIGNAL('triggered()'),self.startDataTransfer)
		self.connect(self.ui.actionWI, QtCore.SIGNAL('triggered()'),self.promptWeatherComment)
		self.connect(self.ui.actionHideCB, QtCore.SIGNAL('triggered()'),self.HideCB)
                self.connect(self.ui.actionCalibration_Helper, QtCore.SIGNAL('triggered()'),self.Calibration_Helper)
		self.connect(self.ui.actionEnable_Disable_Table_Edit, QtCore.SIGNAL('triggered()'),self.enableDisableTableEdit)

		#self.connect(self.ui.addFrameComment, QtCore.SIGNAL('clicked()'),self.commitComment)
		
		self.connect(self.ui.addNoteButton, QtCore.SIGNAL('clicked()'),self.askForCommentLinePID)
		
		
		self.connect(self.ui.tableDB,QtCore.SIGNAL("clicked(const QModelIndex&)"), self.tableItemSelected)
		self.connect(self.ui.tableDB,QtCore.SIGNAL("selectionChanged(const QItemSelection&, const QItemSelection&)"), self.tableItemSelected)
		
		self.connect(self.ui.tableDB,QtCore.SIGNAL("doubleClicked(const QModelIndex&)"), self.displaySelected)
		#self.connect(self.ui.tableDB,QtCore.SIGNAL("columnResized()"), self.saveColumnWidth)
		
                self.connect(self.ui.lineFrameComment,QtCore.SIGNAL('searchPressed()'),self.setSearchCommentLine)

                self.initializeCommentLine()

					 
		header = databaseF.frame_infos.tvDB

		self.ShowInfoOrder = range(len(self.header_CID))

		#
		# Load configuration for Show/Hide
		#
		
		try :
			HideConfig = np.loadtxt(os.path.join(self._CFGFilePath_,self._CFGFiles_['ShowInfo']),dtype='int')
			
			#			print HideConfig
			for i in HideConfig:
				#self.ActionArray[i].setChecked(False)
				self.ui.tableDB.hideColumn(i)
		
		except TypeError:
			#self.ActionArray[HideConfig].setChecked(False)
			self.ui.tableDB.hideColumn(HideConfig)
			HideConfig = np.array([HideConfig])
		except:
			pass

		#
		# Selection for CID
		#
		
		self.changeOrderArray = []

		#
		# Load configuration for order
		#

		self.OrderInfoDict = {}
		
		try :
			SavedInfoOrder = np.loadtxt(os.path.join(self._CFGFilePath_,self._CFGFiles_['OrderInfo']),dtype='int',unpack=True)
			ssort = SavedInfoOrder[1].argsort()
			SavedInfoOrder[0] = SavedInfoOrder[0][ssort]
			SavedInfoOrder[1] = SavedInfoOrder[1][ssort]
			for i in range(len(SavedInfoOrder[0])):
				self.MoveColumn( (SavedInfoOrder[0][i],SavedInfoOrder[1][i]))
				#print SavedInfoOrder[0][i],' --> ',SavedInfoOrder[1][i]
		
				
		except:
			pass
			

		#print self.OrderInfoDict

		#
		# Load Column Width
		#
		colWidth = []
		if os.path.isfile(os.path.join(self._CFGFilePath_,self._CFGFiles_['ColumnWidth'])):
			colWidth = np.loadtxt(os.path.join(self._CFGFilePath_,self._CFGFiles_['ColumnWidth']),unpack=True)

		for i in range(len(colWidth)):
			if colWidth[i] > 0:
				self.ui.tableDB.setColumnWidth(i,colWidth[i])
		
	#
	#	
	##########################################################


#
#
################################################################################################

################################################################################################
#
#
	def enableDisableTableEdit(self):
		
		if self.actionEnable_Disable_Table_Edit.isChecked():
			self.ui.tableDB.model().sourceModel().changeEditableColumns(self.ExtraEditableColumns)
		else:
			self.ui.tableDB.model().sourceModel().changeEditableColumns([self.CommentColumn])

                #
                # Reset search engine when user modify editable role.
                #
                if len(self.searchText) > 0:
                    self.searchText = ''
                    self.searchInitialized = False
                    self.filterTable()
                    self.ui.tableDB.model().reset() #invalidateFilter()
#
#
################################################################################################

################################################################################################
#
#

	def AddFrame(self,filename):
	
		logging.debug('AddFrame received %s'%(filename))
		
		if not filename:
			logging.debug('Filename is empty ...')
			return -1
		
		# Checa se esta no banco de dados
		
		session = self.Session()

		query = session.query(self.Obj_CID.FILENAME).filter(self.Obj_CID.FILENAME == os.path.basename(str(filename)))[:]
		if len(query) > 0:
			logging.debug('File %s already in database...'%(str(filename)))
			return -1
			
		infos = databaseF.frame_infos.GetFrameInfos(str(filename))

		if infos == -1:
			logging.debug(' Could not read file %s... '%(filename))
			return -1
		else:
			#self.commitLock.acquire()
			instKey = infos[0]['INSTRUME']
			
			entry = self.Obj_INSTRUMENTS[instKey](**infos[0])
			entry_CID = self.Obj_CID(**infos[1])
			
			iinfo = ['']*len(self.header_CID)
			for i in range(len(iinfo)):
				iinfo[i] = infos[1][self.header_CID[i]]
			self.updateTable(iinfo)
			
			try:
				session.add(entry_CID)
				session.add(entry)
				session.commit()
			except:
				logging.debug(sys.exc_info()[1])
				logging.debug('Could not commit to instrument specific database. Will do it later.')
				pass
			#finally:
			#	self.commitLock.release()
		
		return 0
#
#
################################################################################################

################################################################################################
#
#
	def insertRecord_Deprecated(self):
		
		self.commitLock.acquire()			
		
		lqueue = self.recordQueue.qsize()

		if lqueue == 0:
			self.commitLock.release()
			return -1

		try:
			self.model.submitAll()
			while not self.recordQueue.empty():
	
			
				record = self.recordQueue.get()
				logging.debug('Inserting %s to main database'%( record.value('FILENAME').toString() ))
				self.model.insertRecord(-1,record)

			logging.debug('Submiting changes to database (%s new entries).'%(lqueue))
			self.model.submitAll()
			
		finally:
			self.commitLock.release()
#
#
################################################################################################

################################################################################################
#
#

	def OpenPreferences(self):

		tbHeader = self.header_CID
		#pref_ui = PrefMenu([ tbHeader[i] for i in self.ShowInfoOrder],self.ui.tableDB)
		pref_ui = PrefMenu(tbHeader, self.ShowInfoOrder,self.ui.tableDB)
		
                self.initThreadLock.acquire()

                try:
                    pref_ui.show()
		
                    if pref_ui.exec_():
#			print 'Changes will be performed'
#
# Change order of table headers
#
#			print [tbHeader.index(pref_ui.listSort.model().getData(i,0)) for i in range(len(tbHeader))]

			for i in range(len(tbHeader)):
#				print i,tbHeader.index(pref_ui.listSort.model().getData(i,0))
                            self.MoveColumn([ tbHeader.index(pref_ui.listSort.model().getData(i,0)),i ])

#
# Show/hide Table columns 
#
			for i in range(len(tbHeader)):
                            if not pref_ui.listVis.isRowHidden(i):
                                self.ui.tableDB.showColumn(i)
                            if not pref_ui.listHide.isRowHidden(i):
                                self.ui.tableDB.hideColumn(i)	

#
# Save changes
#

			if len(self.OrderInfoDict.keys()) > 0:
				np.savetxt(os.path.join(self._CFGFilePath_,self._CFGFiles_['OrderInfo']),zip(self.OrderInfoDict.keys(),self.OrderInfoDict.values()),fmt='%i %i')		

			file = open(os.path.join(self._CFGFilePath_,self._CFGFiles_['ShowInfo']),'w')

			tbHeader = self.header_CID# + databaseF.frame_infos.ExtraTableHeaders

			for i in range(len(tbHeader)):
				if self.ui.tableDB.isColumnHidden(i):
					file.write('%i\n' % i)

			file.close()

			

                    else:
			logging.debug('No changes made to Layout')

                except: 
                    logging.debug('Exception in Preferences')
                finally:
                    self.initThreadLock.release()
                    if self.Queue.qsize() > 0:
                        self.runQueue()
                    
		logging.debug('[DONE]')

		return 0

		
		tableModel = SOLogTableModel(data,["Teste"] ,commitDB=None)
		
		tab1 = pref_ui.tabWidget.widget(0) #.gridLayout.tableView.setModel(tableModel) #.tab.gridLayout.tableView.setModel(tableModel)
		pref_ui.tableView.setModel(tableModel)
		font = QtGui.QFont("Courier New", 8)
		#pref_ui.tabWidget.widget(0).tableView.setFont(font)

		#QtGui.QFileDialog.getExistingDirectory(self, 'Selecione diretorio da noite','~/')
		#pref_ui.prefUI()
		logging.debug(pref_ui.exec_())
		logging.debug('Done')
		return 0
	
################################################################################################
#
#
	def ShowHideCol(self,colId):
	
		#print colName
		if not self.ActionArray[colId].isChecked():
			self.ui.tableDB.hideColumn(colId)
		else:
			self.ui.tableDB.showColumn(colId)
#
#
################################################################################################

################################################################################################
#
#
	def MoveColumn(self,move):
						
		#print self.ShowInfoOrder
		index = [i for i,x in enumerate(self.ShowInfoOrder) if x == move[0]][0]
		
		#print move
		#print index
		#print move

		table_header = self.ui.tableDB.horizontalHeader()
		table_header.moveSection(index,move[1])

		#print self.ShowInfoOrder
		
		self.ShowInfoOrder.insert(move[1], self.ShowInfoOrder.pop(index))		
		
		#tmp = self.ShowInfoOrder[:index] + self.ShowInfoOrder[index+1:]
		
		#self.ShowInfoOrder = tmp[:move[1]] + [self.ShowInfoOrder[index]] + tmp[move[1]:]
				

		self.OrderInfoDict[move[0]] = move[1]
		#print [self.ShowInfoOrder[i] for i in move]
		
		#print move
		#print move[0], 'is in ',self.ShowInfoOrder[move[0]]
		#print move
		#print move[0],self.ShowInfoOrder[move[0]]
		#print self.ShowInfoOrder
#
#
################################################################################################

################################################################################################
#
#
	def ChangeGTLF(self):
		'''
			Go to last frame.
		'''
		self.GTLF = not self.GTLF
#
#
################################################################################################

################################################################################################
#
#
	def ChangeDLF(self):
		'''
			Display last frame
		'''
		self.DLF = not self.DLF
#
#
################################################################################################

################################################################################################
#
#
	def closeEvent(self,event):

		if not __FALSEWATCHER__:
			self.notifier.stop()

                self.STATUS = False
                
		if len(self.OrderInfoDict.keys()) > 0:
			np.savetxt(os.path.join(self._CFGFilePath_,self._CFGFiles_['OrderInfo']),zip(self.OrderInfoDict.keys(),self.OrderInfoDict.values()),fmt='%i %i')		

		file = open(os.path.join(self._CFGFilePath_,self._CFGFiles_['ShowInfo']),'w')
		
		tbHeader = self.header_CID# + databaseF.frame_infos.ExtraTableHeaders

		for i in range(len(tbHeader)):
			if self.ui.tableDB.isColumnHidden(i):
				file.write('%i\n' % i)

		file.close()
		
		self.saveColumnWidth()
		
		sys.exit(0)

#
#
################################################################################################

################################################################################################
#
#    

	def AskFile2Watch(self):

		self.dir = str(QtGui.QFileDialog.getExistingDirectory(self, 'Selecione diretorio da noite','~/'))

		if self.dir:
			os.chdir(self.dir)

			return 0
		else:
			exit(0)


#
#
################################################################################################

################################################################################################
#
#    
	def initWatch(self):
	
#		self.Queue = None
		if not __FALSEWATCHER__:
		


			self.handler = EventHandler(self.wake.set,self.Queue)
			self.notifier = ThreadedNotifier(wm, self.handler)
			self.notifier.start()

			
			# Internally, 'handler' is a callable object which on new events will be called like this: handler(new_event)
			#print self.dir
			wdd = wm.add_watch(self.dir, mask, rec=True)
			logging.debug('Watch initialized...')

#
#
################################################################################################


################################################################################################
#
#
	def saveColumnWidth(self):
		
		tbHeader = self.header_CID# + databaseF.frame_infos.ExtraTableHeaders
		colWidth = np.zeros(len(tbHeader))	
		for i in range(len(tbHeader)):
			colWidth[i] = self.ui.tableDB.columnWidth(i)
#			print self.ui.tableDB.columnWidth(i)
		np.savetxt(os.path.join(self._CFGFilePath_,self._CFGFiles_['ColumnWidth']),X=colWidth,fmt='%f')

		return 0

#
#
################################################################################################

################################################################################################
#
#
	def emmitRunQueue(self):
		self.emit(QtCore.SIGNAL("runQueueEvent()"))    

#
#
################################################################################################

################################################################################################
#
#
	def emmitReloadTableEvent(self,file):
		self.emit(QtCore.SIGNAL("reloadTableEvent(char*)"),file)    
		#self.emit(QtCore.SIGNAL("reloadTableEvent()"))    

#
#
################################################################################################

################################################################################################
#
#
	def emmitTableDataChanged(self,index):
            #self.emmitFileEventLock.acquire()
            #try:
  			#if not self.emmitFileEventLock.locked():
		try:
			new_index = self.ui.tableDB.model().index(index.row(),index.column())
			self.emit(QtCore.SIGNAL("TableDataChanged(QModelIndex,QString)"),new_index,self.ui.tableDB.model().data(new_index).toString())
			logging.debug('emmitTableDataChanged')
		except:
			logging.debug('Exception in emmitTableDataChanged')
                

#
#
################################################################################################

################################################################################################
#
#
	def GetWeatherComment(self):
	
		comments = '''
===============================================================
                      WEATHER CONDITIONS
===============================================================
'''
		#_file = open(self.__FileWeatherComments__,'r')
		session = self.Session()
		query = session.query(self.Obj_WC.Comment)[:]

		return comments+query[0].Comment+'\n'
#
#
################################################################################################

################################################################################################
#
#
	def promptWeatherComment(self):
		
		winfo = WeatherInfo()
		
		session = self.Session()
		query = session.query(self.Obj_WC.Comment)[:]
		if len(query) == 0:
			info = self.Obj_WC(**{'Comment':"No weather comment."})
			session.add(info)
			session.commit()
			winfo.wi_ui.weatherInfo.setPlainText("No weather comment.")
		else:
			winfo.wi_ui.weatherInfo.setPlainText(query[0].Comment)
		winfo.show()	
		if winfo.exec_():
#			print winfo.wi_ui.weatherInfo.toPlainText()

			query = session.query(self.Obj_WC)[0]
			logging.debug(query.Comment)
			query.Comment = str(winfo.wi_ui.weatherInfo.toPlainText())
			logging.debug(query.Comment)
                        self.commitLock.acquire()
                        try:
                            #session.flush()			
                            session.commit()
                        finally:
                            self.commitLock.release()
#			_file = open(self.__FileWeatherComments__,'w')
#			_file.write(winfo.wi_ui.weatherInfo.toPlainText())
#			_file.close()
	
	
		return 0
#
#
################################################################################################

################################################################################################
#
#
	def GetCalibrations(self):
	
		session_CID = self.Session()
		query = session_CID.query(self.Obj_CID.FILENAME).filter(~self.Obj_CID.IMAGETYP.like('OBJECT'))[:]
		calib =  [str(ff[0]) for ff in query]
		
		return '''A total of %i calibration frames exists.
''' % (len(calib))
#
#
################################################################################################

	def getProjects(self):
	
		session_CID = self.Session()
		query = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like('%SO%')).filter(self.Obj_CID.IMAGETYP.like('OBJECT'))[:]
		fnames = np.array([ os.path.basename(str(ff.FILENAME)) for ff in query])
		
		for ff in range(len(fnames)):
			id01 = fnames[ff].find('SO')
			id02 = fnames[ff][id01:].find('_')
                        #if id01 > -1 and id02 > id01:
                        fnames[ff] = fnames[ff][id01:id01+id02]
		
		proj_id = np.unique(fnames)

		if len(proj_id) == 0:
                    return [],[],0
		mask = np.array([len(proj_id[i]) > 0 for i in range(len(proj_id))])

		proj_id = proj_id[mask]
		proj_id2 = proj_id
				
		for i in range(len(proj_id)):
			id01 = proj_id[i].rfind('-')
			proj_id[i] = proj_id[i][id01+1:]

		nframes = []
		for i in range(len(proj_id2)):
			query = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like('%-'+proj_id2[i]+'%'))[:]
			nframes.append(len(query))

		return proj_id,proj_id2,nframes


################################################################################################
#
#
	def GetFrameLog(self,sproj=None):
		session_CID = self.Session()
		query = session_CID.query(self.Obj_CID).filter(self.Obj_CID.IMAGETYP.like('OBJECT'))[:]
		
		logFRAME = '''
{time}LT File:\t%(FILENAME)s
\tOBJECT: %(OBJECT)s
\tNotes: %(OBSNOTES)s
\tX=%(AIRMASS)s Exptime:%(EXPTIME)s s sm= %(SEEING)s
'''
		logNOTE = '''
%(time)LT Notes: %(OBSNOTES)s
'''

		outlog = ''
		
		#
		# Resolve projects
		#
		
		proj_id,proj_id2,nframes = self.getProjects()
                
		logging.debug(proj_id)
		
		#
		# Write log for each project
		#
		
		timeSpentLog = '''
Time Spent:
===========
'''
                if sproj:
                    proj_id = [sproj]

		for i in range(len(proj_id)):
			proj = proj_id[i]

			#
			# Calculate spended time
			#
			
			timeSpent = self.calcTime(proj)
			timeSpentLog += self.semester_ID%(proj) + ': %02.0f:%02.0f\n' % timeSpent

			#
			# Get proj Header
			#
			
			try:
				proj_hdr_file = open(self.dataCalib%proj,'r')
				proj_hdr = proj_hdr_file.readlines()
				proj_hdr_file.close()
			except IOError:
				proj_hdr = ['--\n','--\n',proj,'\n--\n']
				

			#
			# Frames infos
			#
			
			query = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like('%-'+proj_id[i]+'%'))[:]
			obj_list = self.getObjects(query)

			logging.debug(obj_list)

			nlines = 3
			end_hdr = 0
			for j in range(len(proj_hdr)):
				if proj_hdr[j][0] == '-':
					nlines -= 1
				if proj_hdr[j].find('TIME') >= 0:
					proj_hdr[j] = 'TIME SPENT: %02.0f:%02.0f\n' % timeSpent 
				if proj_hdr[j].find('OBJECTS') >= 0:
					obj_list = self.getObjects(query)
					proj_hdr[j] = proj_hdr[j][:-1]
					for iobj in range(len(obj_list)):
						proj_hdr[j] += obj_list[iobj] + ' '
					proj_hdr[j] += '\n'
				outlog +=  proj_hdr[j]
				if nlines == 0:
					break

		
			hour = np.array( [ str(ff.TIMEOBS) for ff in query] )
			day = np.array( [ str(ff.DATEOBS) for ff in query] )
		
			time = np.array( [ day[i]+'T'+hour[i] for i in range(len(hour)) ] )
		
			sumLT = self.LocalTime
			for i in range(len(time)):
				if day[i].find('T') > 0:

					time[i] = day[i]
				
			sort = range(len(query))#time.argsort()
		
			for itr in range(len(query)):

				frame = query[sort[itr]]
				time = frame.TIMEOBS
				log = logFRAME
				writeFlag = True
				frame2 = None
				if frame.INSTRUME == 'Spartan IR Camera':
					try:
						frame2 = session_CID.query(self.Obj_INSTRUMENTS['Spartan IR Camera']).filter(self.Obj_INSTRUMENTS['Spartan IR Camera'].FILENAME.like(os.path.join(frame.PATH,frame.FILENAME)))[0]
						if frame2.DETSERNO != '66':
							writeFlag = False						
					except:
						logging.debug('Error %s on frame %s...'%(sys.exc_info()[1],frame.FILENAME))
						writeFlag = False
				try:
					time = time.split(':')
				except:
					time = [0,0,0]
				hrs = int(time[0].split('T')[-1])+sumLT
				if hrs > 23:
					hrs -= 24
				if hrs < 0:
					hrs += 24
				try:
					time = '%02i:%02i' % (hrs,int(time[1]))
				except:
					time = frame.TIMEOBS

				if frame.INSTRUME == 'NOTE':
					log = logNOTE
				if writeFlag:
					outlog += log%{'time':time, 'FILENAME' : os.path.basename(frame.FILENAME), 'OBJECT' : frame.OBJECT, 'OBSNOTES' : frame.OBSNOTES ,\
										 'AIRMASS' : frame.AIRMASS, 'EXPTIME' : frame.EXPTIME, 'SEEING' : frame.SEEING}
				if frame.INSTRUME == 'Goodman Spectrograph':
					#frame2 = session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like(frame.FILENAME))[0]
					logGS = '\tCONF: %s SLIT: %s OBSTYPE: %s\n'%(frame.SP_CONF,frame.SLIT,frame.IMAGETYP)
					outlog+=logGS

				if frame.INSTRUME == 'Spartan IR Camera' and writeFlag:
					logSP = '\tFILTER: %s OBSTYPE: %s\n'%(frame2.FILTER,frame.IMAGETYP)
					outlog+=logSP
				
	
		outlog += '-'*63 + '\n'
		outlog += timeSpentLog
		return outlog
#
#
################################################################################################

################################################################################################
#
#

	def SaveLogThreaded(self):
            rthread = threading.Thread(target=self.SaveLog)
            rthread.start()
            
            #threading.Thread(target=self.SaveLog).start()

#
#
################################################################################################

################################################################################################
#
#
	def SaveLog(self):
		
		#
		# open file
		#
		
		file = open(self.logfile,'w')
		
		#
		# Write log header
		#
		
		#hdr = 'No header\n'
		try:
			hdr = subprocess.Popen(['logheader.py'],stdout=file,stderr=file)
			hdr.wait()
		except:
			hdr = 'No header\n'
			pass
		
		#file.write(hdr)

		#
		# Calibrations
		#
		
		file.write(self.GetCalibrations())
		
		#
		# Weather comment
		#
		
		file.write(self.GetWeatherComment())
		
		#
		# Write LOG
		#
		
		file.write(self.GetFrameLog())
		
		file.close()
#
#
################################################################################################

################################################################################################
#
#
	def calcTime(self,id):
	
		session_CID = self.Session()
		query = session_CID.query(self.Obj_CID.id,self.Obj_CID.FILENAME,self.Obj_CID.DATEOBS,self.Obj_CID.TIMEOBS,self.Obj_CID.OBJECT,self.Obj_CID.EXPTIME,self.Obj_CID.IMAGETYP).filter(self.Obj_CID.FILENAME.like('%SO%')).filter(self.Obj_CID.OBJECT != "NOTE").filter(self.Obj_CID.IMAGETYP != "FAILED")[:]		
		time_end = []
						
		fid = np.array( [ int(ff.id) for ff in query] )
		fnames = np.array( [ str(ff.FILENAME) for ff in query] )
		hour = np.array( [ str(ff.TIMEOBS) for ff in query] )
		day = np.array( [ str(ff.DATEOBS) for ff in query] )
		obj = np.array( [ str(ff.OBJECT) for ff in query] )
		exptime  = np.array( [ float(ff.EXPTIME) for ff in query] )
		
		#print obj 
		
		time = np.array( [ day[i]+'T'+hour[i] for i in range(len(hour)) ] )
		
		for i in range(len(time)):
                    if day[i].find('T') > 0:
                        time[i] = day[i]
						
		sort = time.argsort()

		#print time, time[sort]
		
		fnames = fnames[sort]
		
		find_proj = np.array( [ i for i in range(len(fnames)) if fnames[i].find('-'+id+'_') > 0] )

                iddiff = fid[find_proj[1:]] - fid[find_proj[:-1]]
                #for i in range(len(find_proj)-1):
                #    print fid[find_proj[i]],fnames[find_proj[i]],iddiff[i]
                    
		#time_start = np.append([int(find_proj[0])], np.array( [ find_proj[i+1] for i in range(1,len(find_proj)-1) if not fid[i] == fid[i+1]-1 ] ) )
		#time_end = np.append( np.array( [ find_proj[i] for i in range(1,len(find_proj)-2) if fid[i] != fid[i+1]-1 ] ), [int(find_proj[-1])] )
                time_start = np.append([int(find_proj[0])],find_proj[1:][iddiff != 1])
                time_end  = np.append(find_proj[:-1][iddiff != 1],[int(find_proj[-1])])
		#print find_proj
		
		time_tmp = np.append(time_start , time_end  )
		
#               print time_tmp
#               print time_tmp[1]
						
#               time_start = time_tmp[0]
#               time_end = time_tmp[1]
		
		time.sort()
		
		calcT = 0
		try:

                    for i in range(len(time_start)):
                        
                        dia_start,hora_start = time[time_start[i]].split('T')
                        dia_end,hora_end = time[time_end[i]].split('T')
                        
                        ano1,mes1,dia1 = dia_start.split('-')
                        hr1,min1,sec1 = hora_start.split(':')
                        
                        ano2,mes2,dia2 = dia_end.split('-')
                        hr2,min2,sec2 = hora_end.split(':')

                        
                        start = float(hr1)/24.+float(min1)/24./60.
                        end = float(hr2)/24.+float(min2)/24./60.
                        if ano1 != ano2 or mes1 != mes2 or dia1 != dia2:
                            end += 1.
                        
                        calcT += (end-start)*24.0 + exptime[time_end[i]]/60./60.
                        #print 'START = ', ano1,mes1,dia1,hr1,min1,sec1,' ->',start
                        #print 'END = ', ano2,mes2,dia2,hr2,min2,sec2,' ->',end
                        #print 'TIME = ',(end-start)*24.0 
						
						
                    #print id, [ time[i] for i in time_start ], [time[i] for i in time_end], '%02.0f:%02.0f' %( np.floor(calcT), (calcT-np.floor(calcT))*60)
                    logging.debug(self.semester_ID%(id)+' %(hora)02.0f:%(min)02.0f (with %(nsub)i subblocks).'%{'nsub':len(time_start), 'hora':np.floor(calcT), 'min':(calcT-np.floor(calcT))*60})
		except:
                    logging.debug('Failed to obtain program time')
				
				
				
		#print calcT

		

		return ( np.floor(calcT), (calcT-np.floor(calcT))*60)
#
#
################################################################################################

################################################################################################
#
#


	def getObjects(self,qq):
		
		obj = np.array([])
		for i in range(len(qq)):
			obj = np.append(obj,qq[i].OBJECT)

		uobj = np.unique(obj)

		lcomm = np.array([])

		for i in range(len(uobj)):
			lcomm = np.append(lcomm,uobj[i].split(' ')[0].split('_')[0])

		lcomm = np.unique(lcomm)
		lcomm2 = np.array([])

		for i in range(len(lcomm)-1):			
			for j in range(i+1,len(lcomm)):
				cobj = LongestCommonSubstring(lcomm[i],lcomm[j])
				if len(cobj) >= 1 and cobj[0] != ' ':
					lcomm2 = np.append(lcomm2,lcomm[i])

		return lcomm #np.unique(lcomm2)
#
#
################################################################################################

################################################################################################
#
#
	def HideCB(self):
		if self.ui.coomentBarWidget.isHidden():
			self.ui.coomentBarWidget.show()
		else:
			self.ui.coomentBarWidget.hide()

#
#
################################################################################################

################################################################################################
#
#
	def tableItemSelected(self,index):

		#print 'tableItemSelected'
		
            self.currentSelectedItem = index
            commentIndex = self.ui.tableDB.model().index(index.row(),self.CommentColumn)
            text = self.ui.tableDB.model().data(commentIndex)
            if type(text) == type(QtCore.QVariant()):
                text = text.toString()
            self.ui.lineFrameComment.setText(text)	

            return 0

#
#
################################################################################################

################################################################################################
#
#

	def commitComment(self):

		text = self.ui.lineFrameComment.text()
                indexes = self.ui.tableDB.selectedIndexes()

		if len(indexes) > 0:

                    workIndexes = [] 
                    workRow = []

                    for i in range(len(indexes)):
                        if indexes[i].row() not in workRow:
                            workRow.append(indexes[i].row())
                            workIndexes.append(self.ui.tableDB.model().sourceModel().createIndex(indexes[i].row(),self.CommentColumn))

                    for i in range(len(workIndexes)):
                        self.ui.tableDB.model().sourceModel().setData(workIndexes[i],text,QtCore.Qt.EditRole)

#
#
################################################################################################
			
################################################################################################
#
#
	def displaySelected(self,index):
		
		session_CID = self.Session()
                
		query = session_CID.query(self.Obj_CID).filter(self.Obj_CID.id == index.row()+1)[0]

		frame = os.path.join(query.PATH,query.FILENAME)

		d = None
		_targets = ds9.ds9_targets()
		#print _targets
		# Check if ds9 is opened

		if not _targets == 0:
			d = ds9.ds9()
                                           
		else: 
			#print _targets[1].split(' ')[1]
			d = ds9.ds9(_targets[0])#.split(' ')[1])
		d.set('preserve regions yes')
                d.set('preserve pan yes')
                d.set('preserve scale yes')
	
		if os.path.isfile(frame):

			try:
				if query.INSTRUME == 'SOI':
					#mscred.mscdisplay(frame,1)
					d.set('file mosaicimage wcs %s'%(frame))
					if self.ui.actionZoom_to_fit.isChecked():
						d.set('zoom to fit')
					if self.ui.actionZscale.isChecked():
						d.set('scale mode zscale')
					return 0
				elif query.INSTRUME == 'Spartan IR Camera':
                                    
					if self.ui.actionSpartan_showall.isChecked():
						detIndex = frame.rfind('.fits')
						#frame2 = frame#[detIndex-1]='%'
						frame2 = frame[:detIndex-1]+'%.fits'
						query2 = session_CID.query(self.Obj_INSTRUMENTS['Spartan IR Camera']).filter(self.Obj_INSTRUMENTS['Spartan IR Camera'].FILENAME.like(frame2))[::]

						zoom = d.get('zoom')
                                                pan = d.get('pan')
                                                #logging.debug(pan)
						d.set('frame clear')
						for nfile in range(len(query2)):
							d.set('file mosaic iraf %s'%(query2[nfile].FILENAME))
						d.set('zoom '+zoom)
                                                d.set('pan to '+pan)
                                                #

					else:
						zoom = d.get('zoom')
						d.set('frame clear')
						d.set('zoom '+zoom)
						d.set('file %s'%(frame))
					if self.ui.actionZoom_to_fit.isChecked():
						d.set('zoom to fit')
					if self.ui.actionZscale.isChecked():
						d.set('scale mode zscale')
					return 0					
				elif query.INSTRUME == 'OSIRIS':
					data = pyfits.getdata(frame)
					if d.set_np2arr(np.array(data,dtype=np.float))==1:
						d.set('file %'%s(frame))
					if self.ui.actionZoom_to_fit.isChecked():
						d.set('zoom to fit')
					if self.ui.actionZscale.isChecked():
						d.set('scale mode zscale')
					#display(frame,1)
					return 0
				else:
					d.set('file %'%(frame))
					#display(frame,1)
					if self.ui.actionZoom_to_fit.isChecked():
						d.set('zoom to fit')
					if self.ui.actionZscale.isChecked():
						d.set('scale mode zscale')
					return 0
			except:
				logging.debug('Could not display file %s'%(frame))
				return -1
		
			return 0
		else:
			logging.debug('File %s does not exists...'%(frame))
			return -1
							
#
#
################################################################################################

################################################################################################
#
#
        def filterTable(self):
            
            if self.searchInitialized:
                logging.debug(str(self.ui.lineFrameComment.text()))
                self.ui.tableDB.model().setFilterRegExp(QtCore.QRegExp(str(self.ui.lineFrameComment.text()), QtCore.Qt.CaseInsensitive,QtCore.QRegExp.Wildcard))
#
#
################################################################################################

################################################################################################
#
#
        def clearFilterTable(self):
            
            if self.searchInitialized:
                self.ui.lineFrameComment.setText('')
                self.ui.tableDB.model().setFilterRegExp(QtCore.QRegExp('', QtCore.Qt.CaseInsensitive,QtCore.QRegExp.Wildcard))
#
#
################################################################################################

################################################################################################
#
#


	def handleKeyEvent(self,event):
		
		#self.commitComment()
		rr = QtGui.QTableWidget.keyPressEvent(self.ui.tableDB, event)

		if len(self.ui.tableDB.selectedIndexes()) > 0:
			if self.ui.tableDB.selectedIndexes()[0].column() == self.CommentColumn:
				try:
                                    #commentIndex = self.ui.tableDB.model().index(index.row(),self.CommentColumn)
                                    text = self.ui.tableDB.model().data(self.ui.tableDB.selectedIndexes()[0])
                                    if type(text) == type(QtCore.QVariant()):
                                        text = text.toString()
                                    self.ui.lineFrameComment.setText( text )
				except AttributeError:
                                    text = self.ui.tableDB.model().data(self.ui.tableDB.selectedIndexes()[0])
                                    self.ui.lineFrameComment.setText( text )
                                    pass
                                return rr
					
		if event.key() == QtCore.Qt.Key_Down or event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_Right or event.key() == QtCore.Qt.Key_Left:
			
			self.tableItemSelected(self.ui.tableDB.selectedIndexes()[0])
                elif event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_F:
                    self.setSearchCommentLine()
                elif event.key() == QtCore.Qt.Key_Escape and self.searchInitialized:
                    self.clearFilterTable()

#                elif event.isAutoRepeat():
#                    return rr
#                elif event.key() == QtCore.Qt.Key_Escape:
#                    logging.debug('Escape pressed')
#                    self.searchText = ''
#                    self.filterTable()
#                    self.ui.tableDB.model().invalidateFilter()
#                    self.searchInitialized = False
#                    return rr
#                elif not self.searchInitialized:
#                    self.searchInitialized = True
#                    itemselection = self.ui.tableDB.selectedIndexes()
#                    self.searchText += event.text()
#                    if len(itemselection) > 0:
#                        if itemselection[0].column() not in self.ui.tableDB.model().sourceModel().EditableColumns:
#                            self.ui.tableDB.model().setFilterKeyColumn(itemselection[0].column())
#                            self.lastSearchColumn = itemselection[0].column()
#                    elif self.lastSearchColumn >= 0 and self.lastSearchColumn not in self.ui.tableDB.model().EditableColumns:
#                        self.ui.tableView.model().setFilterKeyColumn(self.lastSearchColumn)
#                    else:
#                        self.searchInitialized = False
#                        return rr
#                elif event.key() == QtCore.Qt.Key_Return and self.searchInitialized:
#                    self.filterTable()
#                    return rr
#                elif len(self.searchText) > 2:
#                    self.searchText += event.text()
#                    self.filterTable()
#                else:
#                    self.searchText += event.text()
#
#                logging.debug(self.searchText)
		return rr
		
                
#
#
################################################################################################

################################################################################################
#
#
        def setSearchCommentLine(self):
            if not self.searchInitialized:
                self.initializeSearch()
            else:
                self.initializeCommentLine()
#
#
################################################################################################

################################################################################################
#
#

        def initializeSearch(self):
            itemselection = self.ui.tableDB.selectedIndexes()
            
            if len(itemselection) > 0:
                self.ui.tableDB.model().setFilterKeyColumn(itemselection[0].column())
                self.searchColumn = itemselection[0].column()
            elif self.searchColumn >= 0:
                self.ui.tableDB.model().setFilterKeyColumn(self.searchColumn)
            else:
                self.searchInitialized = False
                self.ui.lineFrameComment.text('**[WARNING]: Select a table to search.**')
                return -1

            self.ui.labeLineFrameComment.setText('Search:')
            self.searchInitialized = True
            self.disconnect(self.ui.lineFrameComment,QtCore.SIGNAL('returnPressed()'),self.commitComment)
            self.disconnect(self.ui.lineFrameComment,QtCore.SIGNAL('editingFinished()'),self.commitComment)
            self.connect(self.ui.lineFrameComment,QtCore.SIGNAL('returnPressed()'),self.filterTable)
            self.connect(self.ui.lineFrameComment,QtCore.SIGNAL('editingFinished()'),self.filterTable)
            self.connect(self.ui.lineFrameComment,QtCore.SIGNAL('escapePressed()'),self.clearFilterTable)


#
#
################################################################################################

################################################################################################
#
#

        def initializeCommentLine(self):
            if self.searchInitialized:
                self.clearFilterTable()
            self.ui.labeLineFrameComment.setText('Note:')
            self.searchInitialized = False
            self.disconnect(self.ui.lineFrameComment,QtCore.SIGNAL('returnPressed()'),self.filterTable)
            self.disconnect(self.ui.lineFrameComment,QtCore.SIGNAL('editingFinished()'),self.filterTable)
            self.disconnect(self.ui.lineFrameComment,QtCore.SIGNAL('escapePressed()'),self.clearFilterTable)
            self.connect(self.ui.lineFrameComment,QtCore.SIGNAL('returnPressed()'),self.commitComment)
            self.connect(self.ui.lineFrameComment,QtCore.SIGNAL('editingFinished()'),self.commitComment)


#
#
################################################################################################

################################################################################################
#
#
	def actBeforeUpdate(self,index,record):
		
		session = self.Session()
		rr = session.query(self.Obj_CID).filter(self.Obj_CID.id==index+1)[0]
		logging.debug('acting before update...')
		for i in range(record.count()):
			if not record.field(i).isNull():
				if record.field(i).name() == 'FILENAME':
					if os.path.join(str(rr.PATH),str(rr.FILENAME)) != os.path.join(str(rr.PATH),str(record.field(i).value().toString())):
						shutil.copy(os.path.join(str(rr.PATH),str(rr.FILENAME)),os.path.join(str(rr.PATH),str(record.field(i).value().toString())))
				elif record.field(i).name() == 'OBJECT':
					hdu = pyfits.open(os.path.join(str(rr.PATH),str(rr.FILENAME)),mode='update')
					#hdu.verify('fix')
					hdu[0].header.update('OBJECT', str(record.field(i).value().toString()))
					#pyfits.writeto(os.path.join(str(rr.PATH),str(rr.FILENAME)),hdu[0].data,hdu[0].header)
					hdu.close(output_verify='silentfix')
					
					#print record.field(i).name(),':',rr.FILENAME,'-> ',record.field(i).value().toString()
#
#
################################################################################################

################################################################################################
#
#
	def askForCommentLinePID(self):


		class askPID_UI(QtGui.QDialog):
	
		########################################################################################
		#
		#	
	
			def __init__(self):
		
				QtGui.QDialog.__init__(self)
		
				##########################################################
				#
				# Set up preferences menu
				self.pid_ui = uic.loadUi(os.path.join(uipath,'askPID.ui'),self)

		#
		#
		########################################################################################

		self.pid_ui = askPID_UI()
		self.connect(self.pid_ui.buttonBox, QtCore.SIGNAL('accepted()'), self.handleCommentLine)
		self.connect(self.pid_ui.buttonBox, QtCore.SIGNAL('rejected()'), self.closePIDUI)		
		
		self.pid_ui.show()
		
		self.pid_ui.exec_()
#
#
################################################################################################

################################################################################################
#
#
	def closePIDUI(self):
	
		self.pid_ui.close()
#
#
################################################################################################

################################################################################################
#
#
	def handleCommentLine(self):
	
		if len(self.pid_ui.lineEdit.text()) == 3:
			#print self.semester_ID.format(self.pid_ui.lineEdit.text())
			self.addCommentLine(self.semester_ID%(self.pid_ui.lineEdit.text()))
		self.pid_ui.close()
#
#
################################################################################################

################################################################################################
#
#
	def addCommentLine(self,filename):
		
		session = self.Session()
		
		finfos = {}
		keys = databaseF.frame_infos.tvDB.keys()
		for hdr in keys:
			finfos[hdr] = ''

		finfos['FILENAME'] = filename
		finfos['TIMEOBS'] = time.strftime('%H:%M:%S',time.gmtime())
		finfos['DATEOBS'] = time.strftime('%Y-%m-%dT%H:%M:%S',time.gmtime())
		finfos['INSTRUME'] = 'NOTE'
		finfos['OBJECT'] = 'NOTE'
		finfos['EXPTIME'] = 0.0
		finfos['AIRMASS'] = -1.0

		entry = self.Obj_CID(**finfos)
		session.add(entry)
		session.commit()

		infos = [' ']*len(finfos)
		for i in range(len(keys)):
			infos[i] = finfos[keys[i]]

		self.updateTable(infos)
		self.emmitReloadTableEvent('Note')

################################################################################################
#
#
	def Calibration_Helper(self):

		sMaster = self.MasterSession()

		self.calibhelp_ui = CalibHelper()

		#
		# Set up Calibration Helper UI
		#

		mquery = sMaster.query(self.Obj_DQ)[:]

		pid = np.unique([mquery[i].PID for i in range(len(mquery))]) # list of project ids
		self.calibhelp_ui.Instrument.addItem('')	

		for i in range(len(pid)):
			self.calibhelp_ui.Instrument.addItem(self.semester_ID%(pid[i]))

		self.connect(self.calibhelp_ui.Instrument, QtCore.SIGNAL('currentIndexChanged(int)'), self.readDates)
		#self.connect(self.calibhelp_ui.instConfig, QtCore.SIGNAL('currentIndexChanged(int)'), self.readDates)
		self.connect(self.calibhelp_ui.date      , QtCore.SIGNAL('currentIndexChanged(int)'), self.readCalibrations)

		self.calibhelp_ui.show()
		
		self.calibhelp_ui.exec_()
#
#
################################################################################################

################################################################################################
#
#
	def readDates(self):

		sMaster = self.MasterSession()

		qq = sMaster.query(self.Obj_CDQ).filter(self.Obj_CDQ.PID == str(self.calibhelp_ui.Instrument.currentText()))[:]

		dates = np.unique([qq[i].DATASET for i in range(len(qq))])

		self.disconnect(self.calibhelp_ui.date, QtCore.SIGNAL('currentIndexChanged(int)'), self.readCalibrations)	
		
		self.calibhelp_ui.date.clear()
		self.calibhelp_ui.calibrationInfo.clear()

		self.calibhelp_ui.date.addItem('')

		for i in range(len(dates)):
			self.calibhelp_ui.date.addItem(dates[i])
		self.calibhelp_ui.date.setCurrentIndex(0)

		self.connect(self.calibhelp_ui.date, QtCore.SIGNAL('currentIndexChanged(int)'), self.readCalibrations)

#
#
################################################################################################

################################################################################################
#
#
	def readCalibrations(self):

		sMaster = self.MasterSession()

		qq = sMaster.query(self.Obj_CDQ).filter(self.Obj_CDQ.PID == str(self.calibhelp_ui.Instrument.currentText())).filter(self.Obj_CDQ.DATASET == str(self.calibhelp_ui.date.currentText()))[:]

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
			qq = sMaster.query(self.Obj_CDQ).filter(self.Obj_CDQ.PID == str(self.calibhelp_ui.Instrument.currentText())).filter(self.Obj_CDQ.DATASET == str(self.calibhelp_ui.date.currentText())).filter(self.Obj_CDQ.OBJECT == ctype[i])[:]
			
			for j in range(len(qq)):
				
				config = qq[j].CONFIG
				nf = qq[j].NCONF				

				note = self.dqStatus[int(qq[j].STATUS)]
				cnote = ''
				if len(qq[j].CONFIGNOTE) > 1:
					note += '%s'%(Count[int(qq[j].STATUS)])
					cnote = '%s: %s\n'%(note,qq[j].CONFIGNOTE)
					Count[int(qq[j].STATUS)] += 1
		
				if int(qq[j].STATUS) > 0:
					_calNote = _calNote + cnote
					_repo += '     %(ctype)s: %(CONFIG)s %(NFILES)s [%(STAT)s]\n'%{"CONFIG" : config,
												     "NFILES" : int(nf),
												     "STAT":note,
												     "ctype":str.upper(ctype[i])}


		_repo += self._separator

		_repo += _calNote

		self.calibhelp_ui.calibrationInfo.setText( _repo )


#
#
################################################################################################

#
#
################################################################################################
# END OF CLASS SoarLog
################################################################################################
# START OF CLASS PrefMenu
################################################################################################
#
#

class PrefMenu(QtGui.QDialog):
	
################################################################################################
#
#	

	def __init__(self,tbHeader,tbSort,tableDB):
	
		QtGui.QDialog.__init__(self)

		##########################################################
		#
		# Set up preferences menu
		self.pref_ui = uic.loadUi(os.path.join(uipath,'preferences.ui'),self)
		
		self.pref_ui.tabWidget.setTabText(0,'Hide/Show')
		self.pref_ui.tabWidget.setTabText(1,'Change Order')
		#
		# Set up buttons for hidin/showing
		#
		self.connect(self.pref_ui.push2hide, QtCore.SIGNAL('clicked()'), self.prefHideSelected)
		self.connect(self.pref_ui.push2show, QtCore.SIGNAL('clicked()'), self.prefShowSelected)
		#
		# Set up table with infos on columns shown/hidden. Note that both tables
		# will contain all entries. What I do is just to hide/show the fields as the
		# user select which one he whants to show/hide!
		#
		#tbHeader = self.header_CID + databaseF.frame_infos.ExtraTableHeaders
		
		data = [ [i] for i in tbHeader ]
		
		dataMask = np.zeros(len(tbHeader)) == 0
		
		for i in range(len(tbHeader)):
			dataMask[i] = tableDB.isColumnHidden(i)
		
		
		showModel = SOLogTableModel(data,["Show"] ,commitDB=self.doNothing)
		hideModel = SOLogTableModel(data,["Hide"] ,commitDB=self.doNothing)
		
		self.pref_ui.listVis.setModel(showModel)
		self.pref_ui.listHide.setModel(hideModel)
		
		for i in range(len(tbHeader)):
			if dataMask[i]: 
				self.pref_ui.listVis.setRowHidden(i,True)
			else:
				self.pref_ui.listHide.setRowHidden(i,True)
		#
		# Set up table for changing order of information.
		#
		sortModel = SOLogTableModel([data[i] for i in tbSort],["Sort"] ,commitDB=self.doNothing)		
					
		self.pref_ui.listSort.setModel(sortModel)
		self.pref_ui.listSort.dragEnabled()
		self.pref_ui.listSort.acceptDrops()
		self.pref_ui.listSort.showDropIndicator()
		self.pref_ui.listSort.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
		self.pref_ui.listSort.setDefaultDropAction(QtCore.Qt.MoveAction)
#		self.pref_ui.listSort.setDragEnabled(True)
#		self.pref_ui.listSort.setAcceptDrops(True)
#		self.pref_ui.listSort.__class__.dragMoveEvent = self.dragMoveEvent
#		self.pref_ui.listSort.__class__.dragEnterEvent = self.dragEnterEvent
#		self.pref_ui.listSort.__class__.startDrag = self.startDrag
#		self.MasterDropEvent = self.pref_ui.listSort.__class__.dropEvent
#		self.pref_ui.listSort.__class__.dropEvent = self.dropEvent				

#
#
################################################################################################
			
################################################################################################
#
#
	def dropEvent(self, event): 
		#print 'dropping'
		txt = event.mimeData().data('text/xml')
		item = QtGui.QListWidgetItem(txt,self)     #os.path.basename(url)
		event.accept()

		#		super(DragAndDropList, self).dropEvent(event) 
		#self.itemMoved.emit(self.drag_row, self.row(self.drag_item), 
#							self.drag_item) 
		#self.drag_item = None 
#
#
################################################################################################

################################################################################################
#
#
			
#	def startDrag(self, supportedActions): 
		#print 'start Dragging...'
#		self.drag_item = self.pref_ui.listSort.currentItem() 
#		self.drag_row = self.row(self.drag_item) 
#		super(DragAndDropList, self).startDrag(supportedActions) 

#
#
################################################################################################

################################################################################################
#
#

	def dragMoveEvent(self, event):
		#print 'start move'
		#if event.mimeData().hasUrls:
		#event.setDropAction(QtCore.Qt.CopyAction)
		event.accept()
		#else:
		#event.ignore()

#
#
################################################################################################

################################################################################################
#
#

	def dragEnterEvent(self, event):
		event.accept()
#
#
################################################################################################

################################################################################################
#
#
	def prefHideSelected(self):
		
		for i in self.pref_ui.listVis.selectedIndexes():
			
			self.pref_ui.listVis.setRowHidden(i.row(),True)
			self.pref_ui.listHide.setRowHidden(i.row(),False)
		
		
		return 0
#
#
################################################################################################
	
################################################################################################
#
#
	
	def prefShowSelected(self):	
		
		for i in self.pref_ui.listHide.selectedIndexes():
			
			self.pref_ui.listVis.setRowHidden(i.row(),False)
			self.pref_ui.listHide.setRowHidden(i.row(),True)
		
		
		return 0
#
#
################################################################################################

################################################################################################
#
#
	def doNothing(self,ii):
            return 0
#
#
################################################################################################



#
#
################################################################################################
# END OF CLASS PrefMenu
################################################################################################
# START OF CLASS DataQualityUI
################################################################################################
#
#

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

#
#
################################################################################################
# END OF CLASS DataQualityUI
################################################################################################
# START OF CLASS WeatherInfo
################################################################################################
#
#

class WeatherInfo(QtGui.QDialog):
	
	################################################################################################
	#
	#	
	
	def __init__(self):
		
		QtGui.QDialog.__init__(self)
		
		##########################################################
		#
		# Set up preferences menu
		self.wi_ui = uic.loadUi(os.path.join(uipath,'getweatherinfo.ui'),self)

#
#
################################################################################################

#
#
################################################################################################
# END OF CLASS WeatherInfo
################################################################################################
# START OF CLASS CalibHelper
################################################################################################
#
#

class CalibHelper(QtGui.QDialog):
	
    ########################################################################################
    #
    #	
	
    def __init__(self):
                            
        QtGui.QDialog.__init__(self)
		
        ##########################################################
        #
        # Set up preferences menu
        self.pid_ui = uic.loadUi(os.path.join(uipath,'calibhelper.ui'),self)

        #
        #
        ########################################################################################
