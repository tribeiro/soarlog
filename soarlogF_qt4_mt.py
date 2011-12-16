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
import sys,os

import thread

import os,sys,subprocess
import numpy as np
import pyfits


from soarlogF_watch import *
from soarlogF_watch import __FALSEWATCHER__

from dbComF import *

import time

#from pyraf.iraf import set as IrafSet
#from pyraf.iraf import display
#from pyraf.iraf import mscred
#from pyraf.irafglobals import IrafError
#IrafSet(stdimage='imt4096')


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
		
class SoarLog(QtGui.QMainWindow):


	def __init__(self,*args):
	
		super(SoarLog, self).__init__()
		self.Queue = args[0]
	##########################################################
	# See if configuration directory exists. Create one 
	# otherwise.
	#
		self._CFGFilePath_ = os.path.join(os.path.expanduser('~/'),'.soarlogGUI')
	
		if not os.path.exists(self._CFGFilePath_):
			os.mkdir(self._CFGFilePath_)
		
		self._CFGFiles_ = { 'OrderInfo' : 'orderInfo.txt'	,\
							'ShowInfo' : 'showPar.txt'		,\
							'LogHeader' : 'logheader.txt'	}
		
	#
	#
	#
	##########################################################
	
		self.dir = ''
		self.logfile = 'SOARLOG_%s.txt'
		self.dataCalib = '/data/data_calib/2011B/SO2011B-%s.txt'
		
		self.AskFile2Watch()
		
		self.logfile= self.logfile % (self.dir.split('/')[-1])
					
		self.header_CID = databaseF.frame_infos.CID.keys()
		self.header_dict = { 'OSIRIS' : databaseF.frame_infos.OSIRIS_ID.keys(),\
							 'Goodman Spectrograph' : databaseF.frame_infos.GOODMAN_ID.keys() ,\
							  'SOI' : databaseF.frame_infos.SOI_ID.keys()}
		self.__WeatherComments__ = "No info available\n"
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
		
		fn = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.dir)
		self.Queue.put(fn)
		self.runQueue()
		
		#self.AddFrame(fn)
		

#
#
################################################################################################

################################################################################################
#
#

	def updateTable(self,infos):
	
		index = self.tm.rowCount(None)
		
		self.tm.insertRow(index) #,self.tm.createIndex(index,-1))

		for i in range(len( infos ) ):
			self.tm.setData(self.tm.createIndex(index,i) ,infos[i]  ,QtCore.Qt.DisplayRole)
#
#
################################################################################################
				
