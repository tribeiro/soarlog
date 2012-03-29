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

import pyfits

from sqlalchemy import create_engine, Column, Table, MetaData, ForeignKey, Integer, String
from sqlalchemy import distinct

from sqlalchemy.orm import mapper,sessionmaker

import databaseF

import numpy as np

import os,sys

import Queue

#import thread,time
from threading import Thread

def function():
	return -1


#class soarDB(threading.Thread):
class soarDB():

################################################################################################
#
#

	def __init__(self,queue):
	
		'''
			Set up database.
		'''
		
		#####################################################
		# Setup database
		#
		#
		# Database engine, section and metadata definition
		#
		
		self.Queue = queue

		self.dbname = 'soarlog.db'
		
		self.engine = create_engine('sqlite:///{0}'.format(self.dbname) )

		self.metadata = MetaData()
	
		#
		# Creating a mapper for tvDB
		#
		file_table_TVDB = Table('SoarLogTVDB',self.metadata,Column('id', Integer, primary_key=True))
	
		for keys in databaseF.frame_infos.tvDB.keys():
		
			file_table_TVDB.append_column(databaseF.frame_infos.tvDB[keys])
	
		self.Obj_CID = type(databaseF.FrameUI(**databaseF.frame_infos.tvDB))
		
		#
		# Creating a mapper for supported instruments
		#
		
		self.file_table_INSTRUMENTS = {}
		self.Obj_INSTRUMENTS = {}
		
		for _inst in databaseF.frame_infos.instTemplates.keys():
	
			self.file_table_INSTRUMENTS[_inst] = Table(_inst,self.metadata,Column('id', Integer, primary_key=True))
			
			instTemplate = pyfits.getheader(databaseF.frame_infos.instTemplates[_inst])
			
			for keys in instTemplate.keys():
		
				self.file_table_INSTRUMENTS[_inst].append_column(Column(keys,String))

			self.Obj_INSTRUMENTS[_inst] = type(databaseF.FrameUI(**instTemplate))


	
		mapper(self.Obj_CID,file_table_TVDB)
	
		self.metadata.create_all(self.engine)	
		self.Session = sessionmaker(bind=self.engine)
		#
		# Setup Done
		#####################################################	

		self.file_table_CID = file_table_TVDB
							
#		self.setDaemon(True)


#
#
################################################################################################

################################################################################################
#
#

	def AddFrame(self,filename):
	
		if not filename:

			print '# - Filename is empty ...', filename
			return -1
		print filename
		
		# Checa se esta no banco de dados
		
		session = self.Session()

		query = session.query(self.Obj_CID.FILENAME).filter(self.Obj_CID.FILENAME == os.path.basename(str(filename)))[:]
		if len(query) > 0:
			print 'File %s already in database...' % (str(filename))
			return -1
			
		infos = databaseF.frame_infos.GetFrameInfos(str(filename))

		if infos == -1:
			print '# Could not read file %s... ' %(filename)
			return -1
		else:
			entry_CID = self.Obj_CID(**infos[1])
			
			session.add(entry_CID)

#			instKey = infos[0]['INSTRUME']

#			entry = self.Obj_INSTRUMENTS[instKey](**infos[1])
#			session.add(entry)
			session.commit()
		
		return 0
#
#
################################################################################################

################################################################################################
#
#

	def __del__(self):
		self.session_CID.commit()
		
		for session in self.session_dict.values():
			session.commit()			
#
#
################################################################################################

################################################################################################
#
#
	def runQueue(self):
	
#		thread.start_new_thread(self.run,("Thread No:1",2))

		Thread(target=self.run, args=("Thread No:1",2)).start()

		
		#self.reloadTable()
#
#
################################################################################################

################################################################################################
#
#
	def run(self,*args):

		#self.wake.wait()
		
		#ff = ''
		last = ''
		while not self.Queue.empty():
			
			ff = self.Queue.get()
#			print ff
#			time.sleep(1.0)
			info = self.AddFrame(ff)

			if type(info) == type(-1):
				print 'nothing to do'
			else:
				self.updateTable(info)
				last = ff
		
		self.reloadTable(last)
		
		#self.wake.clear()
		
		#self.run()

		
#
#
################################################################################################

################################################################################################
#
#

	def getTableData(self):
	
		session = self.Session()

		query = session.query(self.Obj_CID)
		
		data = []
		
		for queryRes in query:
		
			indata = []
		
			#
			# Pego infos Comuns
			#
			for info_id in np.array(self.header_CID):
				info = ''
				cmd = 'info = queryRes.%s' % (info_id)
				try:
					exec cmd

				except AttributeError,KeyError:
					info = ''
					pass
				
				if info_id == 'FILENAME' and info:
					info = os.path.basename(info).split('.fits')[0]

				indata.append(str(info))
			print '>>>',len(indata),
			#
			# Pego infos de instrumento
			#
			inst = queryRes.INSTRUME
			
			queryInstrument = []
					
			try:
				queryInstrument = session.query(self.obj_dict[inst]).filter(self.obj_dict[inst].FILENAME == queryRes.FILENAME)[:]
					
			except:
				
				pass

			if len(queryInstrument) > 0:
				queryInstrument = queryInstrument[0]
				
				for itr_info_id in range(len(databaseF.frame_infos.ExtraTableHeaders)):

					info_id = databaseF.frame_infos.dictTableHeaders[inst][itr_info_id]
				
					info = ''
				
					if info_id:
						
						cmd = ''
						
						if type(info_id) == type('aa'):
							cmd = 'info = queryInstrument.%s' % (info_id)
						if type(info_id) == type(['aa']):
							for itr_info in range(len(info_id)):
								cmd += 'info += queryInstrument.%s\n' % (info_id[itr_info])
						if type(info_id) == type(function):
							cmd = ''
							info = info_id(queryInstrument)
								
						try:
							exec cmd
						except AttributeError,KeyError:
							pass
				
					indata.append(str(info))
			else:
				for i in range(len(databaseF.frame_infos.ExtraTableHeaders)):
					indata.append([' '])
			
			data.append(indata)
		
#		data.append([''])

		return data



#
#
################################################################################################
						
################################################################################################
#
#
	def CommitDBTable(self,index,OBSNOTES):
		
		#OBSNOTES = '%s' % self.ui.tableDB.model().data(index,QtCore.Qt.DisplayRole).toString()
		
		session = self.Session()
		
		editFrame = session.query(self.Obj_CID).filter(self.Obj_CID.id == index.row()+1)[0]
		
		OLD_NOTES = editFrame.OBSNOTES
		
		#print '---------------'
		#print OLD_NOTES
		#print '---------------'
		#print OBSNOTES
		#print '---------------'		
		
		editFrame.OBSNOTES = '%s' % OBSNOTES
		session.commit()
		
#
#
################################################################################################

