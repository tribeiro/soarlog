
from PyQt4 import QtCore,QtGui,uic,QtSql
from sqlalchemy import Column,Integer,String,TEXT
from sqlalchemy import FLOAT as REAL


def GOODMAN_RDMODE(query):
	
	RD = {330 : '100kHz', 130 : '200kHz' , 30 : '400kHz'}
	return RD[query['PARAM26']] + ' ATT' + '{0}'.format(query['PARAM27'])

def GOODMAN_SPCONF(query):
	'''
		GOODMAN SP configuration.
	'''
	
	# Grating
	grt = '' #query.GRATNGID.split('_')[1]
	if query['GRATING'] == '<NO GRATING>':
		return 'ACQ'
	else:
		grt = query['GRATING'].split('_')[1]
	
	# Filter (yes or no)
	filter = ''
	
	if query['FILTER'] != '<NO FILTER>' or query['FILTER'] != '<NO FILTER>':
		filter = 'F'
	
	# Region 300() 600(custom,red,mid,blue) 1200(custom,m1,m2,m3,m4,m5,m6,m7)
	
	spcfg = ''
	

	grtAng = [  5. ,   7. ,  10. ,  12. ,  16.3,  18.7,  20.2,  22.2,  24.8, 27.4,  30.1]
	camAng = [ 11. ,  17. ,  20. ,  27. ,  29.5,  34.4,  39.4,  44.4,  49.6, 54.8,  60.2]
	
	if grt == '600' and ( np.abs(float(query['CAM_ANG']) - camAng[1]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[1]) < 1.0):
		
		spcfg = 'b'

	elif grt == '600' and ( np.abs(float(query['CAM_ANG']) - camAng[2]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[2]) < 1.0):
		
		spcfg = 'm'

	elif grt == '600' and ( np.abs(float(query['CAM_ANG']) - camAng[3]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[3]) < 1.0):
		
		spcfg = 'r'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[4]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[4]) < 1.0):
			spcfg = 'm1'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[5]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[5]) < 1.0):
			spcfg = 'm2'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[6]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[6]) < 1.0):
			spcfg = 'm3'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[7]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[7]) < 1.0):
			spcfg = 'm4'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[8]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[8]) < 1.0):
			spcfg = 'm5'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[9]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[9]) < 1.0):
			spcfg = 'm6'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[10]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[10]) < 1.0):
			spcfg = 'm7'
	
	else:
		spcfg = 'C'
	
	return grt+filter+spcfg
		


##################################################################################################################################
#
#

def instConfGoodman(query):
	'''
Return instrument configuration for the GOODMAN Spectrograph.
'''
    
	rdmode = query.RON_MODE

	spconf = query.SP_CONF

	binn = query.BINNING

	slit = query.SLIT

	ffilter = ''

	if query.FILTER != '<NO FILTER>':
		ffilter = query.FILTER
	elif query.FILTER2 != '<NO FILTER>':
		ffilter = query.FILTER2
    
	return spconf+' '+ffilter+' '+binn+' '+rdmode+' '+slit

#
#
##################################################################################################################################

##################################################################################################################################
#
#

def instConfOSIRIS(query):

	slit = query.SLIT
	spconf = query.SP_CONF
	binn = query.BINNING
	ffilter = 'Open'
	if query.FILTER != 'Open':
		ffilter = query.FILTER
	elif query.FILTER2 != 'Open':
  		ffilter = query.FILTER2
	grt = query.GRATING
    
	if spconf == 'ACQ':
		return spconf+' '+ffilter+' '+binn
	elif spconf == 'SP':
		return slit+' '+ffilter+' '+binn
	else:
		return ffilter+' '+binn
 
	return 'None'

#
#
##################################################################################################################################

##################################################################################################################################
#
#

def instConfSOI(query):

	binn = query.BINNING
	ffilter = query.FILTER
	if ffilter.find('Open') >= 0:
		ffilter = query.FILTER2
	
	return ffilter+' '+binn

#
#
##################################################################################################################################

##################################################################################################################################
#
#

def instConfSPARTAN(query):
    
    return query.FILTER+' '+query.FILTER2+' '+query.SLIT

#
#
##################################################################################################################################