################################################################################################
#
#
	def reloadTable(self):

		print 'Signal Captured'
							
		#self.runQueue()
		
		data = self.getTableData()
		
		#tm = SOLogTableModel(data,self.header_CID + databaseF.frame_infos.ExtraTableHeaders,self, commitDB=self.emmitTableDataChanged)
		
		#self.ui.tableDB.setModel(tm)

		#self.tm.insertRow(self.tm.rowCount(None),self.tm.rowCount(None))
		
		#data = self.tm.arraydata
		
		if self.DLF:
			print data[-1][self.header_CID.index('FILENAME')]
			try:
				if data[-1][self.header_CID.index('INSTRUME')] == 'SOI':
					mscred.mscdisplay(data[-1][self.header_CID.index('FILENAME')]+'.fits',1)
				
				elif data[-1][self.header_CID.index('INSTRUME')] == 'Spartan IR Camera':
				
					if data[-1][self.header_CID.index('FILENAME')].find('d3') > 0:
						display(data[-1][self.header_CID.index('FILENAME')]+'.fits',1)
				
				else:
					display(data[-1][self.header_CID.index('FILENAME')]+'.fits',1)
			except:
				print 'Could not display file'
				pass

		if self.GTLF: #self.ui.actionGot_to_last_frame:
			scrollBar = self.ui.tableDB.verticalScrollBar();
			scrollBar.setValue(scrollBar.maximum());

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
		
		self.tm = SOLogTableModel(self.getTableData(), self.header_CID + databaseF.frame_infos.ExtraTableHeaders,self ,commitDB=self.emmitTableDataChanged)
		
		self.ui.tableDB.setModel(self.tm)
		
		font = QtGui.QFont("Courier New", 8)
		self.ui.tableDB.setFont(font)
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
		self.connect(self.ui.actionSave_Log,QtCore.SIGNAL('triggered()'), self.SaveLog)
		self.connect(self.ui.actionPreferences,QtCore.SIGNAL('triggered()'),self.OpenPreferences)
		#self.connect(self, QtCore.SIGNAL('reloadTableEvent(char*)'), self.reloadTable)
		self.connect(self, QtCore.SIGNAL('reloadTableEvent()'), self.reloadTable)
		self.connect(self, QtCore.SIGNAL('runQueueEvent()'), self.runQueue)
		self.connect(self, QtCore.SIGNAL('TableDataChanged(QModelIndex,QString)'), self.CommitDBTable)
		#self.connect(self, QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.CommitDBTable)

		self.connect(self.ui.actionDQ, QtCore.SIGNAL('triggered()'),self.startDataQuality)
		self.connect(self.ui.actionWI, QtCore.SIGNAL('triggered()'),self.promptWeatherComment)
		
		header = databaseF.frame_infos.CID.keys() + databaseF.frame_infos.ExtraTableHeaders
		self.ShowInfoOrder = range(len(header))

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
		
#		try :
		SavedInfoOrder = np.loadtxt(os.path.join(self._CFGFilePath_,self._CFGFiles_['OrderInfo']),dtype='int',unpack=True)
		ssort = SavedInfoOrder[1].argsort()
		SavedInfoOrder[0] = SavedInfoOrder[0][ssort]
		SavedInfoOrder[1] = SavedInfoOrder[1][ssort]
		for i in range(len(SavedInfoOrder[0])):
			self.MoveColumn( (SavedInfoOrder[0][i],SavedInfoOrder[1][i]))
			print SavedInfoOrder[0][i],' --> ',SavedInfoOrder[1][i]
		
				
#		except:
#			pass
			

		print self.OrderInfoDict


		
	#
	#	
	##########################################################


#
#
################################################################################################

################################################################################################
#
#

	def OpenPreferences(self):

		tbHeader = self.header_CID + databaseF.frame_infos.ExtraTableHeaders
		#pref_ui = PrefMenu([ tbHeader[i] for i in self.ShowInfoOrder],self.ui.tableDB)
		pref_ui = PrefMenu(tbHeader, self.ShowInfoOrder,self.ui.tableDB)
		
		pref_ui.show()
		
		if pref_ui.exec_():
			print 'Changes will be performed'
#
# Change order of table headers
#
#			print [tbHeader.index(pref_ui.listSort.model().getData(i,0)) for i in range(len(tbHeader))]
			for i in range(len(tbHeader)):
				self.MoveColumn([tbHeader.index(pref_ui.listSort.model().getData(i,0)),i])

