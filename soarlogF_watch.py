
import databaseF
import sys,os
from sqlalchemy import create_engine, Column, Table, MetaData, ForeignKey, Integer
from sqlalchemy.orm import mapper,sessionmaker
import Queue
import logging

try:

	import pyinotify
	from pyinotify import ThreadedNotifier


	__FALSEWATCHER__ = False

	# The watch manager stores the watches and provides operations on watches
	wm = pyinotify.WatchManager()

	mask = pyinotify.IN_CLOSE_WRITE  # watched events

	class EventHandler(pyinotify.ProcessEvent):
	
		MyObj = type(databaseF.CommonFrame(**databaseF.frame_infos.CID))

		def __init__(self,target_event,queue):
			
			
#			self.session = session
#			self.AddFunc = AddFunc
			self.target_event = target_event
			self.fileQueue = queue
			self.Qsize = 0
			
			
		def process_IN_CLOSE_WRITE(self, event):

			path = os.path.dirname(event.pathname)
			fname = os.path.basename(event.pathname)
			#print "File closed:", event.pathname
			
			#
			# test if is a fits file
			#
			try:
				
				findex = fname.index('.fits')
				#
				# handle temporary files from rsync!
				#
				# len('.fits') = 5!
				if findex+5 != len(fname):
					fname = fname[1:findex]+'.fits'
			
			except ValueError:
				logging.debug(sys.exc_info()[1])
				 # File is not a fits, stop process
				return -1

			#
			# CHECAR SE EXISTE IMAGEM NO BANCO DE DADOS. EM CASO AFIRMATIVO, LE INFOS E FAZ UM 'UPDATE'.
			# TAMBEM POSSO INTERROMPER O PROCEDIMENTO E NAO FAZER NADA. NAO SEI O QUE EH MELHOR.
			#
			
			#infos = databaseF.frame_infos.GetFrameInfos(os.path.join(path,fname))
			
			#if infos == -1:
			#	print 'Unable to read file header (%s).' % (fname)
			#	return -1
			#
			# Apesar de parecer meio idiota fazer a inclusao na lista e no banco de dados nesta thread, no fim
			# acaba sendo uma coisa boa pois nao ocupa a thread que esta gerenciando a janela. 
			#
			#entry = self.MyObj(**infos[0])
			
			#
			# Testa se frame ja esta no banco de dados.
			#
			#query = self.session.query(self.MyObj.FILENAME).filter(self.MyObj.FILENAME == entry.FILENAME)
			
			#print query.FILENAME
			
			#self.session.add(entry)
			self.fileQueue.put(os.path.join(path,fname))
			
			#if self.fileQueue.qsize() < 2:
			self.target_event()
			

			self.Qsize = self.fileQueue.qsize()
			#self.AddFunc(entry.FILENAME)
			#self.target_event()
			#
			#self.AddFunc() # update table
			
			#
			# Este evento eh responsavel por atualizar a informacao mostrada na tela. Note que, no caso de 
			# mudarmos o layout para o esquema de lista (como sugerido pelo Luciono e como utilizado pelo
			# Segio) este procedimento se torna completamente dispensavel!
			#

			#infos = databaseF.frame_infos.GetFrameInfos(dirList[i])
			
			

		def process_IN_DELETE(self, event):
			print "Removing:", event.pathname

		def process_IN_Create(self, event):
			print "Creating:", event.pathname
        
	
except ImportError:

	__FALSEWATCHER__ = True
	
	def EventHandler(session,AddFunc):
		return 0

	class ThreadedNotifier():
	
		def __init__(self,arg1,arg2):
			return None
			
		def start(self):
			return 0
		def stop(self):
			return 0

	class FalseWatcher():
		def add_watch(arg1,arg2,*args,**kwargs):
			return 0
			
	mask = False

	wm = FalseWatcher()

	
