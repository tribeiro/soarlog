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

from sqlalchemy import create_engine, Column, Table, MetaData, ForeignKey, Integer
from sqlalchemy import distinct

from sqlalchemy.orm import mapper,sessionmaker

import databaseF

import numpy as np

import os

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
	
	
#		threading.Thread.__init__(self)
		self.Queue = None
#		self.wake = threading.Event()
		
#		self.local = threading.local()
			
		#####################################################
		# Setup database
		#
		#
		# Database engine, section and metadata definition
		#
		
		self.Queue = queue


		self.engine = create_engine('sqlite:///soarlog.db' )

		self.metadata = MetaData()
	
		#
		# Creating a mapper for CID
		#
		file_table_CID = Table('SoarLogDB',self.metadata,Column('id', Integer, primary_key=True))
	
		for keys in databaseF.frame_infos.CID.keys():
		
			file_table_CID.append_column(databaseF.frame_infos.CID[keys])
	
		#self.metadata.create_all(self.engine)	
		#file_table.drop(engine)

		#
		# Creating a mapper for OSIRIS information DB
		#
	
		file_table_OSIRIS = Table('OSIRIS_DB',self.metadata,Column('id', Integer, primary_key=True))
	
		for keys in databaseF.frame_infos.OSIRIS_ID.keys():
		
			file_table_OSIRIS.append_column(databaseF.frame_infos.OSIRIS_ID[keys])

		#
		# Creating a mapper for SPARTAN information DB
		#
	
		file_table_SPARTAN = Table('SPARTAN_DB',self.metadata,Column('id', Integer, primary_key=True))
	
		for keys in databaseF.frame_infos.SPARTAN_ID.keys():
		
			file_table_SPARTAN.append_column(databaseF.frame_infos.SPARTAN_ID[keys])

		#
		# Creating a mapper for GOODMAN information DB
		#

		file_table_GOODMAN = Table('GOODMAN_DB',self.metadata,Column('id', Integer, primary_key=True))
	
		for keys in databaseF.frame_infos.GOODMAN_ID.keys():
		
			file_table_GOODMAN.append_column(databaseF.frame_infos.GOODMAN_ID[keys])


		#
		# Creating a mapper for SOI information DB
		#

		file_table_SOI = Table('SOI_DB',self.metadata,Column('id', Integer, primary_key=True))
	
		for keys in databaseF.frame_infos.SOI_ID.keys():
		
			file_table_SOI.append_column(databaseF.frame_infos.SOI_ID[keys])


		#
		# Creating a mapper for SBIG information DB
		#

		file_table_SBIG = Table('SBIG_DB',self.metadata,Column('id', Integer, primary_key=True))
	
		for keys in databaseF.frame_infos.SBIG_ID.keys():
		
			file_table_SBIG.append_column(databaseF.frame_infos.SBIG_ID[keys])


		self.Obj_CID = type(databaseF.CommonFrame(**databaseF.frame_infos.CID))
	
		mapper(self.Obj_CID,file_table_CID)
	
		self.metadata.create_all(self.engine)	
		self.Session = sessionmaker(bind=self.engine)

		self.session_CID = self.Session()

		self.OSIRIS_Obj = type(databaseF.OSIRIS(**databaseF.frame_infos.OSIRIS_ID))
		self.GOODMAN_Obj = type(databaseF.GOODMAN(**databaseF.frame_infos.GOODMAN_ID))
		self.SOI_Obj = type(databaseF.SOI(**databaseF.frame_infos.SOI_ID))
		self.SPARTAN_Obj = type(databaseF.SPARTAN(**databaseF.frame_infos.SPARTAN_ID))
		self.SBIG_Obj = type(databaseF.SBIG(**databaseF.frame_infos.SBIG_ID))

		mapper(self.OSIRIS_Obj,file_table_OSIRIS)	
		self.Session_OSIRIS = sessionmaker(bind=self.engine)
		self.session_OSIRIS = self.Session_OSIRIS()

		mapper(self.SPARTAN_Obj,file_table_SPARTAN)	
		self.Session_SPARTAN = sessionmaker(bind=self.engine)
		self.session_SPARTAN = self.Session_SPARTAN()


		mapper(self.SBIG_Obj,file_table_SBIG)	
		self.Session_SBIG = sessionmaker(bind=self.engine)
		self.session_SBIG = self.Session_SBIG()


		mapper(self.GOODMAN_Obj,file_table_GOODMAN)	
		self.Session_GOODMAN = sessionmaker(bind=self.engine)
		self.session_GOODMAN = self.Session_GOODMAN()

		mapper(self.SOI_Obj,file_table_SOI)	
		self.Session_SOI = sessionmaker(bind=self.engine)
		self.session_SOI = self.Session_SOI()

		self.obj_dict = {'OSIRIS' : self.OSIRIS_Obj,\
		'Goodman Spectrograph' : self.GOODMAN_Obj ,\
		'SOI' : self.SOI_Obj ,\
		'Spartan IR Camera' : self.SPARTAN_Obj,
		'SBIG ST-L' : self.SBIG_Obj}
		
		self.session_dict = {'OSIRIS' : self.session_OSIRIS,\
		'Goodman Spectrograph' : self.session_GOODMAN,\
		'SOI' : self.session_SOI ,\
		'Spartan IR Camera' : self.session_SPARTAN,
		'SBIG ST-L' : self.session_SBIG}

		#
		# Setup Done
		#####################################################	

		self.header_CID = databaseF.frame_infos.CID.keys()
		self.header_dict = { 'OSIRIS' : databaseF.frame_infos.OSIRIS_ID.keys(),\
							 'Goodman Spectrograph' : databaseF.frame_infos.GOODMAN_ID.keys() ,\
							  'SOI' : databaseF.frame_infos.SOI_ID.keys(),\
							  'Spartan IR Camera' : databaseF.frame_infos.SPARTAN_ID.keys()}

		self.file_table_CID = file_table_CID
		self.file_table_dict = {	'OSIRIS'	:	file_table_OSIRIS	,\
							'SOI'		:	file_table_SOI		,\
							'Goodman Spectrograph'	:	file_table_GOODMAN ,\
							'Spartan IR Camera' : file_table_SPARTAN}
							
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

		query = session.query(self.Obj_CID.FILENAME).filter(self.Obj_CID.FILENAME == str(filename))[:]
		if len(query) > 0:
			print 'File %s already in database...' % (str(filename))
			return -1
			
		infos = databaseF.frame_infos.GetFrameInfos(str(filename))

		if infos == -1:
			print '# Could not read file %s... ' %(filename)
			return -1
		else:
			entry_CID = self.Obj_CID(**infos[0])
			
			session.add(entry_CID)
			#session_CID.commit()
			
			
			instKey = infos[0]['INSTRUME']
			#mapper(self.obj_dict[instKey],self.file_table_dict[instKey])	
			#Session_Inst = sessionmaker(bind=self.engine)

			entry = self.obj_dict[instKey](**infos[1])
			session.add(entry)
			session.commit()
			
			infos = []
		
			#
			# Pego infos Comuns
			#
			for info_id in np.array(self.header_CID):

				cmd = 'info = entry_CID.%s' % (info_id)
				try:
					exec cmd

				except AttributeError,KeyError:
					info = ''
					pass
				
				if info_id == 'FILENAME':
					info = os.path.basename(info).split('.fits')[0]

				infos.append(str(info))
			#
			# Pego infos de instrumento
			#
			inst = instKey
			
			queryInstrument = entry

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
				
				infos.append(str(info))
			

			return infos
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
		while not self.Queue.empty():
			
			ff = self.Queue.get()
#			print ff
#			time.sleep(1.0)
			info = self.AddFrame(ff)

			if type(info) == type(-1):
				print 'nothing to do'
			else:
				self.updateTable(info)
				
		
		self.reloadTable()
		
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

				cmd = 'info = queryRes.%s' % (info_id)
				try:
					exec cmd

				except AttributeError,KeyError:
					info = ''
					pass
				
				if info_id == 'FILENAME':
					info = os.path.basename(info).split('.fits')[0]

				indata.append(str(info))
			#
			# Pego infos de instrumento
			#
			inst = queryRes.INSTRUME
			
			queryInstrument = session.query(self.obj_dict[inst]).filter(self.obj_dict[inst].FILENAME == queryRes.FILENAME)[:]

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
				indata.append([' ']*len(databaseF.frame_infos.ExtraTableHeaders))
			
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
		
		print '---------------'
		print OLD_NOTES
		print '---------------'
		print OBSNOTES
		print '---------------'		
		
		editFrame.OBSNOTES = '%s' % OBSNOTES
		session.commit()
		
#
#
################################################################################################