#
# Show/hide Table columns 
#
			for i in range(len(tbHeader)):
				if not pref_ui.listVis.isRowHidden(i):
					self.ui.tableDB.showColumn(i)
				if not pref_ui.listHide.isRowHidden(i):
					self.ui.tableDB.hideColumn(i)				
			

		else:
			print 'No changes made to Layout'

		print '[DONE]'
		return 0

		
		tableModel = SOLogTableModel(data,["Teste"] ,commitDB=None)
		
		tab1 = pref_ui.tabWidget.widget(0) #.gridLayout.tableView.setModel(tableModel) #.tab.gridLayout.tableView.setModel(tableModel)
		pref_ui.tableView.setModel(tableModel)
		font = QtGui.QFont("Courier New", 8)
		#pref_ui.tabWidget.widget(0).tableView.setFont(font)

		#QtGui.QFileDialog.getExistingDirectory(self, 'Selecione diretorio da noite','~/')
		#pref_ui.prefUI()
		print pref_ui.exec_()
		print 'Done'
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
		
		print move
		#print index
		#print move

		table_header = self.ui.tableDB.horizontalHeader()
		table_header.moveSection(index,move[1])

		print self.ShowInfoOrder
		
		self.ShowInfoOrder.insert(move[1], self.ShowInfoOrder.pop(index))		
		
		#tmp = self.ShowInfoOrder[:index] + self.ShowInfoOrder[index+1:]
		
		#self.ShowInfoOrder = tmp[:move[1]] + [self.ShowInfoOrder[index]] + tmp[move[1]:]
				

		self.OrderInfoDict[move[0]] = move[1]
		#print [self.ShowInfoOrder[i] for i in move]
		
		#print move
		#print move[0], 'is in ',self.ShowInfoOrder[move[0]]
		#print move
		#print move[0],self.ShowInfoOrder[move[0]]
		print self.ShowInfoOrder
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
				
		if len(self.OrderInfoDict.keys()) > 0:
			np.savetxt(os.path.join(self._CFGFilePath_,self._CFGFiles_['OrderInfo']),zip(self.OrderInfoDict.keys(),self.OrderInfoDict.values()),fmt='%i %i')		

		file = open(os.path.join(self._CFGFilePath_,self._CFGFiles_['ShowInfo']),'w')
		
		tbHeader = self.header_CID + databaseF.frame_infos.ExtraTableHeaders

		for i in range(len(tbHeader)):
			if self.ui.tableDB.isColumnHidden(i):
				file.write('%i\n' % i)

		file.close()
		
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
		


			self.handler = EventHandler(self.emmitRunQueue,self.Queue)
			self.notifier = ThreadedNotifier(wm, self.handler)
			self.notifier.start()

			
			# Internally, 'handler' is a callable object which on new events will be called like this: handler(new_event)
			#print self.dir
			wdd = wm.add_watch(self.dir, mask, rec=True)

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
	def emmitReloadTableEvent(self):
		#self.emit(QtCore.SIGNAL("reloadTableEvent(char*)"),file)    
		self.emit(QtCore.SIGNAL("reloadTableEvent()"))    

#
#
################################################################################################

################################################################################################
#
#
	def emmitTableDataChanged(self,index):
		self.emit(QtCore.SIGNAL("TableDataChanged(QModelIndex,QString)"),index,'%s' % self.ui.tableDB.model().data(index,QtCore.Qt.DisplayRole).toString())    

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
		
		return comments+self.__WeatherComments__+'\n'
#
#
################################################################################################

################################################################################################
#
#
	def promptWeatherComment(self):
		
		winfo = WeatherInfo()
		winfo.wi_ui.weatherInfo.setPlainText(self.__WeatherComments__)
		
		if winfo.exec_():
			self.__WeatherComments__ = winfo.wi_ui.weatherInfo.toPlainText()
	
	
		return 0
#
#
################################################################################################

################################################################################################
#
#
	def GetCalibrations(self):
	
		query = self.session_CID.query(self.Obj_CID.FILENAME).filter(~self.Obj_CID.IMAGETYP.like('OBJECT'))[:]
		calib =  [str(ff[0]) for ff in query]
		
		return '''A total of %i calibration frames exists.
''' % (len(calib))
#
#
################################################################################################

