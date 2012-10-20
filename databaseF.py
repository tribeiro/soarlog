
#import sqlachemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import frame_infos,pyfits


'''
Database class, interface and operations definitions to store frames from observations with SOAR. 
The basic database stores some default information about each frame. These are informations which
are common to all frames such as, filename and OBJECT, EXPTIME, UT and other common header 
parameters shared for all kind of frames. At the same time we define relational database to store 
information particular to specific instruments such as filters for imaging cameras and grating
for spectrographs. 

'''

##################################################################################################################################
#
# Baseclass with common infos
#
class FrameUI(object):
	'''
		This class provides a standard UI for interfacing a fits file with a database entry with 
		sqlalchemy. The user provide a fits file to be used as template and the class takes care
		of everything else. The class assumes the instrument name is in the header parameter 
		"INTRUME". If this is not the case, the user may provide the correct parameter via 
		instHDR argument. 
	'''
	
	def __init__(self,**template):
		
		#hdr = pyfits.getheader()
		
		for info in template.keys():
			self.__dict__[info] = template[info]
#
# End of class
#
##################################################################################################################################		

##################################################################################################################################
#
# Baseclass with common infos
#
class CommonFrame(object):
	
	'''
		This class defines the interface for the Common Information Database (CID), which stores header
		information common to all frames.
	'''
	
	infos = {}
			
	def __init__(self,**header_par):

		for i in header_par.keys():
			if i in frame_infos.CID.keys():

				cmd = 'self.%s = \'%s\''%(i,str(header_par[i]).replace('\'',''))
				exec cmd
				#print cmd
				self.infos[i] = header_par[i]

				#self.infos[i] = header_par[i]
		
		self.osiris = relationship(OSIRIS, backref="FILENAME")
		self.goodman = relationship(GOODMAN, backref="FILENAME")
		self.soi = relationship(SOI, backref="FILENAME")
		
	def __repr__(self):
		return '<CommonFrame%r>' % self.infos.values()

#
# End of class
#
##################################################################################################################################		

##################################################################################################################################
#
# class for OSIRIS infos
#
class OSIRIS(object):

	'''
		Info on OSIRIS.
	'''
	
	infos = {}	
	
	def __init__(self,**header_par):
	
		for i in header_par.keys():
			if i in frame_infos.OSIRIS_ID.keys():
				cmd = 'self.%s = \'%s\''%(i.replace('-','_'),str(header_par[i]).replace('\'',''))
				exec cmd
				self.infos[i] = header_par[i]

	def __repr__(self):
		return '<CommonFrame%r>' % self.infos.values()

#
# End of class
#
##################################################################################################################################		

##################################################################################################################################
#
# class for OSIRIS infos
#
class SPARTAN(object):

	'''
		Info on OSIRIS.
	'''
	
	infos = {}	
	
	def __init__(self,**header_par):
	
		for i in header_par.keys():
			if i in frame_infos.SPARTAN_ID.keys():
				cmd = 'self.%s = \'%s\''%(i.replace('-','_'),str(header_par[i]).replace('\'',''))
				exec cmd
				self.infos[i] = header_par[i]

	def __repr__(self):
		return '<CommonFrame%r>' % self.infos.values()

#
# End of class
#
##################################################################################################################################		

##################################################################################################################################
#
# class for GOODMAN infos
#
class GOODMAN(object):

	'''
		Info on GOODMAN.
	'''

	infos = {}
	
	def __init__(self,**header_par):
	
		for i in header_par.keys():
			if i in frame_infos.GOODMAN_ID.keys():
				cmd = 'self.%s = \'%s\''%(i.replace('-','_'),header_par[i])
				exec cmd
				self.infos[i] = header_par[i]

	def __repr__(self):
		return '<CommonFrame%r>' % self.infos.values()
#
# End of class
#
##################################################################################################################################		

##################################################################################################################################
#
# class for SOI infos
#
class SOI(object):

	'''
		Info on SOI.
	'''
	
	infos = {}
	
	def __init__(self,**header_par):
	
		for i in header_par.keys():
			if i in frame_infos.SOI_ID.keys():
				cmd = 'self.%s = \'%s\''%(i.replace('-','_'),header_par[i])
				exec cmd
				self.infos[i] = header_par[i]

	def __repr__(self):
		return '<CommonFrame%r>' % self.infos.values()

#
# End of class
#
##################################################################################################################################		


##################################################################################################################################
#
# class for SOI infos
#
class SBIG(object):

	'''
		Info on SOI.
	'''
	
	infos = {}
	
	def __init__(self,**header_par):
	
		for i in header_par.keys():
			if i in frame_infos.SBIG_ID.keys():
				cmd = 'self.%s = \'%s\''%(i.replace('-','_'),header_par[i])
				exec cmd
				self.infos[i] = header_par[i]

	def __repr__(self):
		return '<CommonFrame%r>' % self.infos.values()

#
# End of class
#
##################################################################################################################################		

