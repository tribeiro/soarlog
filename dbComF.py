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
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import mapper,sessionmaker

import databaseF

import numpy as np

import os,sys,shutil

import Queue

#import thread,time
#from threading import Thread
import threading 
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

def function():
	return -1


#class soarDB(threading.Thread):
class soarDB():

	dbname = 'soarlog.db'
	masterDBName = '.soarMaster.db'

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
		self.initThreadLock = threading.RLock()
		
		self.engine = create_engine('sqlite:///{0}'.format(self.dbname) )
		self.masterEngine = create_engine('sqlite:///{0}'.format(self.masterDBName) )

		self.metadata = MetaData()
		
		self.Base = declarative_base()
	
		#
		# Creating a mapper for tvDB
		#
		file_table_TVDB = Table('SoarLogTVDB',self.metadata,Column('id', Integer, primary_key=True))
	
		for keys in databaseF.frame_infos.tvDB.keys():
		
			file_table_TVDB.append_column(databaseF.frame_infos.tvDB[keys])

		class FrameUI(object):
			def __init__(self,**template):
				for info in template.keys():
					self.__dict__[info] = template[info]
			def __getitem__(self,index):
				return self.__dict__[index]
#				for foreignRelation in databaseF.frame_infos.instTemplates.keys():
#					self.__dict__[foreignRelation.replace(' ','')] = databaseF.relationship(	foreignRelation, uselist=False,
#																								backref='SoarLogTVDB')
#				dqId = Column(Integer, ForeignKey('dataQualityDB.id'))
#				dataQualityDB = relationship("dataQualityDB")
	
		self.Obj_CID = type(FrameUI(**databaseF.frame_infos.tvDB))

		mapper(	self.Obj_CID,file_table_TVDB)#, properties=relation)	
		
#				properties={'addresses' : relationship(Address, backref='user', order_by=address.c.id)})
		
		#
		# Creating a mapper for weather comment
		#
		self.file_table_WC = Table('weatherComment',self.metadata,Column('id', Integer, primary_key=True))
	
		self.file_table_WC.append_column(Column('Comment',String))
	
		wc_dict = {'Comment' : ''}

		class FrameWC(object):
			def __init__(self,**template):
				for info in template.keys():
					self.__dict__[info] = template[info]
			def clone(self,source,table):
				for c in table.c:
					if not c.name.endswith('id'):
						setattr(self, c.name, getattr(source, c.name))

		
		self.Obj_WC = type(FrameWC(**wc_dict))

		self.Obj_WC.__name__ = self.Obj_WC.__name__ + '_Comment'