################################################################################################
#
#
	def GetFrameLog(self):
	
		query = self.session_CID.query(self.Obj_CID).filter(self.Obj_CID.IMAGETYP.like('OBJECT'))[:]
		
		log = '''
{time}LT File:\t{FILENAME}
\tOBJECT: {OBJECT} 
\tNotes: {OBSNOTES}
\tX={AIRMASS} Exptime:{EXPTIME} s sm= {SEEING}
'''
		outlog = ''
		
		#
		# Resolve projects
		#
		
		fnames = np.array([ os.path.basename(str(ff.FILENAME)) for ff in query])
		
		for ff in range(len(fnames)):
			id01 = fnames[ff].find('SO')
			id02 = fnames[ff][id01:].find('_')
			fnames[ff] = fnames[ff][id01:id01+id02]
		
		proj_id = np.unique(fnames)
		
		mask = np.array([len(proj_id[i]) > 0 for i in range(len(proj_id))])

		proj_id = proj_id[mask]
		proj_id2 = proj_id
				
		for i in range(len(proj_id)):
			id01 = proj_id[i].find('-')
			proj_id[i] = proj_id[i][id01+1:]
		
		print proj_id
		
		#
		# Write log for each project
		#
		
		timeSpentLog = '''
Time Spent:
===========
'''
		for i in range(len(proj_id)):
			proj = proj_id[i]

			#
			# Calculate spended time
			#
			
			timeSpent = self.calcTime(proj)
			timeSpentLog += proj + ': %02.0f:%02.0f\n' % timeSpent

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
			
			query = self.session_CID.query(self.Obj_CID).filter(self.Obj_CID.FILENAME.like('%-'+proj_id2[i]+'%'))[:]
			obj_list = self.getObjects(query)

			print obj_list

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
		
			sumLT = -3
			for i in range(len(time)):
				if day[i].find('T') > 0:

					time[i] = day[i]
				
			sort = time.argsort()
		
			for itr in range(len(query)):

				frame = query[sort[itr]]
				time = frame.TIMEOBS
				
				writeFlag = True
				frame2 = None
				if frame.INSTRUME == 'Spartan IR Camera':
					frame2 = self.session_CID.query(self.SPARTAN_Obj).filter(self.SPARTAN_Obj.FILENAME.like(frame.FILENAME))[0]
					if frame2.DETSERNO != '66':
						writeFlag = False						
				try:
					time = time.split(':')
				except:
					time = [0,0,0]
				hrs = int(time[0].split('T')[-1])+sumLT
				if hrs > 23:
					hrs -= 23
				if hrs < 0:
					hrs += 23
				time = '%02i:%02i' % (hrs,int(time[1]))
				if writeFlag:
					outlog += log.format(time=time, FILENAME = os.path.basename(frame.FILENAME), OBJECT = frame.OBJECT, OBSNOTES = frame.OBSNOTES ,\
										 AIRMASS = frame.AIRMASS, EXPTIME = frame.EXPTIME, SEEING = frame.SEEING)
				if frame.INSTRUME == 'Goodman Spectrograph':
					frame2 = self.session_CID.query(self.GOODMAN_Obj).filter(self.GOODMAN_Obj.FILENAME.like(frame.FILENAME))[0]
					logGS = '\tGRATING: {0} SLIT: {1} OBSTYPE: {2}\n'.format(frame2.GRATING,frame2.SLIT,frame.IMAGETYP)
					outlog+=logGS

				if frame.INSTRUME == 'Spartan IR Camera' and writeFlag:
					logSP = '\tFILTER: {0} OBSTYPE: {1}\n'.format(frame2.FILTER,frame.IMAGETYP)
					outlog+=logSP

#				if frame.INSTRUME == 'OSIRIS':
#					frame2 = self.session_CID.query(self.GOODMAN_Obj).filter(self.GOODMAN_Obj.FILENAME.like(frame.FILENAME))[0]
#					logOS = '\tGRATING: {} SLIT: {} OBSTYPE: {}\n'.format(frame2.GRATING,frame2.SLIT,frame.IMAGETYP)
#					outlog+=logGS
#				
#				if frame.INSTRUME == 'SOI':
#					frame2 = self.session_CID.query(self.SOI_Obj).filter(self.SOI_Obj.FILENAME.like(frame.FILENAME))[0]
#					logSOI = '\tFILTER: {} OBSTYPE: {}\n'.format(frame2.FILTER1,frame.IMAGETYP)
#					outlog+=logGS

					
				