#		wc_obj = type(self.Obj_WC)
		mapper(self.Obj_WC,self.file_table_WC)

		#
		# Creating a mapper for supported instruments
		#
		
		self.file_table_INSTRUMENTS = {}
		self.Obj_INSTRUMENTS = {}
		relation = {}
		
		for _inst in databaseF.frame_infos.instTemplates.keys():
	
			self.file_table_INSTRUMENTS[_inst] = Table(	_inst.replace(' ',''),self.metadata,
														Column('id', Integer, primary_key=True),
														Column('frame_id',Integer, ForeignKey('SoarLogTVDB.id', onupdate="CASCADE", ondelete="CASCADE")))
			
			instTemplate = pyfits.getheader(databaseF.frame_infos.instTemplates[_inst])
			
			self.file_table_INSTRUMENTS[_inst].append_column(Column('FILENAME',String))
							
			for keys in instTemplate.keys():
		
				self.file_table_INSTRUMENTS[_inst].append_column(Column(keys,String))

			class FrameINST(object):
				def __init__(self,**template):
					for info in template.keys():
						self.__dict__[info] = template[info]
						#logging.debug('{0} = {1}'.format(info,template[info]))
					frame_id = Column('frame_id',Integer, ForeignKey('SoarLogTVDB.id'))
				def clone(self,source,table):
					for c in table.c:
						if not c.name.endswith('id'):
							setattr(self, c.name, getattr(source, c.name))


			self.Obj_INSTRUMENTS[_inst] = type(FrameINST(**instTemplate))
			
			#'addresses' : relationship(Address, backref='user', order_by=address.c.id)

			mapper(	self.Obj_INSTRUMENTS[_inst],self.file_table_INSTRUMENTS[_inst]) 

		#
		# Creating a mapper for Data Quality
		#

		self.file_table_DQ = Table('SoarDataQuality_v1',self.metadata,Column('id', Integer, primary_key=True))
		
		for keys in databaseF.frame_infos.dataQualityDB.keys():
			#print keys
			self.file_table_DQ.append_column(databaseF.frame_infos.dataQualityDB[keys])

		class dataQualityUI(object):
			def __init__(self,**template):
				for info in template.keys():
					self.__dict__[info] = template[info]

			def clone(self,source,table):
				for c in table.c:
					if not c.name.endswith('id'):
						setattr(self, c.name, getattr(source, c.name))


		self.Obj_DQ = type(dataQualityUI(**databaseF.frame_infos.dataQualityDB))
  
		self.file_table_frameDQ = Table('SoarFrameDataQuality',self.metadata,Column('id', Integer, primary_key=True))
		
		for keys in databaseF.frame_infos.frameDataQualityDB.keys():
			#print keys
			self.file_table_frameDQ.append_column(databaseF.frame_infos.frameDataQualityDB[keys])

		class frameDataQualityUI(object):
			def __init__(self,**template):
				for info in template.keys():
					self.__dict__[info] = template[info]

			def clone(self,source,table):
				for c in table.c:
					if not c.name.endswith('id'):
						setattr(self, c.name, getattr(source, c.name))


	
		self.Obj_FDQ = type(frameDataQualityUI(**databaseF.frame_infos.frameDataQualityDB))

		self.file_table_frameListDQ = Table('SoarFrameListDataQuality_v1',self.metadata,Column('id', Integer, primary_key=True))
		
		for keys in databaseF.frame_infos.frameListDataQualityDB.keys():
			#print keys
			self.file_table_frameListDQ.append_column(databaseF.frame_infos.frameListDataQualityDB[keys])

		class frameListDataQualityUI(object):
			def __init__(self,**template):
				for info in template.keys():
					self.__dict__[info] = template[info]
			def clone(self,source,table):
				for c in table.c:
					if not c.name.endswith('id'):
						setattr(self, c.name, getattr(source, c.name))

	
		self.Obj_FLDQ = type(frameListDataQualityUI(**databaseF.frame_infos.frameListDataQualityDB))

		self.file_table_CDQ = Table('SoarConfigDataQualityDB',self.metadata,Column('id', Integer, primary_key=True))
		
		for keys in databaseF.frame_infos.configDataQualityDB.keys():
			#print keys
			self.file_table_CDQ.append_column(databaseF.frame_infos.configDataQualityDB[keys])


		class configDataQualityUI(object):
			def __init__(self,**template):
				for info in template.keys():
					self.__dict__[info] = template[info]
	
			def clone(self,source,table):
				for c in table.c:
					if not c.name.endswith('id'):
						setattr(self, c.name, getattr(source, c.name))



	
		self.Obj_CDQ = type(configDataQualityUI(**databaseF.frame_infos.configDataQualityDB))

		self.file_table_RDB = Table('SoarReportDB',self.metadata,Column('id', Integer, primary_key=True))
		
		for keys in databaseF.frame_infos.reportDB.keys():
			#print keys
			self.file_table_RDB.append_column(databaseF.frame_infos.reportDB[keys])


		class reportUI(object):
			def __init__(self,**template):
				for info in template.keys():
					self.__dict__[info] = template[info]
			def clone(self,source,table):
				for c in table.c:
					if not c.name.endswith('id'):
						setattr(self, c.name, getattr(source, c.name))

	
		self.Obj_RDB = type(reportUI(**databaseF.frame_infos.reportDB))

		#
		#####
		#

		mapper(self.Obj_DQ,self.file_table_DQ)#, properties=relation)	
		mapper(self.Obj_FDQ,self.file_table_frameDQ)#, properties=relation)	
		mapper(self.Obj_FLDQ,self.file_table_frameListDQ)#, properties=relation)	
		mapper(self.Obj_CDQ,self.file_table_CDQ)#, properties=relation)	
		mapper(self.Obj_RDB,self.file_table_RDB)#, properties=relation)	
		
		self.metadata.create_all(self.engine)	
		self.Session = sessionmaker(bind=self.engine)

		self.metadata.create_all(self.masterEngine)	
		self.MasterSession = sessionmaker(bind=self.masterEngine)

		#
		# Setup Done
		#####################################################	

		session = self.Session()
		query = session.query(self.Obj_WC.Comment)[:]
		if len(query) == 0:
			info = self.Obj_WC(**{'Comment':"No weather comment."})
			session.add(info)
			session.commit()
			#winfo.wi_ui.weatherInfo.setPlainText("No weather comment.")

		self.file_table_CID = file_table_TVDB
		
		self.rthread = None
		
#		self.setDaemon(True)


#
#
################################################################################################

################################################################################################
#
#

	def AddFrame(self,filename):
	
		if not filename:

			logging.debug('# - Filename is empty ...')
			return -1
		
		# Checa se esta no banco de dados
		
		session = self.Session()

		query = session.query(self.Obj_CID.FILENAME).filter(self.Obj_CID.FILENAME == os.path.basename(str(filename)))[:]
		if len(query) > 0:
			#print 'File %s already in database...' % (str(filename))
			return -1
			
		infos = databaseF.frame_infos.GetFrameInfos(str(filename))

		if infos == -1:
			logging.debug('# Could not read file {0}... ' .format(filename))
			return -1
		else:
			entry_CID = self.Obj_CID(**infos[1])
			
			session.add(entry_CID)

			instKey = infos[0]['INSTRUME']

			entry = self.Obj_INSTRUMENTS[instKey](**infos[1])
			session.add(entry)
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
	
		if self.initThreadLock.acquire(False):
			rthread = threading.Thread(target=self.run)
			rthread.start()
			self.initThreadLock.release()