#outlog += databaseF.frame_infos.frameLog(frame,time)

			#inst = frame.INSTRUME
			
			#queryInstrument = self.session_dict[inst].query(self.obj_dict[inst]).filter(self.obj_dict[inst].FILENAME == queryRes.FILENAME)[:]
			
			#for info_id in databaseF.LogInfo[inst]:
				
	
		outlog += '-'*63 + '\n'
		outlog += timeSpentLog
		return outlog
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
		print self.logfile
		
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
	
		query = self.session_CID.query(self.Obj_CID.FILENAME,self.Obj_CID.DATEOBS,self.Obj_CID.TIMEOBS).filter(self.Obj_CID.FILENAME.like('%SO%'))[:]
		
		time_end = []
				
		fnames = np.array( [ str(ff.FILENAME) for ff in query] )
		hour = np.array( [ str(ff.TIMEOBS) for ff in query] )
		day = np.array( [ str(ff.DATEOBS) for ff in query] )
		
		time = np.array( [ day[i]+'T'+hour[i] for i in range(len(hour)) ] )
		
		for i in range(len(time)):
			if day[i].find('T') > 0:
				time[i] = day[i]
				
		sort = time.argsort()

		#print time, time[sort]
		
		fnames = fnames[sort]
		
		find_proj = np.array( [ i for i in range(len(fnames)) if fnames[i].find('-'+id) > 0] )
		
		time_start = np.append([int(find_proj[0])], np.array( [ find_proj[i] for i in range(len(find_proj)-2) if find_proj[i] != find_proj[i+1]-1 ] ) )
		time_end = np.append( np.array( [ find_proj[i] for i in range(len(find_proj)-2,0,-1) if find_proj[i] != find_proj[i-1]+1 ] ), [int(find_proj[-1])] )
		#print find_proj
		
		time_tmp = np.append(time_start , time_end  )
		
#		print time_tmp
#		print time_tmp[1]
				
#		time_start = time_tmp[0]
#		time_end = time_tmp[1]
		
		time.sort()
		
		calcT = 0
		try:
			for i in range(0,len(time_tmp),2):
		
				dia_start,hora_start = time[time_tmp[i]].split('T')
				dia_end,hora_end = time[time_tmp[i+1]].split('T')
			
				ano1,mes1,dia1 = dia_start.split('-')
				hr1,min1,sec1 = hora_start.split(':')
			
				ano2,mes2,dia2 = dia_end.split('-')
				hr2,min2,sec2 = hora_end.split(':')
			
				start = float(ano1)*365.+float(mes1)*30.+float(dia1)+float(hr1)/24.+float(min1)/24./60.
				end = float(ano2)*365.+float(mes2)*30.+float(dia2)+float(hr2)/24.+float(min2)/24./60.
			
				calcT += (end-start)*24.0
				print start, end, (end-start)*24.0
			
			print id, [ time[i] for i in time_start ], [time[i] for i in time_end], '%02.0f:%02.0f' %( np.floor(calcT), (calcT-np.floor(calcT))*60)

		except:
			print 'Failed to obtain program time'
			
			
			
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
	def startDataQuality(self):

		dataQuality_ui = DataQualityUI()
		
		dataQuality_ui.show()
		
		dataQuality_ui.exec_()

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
		print 'dropping'
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
			
	def startDrag(self, supportedActions): 
		print 'start Dragging...'
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
		print 'start move'
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
		print 'enter drag'
		print event.mimeData().data('text/xml')
		print event.proposedAction()
		#if event.mimeData().hasFormat('text/plain'):
		#	event.acceptProposedAction()
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
# END OF CLASS SoarLog
################################################################################################
# START OF CLASS PrefMenu
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
# END OF CLASS SoarLog
################################################################################################
# START OF CLASS PrefMenu
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