#
#
################################################################################################

################################################################################################
#
#
	def run(self,*args):

		self.initThreadLock.acquire()
		
		try:
			#self.wake.wait()
			session = self.Session()
			#ff = ''

			logging.debug('Starting queue')
			
			fframe = ''
			query = session.query(self.Obj_CID)[:]
			if len(query) > 0:
				fframe = os.path.join(query[-1].PATH,query[-1].FILENAME)
			while not self.Queue.empty():
				
				cframe = self.Queue.get()
				logging.debug('--> Working on {0}'.format(cframe))
				info = self.AddFrame(cframe)
				if info == 0:
					fframe = cframe
				logging.debug('Done')
				
			logging.debug('Ended queue. Preparing reloadTable')

			#query = session.query(self.Obj_CID)[::]
			#last = os.path.join(query[-1].PATH,query[-1].FILENAME)
			
			self.reloadTable(fframe)

			logging.debug('Thread done.')
							
			#self.wake.clear()
			
			#self.run()
		finally:
			self.initThreadLock.release()
		
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
				
				indata.append(str(info))
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
		if str(editFrame.INSTRUME) != 'NOTE': 
			editFrameInst = session.query(self.Obj_INSTRUMENTS[editFrame.INSTRUME]).filter(self.Obj_INSTRUMENTS[editFrame.INSTRUME].FILENAME == os.path.join(editFrame.PATH,editFrame.FILENAME))[:]

			if len(editFrameInst) == 0:
				logging.debug('OPERATION ERROR: No Instrument frame found on database.')
				raise IOError('OPERATION ERROR: No Instrument frame found on database.')

		#OLD_NOTES = editFrame.OBSNOTES
		#
		#print '---------------'
		#print OLD_NOTES
		#print '---------------'
		#print OBSNOTES
		#print '---------------'		
		if index.column() == 16:
			editFrame.OBSNOTES = '{0}'.format(OBSNOTES)
		if index.column() == 0:
			editFrame.OBJECT = '{0}'.format(OBSNOTES)
			editFrameInst[0].OBJECT = '{0}'.format(OBSNOTES)
			logging.debug(os.path.join(str(editFrame.PATH),str(editFrame.FILENAME)))
			hdu = pyfits.open(os.path.join(str(editFrame.PATH),str(editFrame.FILENAME)),mode='update')
			if editFrame.INSTRUME == 'Goodman Spectrograph':
				hdu[0].header.update('PARAM0', hdu[0].header['PARAM0'],"CCD Temperature, C")
				hdu[0].header.update('PARAM61',hdu[0].header['PARAM61'],"Low Temp Limit, C")
				hdu[0].header.update('PARAM62',hdu[0].header['PARAM62'],"CCD Temperature Setpoint, C")
				hdu[0].header.update('PARAM63',hdu[0].header['PARAM63'],"Operational Temp, C")        


			#hdu.verify('fix')
			hdu[0].header.update('OBJECT', '{0}'.format(OBSNOTES))
			#pyfits.writeto(os.path.join(str(rr.PATH),str(rr.FILENAME)),hdu[0].data,hdu[0].header)
			hdu.close(output_verify='silentfix')
		if index.column() == 11:
			editFrame.IMAGETYP = '{0}'.format(OBSNOTES)
			try:
				hdu = pyfits.open(os.path.join(str(editFrame.PATH),str(editFrame.FILENAME)),mode='update')
				#hdu.verify('fix')
				hdu[0].header.update(databaseF.frame_infos.INSTRUMENT_TRANSLATE[editFrame.INSTRUME]['IMAGETYP'], '{0}'.format(OBSNOTES))
				#pyfits.writeto(os.path.join(str(rr.PATH),str(rr.FILENAME)),hdu[0].data,hdu[0].header)
				hdu.close(output_verify='silentfix')
			except:
				pass
		if index.column() == 12:
			oldfile = editFrame.FILENAME
			editFrameInst[0].FILENAME = os.path.join(editFrame.PATH,str(OBSNOTES))
			try:
				editFrame.FILENAME = '{0}'.format(OBSNOTES)
				shutil.copy2(os.path.join(editFrame.PATH,oldfile),os.path.join(editFrame.PATH,str(OBSNOTES)))
			except IOError:
				editFrame.FILENAME = oldfile
				session.commit()
				raise
			#	return -1

			
			
		session.commit()
		return 0
		
#
#
################################################################################################

